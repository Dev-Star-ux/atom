# Atomic Physics Lecture

An **offline**, interactive simulation program for teaching atomic physics.
No internet connection, no API, no external service. Built with Python's
standard-library `tkinter`, so it can be packaged into a single Windows `.exe`.

## Current content

**Chapter 1 — Structure of the Atom**
**Section 1 — The Element of the Atom: Electron**

1. **Electric Charge & the Discovery of the Electron** — Thomson's cathode-ray
   tube. Deflect the electron beam with electric and magnetic fields and see
   that it carries negative charge.
2. **Determining the Mass & Charge of the Electron** — Millikan's oil-drop
   experiment. Balance an oil drop and read a charge that is always a
   whole-number multiple of the elementary charge *e*.
3. **Mass Analysis of Matter** — a mass spectrometer. Accelerate and bend ions
   in a magnetic field, separate isotopes, and build a mass spectrum.

## Run from source

```
python main.py
```

## Build the standalone .exe

```
build.bat
```

The finished program is `dist\AtomicPhysicsLecture.exe`. It runs on its own —
no Python needed on the target machine.

## Configuration (font & language)

- **Settings** (bottom-left button) changes the **language** and **font** while
  the app is running.
- `config.json` (next to the `.exe`) stores those choices and can be edited by
  hand.
- Language files live in the `lang/` folder as `<code>.json`. Only English
  (`en.json`) ships right now. To add a language, copy `en.json` to, e.g.,
  `ko.json`, translate the values, set `"_meta": {"name": "..."}`, and it will
  appear in the Settings language list automatically — no rebuild required.

## Adding more content later

1. Create a new simulation class in `simulations/` (subclass `Simulation` in
   `simulations/base.py`; implement `build_controls`, `reset`, `tick`, `draw`).
2. Register it in `CURRICULUM` in `core/app.py`.
3. Add its text strings to `lang/en.json`.

## Project layout

```
main.py                 entry point
core/
  app.py                main window, navigation, settings, curriculum registry
  config.py             load/save config.json
  i18n.py               language-file loader and lookup
  paths.py              paths that work from source and from the .exe
simulations/
  base.py               shared layout + animation loop
  cathode_ray.py        topic 1
  millikan.py           topic 2
  mass_spec.py          topic 3
lang/en.json            English strings
config.json             saved font / language
build.bat               PyInstaller build script
```
