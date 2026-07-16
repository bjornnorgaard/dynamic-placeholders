"""Visible terminal warnings for Dynamic Placeholders setup issues."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _use_color() -> bool:
    # WebUI consoles often are not TTYs but still render ANSI; respect NO_COLOR.
    return not os.environ.get("NO_COLOR")


def _paint(text: str) -> str:
    if not _use_color():
        return text
    return f"{_YELLOW}{_BOLD}{text}{_RESET}"


def _rule() -> str:
    return "-" * 72


def expected_list_paths(name: str, roots: list[Path]) -> list[Path]:
    """Paths a user would typically create for ``name`` (``.txt`` under each root)."""
    from .library import TEXT_EXTENSIONS

    paths: list[Path] = []
    for root in roots:
        base = root / Path(*name.split("/"))
        # Lead with .txt — the usual convention — then list other extensions.
        for ext in TEXT_EXTENSIONS:
            paths.append(base.with_suffix(ext))
    return paths


def format_missing_placeholder_warning(
    *,
    token: str,
    name: str,
    roots: list[Path],
    path: Path | None = None,
    reason: str = "missing",
) -> str:
    """Build a multi-line, copy-pasteable warning for the terminal."""
    lines = [
        _rule(),
        "[Dynamic Placeholders] WARNING: placeholder not resolved",
        f"  Token:  {token}",
    ]

    if reason == "empty" and path is not None:
        lines.extend(
            [
                "  Reason: list file has no usable values",
                f"  File:   {path}",
                "  Tip:    Add one replacement phrase per line (comments with # are ignored).",
            ]
        )
    elif reason == "unreadable" and path is not None:
        lines.extend(
            [
                "  Reason: list file could not be read",
                f"  File:   {path}",
                "  Tip:    Check file permissions and encoding (UTF-8 expected).",
            ]
        )
    else:
        searched = ", ".join(str(root) for root in roots) or "(no directories configured)"
        expected = expected_list_paths(name, roots)
        # Show one candidate per root (.txt) to keep the tip scannable.
        primary = [p for p in expected if p.suffix == ".txt"] or expected[: len(roots) or 1]
        lines.extend(
            [
                "  Reason: no matching list file found",
                f"  Looked: {searched}",
                "  Expect: " + (str(primary[0]) if primary else "(unknown)"),
            ]
        )
        for extra in primary[1:]:
            lines.append(f"          {extra}")
        lines.append(
            "  Tip:    Create that .txt file, fix the token spelling, "
            "or add an extra placeholders directory in the script UI."
        )

    lines.append(_rule())
    return "\n".join(lines)


def format_missing_directory_warning(path: Path) -> str:
    lines = [
        _rule(),
        "[Dynamic Placeholders] WARNING: placeholders directory not found",
        f"  Path:   {path}",
        "  Tip:    Create the folder, or set Settings → Dynamic Placeholders "
        "→ placeholders directory / Additional placeholders directory.",
        _rule(),
    ]
    return "\n".join(lines)


def emit_warning(message: str) -> None:
    """Print a highlighted warning to the console and mirror a short line to the logger."""
    print(_paint(message), flush=True)
    # One-line summary for log files / handlers — avoids reprinting the full
    # banner when a StreamHandler is attached to the console.
    first_content = next(
        (line for line in message.splitlines() if line.startswith("[Dynamic Placeholders]")),
        message.splitlines()[0] if message else "warning",
    )
    logger.warning("%s", first_content)
