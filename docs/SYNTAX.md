# Dynamic Placeholders syntax

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
3. If that line contains further placeholders, they are expanded recursively (default max depth: 8).
4. Circular references (A → B → A) stop and leave the cycling token unresolved.
5. Unknown tokens are left unchanged by default (or removed if that setting is off).
6. With **Link seed to placeholder choices** enabled, sampling is driven by the image seed so reruns are reproducible.

## Examples

**Basic**

Prompt:

```
a man __pose__ on a __furniture__
```

Possible result:

```
a man kneeling on a wooden bench
```

**Longer scene fragments**

`placeholders/scene.txt`:

```
a quiet rainy street at dusk, reflections on wet asphalt
an overgrown greenhouse filled with tropical plants
```

Prompt:

```
cinematic photo of __scene__, 35mm
```

**Nested placeholders**

`placeholders/lighting.txt`:

```
soft morning light through curtains
__lighting/color__ studio softboxes
```

`placeholders/lighting/color.txt`:

```
golden amber
cool blue
```

Prompt:

```
portrait, __lighting__
```

Possible result:

```
portrait, cool blue studio softboxes
```

**Negative prompts**

Placeholders work in negative prompts when the setting is enabled:

```
__bad_quality__, blurry, watermark
```

## Tips

- Prefer descriptive filenames (`pose`, `camera_angle`, `wardrobe`) over cryptic abbreviations.
- Keep one concept per file so prompts stay readable.
- Use `#` comments at the top of a file to document intended usage.
- After editing list files, generate again — no WebUI restart is required (cache keys on file mtime).
