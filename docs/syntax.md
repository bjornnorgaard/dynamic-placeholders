# Dynamic Placeholders syntax

Related docs: [placeholders.md](placeholders.md) (shipped tokens) · [settings.md](settings.md) (UI & options) · [examples.md](examples.md) (ready-to-paste prompts)

## Tokens

A placeholder is a name wrapped on both sides by the wrap string (default `__`):

```
__pose__
__furniture__
__lighting/color__
```

Names may contain letters, digits, `_`, `-`, and path separators `/` or `\`.

The wrap string is configurable in **Settings → Dynamic Placeholders**. If you change it to `@@`, tokens look like `@@pose@@`.

## File mapping

Given placeholders root `R`:

| Step | Behavior |
|---|---|
| 1. Exact path | `__name__` → `R/name.txt` (also `.text` / `.list`); `__a/b__` → `R/a/b.txt` |
| 2. Short-path | If exact misses, find a **unique** file whose relative name equals the token or ends with `/{token}` |

Examples:

- `__eyes__` → `face/eyes.txt` when that is the only `eyes` list
- `__ballroom__` → `location/castle/ballroom.txt` when unique
- `__castle/ballroom__` → `location/castle/ballroom.txt` via suffix match

If two or more files match a short-path (e.g. `house/kitchen.txt` and `castle/kitchen.txt` for `__kitchen__`), the token is left unresolved — use a fuller path (`__castle/kitchen__` or `__location/castle/kitchen__`). Exact paths always win over deeper short-path candidates.

Example tree:

```
placeholders/
  pose.txt
  color.txt
  face/
    eyes.txt
  location/
    castle/
      ballroom.txt
```

## List file format

```
# Comments start with #
# Empty lines are skipped

jumping
sitting
lying on side
sitting cross-legged on the floor
```

- Encoding: UTF-8
- Each non-empty, non-comment line is one full replacement candidate
- Lines may be long; multi-word phrases and sentences are first-class

## Expansion rules

1. Every `__token__` in the prompt is replaced independently (two `__pose__` tokens can become two different poses).
2. The chosen line is inserted as-is.
3. **Composition:** if that line contains further `__placeholders__`, they are expanded recursively (default max depth: 8). A single parent file can pull in many child lists this way.
4. Circular references (A → B → A) stop and leave the cycling token unresolved.
5. Unknown tokens are left unchanged by default (or removed if that setting is off).
6. With **Link seed to placeholder choices** enabled, sampling is driven by the image seed so reruns are reproducible.

## Composition (nested placeholders)

Placeholders are fully composable. Put `__child__` tokens inside a parent list file; when the parent is expanded, each nested token is resolved from its own file.

### Hair composition example

`placeholders/hair.txt`:

```
__length__ __hair/color__ __hair/style__ hair
__length__ __hair/color__ hair, __hair/style__
```

Shared `__length__` and `__color__` live at the placeholders root; `hair/color.txt` composes `__color__` plus hair-only shades. `hair/style.txt` holds cuts and arrangements.

Prompt:

```
portrait of a woman with __hair__
```

You can nest as deep as you need (outfit → top → color, and so on). Depth is capped by **Maximum nested replacement depth** in Settings.

### Clothes composition example

`placeholders/clothes.txt` keeps **separates** (torso + legs), **full-body**, and **swimwear** on different lines so layers never stack. Head and torso are themselves composable groups:

```
wearing __clothes/head__, __clothes/torso__, __clothes/legs/pants__, and __clothes/feet/shoes__
wearing __clothes/fullbody__ with __clothes/feet/shoes__ and __clothes/accessories__
wearing __clothes/swimwear__ and __clothes/feet/shoes__
```

Child lists live under `placeholders/clothes/` by body zone (`head/`, `torso/`, `legs/`, `feet/`, plus `fullbody`, `swimwear`, …).
## Minimal examples

Prompt:

```
portrait of a __profession__ with __hair__
```

Possible result (composition from `hair.txt`):

```
portrait of a firefighter in turnout gear with reflective stripes, helmet, and soot-smudged face with long auburn ponytail hair
```

Custom nested lists of your own:

```
placeholders/
  lighting.txt          →  soft morning light / __lighting/color__ studio softboxes
  lighting/color.txt    →  golden amber / cool blue
```

Prompt `portrait, __lighting__` might become `portrait, cool blue studio softboxes`.

For fuller ready-to-paste prompts (focused demos and kitchen-sink showcases), see [examples.md](examples.md).

## Tips

- Prefer descriptive filenames (`pose`, `hair/color`, `wardrobe`) over cryptic abbreviations.
- Keep one concept per file, then compose them in higher-level files (e.g. `hair.txt`).
- Use `#` comments at the top of a file to document intended usage.
- After editing list files, generate again — no WebUI restart is required (cache keys on file mtime).
- Placeholders also expand in negative / Hires prompts when those settings are on — see [settings.md](settings.md).
