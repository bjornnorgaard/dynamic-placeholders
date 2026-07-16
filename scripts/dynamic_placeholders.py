from __future__ import annotations

import html
import logging

import gradio as gr
from fastapi.responses import JSONResponse

from modules import script_callbacks, scripts
from modules.processing import fix_seed

from lib_dynamic_placeholders.autocomplete import (
    ensure_wildcards_link_for_tagcomplete,
    list_completion_names,
)
from lib_dynamic_placeholders.resolver import expand_prompt_list, make_resolver_from_settings
from lib_dynamic_placeholders.settings import (
    get_extra_placeholders_dir,
    on_ui_settings,
    persist_extra_placeholders_dir,
)
from lib_dynamic_placeholders.ui import (
    example_prompt_box,
    field_help,
    section_description,
    setting_block,
)

logger = logging.getLogger("dynamic_placeholders")


def _effective_prompt(prompts: list[str] | None, fallback: str) -> str:
    if prompts:
        return prompts[0] or fallback or ""
    return fallback or ""


def _expand_hr_prompts(
    expanded_base: list[str],
    hr_template: str,
    base_template: str,
    resolver,
    seeds: list[int] | None,
) -> list[str]:
    """
    Mirror sd-dynamic-prompts HR behaviour:

    - If the HR prompt equals the base template, reuse the already-expanded base prompts.
    - Otherwise expand the HR template on its own.
    """
    if (hr_template or "") == (base_template or ""):
        return list(expanded_base)
    return expand_prompt_list(
        [hr_template] * len(expanded_base),
        resolver=resolver,
        seeds=seeds,
    )


