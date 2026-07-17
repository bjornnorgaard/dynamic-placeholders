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

### Fantasy race + cultural look

`__race__` and `__country__` both add silhouette cues; useful for stylized fantasy.

```
__artstyle__ of a __race__ warrior, __country__, with __expression__, __face__, __hair__, __clothes__, __pose__
```

### Scene — game aesthetic

`__game__` is a pop-culture franchise look; use it for style / world cues, not as a subject job.

```
__artstyle__ scene inspired by __game__, __view__, in a __setting__ at __time__
```

### Outdoor scene

Environment-first: setting, city, and time drive the backdrop.

```
__photostyle__ of a __profession__ __pose__ in a __setting__ in __city__ at __time__, __view__
```

### Situation-driven scene

`__situation__` supplies the activity; pair with pose/setting only when you want extra control.

```
__photostyle__ of a __profession__ __situation__, __expression__, __clothes__, __view__
```

### Indoor scene

Use `__room__` instead of `__setting__` for interiors.

```
__photostyle__, __focus__, __view__ of a __profession__ with __expression__, __hair__, __clothes__, __pose__ in a __room__ at __time__
```

### Animal companion / creature focus

```
__artstyle__ of a __animal__ beside a __profession__, in a __setting__ at __time__, __view__
```

### Photography look vs art medium

Pick one style family per prompt so they do not compete.

Photoreal:

```
__photostyle__, __focus__, __view__ of a __country__ __profession__ with __face__, __hair__, __clothes__, __pose__, in a __setting__ at __time__
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
full body, standing in a __room/mood__ __room/type__, soft __time__ light
```

### Negative prompt

With **Also expand placeholders in negative prompts** enabled (default), tokens work there too — useful if you add your own `bad_quality.txt` (or similar) lists.

```
blurry, watermark, lowres
```

(Shipped lists do not include a negative-quality token; this slot is for your own files.)

---

## Kitchen-sink showcases

These pack as many shipped top-level tokens as practical into one line. Expect long expansions — that is the point: one template, many nested lists.

### Character sheet — art style (most subject tokens)

Covers crop, camera, medium, race, job, culture, expression, makeup, face stack, hair, clothes, pose, outdoor place, city, and time.

```
__focus__, __view__, __pose__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, in a __setting__ in __city__ at __time__
```

### Character sheet — photo style + indoor room

Same idea with `__photostyle__` and `__room__` instead of art medium / outdoor setting.

```
__focus__, __view__, __pose__, __photostyle__ of a __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, in a __room__ in __city__ at __time__
```

### Full cast of top-level tokens (including animal)

Uses every shipped top-level token except the competing style pair — here `__artstyle__` is chosen; swap to `__photostyle__` for camera looks. `__setting__` and `__room__` both appear so you can see outdoor + interior cues in one template (trim one if the scene feels crowded).

```
__focus__, __view__, __pose__, __artstyle__ of a __race__ __profession__, __country__, with a __expression__, __makeup__, __face__, __hair__, __clothes__, next to a __animal__, outdoors in a __setting__, indoors hint of a __room__, near __city__ at __time__
```

### Maximal nesting — parents only

One line of parents; the resolver walks into hair / face / clothes / room children automatically.

```
__photostyle__ __focus__ __view__: __pose__ __race__ __profession__ (__country__), __expression__, __makeup__, __face__, __hair__, __clothes__, location __room__ / __setting__, __city__, __time__
```

### Maximal nesting — mix parents and children

Shows direct child tokens alongside parents (child wins for that slot; parent still expands its other layers).

```
__artstyle__, __focus__, __view__, __pose__ of a __race__ with __expression__, __makeup__, __face/structure__ with __eyes__, __nose__, __lips__, __ears__, __hair/length__ __hair/color__ __hair/style__ hair, wearing __clothes/head__ and __clothes/fullbody__ with __clothes/shoes__, in a __room/size__ __room/mood__ __room/type__ in a __room/place__, or outdoors in a __setting__ in __city__ at __time__
```

---

## Tips when trying examples

- Start with a focused demo, then graduate to a kitchen-sink line once you know which tokens your model respects.
- Prefer either `__artstyle__` **or** `__photostyle__`, and either `__setting__` **or** `__room__`, unless you are deliberately stress-testing.
- `__view__`, `__focus__`, and `__pose__` pair well; avoid stuffing three conflicting camera instructions outside those tokens.
- After editing any `.txt` under `placeholders/`, generate again — no restart required.
