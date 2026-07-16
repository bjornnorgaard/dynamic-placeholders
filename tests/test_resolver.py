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

    def test_lookup_missing_vs_empty(self):
        (self.root / "blank.txt").write_text("# comment only\n\n", encoding="utf-8")
        missing = self.library.lookup("nope")
        self.assertEqual(missing.status, "missing")
        self.assertEqual(missing.values, [])
        self.assertIsNone(missing.path)

        empty = self.library.lookup("blank")
        self.assertEqual(empty.status, "empty")
        self.assertEqual(empty.values, [])
        self.assertEqual(empty.path, self.root / "blank.txt")

        ok = self.library.lookup("pose")
        self.assertEqual(ok.status, "ok")
        self.assertTrue(ok.ok)
        self.assertEqual(ok.values, ["jumping", "sitting", "standing"])


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

    def test_missing_placeholder_emits_visible_warning(self):
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf), self.assertLogs(
            "lib_dynamic_placeholders.console", level="WARNING"
        ) as logs:
            self.resolver.expand("hello __missing__", seed=1)
        printed = buf.getvalue()
        self.assertIn("placeholder not resolved", printed)
        self.assertIn("__missing__", printed)
        self.assertIn("no matching list file found", printed)
        self.assertIn("missing.txt", printed)
        self.assertTrue(
            any("placeholder not resolved" in r.getMessage() for r in logs.records)
        )

    def test_empty_placeholder_file_emits_distinct_warning(self):
        from io import StringIO
        from unittest.mock import patch

        (self.root / "blank.txt").write_text("# only comments\n\n", encoding="utf-8")
        buf = StringIO()
        with patch("sys.stdout", buf):
            self.resolver.expand("hello __blank__", seed=1)
        printed = buf.getvalue()
        self.assertIn("list file has no usable values", printed)
        self.assertIn("blank.txt", printed)

    def test_missing_placeholder_warning_is_deduped(self):
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf):
            self.resolver.expand("__missing__ and again __missing__", seed=1)
            self.resolver.expand("still __missing__", seed=2)
        printed = buf.getvalue()
        self.assertEqual(printed.count("placeholder not resolved"), 1)

    def test_missing_directory_warning(self):
        from io import StringIO
        from unittest.mock import patch

        missing_root = self.root / "does-not-exist"
        resolver = PlaceholderResolver(PlaceholderLibrary(missing_root))
        buf = StringIO()
        with patch("sys.stdout", buf):
            resolver.warn_missing_directories()
            resolver.warn_missing_directories()  # deduped
        printed = buf.getvalue()
        self.assertEqual(printed.count("placeholders directory not found"), 1)
        self.assertIn(str(missing_root), printed)

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

class MultiRootLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.primary = base / "primary"
        self.extra = base / "extra"
        self.primary.mkdir()
        self.extra.mkdir()
        (self.primary / "pose.txt").write_text("primary-pose\n", encoding="utf-8")
        (self.extra / "pose.txt").write_text("extra-pose\n", encoding="utf-8")
        (self.extra / "mood.txt").write_text("cheerful\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_lists_names_from_all_roots(self):
        library = PlaceholderLibrary([self.primary, self.extra])
        self.assertEqual(library.list_placeholders(), ["mood", "pose"])

    def test_primary_wins_on_name_conflict(self):
        library = PlaceholderLibrary([self.primary, self.extra])
        self.assertEqual(library.get_values("pose"), ["primary-pose"])
        self.assertEqual(library.resolve_file("pose"), self.primary / "pose.txt")

    def test_extra_root_supplies_missing_names(self):
        library = PlaceholderLibrary([self.primary, self.extra])
        self.assertEqual(library.get_values("mood"), ["cheerful"])

    def test_resolver_uses_extra_root(self):
        library = PlaceholderLibrary([self.primary, self.extra])
        resolver = PlaceholderResolver(library)
        self.assertEqual(resolver.expand("feel __mood__", seed=0), "feel cheerful")
        self.assertEqual(resolver.expand("__pose__", seed=0), "primary-pose")


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
