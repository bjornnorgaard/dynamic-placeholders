# Dynamic Placeholders

A Stable Diffusion WebUI extension that turns prompt tokens into random phrase expansions from plain text files.

Write lists under `placeholders/`, then use `__name__` in a prompt. At generation time each token is replaced with a random line from the matching file. Nested tokens inside those lines expand recursively, so one high-level placeholder can compose hair, clothes, setting, and more from smaller lists.

```
portrait of __profession__ with a __expression__, __hair__, __clothes__, in a __setting__ at __time__, __city__
```

Example expansion:

```
portrait of firefighter in turnout gear with reflective stripes, helmet, and soot-smudged face with a sly smirk, long auburn high ponytail hair, wearing knit beanie, wire-rim glasses, flannel shirt under a denim jacket, blue jeans, and sneakers, in a pine forest misty at dawn at golden hour, Tokyo with neon streets, dense towers, and Shinto shrine courtyards
```

Built for **Stable Diffusion WebUI Forge - Neo** and other Automatic1111-compatible frontends.

## Why this exists

[sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts) is a full combinatorial / Jinja / magic-prompt toolkit. Dynamic Placeholders is narrower on purpose:

- A dedicated `placeholders/` folder (not `wildcards/`)
- One random line per token — no combinatorial explosion
- List lines are first-class **phrases and sentences**, not only single words
- Nested composition so parent lists (`__hair__`, `__clothes__`) pull in child lists automatically
- Shipped lists tuned for **visual distinctiveness** in image models (fewer near-duplicates, sharper silhouettes)

Use it when you want varied, readable prompt fragments without learning a template language.

## Install

1. Copy or clone this folder into your Forge Neo `extensions/` directory:

   ```
   .../Stable Diffusion WebUI Forge - Neo/extensions/dynamic-placeholders/
   ```

2. Restart the WebUI (Stability Matrix → restart package, or rerun `webui.sh`).

3. Confirm **Dynamic Placeholders** appears as an accordion under the txt2img / img2img generation controls.

No extra Python packages are required.

## Quick start

1. Open the **Dynamic Placeholders** accordion and leave **Enable** checked.
2. Use a prompt like:

   ```
   portrait of __profession__ with __hair__, __clothes__, in a __setting__
   ```

3. Edit the shipped lists under `placeholders/`, or add new `.txt` files. Changes are picked up on the next generation (mtime-based cache — no restart).

Composition is built in: `__hair__` expands into length / color / style; `__clothes__` expands into separates or full-body outfits without stacking conflicting layers. Full syntax: [docs/SYNTAX.md](docs/SYNTAX.md).

## What ships in `placeholders/`

| Token | Role |
|---|---|
| `__profession__` | Subject look (silhouette + distinctive gear / traits) |
| `__expression__` | Facial expression / mood |
| `__hair__` | Composable hair → `hair/length`, `hair/color`, `hair/style` |
| `__clothes__` | Composable attire → head, torso, pants, fullbody, shoes, etc. |
| `__setting__` | Environment / backdrop |
| `__time__` | Time of day / lighting cue |
| `__city__` | Visually distinct city / place names |

Composable groups use nested paths:

| Token | File |
|---|---|
| `__hair__` | `placeholders/hair.txt` |
| `__hair/color__` | `placeholders/hair/color.txt` |
| `__clothes__` | `placeholders/clothes.txt` |
| `__clothes/torso__` | `placeholders/clothes/torso.txt` |
| `__clothes/torso/shirt__` | `placeholders/clothes/torso/shirt.txt` |
| `__clothes/fullbody__` | `placeholders/clothes/fullbody.txt` |

`clothes.txt` keeps **separates** (torso + pants) and **full-body** outfits on different lines so layers never stack. Head and torso are themselves nested groups (`hat` / `glasses` / `piercings`, `shirt` / `jacket`).

You can use child tokens directly (`__hair/color__`, `__clothes/shoes__`) or only the parent and let composition do the work.

## Placeholder files

Rules:

- One replacement per line (words, phrases, or full sentences).
- Blank lines and lines starting with `#` are ignored.
- The placeholder name is the file path relative to the placeholders root, without the extension.
- Supported extensions: `.txt`, `.text`, `.list`.
- Nested folders use `/` in the token: `__clothes/head/hat__`.
- A list entry may itself contain placeholders; they expand recursively.

Default root:

```
extensions/dynamic-placeholders/placeholders/
```

Override under **Settings → Dynamic Placeholders → Placeholders directory**, or point an extra folder at generation time (see below).

## UI options

| Control | Effect |
|---|---|
| Enable Dynamic Placeholders | Master switch for the current generation |
| Link seed to placeholder choices | Same seed → same replacements (reproducible) |
| Additional placeholders directory | Optional second folder searched after the default/settings directory (default wins on name conflicts) |

## Settings

**Settings → Dynamic Placeholders**

| Setting | Default | Meaning |
|---|---|---|
| Placeholders directory | extension `placeholders/` | Where list files live |
| Placeholder wrap string | `__` | Characters around the name |
| Maximum nested replacement depth | `8` | Cap for recursive expansion |
| Leave unknown placeholders unchanged | on | Missing files keep `__name__` in the prompt |
| Save original template in generation parameters | on | Writes template into PNG info |
| Also expand placeholders in negative prompts | on | |
| Also expand placeholders in Hires. fix prompts | on | |

## How it works

Forge Neo uses the same extension script API as Automatic1111. This extension registers an `AlwaysVisible` script and rewrites `p.all_prompts` (and optional negative / HR prompts) inside `Script.process()`, after `setup_prompts()` and before sampling.

Each `__token__` is resolved independently (two `__expression__` tokens can become two different faces). With seed linking enabled, sampling is driven by the image seed so reruns match. The unresolved template stays in the UI / PNG info when that setting is on.

You do **not** need Forge-specific APIs for prompt rewriting.

## Coexistence with sd-dynamic-prompts

Both extensions understand `__name__`-style tokens. If both are enabled they can interfere. Prefer one of:

- Disable Dynamic Prompts when using Dynamic Placeholders, or
- Disable Dynamic Placeholders when using Dynamic Prompts, or
- Point each at different directories and avoid overlapping token names.

Dynamic Placeholders uses `placeholders/` by default; Dynamic Prompts uses `wildcards/`.

## Tests

From the extension directory (WebUI does not need to be running):

```bash
python -m unittest discover -s tests -v
```

## Layout

```
dynamic-placeholders/
├── README.md
├── docs/
│   └── SYNTAX.md
├── lib_dynamic_placeholders/
│   ├── library.py      # file discovery + caching
│   ├── paths.py        # directory resolution
│   ├── resolver.py     # __token__ expansion
│   └── settings.py     # WebUI settings page
├── placeholders/       # shipped + your list files
├── scripts/
│   └── dynamic_placeholders.py
└── tests/
    └── test_resolver.py
```

## License

MIT — see [LICENSE](LICENSE).
