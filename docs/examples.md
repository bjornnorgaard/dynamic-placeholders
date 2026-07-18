# Example prompts

Copy these into txt2img with **Dynamic Placeholders → Enable** checked. Each generation picks new lines; turn on **Link seed to placeholder choices** if you want the same seed to reproduce the same expansions.

Token reference: [placeholders.md](placeholders.md). Syntax rules: [syntax.md](syntax.md).

---

## Focused demos

### Portrait — subject + hair + clothes

Simple character sheet. Parents do the nesting work.

```
portrait of a __profession__ with __expression__, __hair__, __clothes__
```

### Portrait — with makeup

`__makeup__` is a full-face cosmetic look; keep it separate from `__lips__` / `__expression__`.

```
portrait of a __profession__ with __expression__, __makeup__, __hair__, __clothes__
```

### Portrait — with skin tone

`__skin__` sets complexion; pair with hair / clothes, not with fantasy race skin cues unless you want them to fight.

```
portrait of a __profession__ with __skin__, __expression__, __hair__, __clothes__
```

### Body build & parts

`__body__` composes overall frame plus optional parts. Pin a part when you want it fixed (`__legs__`, `__stomach__`, …).

```
portrait of a __profession__ with __body__, __expression__, __hair__, __clothes__
```

```
__artstyle__ of a __race__ with __body/frame__, __stomach__, __legs__, __pose__
```

### Famous hero / heroine

`__hero__` and `__heroine__` live under `character/` (short-path works). Use one at a time as the subject — they already carry costume and silhouette. Pin a franchise with `__character/heroine/game/ff7__` when you want a fixed list.

```
__artstyle__ portrait of __hero__, __expression__, __pose__, in a __outdoor__ at __time__
```

```
__photostyle__ of __heroine__ __pose__, __view__, in a __location__
```

### Fantasy race + cultural look

`__race__` and `__country__` both add silhouette cues; useful for stylized fantasy.

```
__artstyle__ of a __race__ warrior, __country__, with __expression__, __face__, __hair__, __clothes__, __pose__
```

### Warrior in armor

`__armor__` is a protective-gear look; use instead of `__clothes__` when you want battle kit, not everyday attire.

```
__artstyle__ of a __race__ warrior in __armor__, __expression__, __pose__, in a __outdoor__
```

### Armed with a weapon

`__weapon__` is an armament look (medieval through modern and sci-fi); pair with armor or clothes, not with hero costume cues that already carry a signature weapon.

```
__artstyle__ of a __profession__ wielding a __weapon__, __expression__, __pose__, in a __outdoor__
```

### Vehicle / conveyance

`__vehicle__` picks one type (car, boat, plane, …) then a distinctive model. Pin a child when you want a family fixed.

```
__photostyle__ of a __profession__ beside a __vehicle__, __pose__, in a __outdoor__ at __time__, __view__
```

```
__artstyle__ of a __vehicle/boat__ on the water at __time__, __weather__, __view__
```

### Scene — game aesthetic

`__game__` is a pop-culture franchise look; use it for style / world cues, not as a subject job.

```
__artstyle__ scene inspired by __game__, __view__, in a __outdoor__ at __time__
```

### Named artist look

`__artist__` is a named animator, cartoonist, or internet-popular illustrator. Use for “by X” / “in the style of X” cues; prefer it instead of stacking with `__artstyle__` so medium and creator do not fight.

```
by __artist__, __focus__, __view__ of a __profession__ with __expression__, __hair__, __clothes__, __pose__
```

### Outdoor scene

Environment-first: outdoor place, city, and time drive the scene.

```
__photostyle__ of a __profession__ __pose__ in a __outdoor__ in __city__ at __time__, __view__
```

### Scenic background / vista

`__background__` is scenery *behind* the subject. Prefer it instead of `__outdoor__` when you want a backdrop, not a place to stand in.

```
__photostyle__ portrait of a __profession__ with __expression__, __pose__, against a __background__, __view__
```

```
__artstyle__ of a __heroine__ standing before a __location/background/cityscape__ at __time__, __weather__
```

### Weather atmosphere

`__weather__` is sky / precipitation / atmosphere only — pair with `__outdoor__` and `__time__`, not as a place substitute.

```
__photostyle__ of a __profession__ __pose__ in a __outdoor__ in __weather__ at __time__, __view__
```

### Situation-driven scene

`__situation__` supplies the activity; pair with pose/location only when you want extra control.

```
__photostyle__ of a __profession__ __situation__, __expression__, __clothes__, __view__
```

