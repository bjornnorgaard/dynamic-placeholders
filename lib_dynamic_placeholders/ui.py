"""Shared Gradio helpers for consistent headings, descriptions, and help text."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import gradio as gr

# Demo prompt for the script accordion — uses the shipped top-level lists.
# Swap __artstyle__ for __photostyle__ for a photography look.
EXAMPLE_PROMPT = (
    "__view__, __artstyle__ of a __race__ __profession__, __country__, "
    "with a __expression__, __face__, __hair__, __clothes__, "
    "in a __setting__ in __city__ at __time__"
)


def section_description(html: str) -> gr.HTML:
    """Intro copy under a section/accordion heading (same type as field help)."""
    return gr.HTML(f'<p class="dynph-ui-desc dynph-ui-intro">{html}</p>')


def field_help(html: str) -> gr.HTML:
    """Description placed immediately under a control (same look as section copy)."""
    return gr.HTML(f'<p class="dynph-ui-desc">{html}</p>')


@contextmanager
def setting_block() -> Iterator[None]:
    """
    One setting: control(s) then ``field_help``.

    Shared spacing so checkboxes, textboxes, and other inputs stack evenly.
    """
    with gr.Group(elem_classes=["dynph-setting"]):
        yield


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
