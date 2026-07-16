from __future__ import annotations

import logging
import random
import re
from pathlib import Path

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

    def wrap_name(self, name: str) -> str:
        return f"{self.wrap}{name}{self.wrap}"

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
            logger.warning(
                "Dynamic Placeholders: max nesting depth (%s) reached; leaving remaining tokens",
                self.max_depth,
            )
            return text

        def replace(match: re.Match[str]) -> str:
            name = normalize_placeholder_name(match.group(1))
            if name in stack:
                logger.warning(
                    "Dynamic Placeholders: circular reference involving %s",
                    self.wrap_name(name),
                )
                return match.group(0)

            values = self.library.get_values(name)
            if not values:
                logger.warning(
                    "Dynamic Placeholders: no values found for %s (looked under %s)",
                    self.wrap_name(name),
                    self.library.root,
                )
                return match.group(0) if self.leave_unresolved else ""

            chosen = rng.choice(values)
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


def make_resolver_from_settings() -> PlaceholderResolver:
    """Build a resolver using current WebUI settings (with safe defaults)."""
    wrap = DEFAULT_WRAP
    max_depth = DEFAULT_MAX_DEPTH
    leave_unresolved = True
    root: Path = get_placeholders_dir()

    try:
        from modules.shared import opts

        wrap = getattr(opts, "dynph_wrap", DEFAULT_WRAP) or DEFAULT_WRAP
        max_depth = int(getattr(opts, "dynph_max_depth", DEFAULT_MAX_DEPTH))
        leave_unresolved = bool(getattr(opts, "dynph_leave_unresolved", True))
        configured = getattr(opts, "dynph_placeholders_dir", None)
        if configured and str(configured).strip():
            root = Path(str(configured).strip()).expanduser()
    except Exception:
        pass

    return PlaceholderResolver(
        PlaceholderLibrary(root),
        wrap=wrap,
        max_depth=max_depth,
        leave_unresolved=leave_unresolved,
    )
