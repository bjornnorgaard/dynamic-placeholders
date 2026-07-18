"""Shared Gradio helpers for consistent headings, descriptions, and help text."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import gradio as gr

# Light in-UI guide — not a substitute for README / docs/*.
_USAGE_GUIDE_HTML = """
<div class="dynph-usage-guide">
  <p>
    Placeholders are tokens like <code>__profession__</code> or <code>__hair__</code>
    in your prompt. At generation, each token is replaced with a random line from a
    matching list file.
  </p>

  <h4>In the prompt</h4>
  <ul>
    <li>Write tokens anywhere you would write a normal phrase:
      <code>portrait of a __profession__ with __hair__</code></li>
    <li>Type <code>__</code> in the prompt box to autocomplete names
      (arrows + Enter / Tab to insert).</li>
    <li>Each token is chosen independently — two <code>__pose__</code>
      tokens can become two different poses.</li>
  </ul>

  <h4>List files</h4>
  <ul>
    <li>Default folder:
      <code>extensions/sd-dynamic-placeholders/placeholders/</code></li>
    <li>File name (without extension) = token name:
      <code>pose.txt</code> → <code>__pose__</code></li>
    <li>Subfolders use <code>/</code>:
      <code>face/eyes.txt</code> → <code>__face/eyes__</code></li>
    <li>Unique short names also work:
      <code>__eyes__</code> finds <code>face/eyes.txt</code> when it is the only match.</li>
    <li>One candidate per line; blank lines and <code>#</code> comments are ignored.</li>
    <li>Edits apply on the next generation — no WebUI restart.</li>
  </ul>

  <h4>Composition</h4>
  <p>
    A list line may itself contain placeholders. Those expand recursively, so a
    parent like <code>__hair__</code> can pull in shared
    <code>__length__</code>, <code>__hair/color__</code>, and
    <code>__hair/style__</code>. Use the parent alone, or any child token directly.
  </p>

  <h4>Extra folders &amp; settings</h4>
  <ul>
    <li>Optional second folder: field above + <strong>Save directory</strong>
      (kept after restart).</li>
    <li>More options under <strong>Settings → Dynamic Placeholders</strong>
      (wrap string, nesting depth, negative / Hires prompts, …).</li>
    <li>With <strong>Link seed to placeholder choices</strong>, the same seed
      reproduces the same replacements.</li>
  </ul>

  <p class="dynph-usage-guide-footnote">
    This is a short overview only. Full docs live in the extension repository:
    <code>README.md</code> plus <code>docs/</code>
    (<code>syntax.md</code>, <code>placeholders.md</code>, <code>settings.md</code>,
    <code>examples.md</code>).
  </p>
</div>
"""


def section_description(html: str) -> gr.HTML:
    """Intro copy under a section/accordion heading (same type as field help)."""
    return gr.HTML(f'<p class="dynph-ui-desc dynph-ui-intro">{html}</p>')


def field_help(html: str) -> gr.HTML:
    """Description placed immediately under a control (same look as section copy)."""
    return gr.HTML(f'<p class="dynph-ui-desc">{html}</p>')


def usage_guide() -> gr.HTML:
    """Collapsed quick-start copy for less technical users (not full docs)."""
    return gr.HTML(_USAGE_GUIDE_HTML)


@contextmanager
def setting_block() -> Iterator[None]:
    """
    One setting: control(s) then ``field_help``.

    Shared spacing so checkboxes, textboxes, and other inputs stack evenly.
    """
    with gr.Group(elem_classes=["dynph-setting"]):
        yield
