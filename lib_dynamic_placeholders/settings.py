from __future__ import annotations

import json
import logging
from pathlib import Path

from modules import shared

from .paths import get_default_placeholders_dir, get_extension_base_path
from .resolver import DEFAULT_MAX_DEPTH, DEFAULT_WRAP


logger = logging.getLogger(__name__)

SECTION = ("dynamic_placeholders", "Dynamic Placeholders")
USER_SETTINGS_FILENAME = "user_settings.json"
_EXTRA_DIR_KEY = "extra_placeholders_dir"


def _user_settings_path() -> Path:
    return get_extension_base_path() / USER_SETTINGS_FILENAME


def _read_user_settings() -> dict:
    path = _user_settings_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Dynamic Placeholders: failed to read %s", path)
        return {}
    return data if isinstance(data, dict) else {}


def _write_user_settings(data: dict) -> None:
    path = _user_settings_path()
    try:
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError:
        logger.exception("Dynamic Placeholders: failed to write %s", path)
        raise


def get_extra_placeholders_dir() -> str:
    """
    Return the persisted additional placeholders directory, or ``""``.

    Preference: extension ``user_settings.json``, then WebUI ``config.json``.
    Migrates a WebUI-only value into ``user_settings.json`` on first read.
    """
    data = _read_user_settings()
    if _EXTRA_DIR_KEY in data:
        return str(data.get(_EXTRA_DIR_KEY, "")).strip()

    opts_value = ""
    try:
        value = getattr(shared.opts, "dynph_extra_placeholders_dir", None)
        if value is not None:
            opts_value = str(value).strip()
    except Exception:
        opts_value = ""

    if opts_value:
        data[_EXTRA_DIR_KEY] = opts_value
        try:
            _write_user_settings(data)
        except OSError:
            pass
    return opts_value


def _on_extra_dir_opt_change() -> None:
    """Keep ``user_settings.json`` in sync when Settings → Apply is used."""
    try:
        value = getattr(shared.opts, "dynph_extra_placeholders_dir", None)
        normalized = "" if value is None else str(value).strip()
        data = _read_user_settings()
        if _EXTRA_DIR_KEY in data and str(data.get(_EXTRA_DIR_KEY, "")).strip() == normalized:
            return
        data[_EXTRA_DIR_KEY] = normalized
        _write_user_settings(data)
    except Exception:
        logger.exception(
            "Dynamic Placeholders: failed to sync Settings extra directory to user_settings.json",
        )


def _sync_opts_extra_dir(normalized: str) -> None:
    """Best-effort write into WebUI settings (Settings page + config.json)."""
    try:
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
            "Dynamic Placeholders: failed to sync extra directory to WebUI settings",
        )


def persist_extra_placeholders_dir(path: str | None) -> str:
    """
    Store ``path`` so it survives restarts.

    Writes extension-local ``user_settings.json`` (authoritative) and syncs
    WebUI Settings when possible. Returns the normalized value written.
    """
    normalized = "" if path is None else str(path).strip()
    data = _read_user_settings()
    if _EXTRA_DIR_KEY in data and str(data.get(_EXTRA_DIR_KEY, "")).strip() == normalized:
        return normalized

    data[_EXTRA_DIR_KEY] = normalized
    try:
        _write_user_settings(data)
    except OSError:
        return get_extra_placeholders_dir()

    _sync_opts_extra_dir(normalized)
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

    extra_dir_opt = shared.OptionInfo(
        "",
        "Additional placeholders directory",
        section=SECTION,
    ).info(
        "Optional second folder searched after the primary directory "
        "(primary wins on name conflicts). Also editable in the script accordion."
    )
    extra_dir_opt.onchange = _on_extra_dir_opt_change
    shared.opts.add_option("dynph_extra_placeholders_dir", extra_dir_opt)

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
