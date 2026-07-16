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


def get_placeholders_dir() -> Path:
    """
    Resolve the placeholders directory.

    Preference order:
    1. Settings option ``dynph_placeholders_dir`` (if set and non-empty)
    2. Extension-local ``placeholders/`` folder
    """
    placeholders_dir: Path | None = None

    try:
        from modules.shared import opts

        configured = getattr(opts, "dynph_placeholders_dir", None)
        if configured:
            configured = str(configured).strip()
            if configured:
                placeholders_dir = Path(configured).expanduser()
    except Exception:
        # Outside WebUI context (unit tests) — fall through to default.
        placeholders_dir = None

    if placeholders_dir is None:
        placeholders_dir = get_default_placeholders_dir()

    try:
        placeholders_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("Failed to create placeholders directory %s", placeholders_dir)

    return placeholders_dir