class Script(scripts.Script):
    def title(self):
        return "Dynamic Placeholders"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Dynamic Placeholders", open=False):
            section_description(
                "Use <code>__name__</code> in prompts. "
                "Type <code>__</code> to autocomplete available names. "
                "Each name maps to a newline-separated list file in the placeholders folder "
                "(Settings → Dynamic Placeholders), and optionally an extra folder below."
            )
            with setting_block():
                example_prompt_box()
                field_help(
                    "Select all and paste into the prompt box, then generate. "
                    "Each <code>__token__</code> is replaced from its list file; "
                    "<code>__hair__</code> and <code>__clothes__</code> expand into nested lists. "
                    "Swap <code>__artstyle__</code> for <code>__photostyle__</code> for a photo look."
                )
            with setting_block():
                enabled = gr.Checkbox(
                    label="Enable",
                    value=True,
                    elem_id="dynph_enabled",
                )
                field_help("When off, prompts are left unchanged.")
            with setting_block():
                same_seed_link = gr.Checkbox(
                    label="Link seed to placeholder choices",
                    value=True,
                    elem_id="dynph_link_seed",
                )
                field_help("When enabled, the same seed reproduces the same replacements.")
            with setting_block():
                extra_placeholders_dir = gr.Textbox(
                    label="Additional placeholders directory",
                    value=get_extra_placeholders_dir(),
                    placeholder="/path/to/your/placeholders",
                    elem_id="dynph_extra_dir",
                )
                with gr.Row(elem_id="dynph_extra_dir_actions"):
                    save_extra_dir = gr.Button(
                        "Save directory",
                        elem_id="dynph_extra_dir_save",
                        variant="secondary",
                    )
                    save_extra_status = gr.HTML(
                        value="",
                        elem_id="dynph_extra_dir_status",
                    )
                field_help(
                    "Optional folder outside the extension install path. "
                    "List files there are used alongside the default/settings directory "
                    "(default wins on name conflicts). "
                    "Click <strong>Save directory</strong> so the path is kept after restart."
                )

            def _save_extra_dir(path: str):
                saved = persist_extra_placeholders_dir(path)
                if saved:
                    msg = (
                        f'<p class="dynph-ui-desc">Saved — will be restored after restart: '
                        f"<code>{html.escape(saved)}</code></p>"
                    )
                    return saved, msg
                msg = (
                    '<p class="dynph-ui-desc">Cleared saved directory '
                    "(empty path stored).</p>"
                )
                return "", msg

            save_extra_dir.click(
                fn=_save_extra_dir,
                inputs=[extra_placeholders_dir],
                outputs=[extra_placeholders_dir, save_extra_status],
            )
        return [enabled, same_seed_link, extra_placeholders_dir]

    def process(self, p, enabled: bool, same_seed_link: bool, extra_placeholders_dir: str = ""):
        if not enabled:
            return

        fix_seed(p)

        # Prefer the textbox when non-empty. Do not persist empty from here —
        # after restart ui-config often blanks the field and would wipe the save.
        # Clearing requires the Save directory button (or Settings).
        ui_path = (extra_placeholders_dir or "").strip()
        saved_path = get_extra_placeholders_dir()
        if ui_path:
            persist_extra_placeholders_dir(ui_path)
            effective_extra = ui_path
        else:
            effective_extra = saved_path
        resolver = make_resolver_from_settings(effective_extra)
        resolver.warn_missing_directories()
        original_prompt = _effective_prompt(getattr(p, "all_prompts", None), p.prompt)
        original_negative = _effective_prompt(
            getattr(p, "all_negative_prompts", None),
            p.negative_prompt,
        )

        seeds = getattr(p, "all_seeds", None) if same_seed_link else None

        if getattr(p, "all_prompts", None):
            p.all_prompts = expand_prompt_list(p.all_prompts, resolver=resolver, seeds=seeds)
        else:
            p.prompt = resolver.expand(p.prompt or "", seed=seeds[0] if seeds else None)

        apply_negative = True
        apply_hr = True
        save_template = True
        try:
            from modules.shared import opts

            apply_negative = bool(getattr(opts, "dynph_apply_to_negative", True))
            apply_hr = bool(getattr(opts, "dynph_apply_to_hr", True))
            save_template = bool(getattr(opts, "dynph_save_template", True))
        except Exception:
            pass

        if apply_negative:
            if getattr(p, "all_negative_prompts", None):
                p.all_negative_prompts = expand_prompt_list(
                    p.all_negative_prompts,
                    resolver=resolver,
                    seeds=seeds,
                )
            else:
                p.negative_prompt = resolver.expand(
                    p.negative_prompt or "",
                    seed=seeds[0] if seeds else None,
                )

        hr_enabled = bool(getattr(p, "enable_hr", False))
        if apply_hr and hr_enabled and hasattr(p, "all_hr_prompts"):
            original_hr = _effective_prompt(p.all_hr_prompts, getattr(p, "hr_prompt", "") or "")
            original_hr_neg = _effective_prompt(
                getattr(p, "all_hr_negative_prompts", None),
                getattr(p, "hr_negative_prompt", "") or "",
            )
            p.all_hr_prompts = _expand_hr_prompts(
                p.all_prompts,
                original_hr,
                original_prompt,
                resolver,
                seeds,
            )
            if apply_negative and hasattr(p, "all_hr_negative_prompts"):
                p.all_hr_negative_prompts = _expand_hr_prompts(
                    p.all_negative_prompts,
                    original_hr_neg,
                    original_negative,
                    resolver,
                    seeds,
                )

        # Keep the unresolved template visible / restorable.
        p.prompt_for_display = original_prompt
        p.prompt = original_prompt

        if save_template:
            params = p.extra_generation_params
            if original_prompt:
                params["Dynamic Placeholders Template"] = original_prompt
            if apply_negative and original_negative:
                params["Dynamic Placeholders Negative Template"] = original_negative

        sample = (p.all_prompts[0] if getattr(p, "all_prompts", None) else "") or ""
        logger.info("Dynamic Placeholders expanded prompt: %s", sample)


def _on_app_started(demo, app):
    """Register autocomplete API and expose lists to Tag Autocomplete."""
    ensure_wildcards_link_for_tagcomplete()

    @app.get("/dynph/v1/completions")
    async def dynph_completions():
        wrap, names = list_completion_names()
        return JSONResponse({"wrap": wrap, "names": names})

    @app.get("/dynph/v1/extra-dir")
    async def dynph_extra_dir():
        return JSONResponse({"path": get_extra_placeholders_dir()})


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_app_started(_on_app_started)
