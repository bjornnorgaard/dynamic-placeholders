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

| Token | Resolved file (first match wins) |
|---|---|
| `__name__` | `R/name.txt`, `R/name.text`, or `R/name.list` |
| `__a/b__` | `R/a/b.txt` (etc.) |

Example:

```
placeholders/
  pose.txt
  furniture.txt
  lighting.txt
  lighting/
    color.txt
  scene.txt
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
__hair/length__ __hair/color__ __hair/style__ hair
__hair/color__ __hair/style__, __hair/length__
messy __hair/length__ __hair/color__ hair in a __hair/style__
```

`placeholders/hair/length.txt`:

```
short
long
shoulder-length
```

`placeholders/hair/color.txt`:

```
blonde
brunette
auburn
```

`placeholders/hair/style.txt`:

```
ponytail
loose waves
messy bun
```

Prompt:

```
portrait of a woman with __hair__
```

Possible results:

```
portrait of a woman with long auburn ponytail hair
portrait of a woman with brunette loose waves, short
portrait of a woman with messy shoulder-length blonde hair in a messy bun
```

You can nest as deep as you need (outfit → top → color, and so on). Depth is capped by **Maximum nested replacement depth** in Settings.

### Clothes composition example

`placeholders/clothes.txt` keeps **separates** (torso + pants), **full-body**, and **swimwear** on different lines so layers never stack. Head and torso are themselves composable groups:

```
wearing __clothes/head__, __clothes/torso__, __clothes/pants__, and __clothes/shoes__
wearing __clothes/fullbody__ with __clothes/shoes__ and __clothes/accessories__
wearing __clothes/swimwear__ and __clothes/shoes__
```

Child lists live under `placeholders/clothes/`:

- `head/` — `hat`, `glasses`, `piercings` (composed by `head.txt`)
- `torso/` — `shirt`, `jacket` (composed by `torso.txt`)
- plus `scarf`, `fullbody`, `swimwear`, `pants`, `shoes`, `accessories`, `jewelry`

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
