# Agent guidance — placeholder lists

This repo ships text lists under `placeholders/` for Stable Diffusion prompt tokens (`__name__`). When creating or editing those lists, optimize for **image-model distinguishability**, not geographic or taxonomic completeness.

## Core rule: variety without redundancy

Each line must produce a **visually different** result from every other line in the same file when sampled by a typical Stable Diffusion model.

- Prefer **fewer, sharper entries** over long near-duplicate catalogs.
- If two entries would likely share the same skyline, street fabric, climate palette, or architectural family, **keep only the most distinctive one**.
- Descriptors help, but they do not rescue lookalikes — models often ignore fine landmark wording and fall back to a generic regional look.

### Cities / places (hard lesson)

Do **not** list every capital (or city) in a region. East Asian capitals such as Tokyo, Seoul, Beijing, and Pyongyang are a classic failure mode: the model will not reliably tell them apart. Same for clusters like Central European Gothic cities, Nordic harbor capitals, Andean highland cities, Gulf desert towers, or Caribbean coastal towns.

Pick **one exemplar per visual family**, worldwide coverage by contrast — not by count.

Bad: Tokyo + Seoul + Beijing + Pyongyang  
Good: Tokyo (and leave the rest of that visual family out)

Bad: Prague + Budapest + Vienna + Warsaw  
Good: one Central / Imperial European look, or skip the cluster if another European entry already covers it

## Applies to every placeholder category

Same logic for professions, settings, clothes, hair, expressions, lighting, etc.:

| Prefer | Avoid |
|---|---|
| Distinct silhouettes, materials, climates, eras | Near-synonyms and slight variants |
| Entries that change composition or palette | Exhaustive regional / taxonomic coverage |
| Short signature cues the model already knows | Long landmark laundry lists hoping to force a difference |

Before adding a line, ask: *If this and an existing line both got sampled, would the images look interchangeable?* If yes, do not add it — replace or drop.

## Namespacing

Organize lists in folders so related tokens read as a tree:

| Umbrella | Lives under | Example |
|---|---|---|
| Place | `location/` | `location/castle/ballroom.txt` |
| Character | `character/` | `character/heroine/game/ff7.txt` |
| Face features | `face/` | `face/eyes/color.txt` |
| Clothes zones | `clothes/` | `clothes/legs/pants.txt` |

- Token name = path without extension; nested folders use `/`.
- Root composers (`location.txt`, `clothes.txt`, `face.txt`) pick **one** mutually exclusive family per line so layers never stack.
- Short-path resolution: unique leaf / suffix names also match (`__eyes__` → `face/eyes.txt`, `__ballroom__` → `location/castle/ballroom.txt`). If two files share a basename, short-path fails — rename for uniqueness or require a fuller path.
- Prefer unique basenames for leaves users will pin often.

### Shared vs local attributes

Top-level shared lists:

- `__color__` — base palette
- `__size__` — generic scale
- `__length__` — generic length

Domain files should **compose** these (`__color__` as a line) and add only domain-only extras (lipstick shades, heterochromia, fashion hair blends, cavernous rooms). Do not duplicate the shared palette inside every namespace.

## Token boundaries & familiarity

Do not dump lookalikes across adjacent tokens. Prefer the sharper home for the entry:

| Token | Keep | Leave out |
|---|---|---|
| `__monster__` | Horror / pop-culture icons with dread | Simple beasts (`__animal__`), RPG types like vampire (`__race__`), plain human slashers |
| `__game__` | Breakthrough franchise looks | Near-clone genres and niche titles |
| `__artist__` | Named animators / cartoonists / internet illustrators | Bare mediums (`__artstyle__`), oil painters, photographers |
| `__makeup__` | Full-face cosmetic looks | Bare lip color (`__lips__`), expression blush |
| `__location/outdoor__` | Biomes / environments | Movie set pieces (`location/scene`), dwelling rooms |
| `__location/scene__` | Film / animation tropes | Outdoor biomes, named cities |

When a list is meant for named cultural icons (monsters, games, heroes), prefer **broadly familiar** exemplars over niche completeness. One short signature cue after the name is enough — do not pad with landmark laundry lists.

## File conventions

- One replacement phrase per line; `#` comments and blank lines are ignored.
- Match existing style: short, no leading `a`/`an`/`the`, lead with the main noun.
- Header comments should state the token, intended prompt slots, and the distinctiveness rule.
- New **families** (new umbrella roots): add the lists, then a short note in `docs/placeholders.md` and a demo in `docs/examples.md` if useful. Do **not** catalog every leaf file in the docs — the folder tree is the catalog.
