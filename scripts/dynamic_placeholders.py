from __future__ import annotations

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
from lib_dynamic_placeholders.settings import on_ui_settings

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
            enabled = gr.Checkbox(
                label="Enable Dynamic Placeholders",
                value=True,
                elem_id="dynph_enabled",
            )
            gr.HTML(
                "<p style='margin:0.4em 0 0'>"
                "Use <code>__name__</code> in prompts. "
                "Type <code>__</code> to autocomplete available names. "
                "Each name maps to a newline-separated list file in the placeholders folder "
                "(Settings → Dynamic Placeholders), and optionally an extra folder below."
                "</p>"
            )
            same_seed_link = gr.Checkbox(
                label="Link seed to placeholder choices",
                value=True,
                elem_id="dynph_link_seed",
            )
            gr.HTML(
                "<p style='margin:0.2em 0 0;opacity:0.8'>"
                "When enabled, the same seed reproduces the same replacements."
                "</p>"
            )
            extra_placeholders_dir = gr.Textbox(
                label="Additional placeholders directory",
                value="",
                placeholder="/path/to/your/placeholders",
                elem_id="dynph_extra_dir",
            )
            gr.HTML(
                "<p style='margin:0.2em 0 0;opacity:0.8'>"
                "Optional folder outside the extension install path. "
                "List files there are used alongside the default/settings directory "
                "(default wins on name conflicts)."
                "</p>"
            )
        return [enabled, same_seed_link, extra_placeholders_dir]

    def process(self, p, enabled: bool, same_seed_link: bool, extra_placeholders_dir: str = ""):
        if not enabled:
            return

        fix_seed(p)

        resolver = make_resolver_from_settings(extra_placeholders_dir)
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


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_app_started(_on_app_started)
