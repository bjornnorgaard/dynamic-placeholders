# Dynamic Placeholders

A [Stable Diffusion WebUI Forge - Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) extension that turns prompt tokens into random phrase expansions from plain text files.

**Only tested with Forge Neo.** It may work on other Automatic1111-compatible frontends, but that is unsupported.

Write lists under `placeholders/`, then use `__name__` in a prompt. At generation time each token is replaced with a random line from the matching file. Nested tokens inside those lines expand recursively, so one high-level placeholder can compose hair, clothes, setting, and more from smaller lists.

```
__focus__, __view__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __face__, __hair__, __clothes__, in a __setting__ in __city__ at __time__
```

Example expansion:

```
upper body from the waist up, three-quarter view, watercolor painting of a orc with green-gray skin, protruding tusks, and heavy brow firefighter in turnout gear with reflective stripes, helmet, and soot-smudged face, Japanese in kimono with obi sash and wooden geta, with a sly smirk, oval face with soft jawline and high cheekbones with large green almond-shaped eyes, straight nose, full pink lips, and pointed ears, long auburn high ponytail hair, wearing knit beanie, wire-rim glasses, flannel shirt under a denim jacket, blue jeans, and sneakers, in a pine forest misty at dawn in Tokyo with neon streets, dense towers, and Shinto shrine courtyards at golden hour
```

## Features

- A dedicated `placeholders/` folder for list files
- One random line per token — no combinatorial explosion
- List lines are first-class **phrases and sentences**, not only single words
- Nested composition so parent lists (`__hair__`, `__clothes__`, `__face__`, `__room__`) pull in child lists automatically
- Shipped lists tuned for **visual distinctiveness** in image models (fewer near-duplicates, sharper silhouettes)

## Install

1. Copy or clone this folder into your Forge Neo `extensions/` directory:

   ```
   .../Stable Diffusion WebUI Forge - Neo/extensions/sd-dynamic-placeholders/
   ```

2. Restart the WebUI (Stability Matrix → restart package, or rerun `webui.sh`).

3. Confirm **Dynamic Placeholders** appears as an accordion under the txt2img / img2img generation controls.

No extra Python packages are required.

## Quick start

1. Open the **Dynamic Placeholders** accordion and leave **Enable** checked. The collapsed **How to use** section is a short in-UI overview.
2. Use a prompt with tokens, for example:

   ```
   portrait of __profession__ with __hair__, __clothes__, in a __setting__
   ```

3. Edit the shipped lists under `placeholders/`, or add new `.txt` files. Changes are picked up on the next generation (mtime-based cache — no restart).

4. In the prompt box, type `__` to autocomplete placeholder names (arrow keys / Enter or Tab to insert `__name__`).

Composition is built in: `__hair__` expands into length / color / style; `__clothes__` into separates or full-body outfits; `__face__` into structure plus eyes / nose / lips / ears; `__room__` into type with optional size / mood / place. Full syntax: [docs/SYNTAX.md](docs/SYNTAX.md).

## What ships in `placeholders/`

| Token | Role |
|---|---|
| `__profession__` | Subject look (silhouette + distinctive gear / traits) |
| `__expression__` | Facial expression / mood |
| `__race__` | Fantasy / D&D-style subject races (silhouette + signature traits) |
| `__animal__` | Real and mythical creatures (single-word names) |
| `__face__` | Composable face → structure, eyes, nose, lips, ears |
| `__hair__` | Composable hair → `hair/length`, `hair/color`, `hair/style` |
| `__clothes__` | Composable attire → head, torso, pants, fullbody, shoes, etc. |
| `__setting__` | Outdoor / environment backdrop |
| `__room__` | Composable interior → type, size, mood, place |
| `__time__` | Time of day / lighting cue |
| `__city__` | Visually distinct city / place names |
| `__country__` | National / cultural subject looks (demonym + signature dress) |
| `__artstyle__` | Non-photorealistic mediums (anime, painting, comic, craft, …) |
| `__photostyle__` | Photorealistic photography looks (cinematic, film stock, optics, …) |
| `__view__` | Viewpoint, facing & composition (dutch angle, profile, …) |
| `__focus__` | Character crop / body focus (upper body, full body, …) |
| `__pose__` | Body stance & gesture (standing, sitting, anime/game tropes, …) |

Composable groups use nested paths:

| Token | File |
|---|---|
| `__hair__` | `placeholders/hair.txt` |
| `__hair/color__` | `placeholders/hair/color.txt` |
| `__face__` | `placeholders/face.txt` |
| `__face/structure__` | `placeholders/face/structure.txt` |
| `__eyes__` | `placeholders/eyes.txt` |
| `__eyes/color__` | `placeholders/eyes/color.txt` |
| `__clothes__` | `placeholders/clothes.txt` |
| `__clothes/torso__` | `placeholders/clothes/torso.txt` |
| `__clothes/torso/shirt__` | `placeholders/clothes/torso/shirt.txt` |
| `__clothes/fullbody__` | `placeholders/clothes/fullbody.txt` |
| `__room__` | `placeholders/room.txt` |
| `__room/type__` | `placeholders/room/type.txt` |

