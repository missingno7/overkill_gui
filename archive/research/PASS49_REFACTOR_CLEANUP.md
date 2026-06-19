# Pass49 refactor cleanup

## Cleanup

- Moved root-level `PASS*.md` research notes into:

    archive/research/

- Moved `analysis/` into:

    archive/analysis/

- Deleted old generated `sample_previews/`.

## Refactor

Created package structure:

    overkill/
      core.py
      gui/app.py

`overkill/core.py` now contains:
- SHADOW archive parsing,
- BIC decoding,
- LOGO type-0 escape-RLE parser,
- type-3/type-4 BIC parser helpers,
- BLX/MAP parsing,
- EGA rendering helpers,
- level rendering helpers.

`overkill/gui/app.py` now contains:
- Tkinter UI,
- resource browser,
- level viewer,
- inspector handling.

`overkill_graphics_browser.py` is now only a compatibility runner.

## GUI

Added top-level tabs:

- Graphics Browser
- Level Viewer

The Level Viewer has its own focused render button and canvas for LEVxMAP/LEVxBLX.
Clicking a cell uses the same MAP inspector logic.
