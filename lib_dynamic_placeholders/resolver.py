from __future__ import annotations

import logging
import random
import re
from pathlib import Path

from .console import (
    emit_warning,
    format_missing_directory_warning,
    format_missing_placeholder_warning,
)
from .library import PLACEHOLDER_NAME_RE, PlaceholderLibrary, normalize_placeholder_name
from .paths import get_placeholders_dir

logger = logging.getLogger(__name__)

DEFAULT_WRAP = "__"
DEFAULT_MAX_DEPTH = 8


def build_placeholder_pattern(wrap: str = DEFAULT_WRAP) -> re.Pattern[str]:
    """Build a regex that finds ``{wrap}name{wrap}`` tokens."""
    escaped = re.escape(wrap)
    return re.compile(
        rf"{escaped}({PLACEHOLDER_NAME_RE.pattern}){escaped}",
    )


class PlaceholderResolver:
    """
    Expand ``__placeholder__`` tokens by sampling from matching list files.

    Designed for longer phrase/sentence replacements — each line in a list file
    is taken as a full replacement string (no length limit beyond the file).
    Nested placeholders inside replacements are expanded recursively.
    """

    def __init__(
        self,
        library: PlaceholderLibrary | None = None,
        *,
        wrap: str = DEFAULT_WRAP,
        max_depth: int = DEFAULT_MAX_DEPTH,
        leave_unresolved: bool = True,
    ):
        self.library = library or PlaceholderLibrary(get_placeholders_dir())
        self.wrap = wrap
        self.max_depth = max(1, int(max_depth))
        self.leave_unresolved = leave_unresolved
        self._pattern = build_placeholder_pattern(wrap)
        # Deduplicate console warnings within one generation / resolver lifetime.
        self._warned_names: set[str] = set()
        self._warned_dirs: set[Path] = set()
        self._warned_depth = False
        self._warned_cycles: set[str] = set()

    def wrap_name(self, name: str) -> str:
        return f"{self.wrap}{name}{self.wrap}"

    def warn_missing_directories(self) -> None:
        """Emit a visible warning for each configured root that is not a directory."""
        for root in self.library.roots:
            key = root.resolve() if root.exists() else root
            if key in self._warned_dirs:
                continue
            if root.is_dir():
                continue
            self._warned_dirs.add(key)
            emit_warning(format_missing_directory_warning(root))

    def _warn_unresolved(self, name: str, *, status: str, path: Path | None) -> None:
        if name in self._warned_names:
            return
        self._warned_names.add(name)
        emit_warning(
            format_missing_placeholder_warning(
                token=self.wrap_name(name),
                name=name,
                roots=list(self.library.roots),
                path=path,
                reason=status,
            )
        )

    def expand(
        self,
        prompt: str,
        *,
        rng: random.Random | None = None,
        seed: int | None = None,
    ) -> str:
        """
        Expand all placeholders in ``prompt``.

        Provide either ``rng`` or ``seed`` for reproducible sampling. If neither
        is given, the global ``random`` module is used.
        """
        if not prompt or self.wrap not in prompt:
            return prompt

        if rng is None:
            rng = random.Random(seed) if seed is not None else random

        return self._expand_recursive(prompt, rng, depth=0, stack=())

    def _expand_recursive(
        self,
        text: str,
        rng: random.Random,
        *,
        depth: int,
        stack: tuple[str, ...],
    ) -> str:
        if depth >= self.max_depth:
            if not self._warned_depth:
                self._warned_depth = True
                emit_warning(
                    "\n".join(
                        [
                            "-" * 72,
                            "[Dynamic Placeholders] WARNING: max nesting depth reached",
                            f"  Depth:  {self.max_depth}",
                            "  Tip:    Check for deeply nested or circular list files; "
                            "remaining tokens were left unchanged.",
                            "-" * 72,
                        ]
                    )
                )
            return text

        def replace(match: re.Match[str]) -> str:
            name = normalize_placeholder_name(match.group(1))
            if name in stack:
                if name not in self._warned_cycles:
                    self._warned_cycles.add(name)
                    emit_warning(
                        "\n".join(
                            [
                                "-" * 72,
                                "[Dynamic Placeholders] WARNING: circular placeholder reference",
                                f"  Token:  {self.wrap_name(name)}",
                                f"  Chain:  {' → '.join(self.wrap_name(n) for n in stack + (name,))}",
                                "  Tip:    Break the cycle in your list files.",
                                "-" * 72,
                            ]
                        )
                    )
                return match.group(0)

            result = self.library.lookup(name)
            if not result.ok:
                self._warn_unresolved(
                    name,
                    status=result.status,
                    path=result.path,
                )
                return match.group(0) if self.leave_unresolved else ""

            chosen = rng.choice(result.values)
            return self._expand_recursive(
                chosen,
                rng,
                depth=depth + 1,
                stack=stack + (name,),
            )

        # One pass replaces every top-level token; nested tokens inside chosen
        # values are handled by recursion above.
        return self._pattern.sub(replace, text)


