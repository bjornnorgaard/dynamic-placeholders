# Shipped placeholders (overview)

Token name = path under `placeholders/` without the extension (`pose.txt` → `__pose__`). Nested folders use `/` (`face/eyes/color.txt` → `__face/eyes/color__`).

Browse `placeholders/` for the full set. This page maps **families** and how they fit together — not every leaf file.

## Short-path resolution

Exact paths always win. If a token has no exact file, the library looks for a **unique** file whose relative name equals the token or ends with `/{token}`:

| Token | Can resolve to |
|---|---|
| `__eyes__` | `face/eyes.txt` |
| `__ballroom__` | `location/castle/ballroom.txt` |
| `__castle/ballroom__` | `location/castle/ballroom.txt` |
| `__heroine__` | `character/heroine.txt` |

Ambiguous short names (two kitchens, two libraries) stay unresolved — use a fuller path. Prefer unique leaf names for rooms and features you pin often.

## Shared primitives

| Token | Role |
|---|---|
| `__color__` | Reusable base palette; domain lists compose this plus local-only shades |
| `__size__` | Generic scale (tiny → huge); features add cues like beady / doe-eyed |
| `__length__` | Generic length (cropped → very long); used by hair and similar |

## Namespace map

### Subject

| Family | Root | Notes |
|---|---|---|
| Character | `__character__` | Umbrella → `__hero__` / `__heroine__` → media → franchise |
| Profession / race | `__profession__`, `__race__` | Subject look |
| Body | `__body__` | Frame + optional parts (`legs`, `stomach`, `chest`, `arms`, …) |
| Creature | `__animal__`, `__monster__` | Beasts vs horror icons |
| Culture | `__country__` | Demonym + signature dress (under `location/country`) |

### Appearance

| Family | Root | Notes |
|---|---|---|
| Face | `__face__` | Structure + `face/eyes`, `nose`, `lips`, `ears` |
| Hair | `__hair__` | `__length__` + `hair/color` + `hair/style` |
| Skin / makeup / expression | `__skin__`, `__makeup__`, `__expression__` | Keep makeup separate from bare lip color |

### Attire & gear

| Family | Root | Notes |
|---|---|---|
| Clothes | `__clothes__` | Zones: head, torso, legs, feet, fullbody, swimwear, … |
| Armor / weapon | `__armor__`, `__weapon__` | Battle kit vs everyday clothes |
| Vehicle | `__vehicle__` | One conveyance type per expand |

### Place

| Family | Root | Notes |
|---|---|---|
| Location | `__location__` | Umbrella — picks **one** family per expand |
| Outdoor | `__outdoor__` | Biomes / environments |
| Scene | `__scene__` | Movie / animation set pieces by category |
| Background | `__background__` | Scenic vistas behind the subject |
| Dwellings | `__house__`, `__castle__`, `__mansion__`, `__cabin__` | Rooms nested under each dwelling |
| City | `__city__` | Named places with signature looks |

Prefer one place family per prompt so outdoor, scene, background, and rooms do not fight.

### Shot & style

| Family | Tokens |
|---|---|
| Camera | `__view__`, `__focus__`, `__pose__` |
| Light | `__lighting__` (photo / cinema / cartoon / anime illumination — not time or weather) |
| Event | `__situation__` |
| Time / weather | `__time__`, `__weather__` |
| Look | `__artstyle__`, `__artist__`, `__photostyle__` |
| Franchise look | `__game__` |

### Catch-all

| Token | Role |
|---|---|
| `__random__` | Full-prompt recipes that nest other families in coherent combos (one style, one subject, one place, clothes XOR armor, …). Use alone to smoke-test the library. |

## Composition patterns

Parents pull in children; pin a child when you want a family fixed.

- `__hair__` → length + color + style
- `__face__` → structure ± eyes / nose / lips / ears
- `__body__` → frame ± legs / stomach / chest / arms / hips / … (pin `__stomach__`, `__legs__`, …)
- `__clothes__` → separates **or** fullbody **or** swimwear (never stacked)
- `__location__` → outdoor **or** scene **or** background **or** city **or** a dwelling room
- `__character/heroine__` → game / movie / comics / animation → franchise list
- `__vehicle__` / `__background__` → one type per expand
- `__random__` → one full prompt recipe per expand (parents inside still nest)

## File format (short)

- One replacement per line; blank lines and `#` comments ignored
- Extensions: `.txt`, `.text`, `.list`
- Lines may contain further placeholders (recursive expand)

Full rules: [syntax.md](syntax.md). Authoring: [../AGENTS.md](../AGENTS.md).