### Indoor scene

Use `__house__`, `__castle__`, or `__ballroom__` for interiors; `__outdoor__` for biomes.

```
__photostyle__, __focus__, __view__ of a __profession__ with __expression__, __hair__, __clothes__, __pose__ in a __house__ at __time__
```

### Animal companion / creature focus

```
__artstyle__ of a __animal__ beside a __profession__, in a __outdoor__ at __time__, __view__
```

### Horror monster

`__monster__` is a pop-culture horror creature (film, books, games) — use it instead of `__animal__` when you want dread and familiar iconography, not a simple beast.

```
__artstyle__ of a __monster__ looming in a __outdoor__ at __time__, __view__
```

### Photography look vs art medium

Pick one style family per prompt so they do not compete.

Photoreal:

```
__photostyle__, __focus__, __view__ of a __country__ __profession__ with __face__, __hair__, __clothes__, __pose__, in a __outdoor__ at __time__
```

Stylized:

```
__artstyle__, __focus__, __view__ of a __race__ with __expression__, __hair__, __clothes__, __pose__, in a __city__ street at __time__
```

### Pin child tokens (partial composition)

Bypass the parent when you want one layer fixed and others free — or when you only need a color / crop.

```
close-up portrait, __eyes/color__ eyes, __hair/color__ __hair/style__ hair, wearing __clothes/torso/shirt__
```

```
full body at the beach, wearing __clothes/swimwear__, __pose__, __time__
```

```
full body, standing in a __ballroom__, soft __time__ light
```

### Negative prompt

With **Also expand placeholders in negative prompts** enabled (default), tokens work there too — useful if you add your own `bad_quality.txt` (or similar) lists.

```
blurry, watermark, lowres
```

(Shipped lists do not include a negative-quality token; this slot is for your own files.)

---

## Kitchen-sink showcases

### One-token smoke test — `__random__`

`__random__` picks a full prompt recipe that already nests other families in coherent combinations (portrait, hero, warrior, creature, vehicle, weather, …). Paste it alone to exercise the library without hand-building a kitchen-sink line.

```
__random__
```

These pack as many shipped top-level tokens as practical into one line. Expect long expansions — that is the point: one template, many nested lists.

### Character sheet — art style (most subject tokens)

Covers crop, camera, medium, race, job, culture, expression, makeup, face stack, hair, clothes, pose, outdoor place, city, and time.

```
__focus__, __view__, __pose__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, in a __outdoor__ in __city__ at __time__
```

### Character sheet — photo style + indoor room

Same idea with `__photostyle__` and a dwelling (`__house__` / `__castle__`) instead of art medium / outdoor.

```
__focus__, __view__, __pose__, __photostyle__ of a __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, in a __house__ in __city__ at __time__
```

### Full cast of top-level tokens (including animal)

Uses a wide mix of families — here `__artstyle__` is chosen; swap to `__photostyle__` for camera looks. Prefer one place family unless you are stress-testing.

```
__focus__, __view__, __pose__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, next to a __animal__, outdoors in a __outdoor__, or indoors in a __house__, near __city__ at __time__
```

### Maximal nesting — parents only

One line of parents; the resolver walks into hair / face / clothes / room children automatically.

```
__photostyle__ __focus__ __view__: __pose__ __race__ __profession__ (__country__), __expression__, __makeup__, __face__, __hair__, __clothes__, location __house__ / __outdoor__, __city__, __time__
```

### Maximal nesting — mix parents and children

Shows direct child tokens alongside parents (child wins for that slot; parent still expands its other layers).

```
__artstyle__, __focus__, __view__, __pose__ of a __race__ with __expression__, __makeup__, __face/structure__ with __eyes__, __nose__, __lips__, __ears__, __length__ __hair/color__ __hair/style__ hair, wearing __clothes/head__ and __clothes/fullbody__ with __clothes/feet/shoes__, in a __castle/ballroom__, or outdoors in a __outdoor__ in __city__ at __time__
```

---

## Tips when trying examples

- Start with a focused demo, then graduate to a kitchen-sink line once you know which tokens your model respects.
- Prefer either `__artstyle__` **or** `__photostyle__`, and one place family (`__outdoor__`, `__scene__`, `__background__`, or a dwelling), unless you are deliberately stress-testing.
- `__view__`, `__focus__`, and `__pose__` pair well; avoid stuffing three conflicting camera instructions outside those tokens.
- After editing any `.txt` under `placeholders/`, generate again — no restart required.
