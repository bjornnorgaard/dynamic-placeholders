from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

from lib_dynamic_placeholders.autocomplete import (
    ensure_wildcards_link_for_tagcomplete,
    filter_placeholder_names,
    find_incomplete_placeholder,
)


class IncompletePlaceholderTests(unittest.TestCase):
    def test_triggers_on_double_underscore(self):
        self.assertEqual(find_incomplete_placeholder("portrait __"), (9, ""))
        self.assertEqual(find_incomplete_placeholder("__"), (0, ""))

    def test_partial_name(self):
        self.assertEqual(find_incomplete_placeholder("x __hai"), (2, "hai"))
        self.assertEqual(
            find_incomplete_placeholder("x __clothes/torso"),
            (2, "clothes/torso"),
        )
        self.assertEqual(find_incomplete_placeholder("x __hair/"), (2, "hair/"))

    def test_closed_token_is_not_incomplete(self):
        self.assertIsNone(find_incomplete_placeholder("x __hair__"))
        self.assertIsNone(find_incomplete_placeholder("__hair__ more"))

    def test_single_underscore_does_not_trigger(self):
        self.assertIsNone(find_incomplete_placeholder("foo _"))
        self.assertIsNone(find_incomplete_placeholder("foo_bar"))

    def test_names_with_underscores(self):
        self.assertEqual(find_incomplete_placeholder("__my_pose"), (0, "my_pose"))
        self.assertIsNone(find_incomplete_placeholder("__my_pose__"))

    def test_custom_wrap(self):
        self.assertEqual(find_incomplete_placeholder("a @@po", "@@"), (2, "po"))
        self.assertIsNone(find_incomplete_placeholder("a @@pose@@", "@@"))
        self.assertEqual(find_incomplete_placeholder("a @@", "@@"), (2, ""))


class FilterNamesTests(unittest.TestCase):
    def test_prefix_preferred(self):
        names = ["hair", "hair/color", "chair", "clothes"]
        self.assertEqual(
            filter_placeholder_names(names, "hai"),
            ["hair", "hair/color", "chair"],
        )

    def test_empty_prefix_returns_sorted_short_first(self):
        names = ["clothes/shoes", "hair", "city"]
        self.assertEqual(
            filter_placeholder_names(names, ""),
            ["city", "hair", "clothes/shoes"],
        )


class WildcardsLinkTests(unittest.TestCase):
    def test_creates_symlink_to_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            placeholders = base / "placeholders"
            placeholders.mkdir()
            (placeholders / "pose.txt").write_text("a\n", encoding="utf-8")

            with mock.patch(
                "lib_dynamic_placeholders.autocomplete.get_extension_base_path",
                return_value=base,
            ), mock.patch(
                "lib_dynamic_placeholders.autocomplete.get_placeholders_dir",
                return_value=placeholders,
            ), mock.patch(
                "lib_dynamic_placeholders.autocomplete.get_default_placeholders_dir",
                return_value=placeholders,
            ):
                link = ensure_wildcards_link_for_tagcomplete()
                self.assertIsNotNone(link)
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), placeholders.resolve())
                # Idempotent
                again = ensure_wildcards_link_for_tagcomplete()
                self.assertEqual(again.resolve(), placeholders.resolve())


if __name__ == "__main__":
    unittest.main()
