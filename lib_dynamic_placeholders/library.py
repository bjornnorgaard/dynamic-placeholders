from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Placeholder names: letters, digits, underscore, hyphen, and optional nested path
# segments separated by `/` or `\`. Matches filename stem without extension.
PLACEHOLDER_NAME_RE = re.compile(
    r"[A-Za-z0-9_\-]+(?:[\\/][A-Za-z0-9_\-]+)*",
)

# Supported list file extensions (matched case-insensitively).
TEXT_EXTENSIONS = (".txt", ".text", ".list")

LookupStatus = Literal["ok", "missing", "empty", "unreadable"]


@dataclass(frozen=True)
class PlaceholderLookup:
    """Result of resolving a placeholder name to list-file values."""

    name: str
    values: list[str]
    status: LookupStatus = "ok"
    path: Path | None = None

    @property
    def ok(self) -> bool:
        return self.status == "ok" and bool(self.values)


def is_skippable_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def normalize_placeholder_name(name: str) -> str:
    """Normalize path separators so ``pose\\action`` and ``pose/action`` match."""
    return name.strip().replace("\\", "/")


def _normalize_roots(root: Path | str | Sequence[Path | str]) -> list[Path]:
    if isinstance(root, (str, Path)):
        candidates = [root]
    else:
        candidates = list(root)

    roots: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate is None:
            continue
        path = Path(candidate).expanduser()
        if not str(path).strip():
            continue
        resolved = path.resolve() if path.exists() else path
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(path)
    return roots


class PlaceholderLibrary:
    """
    Loads newline-separated replacement lists from one or more directory trees.

    ``placeholders/pose.txt``          → ``__pose__``
    ``placeholders/furniture/sofa.txt`` → ``__furniture/sofa__``

    When multiple roots are given, the first root that contains a matching
    list file wins. Extra roots are a convenient place for portable lists
    kept outside the extension install folder.
    """

    def __init__(
        self,
        root: Path | str | Sequence[Path | str],
        *,
        encoding: str = "utf-8",
    ):
        roots = _normalize_roots(root)
        if not roots:
            raise ValueError("PlaceholderLibrary requires at least one root directory")
        self.roots = roots
        # Back-compat: callers and log messages that expect a single root.
        self.root = roots[0]
        self.encoding = encoding
        self._cache: dict[str, tuple[float, list[str]]] = {}

    def clear_cache(self) -> None:
        self._cache.clear()

    def list_placeholders(self) -> list[str]:
        """Return sorted placeholder names discovered under all roots."""
        names: set[str] = set()
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                try:
                    relative = path.relative_to(root)
                except ValueError:
                    continue
                name = normalize_placeholder_name(str(relative.with_suffix("")))
                if name:
                    names.add(name)
        return sorted(names)

    def resolve_file(self, name: str) -> Path | None:
        """
        Locate the list file for a placeholder name, if it exists.

        Resolution order:
        1. Exact relative path under a root (``eyes`` → ``eyes.txt``).
        2. Unique short-path match: a file whose relative name equals the
           token or ends with ``/{token}`` (``eyes`` → ``face/eyes.txt``,
           ``castle/ballroom`` → ``location/castle/ballroom.txt``).

        Ambiguous short-path matches (0 or 2+) return ``None`` — never guess.
        """
        name = normalize_placeholder_name(name)
        if not name or ".." in name.split("/"):
            return None

        for root in self.roots:
            base = root / Path(*name.split("/"))
            for ext in TEXT_EXTENSIONS:
                candidate = base.with_suffix(ext)
                if candidate.is_file():
                    return candidate

        return self._resolve_short_path(name)

    def _resolve_short_path(self, name: str) -> Path | None:
        """Return the unique file whose relative stem equals or ends with name."""
        matches: list[Path] = []
        suffix = f"/{name}"
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                try:
                    relative = path.relative_to(root)
                except ValueError:
                    continue
                stem = normalize_placeholder_name(str(relative.with_suffix("")))
                if not stem:
                    continue
                if stem == name or stem.endswith(suffix):
                    matches.append(path)

        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            logger.warning(
                "Ambiguous short-path placeholder %r matches %d files; "
                "use a fuller path",
                name,
                len(matches),
            )
        return None

    def lookup(self, name: str) -> PlaceholderLookup:
        """
        Resolve a placeholder name to values, with an explicit status.

        Distinguishes missing files from empty/comment-only files so callers
        can surface actionable setup warnings.
        """
        name = normalize_placeholder_name(name)
        path = self.resolve_file(name)
        if path is None:
            return PlaceholderLookup(name=name, values=[], status="missing")

        try:
            mtime = path.stat().st_mtime
        except OSError:
            logger.warning("Unable to stat placeholder file: %s", path)
            return PlaceholderLookup(
                name=name,
                values=[],
                status="unreadable",
                path=path,
            )

        cached = self._cache.get(name)
        if cached is not None and cached[0] == mtime:
            values = cached[1]
            if not values:
                return PlaceholderLookup(
                    name=name,
                    values=[],
                    status="empty",
                    path=path,
                )
            return PlaceholderLookup(name=name, values=values, status="ok", path=path)

        try:
            text = path.read_text(encoding=self.encoding, errors="replace")
        except OSError:
            logger.exception("Failed to read placeholder file: %s", path)
            return PlaceholderLookup(
                name=name,
                values=[],
                status="unreadable",
                path=path,
            )

        values = [line.strip() for line in text.splitlines() if not is_skippable_line(line)]
        self._cache[name] = (mtime, values)
        if not values:
            return PlaceholderLookup(
                name=name,
                values=[],
                status="empty",
                path=path,
            )
        return PlaceholderLookup(name=name, values=values, status="ok", path=path)

    def get_values(self, name: str) -> list[str]:
        """
        Return non-empty, non-comment lines from the matching list file.

        Results are cached and invalidated when the file mtime changes.
        """
        return self.lookup(name).values