`clothes.txt` keeps **separates** (torso + pants) and **full-body** outfits on different lines so layers never stack. Head and torso are themselves nested groups (`hat` / `glasses` / `piercings`, `shirt` / `jacket`).

`face.txt` mixes structure with optional feature groups (`__eyes__`, `__nose__`, `__lips__`, `__ears__`) so prompts stay light when you omit layers. Each feature group nests size / shape / color / adjective lists the same way hair does.

`room.txt` composes indoor locations from `type` with optional `size`, `mood`, and `place` (dwelling context). Use `__room__` for interiors and `__setting__` for outdoor / environment backdrops.

`__view__` covers angle and composition; `__focus__` covers how much of the figure is in frame; `__pose__` covers how the body is held — keep them separate so they do not fight.

You can use child tokens directly (`__hair/color__`, `__eyes/shape__`, `__clothes/shoes__`, `__room/mood__`) or only the parent and let composition do the work.

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
extensions/sd-dynamic-placeholders/placeholders/
```

Override under **Settings → Dynamic Placeholders → Placeholders directory**, or add an extra folder in the script accordion and click **Save directory**. The extra path is stored in the extension’s `user_settings.json` (and synced to WebUI settings when possible) so it survives restarts.

## UI options

| Control | Effect |
|---|---|
| Enable | Master switch for the current generation |
| Link seed to placeholder choices | Same seed → same replacements (reproducible) |
| Additional placeholders directory | Optional second folder searched after the default/settings directory (default wins on name conflicts). Use **Save directory** to keep it across restarts. |
| How to use | Collapsed quick-start overview (syntax, list files, composition, settings) |

## Settings

**Settings → Dynamic Placeholders**

| Setting | Default | Meaning |
|---|---|---|
| Placeholders directory | extension `placeholders/` | Where list files live |
| Additional placeholders directory | _(empty)_ | Optional second folder (same as the script accordion field) |
| Placeholder wrap string | `__` | Characters around the name |
| Maximum nested replacement depth | `8` | Cap for recursive expansion |
| Leave unknown placeholders unchanged | on | Missing files keep `__name__` in the prompt |
| Save original template in generation parameters | on | Writes template into PNG info |
| Also expand placeholders in negative prompts | on | Same expansion as the positive prompt |
| Also expand placeholders in Hires. fix prompts | on | Expands placeholders in HR prompts |

## How it works

On Forge Neo this extension registers an `AlwaysVisible` script and rewrites `p.all_prompts` (and optional negative / HR prompts) inside `Script.process()`, after `setup_prompts()` and before sampling.

Each `__token__` is resolved independently (two `__expression__` tokens can become two different faces). With seed linking enabled, sampling is driven by the image seed so reruns match. The unresolved template stays in the UI / PNG info when that setting is on. Missing list files or an empty placeholders directory produce clear console warnings.

## Autocomplete

Typing `__` in a prompt (or negative / HR prompt) opens a list of available placeholder names. Choose one to insert a closed token such as `__hair__` or `__clothes/torso/shirt__`.

- Built-in: works without other extensions. Uses the wrap string and placeholders directory from Settings.
- [Tag Autocomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete): if that extension is installed with wildcard search enabled, it owns `__` completion instead. This extension keeps a `wildcards/` symlink to `placeholders/` so Tag Autocomplete can discover the same lists.

## Tests

From the extension directory (WebUI does not need to be running):

```bash
python -m unittest discover -s tests -v
```

## Layout

```
sd-dynamic-placeholders/
├── README.md
├── docs/
│   └── SYNTAX.md
├── javascript/
│   ├── dynamic_placeholders_autocomplete.js
│   └── dynamic_placeholders_extra_dir.js
├── lib_dynamic_placeholders/
│   ├── autocomplete.py # __ prefix matching + TAC wildcards link
│   ├── console.py      # missing-list / empty-dir warnings
│   ├── library.py      # file discovery + caching
│   ├── paths.py        # directory resolution
│   ├── resolver.py     # __token__ expansion
│   ├── settings.py     # WebUI settings + user_settings.json
│   └── ui.py           # accordion helpers + How to use guide
├── placeholders/       # shipped + your list files
├── wildcards/          # symlink → placeholders (Tag Autocomplete)
├── scripts/
│   └── dynamic_placeholders.py
├── style.css
└── tests/
    ├── test_autocomplete.py
    ├── test_paths.py
    └── test_resolver.py
```

## License

MIT — see [LICENSE](LICENSE).
