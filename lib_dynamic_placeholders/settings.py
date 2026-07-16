from __future__ import annotations

from modules import shared

from .paths import get_default_placeholders_dir
from .resolver import DEFAULT_MAX_DEPTH, DEFAULT_WRAP


SECTION = ("dynamic_placeholders", "Dynamic Placeholders")


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
