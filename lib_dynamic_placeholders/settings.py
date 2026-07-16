from __future__ import annotations

import logging

from modules import shared

from .paths import get_default_placeholders_dir
from .resolver import DEFAULT_MAX_DEPTH, DEFAULT_WRAP


logger = logging.getLogger(__name__)

SECTION = ("dynamic_placeholders", "Dynamic Placeholders")


def get_extra_placeholders_dir() -> str:
    """Return the persisted additional placeholders directory, or ``""``."""
    try:
        value = getattr(shared.opts, "dynph_extra_placeholders_dir", None)
    except Exception:
        return ""
    if value is None:
        return ""
    return str(value).strip()


def persist_extra_placeholders_dir(path: str | None) -> str:
    """
    Store ``path`` in WebUI settings so it survives restarts.

    Returns the normalized value written (empty string when cleared).
    No-ops when the value is already stored.
    """
    normalized = "" if path is None else str(path).strip()
    if normalized == get_extra_placeholders_dir():
        return normalized
    try:
        # Prefer Options.set when available (validates + updates data).
        if hasattr(shared.opts, "set"):
            shared.opts.set("dynph_extra_placeholders_dir", normalized)
        else:
            shared.opts.dynph_extra_placeholders_dir = normalized
            if hasattr(shared.opts, "data"):
                shared.opts.data["dynph_extra_placeholders_dir"] = normalized

        config_filename = getattr(shared, "config_filename", None)
        if config_filename and hasattr(shared.opts, "save"):
            shared.opts.save(config_filename)
    except Exception:
        logger.exception(
            "Dynamic Placeholders: failed to persist extra placeholders directory",
        )
    return normalized


def on_ui_settings() -> None:
    shared.opts.add_option(
        "dynph_placeholders_dir",
        shared.OptionInfo(
            str(get_default_placeholders_dir()),
            "Placeholders directory",
            section=SECTION,
        )
        .info("Folder of newline-separated list files. Filename (without extension) = placeholder name."),
    )

    shared.opts.add_option(
        "dynph_extra_placeholders_dir",
        shared.OptionInfo(
            "",
            "Additional placeholders directory",
            section=SECTION,
        )
        .info(
            "Optional second folder searched after the primary directory "
            "(primary wins on name conflicts). Also editable in the script accordion."
        ),
    )

    shared.opts.add_option(
        "dynph_wrap",
        shared.OptionInfo(
            DEFAULT_WRAP,
            "Placeholder wrap string",
            section=SECTION,
        )
        .info('Characters surrounding the name, e.g. "__" produces __pose__.'),
    )

    shared.opts.add_option(
        "dynph_max_depth",
        shared.OptionInfo(
            DEFAULT_MAX_DEPTH,
            "Maximum nested replacement depth",
            section=SECTION,
        )
        .info("Stops recursive expansion if list entries contain further placeholders."),
    )

    shared.opts.add_option(
        "dynph_leave_unresolved",
        shared.OptionInfo(
            True,
            "Leave unknown placeholders unchanged",
            section=SECTION,
        )
        .info("When unchecked, missing placeholders are removed from the prompt."),
    )

    shared.opts.add_option(
        "dynph_save_template",
        shared.OptionInfo(
            True,
            "Save original template in generation parameters",
            section=SECTION,
        )
        .info('Writes "Dynamic Placeholders Template" into PNG info / parameters.'),
    )

    shared.opts.add_option(
        "dynph_apply_to_negative",
        shared.OptionInfo(
            True,
            "Also expand placeholders in negative prompts",
            section=SECTION,
        )
        .info("Applies the same __name__ expansion used on the positive prompt."),
    )

    shared.opts.add_option(
        "dynph_apply_to_hr",
        shared.OptionInfo(
            True,
            "Also expand placeholders in Hires. fix prompts",
            section=SECTION,
        )
        .info("Expands placeholders in HR prompts when Hires. fix is enabled."),
    )
