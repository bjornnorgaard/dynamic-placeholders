from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Placeholder names: letters, digits, underscore, hyphen, and optional nested path
# segments separated by `/` or `\`. Matches filename stem without extension.
PLACEHOLDER_NAME_RE = re.compile(
    r"[A-Za-z0-9_\-]+(?:[\\/][A-Za-z0-9_\-]+)*",
)

# Supported list file extensions (matched case-insensitively).
TEXT_EXTENSIONS = (".txt", ".text", ".list")


def is_skippable_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def normalize_placeholder_name(name: str) -> str:
    """Normalize path separators so ``pose\\action`` and ``pose/action`` match."""
    return name.strip().replace("\\", "/")


class PlaceholderLibrary:
    """
    Loads newline-separated replacement lists from a directory tree.

    ``placeholders/pose.txt``          → ``__pose__``
    ``placeholders/furniture/sofa.txt`` → ``__furniture/sofa__``
    """

    def __init__(self, root: Path, *, encoding: str = "utf-8"):
        self.root = Path(root)
        self.encoding = encoding
        self._cache: dict[str, tuple[float, list[str]]] = {}

    def clear_cache(self) -> None:
        self._cache.clear()

    def list_placeholders(self) -> list[str]:
        """Return sorted placeholder names discovered under the root."""
        names: set[str] = set()
        if not self.root.is_dir():
            return []

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                relative = path.relative_to(self.root)
            except ValueError:
                continue
            name = normalize_placeholder_name(str(relative.with_suffix("")))
            if name:
                names.add(name)
        return sorted(names)

    def resolve_file(self, name: str) -> Path | None:
        """Locate the list file for a placeholder name, if it exists."""
        name = normalize_placeholder_name(name)
        if not name or ".." in name.split("/"):
            return None

        base = self.root / Path(*name.split("/"))
        for ext in TEXT_EXTENSIONS:
            candidate = base.with_suffix(ext)
            if candidate.is_file():
                return candidate
        return None

    def get_values(self, name: str) -> list[str]:
        """
        Return non-empty, non-comment lines from the matching list file.

        Results are cached and invalidated when the file mtime changes.
        """
        name = normalize_placeholder_name(name)
        path = self.resolve_file(name)
        if path is None:
            return []

        try:
            mtime = path.stat().st_mtime
        except OSError:
            logger.warning("Unable to stat placeholder file: %s", path)
            return []

        cached = self._cache.get(name)
        if cached is not None and cached[0] == mtime:
            return cached[1]

        try:
            text = path.read_text(encoding=self.encoding, errors="replace")
        except OSError:
            logger.exception("Failed to read placeholder file: %s", path)
            return []

        values = [line.strip() for line in text.splitlines() if not is_skippable_line(line)]
        self._cache[name] = (mtime, values)
        return values
