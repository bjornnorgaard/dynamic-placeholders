# Dynamic Placeholders

A [Stable Diffusion WebUI Forge - Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) extension that turns prompt tokens into random phrase expansions from plain text files.

**Only tested with Forge Neo.** It may work on other Automatic1111-compatible frontends, but that is unsupported.

Write lists under `placeholders/`, then use `__name__` in a prompt. At generation time each token is replaced with a random line from the matching file. Nested tokens inside those lines expand recursively, so one high-level placeholder can compose hair, clothes, location, and more from smaller lists.

```
__focus__, __view__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, in a __location__ at __time__
```

Browse `placeholders/` for every shipped token. Docs give an overview of families, not a full catalog.

## Features

- Dedicated `placeholders/` folder for list files
- One random line per token — no combinatorial explosion
- List lines are phrases and sentences, not only single words
- Nested composition and short-path lookup (`__eyes__` → `face/eyes.txt` when unique)
- Shared primitives (`__color__`, `__size__`, `__length__`) reused across domains
- Shipped lists tuned for **visual distinctiveness** in image models

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
   portrait of __profession__ with __hair__, __clothes__, in a __location__
   ```

3. Edit the shipped lists under `placeholders/`, or add new `.txt` files. Changes are picked up on the next generation (mtime-based cache — no restart).

4. In the prompt box, type `__` to autocomplete placeholder names (arrow keys / Enter or Tab to insert `__name__`).

Composition is built in: `__hair__` expands into length / color / style; `__clothes__` into separates or full-body outfits; `__face__` into structure plus features; `__location__` into outdoor, scene, background, city, or a dwelling room. Details: [docs/syntax.md](docs/syntax.md).

## Documentation

| Doc | Contents |
|---|---|
| [docs/syntax.md](docs/syntax.md) | Token syntax, short-path lookup, expansion & composition rules |
| [docs/placeholders.md](docs/placeholders.md) | Namespace map and composition families (not a full catalog) |
| [docs/settings.md](docs/settings.md) | Accordion controls, Settings page, logging, autocomplete |
| [docs/examples.md](docs/examples.md) | Ready-to-paste prompts (focused demos and kitchen-sink showcases) |

For authors editing shipped lists: [AGENTS.md](AGENTS.md) (visual distinctiveness rules).

## Tests

From the extension directory (WebUI does not need to be running):

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
