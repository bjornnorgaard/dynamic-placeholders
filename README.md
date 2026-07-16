# Dynamic Placeholders

File-based prompt placeholders for **Stable Diffusion WebUI Forge - Neo** (also works with Automatic1111-compatible frontends).

Write lists of words or longer phrases in text files, then reference them in prompts with `__name__`. At generation time each placeholder is replaced with a random line from the matching file.

```
a man __pose__ on a __furniture__, __scene__
```

Example expansion:

```
a man sitting cross-legged on the floor on a leather recliner, a quiet rainy street at dusk, reflections on wet asphalt
```

This extension is intentionally separate from [sd-dynamic-prompts](https://github.com/adieyal/sd-dynamic-prompts): a dedicated `placeholders/` folder, no combinatorial/Jinja/magic-prompt stack, and list lines meant for full phrases and sentences.

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
   a man __pose__ on a __furniture__
   ```

3. Sample lists ship in `placeholders/` (`pose`, `furniture`, composable `hair` → `hair/*`, etc.). Edit those files or add new ones — changes are picked up on the next generation (mtime-based cache).

Composition works out of the box: put `__hair/length__ __hair/color__ __hair/style__` inside `hair.txt`, then use `__hair__` in the prompt and all nested tokens expand recursively. See [docs/SYNTAX.md](docs/SYNTAX.md).
## Placeholder files

| Prompt token | File |
|---|---|
| `__pose__` | `placeholders/pose.txt` |
| `__furniture__` | `placeholders/furniture.txt` |
| `__hair__` | `placeholders/hair.txt` |
| `__hair/color__` | `placeholders/hair/color.txt` |
| `__lighting/color__` | `placeholders/lighting/color.txt` |
| `__scene__` | `placeholders/scene.txt` |

Rules:

- One replacement per line (words, phrases, or full sentences).
- Blank lines and lines starting with `#` are ignored.
- The placeholder name is the file path relative to the placeholders root, without the extension.
- Supported extensions: `.txt`, `.text`, `.list`.
- Nested folders use `/` in the token: `__lighting/color__`.
- A list entry may itself contain placeholders; they expand recursively.

Default root:

```
extensions/dynamic-placeholders/placeholders/
```

Override under **Settings → Dynamic Placeholders → Placeholders directory**.

## UI options

| Control | Effect |
|---|---|
| Enable Dynamic Placeholders | Master switch for the current generation |
| Link seed to placeholder choices | Same seed → same replacements (reproducible) |

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

## How it hooks into Forge Neo

Forge Neo uses the same extension script API as Automatic1111. This extension registers an `AlwaysVisible` script and rewrites `p.all_prompts` (and optional negative / HR prompts) inside `Script.process()`, after `setup_prompts()` and before sampling — the same stage sd-dynamic-prompts uses.

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
├── placeholders/       # your list files live here
├── scripts/
│   └── dynamic_placeholders.py
└── tests/
    └── test_resolver.py
```

## License

MIT — see [LICENSE](LICENSE).
