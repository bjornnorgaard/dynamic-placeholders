"""Shared Gradio helpers for consistent headings, descriptions, and help text."""

from __future__ import annotations

import gradio as gr


def section_description(html: str) -> gr.HTML:
    """Intro copy under a section/accordion heading."""
    return gr.HTML(f'<p class="dynph-ui-desc">{html}</p>')


def field_help(html: str) -> gr.HTML:
    """Help text placed immediately under a control."""
    return gr.HTML(f'<p class="dynph-ui-help">{html}</p>')
