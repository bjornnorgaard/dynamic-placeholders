from __future__ import annotations

import logging
import re
from pathlib import Path

from .library import PLACEHOLDER_NAME_RE
from .paths import get_extension_base_path, get_placeholders_dir
from .resolver import DEFAULT_WRAP, make_resolver_from_settings

logger = logging.getLogger(__name__)

# Incomplete name while typing — allows empty and trailing ``/`` (unlike the
# closed-token grammar, which requires a full segment after each separator).
_NAME_PREFIX_RE = re.compile(r"^[A-Za-z0-9_\-]*(?:[\\/][A-Za-z0-9_\-]*)*$")


def find_incomplete_placeholder(
    text_before_cursor: str,
    wrap: str = DEFAULT_WRAP,
) -> tuple[int, str] | None:
    """
    If ``text_before_cursor`` ends with an open ``{wrap}…`` prefix, return
    ``(start_index, typed_name_prefix)``.

    Examples (wrap ``__``)::

        "foo __"        → (4, "")
        "foo __hai"     → (4, "hai")
        "foo __hair__"  → None
        "foo _"         → None
    """
    if not wrap or not text_before_cursor:
        return None

    # Trailing wrap is either an empty open token or the closer of ``__name__``.
    if text_before_cursor.endswith(wrap):
        idx = len(text_before_cursor) - len(wrap)
        before = text_before_cursor[:idx]
        prev = before.rfind(wrap)
        if prev >= 0:
            between = before[prev + len(wrap) :]
            if between and PLACEHOLDER_NAME_RE.fullmatch(between):
                return None
        return idx, ""

    idx = text_before_cursor.rfind(wrap)
    if idx < 0:
        return None

    after = text_before_cursor[idx + len(wrap) :]
    # Closing wrap already handled above; a wrap inside the typed prefix means
    # the caret is past a finished token (or invalid input).
    if not after or wrap in after:
        return None
    if not _NAME_PREFIX_RE.fullmatch(after):
        return None
    return idx, after


def filter_placeholder_names(
    names: list[str],
    prefix: str,
    *,
    limit: int = 50,
) -> list[str]:
    """Filter placeholder names by a typed prefix (case-insensitive)."""
    needle = (prefix or "").lower().replace("\\", "/")
    matches = [name for name in names if needle in name.lower()]
    # Prefer prefix matches, then shorter names, then alphabetical.
    matches.sort(
        key=lambda name: (
            0 if name.lower().startswith(needle) else 1,
            len(name),
            name.lower(),
        ),
    )
    return matches[: max(1, int(limit))]


def list_completion_names(
    extra_placeholders_dir: str | Path | None = None,
) -> tuple[str, list[str]]:
    """Return ``(wrap, sorted_names)`` from current settings / roots."""
    resolver = make_resolver_from_settings(extra_placeholders_dir)
    return resolver.wrap, resolver.library.list_placeholders()


def ensure_wildcards_link_for_tagcomplete() -> Path | None:
    """
    Expose ``placeholders/`` as ``wildcards/`` so Tag Autocomplete can list
    tokens when the user types ``__``.

    Tag Autocomplete only scans ``extensions/*/wildcards/``. We keep lists under
    ``placeholders/`` and maintain a directory symlink for discovery.

    Returns the link path when created or already present, else ``None``.
    """
    base = get_extension_base_path()
    link = base / "wildcards"
    # Always the resolved primary placeholders dir (stale renamed-install
    # settings are rewritten by get_placeholders_dir).
    target = get_placeholders_dir()

    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("Failed to ensure placeholders directory %s", target)
        return None

    # Prefer a relative link when the target lives under this extension root
    # (typical case: wildcards → placeholders). Absolute only for custom dirs.
    try:
        link_target: str | Path = target.resolve().relative_to(base.resolve())
    except (OSError, ValueError):
        link_target = target

    if link.is_symlink():
        try:
            current = link.resolve()
            desired = target.resolve()
            if current == desired:
                return link
            link.unlink()
        except OSError:
            # Broken or unreadable link (e.g. after a folder rename) — replace it.
            try:
                link.unlink()
            except OSError:
                logger.exception("Failed to refresh wildcards symlink at %s", link)
                return link if link.exists() else None
    elif link.exists():
        # Real directory — do not destroy user content.
        if link.is_dir():
            logger.debug(
                "Leaving existing wildcards directory in place at %s "
                "(Tag Autocomplete will scan it)",
                link,
            )
            return link
        logger.warning(
            "Cannot create wildcards link; a non-directory already exists at %s",
            link,
        )
        return None

    try:
        link.symlink_to(link_target, target_is_directory=True)
        logger.info(
            "Created wildcards → %s for Tag Autocomplete (__ completion)",
            link_target,
        )
        return link
    except OSError:
        logger.exception("Failed to create wildcards symlink at %s", link)
        return None