def expand_placeholders(
    prompt: str,
    *,
    library: PlaceholderLibrary | None = None,
    seed: int | None = None,
    wrap: str = DEFAULT_WRAP,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> str:
    """Convenience wrapper around :class:`PlaceholderResolver`."""
    resolver = PlaceholderResolver(
        library=library,
        wrap=wrap,
        max_depth=max_depth,
    )
    return resolver.expand(prompt, seed=seed)


def expand_prompt_list(
    prompts: list[str],
    *,
    resolver: PlaceholderResolver,
    seeds: list[int] | None = None,
) -> list[str]:
    """Expand each prompt with an optional per-index seed for reproducibility."""
    expanded: list[str] = []
    for index, prompt in enumerate(prompts):
        seed = None
        if seeds is not None and index < len(seeds):
            seed = seeds[index]
        expanded.append(resolver.expand(prompt, seed=seed))
    return expanded


def _optional_dir(path: str | Path | None) -> Path | None:
    if path is None:
        return None
    text = str(path).strip()
    if not text:
        return None
    return Path(text).expanduser()


def make_resolver_from_settings(
    extra_placeholders_dir: str | Path | None = None,
) -> PlaceholderResolver:
    """
    Build a resolver using current WebUI settings (with safe defaults).

    ``extra_placeholders_dir`` is an optional second folder (typically from the
    script UI) searched after the configured/default placeholders directory.
    When omitted (``None``), the persisted Settings value
    ``dynph_extra_placeholders_dir`` is used. Pass ``""`` to skip the extra root.
    """
    wrap = DEFAULT_WRAP
    max_depth = DEFAULT_MAX_DEPTH
    leave_unresolved = True
    # Goes through path resolution (empty setting + stale renamed-install paths).
    root: Path = get_placeholders_dir()
    settings_extra: str | None = None

    try:
        from modules.shared import opts

        wrap = getattr(opts, "dynph_wrap", DEFAULT_WRAP) or DEFAULT_WRAP
        max_depth = int(getattr(opts, "dynph_max_depth", DEFAULT_MAX_DEPTH))
        leave_unresolved = bool(getattr(opts, "dynph_leave_unresolved", True))
        settings_extra = getattr(opts, "dynph_extra_placeholders_dir", None)
    except Exception:
        pass

    if extra_placeholders_dir is None:
        extra_placeholders_dir = settings_extra

    roots: list[Path] = [root]
    extra = _optional_dir(extra_placeholders_dir)
    if extra is not None:
        try:
            same_dir = extra.resolve() == root.resolve()
        except OSError:
            same_dir = extra == root
        if not same_dir:
            roots.append(extra)

    return PlaceholderResolver(
        PlaceholderLibrary(roots),
        wrap=wrap,
        max_depth=max_depth,
        leave_unresolved=leave_unresolved,
    )
