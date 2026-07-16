from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing the extension package without launching the WebUI.
EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

from lib_dynamic_placeholders.library import PlaceholderLibrary
from lib_dynamic_placeholders.resolver import PlaceholderResolver, expand_placeholders


class LibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "pose.txt").write_text(
            "# comment\n\njumping\nsitting\nstanding\n",
            encoding="utf-8",
        )
        furniture = self.root / "furniture"
        furniture.mkdir()
        (furniture / "sofa.txt").write_text(
            "leather sofa\nvelvet chaise longue\n",
            encoding="utf-8",
        )
        (self.root / "scene.txt").write_text(
            "a quiet rainy street at dusk\nan overgrown greenhouse\n",
            encoding="utf-8",
        )
        self.library = PlaceholderLibrary(self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_list_placeholders(self):
        names = self.library.list_placeholders()
        self.assertEqual(names, ["furniture/sofa", "pose", "scene"])

    def test_skips_comments_and_blanks(self):
        self.assertEqual(
            self.library.get_values("pose"),
            ["jumping", "sitting", "standing"],
        )

    def test_nested_path(self):
        self.assertEqual(
            self.library.get_values("furniture/sofa"),
            ["leather sofa", "velvet chaise longue"],
        )

    def test_long_lines_preserved(self):
        values = self.library.get_values("scene")
        self.assertIn("a quiet rainy street at dusk", values)
        self.assertTrue(all(" " in v for v in values))


class ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "pose.txt").write_text("jumping\nsitting\n", encoding="utf-8")
        (self.root / "furniture.txt").write_text("chair\nsofa\n", encoding="utf-8")
        (self.root / "a.txt").write_text("prefix __b__\n", encoding="utf-8")
        (self.root / "b.txt").write_text("nested-value\n", encoding="utf-8")
        (self.root / "loop_a.txt").write_text("__loop_b__\n", encoding="utf-8")
        (self.root / "loop_b.txt").write_text("__loop_a__\n", encoding="utf-8")
        self.library = PlaceholderLibrary(self.root)
        self.resolver = PlaceholderResolver(self.library)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_basic_replacement(self):
        result = self.resolver.expand("a man __pose__ on a __furniture__", seed=0)
        self.assertNotIn("__pose__", result)
        self.assertNotIn("__furniture__", result)
        self.assertTrue(result.startswith("a man "))
        self.assertIn(" on a ", result)

    def test_seed_reproducibility(self):
        prompt = "a man __pose__ on a __furniture__"
        a = self.resolver.expand(prompt, seed=42)
        b = self.resolver.expand(prompt, seed=42)
        c = self.resolver.expand(prompt, seed=99)
        self.assertEqual(a, b)
        self.assertNotIn("__pose__", c)
        self.assertNotIn("__furniture__", c)

    def test_unknown_left_in_place(self):
        result = self.resolver.expand("hello __missing__", seed=1)
        self.assertEqual(result, "hello __missing__")

    def test_unknown_removed_when_configured(self):
        resolver = PlaceholderResolver(self.library, leave_unresolved=False)
        result = resolver.expand("hello __missing__ world", seed=1)
        self.assertEqual(result, "hello  world")

    def test_nested_expansion(self):
        result = self.resolver.expand("look __a__", seed=0)
        self.assertEqual(result, "look prefix nested-value")

    def test_circular_does_not_hang(self):
        result = self.resolver.expand("__loop_a__", seed=0)
        # Cycle is left unresolved rather than spinning forever.
        self.assertIn("__", result)

    def test_convenience_helper(self):
        result = expand_placeholders(
            "__pose__",
            library=self.library,
            seed=0,
        )
        self.assertIn(result, {"jumping", "sitting"})

    def test_bundled_samples_exist(self):
        samples = EXTENSION_ROOT / "placeholders"
        self.assertTrue((samples / "pose.txt").is_file())
        self.assertTrue((samples / "furniture.txt").is_file())
        lib = PlaceholderLibrary(samples)
        pose = lib.get_values("pose")
        furniture = lib.get_values("furniture")
        self.assertGreaterEqual(len(pose), 4)
        self.assertGreaterEqual(len(furniture), 4)
        # Longer phrase present in sample data
        self.assertTrue(any(len(v.split()) > 2 for v in pose))

        prompt = "a man __pose__ on a __furniture__"
        expanded = PlaceholderResolver(lib).expand(prompt, seed=7)
        self.assertRegex(expanded, r"^a man .+ on a .+$")
        self.assertNotIn("__pose__", expanded)
        self.assertNotIn("__furniture__", expanded)


class PatternEdgeCaseTests(unittest.TestCase):
    def test_custom_wrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mood.txt").write_text("cheerful\n", encoding="utf-8")
            resolver = PlaceholderResolver(
                PlaceholderLibrary(root),
                wrap="@@",
            )
            self.assertEqual(resolver.expand("feel @@mood@@", seed=0), "feel cheerful")


if __name__ == "__main__":
    unittest.main()
