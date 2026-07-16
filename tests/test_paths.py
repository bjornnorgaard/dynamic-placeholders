from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

from lib_dynamic_placeholders import paths


class PathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.extensions = Path(self.tmp.name) / "extensions"
        self.extensions.mkdir()
        self.current = self.extensions / "sd-dynamic-placeholders"
        self.current.mkdir()
        (self.current / "lib_dynamic_placeholders").mkdir()
        (self.current / "scripts").mkdir()
        (self.current / "placeholders").mkdir()
        paths.get_extension_base_path.cache_clear()

    def tearDown(self) -> None:
        paths.get_extension_base_path.cache_clear()
        self.tmp.cleanup()

    def _patch_base(self):
        return mock.patch.object(paths, "get_extension_base_path", return_value=self.current)

    def test_stale_sibling_renamed_install(self):
        old = self.extensions / "dynamic-placeholders" / "placeholders"
        default = self.current / "placeholders"
        with self._patch_base():
            self.assertTrue(paths.is_stale_extension_placeholders_dir(old, default))
            self.assertEqual(paths.resolve_placeholders_dir(old), default)

    def test_current_default_not_stale(self):
        default = self.current / "placeholders"
        with self._patch_base():
            self.assertFalse(paths.is_stale_extension_placeholders_dir(default, default))
            self.assertEqual(paths.resolve_placeholders_dir(default), default)

    def test_custom_dir_outside_extensions_not_stale(self):
        custom = Path(self.tmp.name) / "my-lists"
        default = self.current / "placeholders"
        with self._patch_base():
            self.assertFalse(paths.is_stale_extension_placeholders_dir(custom, default))
            self.assertEqual(paths.resolve_placeholders_dir(custom), custom)

    def test_live_sibling_install_not_stale(self):
        """A second real install of this extension should not be treated as stale."""
        other = self.extensions / "dynamic-placeholders"
        other.mkdir()
        (other / "lib_dynamic_placeholders").mkdir()
        configured = other / "placeholders"
        default = self.current / "placeholders"
        with self._patch_base():
            self.assertFalse(paths.is_stale_extension_placeholders_dir(configured, default))

    def test_get_placeholders_dir_does_not_recreate_stale_tree(self):
        old_root = self.extensions / "dynamic-placeholders"
        old = old_root / "placeholders"
        self.assertFalse(old_root.exists())

        with (
            self._patch_base(),
            mock.patch.object(paths, "_configured_placeholders_dir", return_value=old),
            mock.patch.object(paths, "_clear_stale_placeholders_dir_opt") as clear,
        ):
            resolved = paths.get_placeholders_dir()
            clear.assert_called_once()

        self.assertEqual(resolved, self.current / "placeholders")
        self.assertTrue(resolved.is_dir())
        self.assertFalse(old_root.exists())

    def test_empty_configured_uses_default(self):
        default = self.current / "placeholders"
        with self._patch_base():
            self.assertEqual(paths.resolve_placeholders_dir(None), default)


if __name__ == "__main__":
    unittest.main()
