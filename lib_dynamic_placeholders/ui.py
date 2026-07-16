"""Shared Gradio helpers for consistent headings, descriptions, and help text."""

from __future__ import annotations

import gradio as gr

# Demo prompt for the script accordion — uses the shipped top-level lists.
# Swap __artstyle__ for __photostyle__ for a photography look.
EXAMPLE_PROMPT = (
    "__view__, __artstyle__ of a __race__ __profession__, __country__, "
    "with a __expression__, __hair__, __clothes__, "
    "in a __setting__ in __city__ at __time__"
)


def section_description(html: str) -> gr.HTML:
    """Intro copy under a section/accordion heading."""
    return gr.HTML(f'<p class="dynph-ui-desc">{html}</p>')


def field_help(html: str) -> gr.HTML:
    """Help text placed immediately under a control."""
    return gr.HTML(f'<p class="dynph-ui-help">{html}</p>')


def example_prompt_box(prompt: str = EXAMPLE_PROMPT) -> gr.Textbox:
    """Copy-paste demo prompt showing how shipped placeholders compose."""
    return gr.Textbox(
        label="Example prompt (copy into your prompt box)",
        value=prompt,
        lines=3,
        max_lines=6,
        elem_id="dynph_example_prompt",
        elem_classes=["dynph-example-prompt"],
    )
