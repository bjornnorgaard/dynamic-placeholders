from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_extension_base_path() -> Path:
    """Return the installed extension root directory."""
    path = Path(__file__).resolve().parent.parent
    assert (path / "lib_dynamic_placeholders").is_dir()
    assert (path / "scripts").is_dir()
    return path


def get_default_placeholders_dir() -> Path:
    return get_extension_base_path() / "placeholders"


def _paths_equal(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return a == b


def is_stale_extension_placeholders_dir(configured: Path, default: Path | None = None) -> bool:
    """
    Return True when ``configured`` looks like this extension's old install-local
    ``placeholders/`` after a folder rename (e.g. ``dynamic-placeholders`` →
    ``sd-dynamic-placeholders``).

    Heuristic: same parent as the current extension (typically ``extensions/``),
    path ends with ``…/<other-folder>/placeholders``, and that sibling is not a
    live install of this package (no ``lib_dynamic_placeholders/``).
    """
    if default is None:
        default = get_default_placeholders_dir()

    if configured.name != "placeholders":
        return False
    if _paths_equal(configured, default):
        return False

    current_base = get_extension_base_path()
    parent = configured.parent
    if parent.parent != current_base.parent:
        return False
    if _paths_equal(parent, current_base):
        return False
    return not (parent / "lib_dynamic_placeholders").is_dir()


def _configured_placeholders_dir() -> Path | None:
    """Read ``dynph_placeholders_dir`` from WebUI opts when available."""
    try:
        from modules.shared import opts

        configured = getattr(opts, "dynph_placeholders_dir", None)
        if configured:
            configured = str(configured).strip()
            if configured:
                return Path(configured).expanduser()
    except Exception:
        # Outside WebUI context (unit tests) — fall through to default.
        pass
    return None


def _clear_stale_placeholders_dir_opt() -> None:
    """Best-effort clear of a relocated install path from WebUI settings."""
    try:
        from modules.shared import opts

        if hasattr(opts, "set"):
            opts.set("dynph_placeholders_dir", "")
        else:
            opts.dynph_placeholders_dir = ""
            if hasattr(opts, "data"):
                opts.data["dynph_placeholders_dir"] = ""

        from modules import shared

        config_filename = getattr(shared, "config_filename", None)
        if config_filename and hasattr(opts, "save"):
            opts.save(config_filename)
        logger.info(
            "Cleared stale dynph_placeholders_dir (extension was renamed/moved); "
            "using %s",
            get_default_placeholders_dir(),
        )
    except Exception:
        logger.exception("Failed to clear stale dynph_placeholders_dir setting")


def resolve_placeholders_dir(configured: Path | None = None) -> Path:
    """
    Resolve which placeholders directory to use without creating it.

    Empty / unset ``configured`` means the extension-local default. A setting
    that still points at a previous install folder under ``extensions/`` is
    treated as stale and replaced by the current default.
    """
    default = get_default_placeholders_dir()
    if configured is None:
        configured = _configured_placeholders_dir()
    if configured is None:
        return default
    if is_stale_extension_placeholders_dir(configured, default):
        return default
    return configured


def get_placeholders_dir() -> Path:
    """
    Resolve the placeholders directory and ensure it exists.

    Preference order:
    1. Settings option ``dynph_placeholders_dir`` (if set and non-empty),
       unless it is a stale path from a renamed/moved install
    2. Extension-local ``placeholders/`` folder
    """
    configured = _configured_placeholders_dir()
    placeholders_dir = resolve_placeholders_dir(configured)

    if (
        configured is not None
        and is_stale_extension_placeholders_dir(configured, get_default_placeholders_dir())
    ):
        _clear_stale_placeholders_dir_opt()

    try:
        placeholders_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("Failed to create placeholders directory %s", placeholders_dir)

    return placeholders_dir
