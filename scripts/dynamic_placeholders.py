from __future__ import annotations

import logging

import gradio as gr

from modules import script_callbacks, scripts
from modules.processing import fix_seed

from lib_dynamic_placeholders.library import PlaceholderLibrary
from lib_dynamic_placeholders.paths import get_placeholders_dir
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


def sort_placeholder_lists() -> str:
    """Alphabetically sort every placeholder list file under the configured directory."""
    root = get_placeholders_dir()
    library = PlaceholderLibrary(root)
    changed, total = library.sort_all_files()
    logger.info(
        "Sorted placeholder lists under %s: %s changed / %s total",
        root,
        changed,
        total,
    )
    if total == 0:
        return (
            "<p style='margin:0.4em 0 0;opacity:0.8'>"
            f"No placeholder list files found in <code>{root}</code>."
            "</p>"
        )
    if changed == 0:
        return (
            "<p style='margin:0.4em 0 0;opacity:0.8'>"
            f"All {total} placeholder list(s) were already alphabetically sorted."
            "</p>"
        )
    return (
        "<p style='margin:0.4em 0 0;opacity:0.8'>"
        f"Sorted {changed} of {total} placeholder list(s) alphabetically. "
        "Leading <code>#</code> comments were kept; seed → choice mapping may change."
        "</p>"
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
                "Each name maps to a newline-separated list file in the placeholders folder "
                "(Settings → Dynamic Placeholders)."
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
            sort_btn = gr.Button(
                "Sort placeholder lists A–Z",
                elem_id="dynph_sort_lists",
            )
            sort_status = gr.HTML(value="", elem_id="dynph_sort_status")
            gr.HTML(
                "<p style='margin:0.2em 0 0;opacity:0.8'>"
                "Rewrites every list file so values are alphabetical (case-insensitive). "
                "Header comments stay at the top."
                "</p>"
            )
            sort_btn.click(fn=sort_placeholder_lists, inputs=[], outputs=[sort_status])
        return [enabled, same_seed_link]

    def process(self, p, enabled: bool, same_seed_link: bool):
        if not enabled:
            return

        fix_seed(p)

        resolver = make_resolver_from_settings()
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


script_callbacks.on_ui_settings(on_ui_settings)
