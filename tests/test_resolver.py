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

    def test_composable_hair_expands_all_nested_tokens(self):
        """A parent list line can compose multiple child placeholders."""
        (self.root / "hair.txt").write_text(
            "__hair/length__ __hair/color__ __hair/style__ hair\n",
            encoding="utf-8",
        )
        hair_dir = self.root / "hair"
        hair_dir.mkdir()
        (hair_dir / "length.txt").write_text("short\nlong\n", encoding="utf-8")
        (hair_dir / "color.txt").write_text("blonde\nbrunette\n", encoding="utf-8")
        (hair_dir / "style.txt").write_text("ponytail\nloose waves\n", encoding="utf-8")

        result = self.resolver.expand("portrait of a woman with __hair__", seed=0)

        self.assertNotIn("__hair__", result)
        self.assertNotIn("__hair/length__", result)
        self.assertNotIn("__hair/color__", result)
        self.assertNotIn("__hair/style__", result)
        self.assertTrue(result.startswith("portrait of a woman with "))
        self.assertTrue(result.endswith(" hair"))

        # All three child lists contributed a concrete value.
        length = next(v for v in ("short", "long") if f" {v} " in f" {result} ")
        color = next(v for v in ("blonde", "brunette") if v in result)
        style = next(v for v in ("ponytail", "loose waves") if v in result)
        self.assertIn(length, result)
        self.assertIn(color, result)
        self.assertIn(style, result)

    def test_underscore_names_are_valid_placeholders(self):
        (self.root / "hair_color.txt").write_text("auburn\n", encoding="utf-8")
        result = self.resolver.expand("__hair_color__", seed=0)
        self.assertEqual(result, "auburn")

    def test_multi_level_composition(self):
        """Parent → child → grandchild all expand in one pass chain."""
        (self.root / "outfit.txt").write_text("wearing __top__\n", encoding="utf-8")
        (self.root / "top.txt").write_text("a __color__ blouse\n", encoding="utf-8")
        (self.root / "color.txt").write_text("crimson\n", encoding="utf-8")
        result = self.resolver.expand("__outfit__", seed=0)
        self.assertEqual(result, "wearing a crimson blouse")

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
        self.assertTrue((samples / "hair.txt").is_file())
        self.assertTrue((samples / "hair" / "length.txt").is_file())
        self.assertTrue((samples / "hair" / "color.txt").is_file())
        self.assertTrue((samples / "hair" / "style.txt").is_file())
        self.assertTrue((samples / "clothes.txt").is_file())
        self.assertTrue((samples / "clothes" / "head.txt").is_file())
        self.assertTrue((samples / "clothes" / "torso.txt").is_file())
        for layer in (
            "scarf",
            "fullbody",
            "pants",
            "shoes",
            "accessories",
        ):
            self.assertTrue((samples / "clothes" / f"{layer}.txt").is_file())
        for layer in ("hat", "glasses", "piercings"):
            self.assertTrue((samples / "clothes" / "head" / f"{layer}.txt").is_file())
        for layer in ("shirt", "jacket"):
            self.assertTrue((samples / "clothes" / "torso" / f"{layer}.txt").is_file())
        lib = PlaceholderLibrary(samples)

        # Bundled composable hair fully resolves nested tokens.
        haired = PlaceholderResolver(lib).expand(
            "a woman with __hair__",
            seed=3,
        )
        self.assertNotIn("__", haired)
        self.assertTrue(haired.startswith("a woman with "))

        # Bundled composable clothes fully resolves nested tokens.
        clothed = PlaceholderResolver(lib).expand(
            "a person __clothes__",
            seed=3,
        )
        self.assertNotIn("__", clothed)
        self.assertTrue(clothed.startswith("a person "))

    def test_bundled_hair_composition_variants(self):
        samples = EXTENSION_ROOT / "placeholders"
        resolver = PlaceholderResolver(PlaceholderLibrary(samples))
        for seed in range(12):
            result = resolver.expand("__hair__", seed=seed)
            self.assertNotIn("__hair/length__", result)
            self.assertNotIn("__hair/color__", result)
            self.assertNotIn("__hair/style__", result)
            self.assertNotIn("__hair__", result)

    def test_bundled_clothes_composition_variants(self):
        samples = EXTENSION_ROOT / "placeholders"
        resolver = PlaceholderResolver(PlaceholderLibrary(samples))
        for seed in range(40):
            result = resolver.expand("__clothes__", seed=seed)
            self.assertNotIn("__clothes/", result)
            self.assertNotIn("__clothes__", result)

        # Separates vs fullbody stay mutually exclusive in composition lines.
        lines = [
            line.strip()
            for line in (samples / "clothes.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        separates = [
            line
            for line in lines
            if "__clothes/torso__" in line or "__clothes/pants__" in line
        ]
        fullbody = [line for line in lines if "__clothes/fullbody__" in line]
        self.assertGreaterEqual(len(separates), 12)
        self.assertGreaterEqual(len(fullbody), 12)
        self.assertEqual(len(lines), len(separates) + len(fullbody))

        for line in lines:
            has_fullbody = "__clothes/fullbody__" in line
            has_torso = "__clothes/torso__" in line
            has_pants = "__clothes/pants__" in line
            self.assertFalse(
                has_fullbody and has_torso,
                f"composition mixes fullbody with torso: {line!r}",
            )
            self.assertFalse(
                has_fullbody and has_pants,
                f"composition mixes fullbody with pants: {line!r}",
            )
            # Separates always keep torso + pants together.
            if has_torso or has_pants:
                self.assertTrue(
                    has_torso and has_pants,
                    f"separates line missing torso or pants: {line!r}",
                )

        # Head and torso group files resolve their nested children.
        for seed in range(12):
            head = resolver.expand("__clothes/head__", seed=seed)
            self.assertNotIn("__clothes/head/", head)
            self.assertNotIn("__clothes/head__", head)
            torso = resolver.expand("__clothes/torso__", seed=seed)
            self.assertNotIn("__clothes/torso/", torso)
            self.assertNotIn("__clothes/torso__", torso)

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
