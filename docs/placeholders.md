# Shipped placeholders

Token name = path under `placeholders/` without the extension (`city.txt` → `__city__`). Nested folders use `/` in the token (`hair/color.txt` → `__hair/color__`).

You can use a parent alone (`__hair__`) and let composition pull in children, or pin a child token directly (`__hair/color__`).

## Top-level tokens

| Token | Role |
|---|---|
| `__profession__` | Subject look (silhouette + distinctive gear / traits) |
| `__expression__` | Facial expression / mood |
| `__makeup__` | Full-face cosmetic looks (natural through theatrical / fantasy) |
| `__race__` | Fantasy / D&D-style subject races (silhouette + signature traits) |
| `__animal__` | Real and mythical creatures (single-word names) |
| `__face__` | Composable face → structure, eyes, nose, lips, ears |
| `__hair__` | Composable hair → `hair/length`, `hair/color`, `hair/style` |
| `__clothes__` | Composable attire → head, torso, pants, fullbody, shoes, etc. |
| `__setting__` | Outdoor / environment backdrop |
| `__location__` | Stereotypical movie / animation scene places |
| `__room__` | Composable interior → type, size, mood, place |
| `__time__` | Time of day / lighting cue |
| `__city__` | Visually distinct city / place names |
| `__country__` | National / cultural subject looks (demonym + signature dress) |
| `__artstyle__` | Non-photorealistic mediums (anime, painting, comic, craft, …) |
| `__photostyle__` | Photorealistic photography looks (cinematic, film stock, optics, …) |
| `__view__` | Viewpoint, facing & composition (dutch angle, profile, …) |
| `__focus__` | Character crop / body focus (upper body, full body, …) |
| `__pose__` | Body stance & gesture (standing, sitting, anime/game tropes, …) |
| `__situation__` | Activity / event (everyday errands through extreme set pieces) |
| `__game__` | Pop-culture breakthrough games (franchise look + signature cues) |

## Composition groups

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

### Clothes

`clothes.txt` keeps **separates** (torso + pants) and **full-body** outfits on different lines so layers never stack. Head and torso are themselves nested groups (`hat` / `glasses` / `piercings`, `shirt` / `jacket`).

Child lists under `placeholders/clothes/`:

- `head/` — `hat`, `glasses`, `piercings` (composed by `head.txt`)
- `torso/` — `shirt`, `jacket` (composed by `torso.txt`)
- plus `scarf`, `fullbody`, `pants`, `shoes`, `accessories`, `jewelry`

### Face

`face.txt` mixes structure with optional feature groups (`__eyes__`, `__nose__`, `__lips__`, `__ears__`) so prompts stay light when you omit layers. Each feature group nests size / shape / color / adjective lists the same way hair does.

### Room vs setting vs location

`room.txt` composes indoor locations from `type` with optional `size`, `mood`, and `place` (dwelling context). Use `__room__` for dwelling interiors, `__setting__` for outdoor / environment backdrops, and `__location__` for stereotypical movie and animation scene places (diner, school hallway, spaceship bridge, and similar).

### View, focus, pose, situation

`__view__` covers angle and composition; `__focus__` covers how much of the figure is in frame; `__pose__` covers how the body is held; `__situation__` covers what is happening — keep them separate so they do not fight.

## File format (short)

- One replacement per line (words, phrases, or full sentences)
- Blank lines and lines starting with `#` are ignored
- Supported extensions: `.txt`, `.text`, `.list`
- A list entry may itself contain placeholders; they expand recursively

Full rules: [syntax.md](syntax.md). Authoring guidance for distinctiveness: [../AGENTS.md](../AGENTS.md).
