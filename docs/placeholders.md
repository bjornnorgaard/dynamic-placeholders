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
| `__age__` | `body/age.txt` |
| `__marking__` | `body/marking.txt` |
| `__villain__` | `character/villain.txt` |
| `__gloves__` | `clothes/hands/gloves.txt` |

Ambiguous short names (two kitchens, two `hands` composers) stay unresolved — use a fuller path. Prefer unique basenames for rooms and features you pin often.

## Shared primitives

| Token | Role |
|---|---|
| `__color__` | Reusable base palette; domain lists compose this plus local-only shades |
| `__size__` | Generic scale (tiny → huge); features add cues like beady / doe-eyed |
| `__length__` | Generic length (cropped → very long); used by hair and similar |
| `__material__` | Hard surfaces (steel, marble, wood, glass, …); armor, furniture, shoes compose this |
| `__fabric__` | Cloth / soft goods (silk, denim, velvet, …); clothes zones compose this |
| `__pattern__` | Prints / repeating designs (stripes, tartan, floral, …); compose with fabric or material |

Domain files should **compose** these (`__fabric__` as a line) and add only domain-only extras. Do not duplicate the shared palette inside every namespace.

## Namespace map

### Subject

| Family | Root | Notes |
|---|---|---|
| Character | `__character__` | Umbrella → hero / heroine / villain / historical / celebrity |
| Profession / race / age | `__profession__`, `__race__`, `__age__` | Subject look (`age` lives under `body/`) |
| Body | `__body__` | Frame + parts + optional `__age__` / `__marking__` / `__hands__` |
| Markings | `__marking__` | Tattoo / scar / birthmark / brand (one family per expand) |
| Creature | `__animal__`, `__monster__`, `__plant__` | Beasts vs horror icons vs flora |
| Culture | `__country__` | Demonym + signature dress (under `location/country`) |

### Appearance

| Family | Root | Notes |
|---|---|---|
| Face | `__face__` | Structure + eyes / nose / lips / ears / eyebrows / facial hair |
| Hair | `__hair__` | `__length__` + `hair/color` + `hair/style` |
| Skin / makeup / expression | `__skin__`, `__makeup__`, `__expression__` | Keep makeup separate from bare lip color and markings |

### Attire & gear

| Family | Root | Notes |
|---|---|---|
| Clothes | `__clothes__` | Zones: head, torso, legs, feet, hands/gloves, fullbody, swimwear, … |
| Armor / weapon | `__armor__`, `__weapon__` | Battle kit vs everyday clothes |
| Props | `__prop__` | Held / furniture / small objects (not weapons) |
| Vehicle | `__vehicle__` | One conveyance type per expand |

### Place

| Family | Root | Notes |
|---|---|---|
| Location | `__location__` | Umbrella — picks **one** family per expand |
| Outdoor | `__outdoor__` | Biomes / environments |
| Scene | `__scene__` | Movie / animation set pieces by category |
| Background | `__background__` | Scenic vistas behind the subject |
| Dwellings | `__house__`, `__castle__`, `__mansion__`, `__cabin__`, `__laboratory__`, `__office__` | Rooms nested under each dwelling |
| City | `__city__` | Named places with signature looks |

Prefer one place family per prompt so outdoor, scene, background, and rooms do not fight.

### Shot, style & atmosphere

| Family | Tokens |
|---|---|
| Camera | `__view__`, `__focus__`, `__pose__` | `__view__` → facing×height under `view/` **or** a composition device; `__pose__` → stance×gesture under `pose/` **or** sit/lie **or** action |
| Light | `__lighting__` (photo / cinema / cartoon / anime illumination — not time or weather) |
| Event | `__situation__` |
| Time / weather / era | `__time__`, `__weather__`, `__era__` |
| Mood | `__atmosphere__` (scene feeling via visual descriptors — not facial expression or lighting technique) |
| Magic | `__magic__` → element or effect (one family per expand) |
| Look | `__artstyle__`, `__artist__`, `__photostyle__` |
| Franchise look | `__game__` |

### Catch-all

| Token | Role |
|---|---|
| `__random__` | Full-prompt recipes that nest other families in coherent combos (one style, one subject, one place, clothes XOR armor, …). Use alone to smoke-test the library. |

## Composition patterns

Parents inject children; pin a child when you want a family fixed.

- `__hair__` → length + color + style
- `__face__` → structure ± eyes / nose / lips / ears / eyebrows / facial hair
- `__body__` → frame ± legs / stomach / chest / arms / hips / hands / age / marking
- `__clothes__` → separates **or** fullbody **or** swimwear (never stacked); zones may compose `__fabric__` / `__pattern__`
- `__marking__` → tattoo **or** scar **or** birthmark **or** brand
- `__prop__` → held **or** furniture **or** small
- `__magic__` → element **or** effect
- `__view__` → `__view/horizontal__` + `__view/vertical__` (facing × height) **or** `__view/composition__`
- `__pose__` → `__pose/stance__` ± `__pose/gesture__` **or** sitting `__pose/sit__` **or** lying `__pose/lie__` **or** `__pose/action__`
- `__location__` → outdoor **or** scene **or** background **or** city **or** a dwelling room
- `__character__` → hero / heroine / villain / historical / celebrity
- `__vehicle__` / `__background__` → one type per expand
- `__random__` → one full prompt recipe per expand (parents inside still nest)

## File format (short)

- One replacement per line; blank lines and `#` comments ignored
- Extensions: `.txt`, `.text`, `.list`
- Lines may contain further placeholders (recursive expand)

Full rules: [syntax.md](syntax.md). Authoring: [../AGENTS.md](../AGENTS.md).
