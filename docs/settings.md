# Settings & UI

## Script accordion (txt2img / img2img)

| Control | Effect |
|---|---|
| Enable | Master switch for the current generation |
| Link seed to placeholder choices | Same seed → same replacements (reproducible) |
| Additional placeholders directory | Optional second folder searched after the default/settings directory (default wins on name conflicts). Use **Save directory** to keep it across restarts. |
| How to use | Collapsed quick-start overview (syntax, list files, composition, settings) |

## Settings page

**Settings → Dynamic Placeholders**

| Setting | Default | Meaning |
|---|---|---|
| Placeholders directory | extension `placeholders/` | Where list files live (empty = default) |
| Additional placeholders directory | _(empty)_ | Optional second folder (same as the script accordion field) |
| Placeholder wrap string | `__` | Characters around the name |
| Maximum nested replacement depth | `8` | Cap for recursive expansion |
| Leave unknown placeholders unchanged | on | Missing files keep `__name__` in the prompt |
| Save original template in generation parameters | on | Writes template into PNG info |
| Also expand placeholders in negative prompts | on | Same expansion as the positive prompt |
| Also expand placeholders in Hires. fix prompts | on | Expands placeholders in HR prompts |

## Directories

Default root:

```
extensions/sd-dynamic-placeholders/placeholders/
```

Override under **Settings → Dynamic Placeholders → Placeholders directory**, or add an extra folder in the script accordion and click **Save directory**. The extra path is stored in the extension’s `user_settings.json` (and synced to WebUI settings when possible) so it survives restarts.

Search order when an additional directory is set:

1. Primary placeholders directory (settings / default)
2. Additional directory

On name conflicts, the **primary** file wins.

## Autocomplete

Typing `__` in a prompt (or negative / HR prompt) opens a list of available placeholder names. Choose one to insert a closed token such as `__hair__` or `__clothes/torso/shirt__`.

- **Built-in:** works without other extensions. Uses the wrap string and placeholders directory from Settings.
- [Tag Autocomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete): if that extension is installed with wildcard search enabled, it owns `__` completion instead. This extension keeps a `wildcards/` symlink to `placeholders/` so Tag Autocomplete can discover the same lists.

## How it works (Forge Neo)

On Forge Neo this extension registers an `AlwaysVisible` script and rewrites `p.all_prompts` (and optional negative / HR prompts) inside `Script.process()`, after `setup_prompts()` and before sampling.

Each `__token__` is resolved independently (two `__expression__` tokens can become two different faces). With seed linking enabled, sampling is driven by the image seed so reruns match. The unresolved template stays in the UI / PNG info when that setting is on. Missing list files or an empty placeholders directory produce clear console warnings.

## Layout

```
sd-dynamic-placeholders/
├── README.md
├── AGENTS.md                 # list-authoring rules (distinctiveness)
├── docs/
│   ├── syntax.md
│   ├── placeholders.md
│   ├── settings.md
│   └── examples.md
├── javascript/
│   ├── dynamic_placeholders_autocomplete.js
│   └── dynamic_placeholders_extra_dir.js
├── lib_dynamic_placeholders/
│   ├── autocomplete.py       # __ prefix matching + TAC wildcards link
│   ├── console.py            # missing-list / empty-dir warnings
│   ├── library.py            # file discovery + caching
│   ├── paths.py              # directory resolution
│   ├── resolver.py           # __token__ expansion
│   ├── settings.py           # WebUI settings + user_settings.json
│   └── ui.py                 # accordion helpers + How to use guide
├── placeholders/             # shipped + your list files
├── wildcards/                # symlink → placeholders (Tag Autocomplete)
├── scripts/
│   └── dynamic_placeholders.py
├── style.css
└── tests/
```
