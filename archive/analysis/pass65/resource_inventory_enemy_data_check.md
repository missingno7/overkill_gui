# Resource inventory / enemy data check

Archive resources are mostly BIC graphics/tiles/maps and ENC screen/audio resources.

Current conclusion:

- LEVxMAP.BIC payloads decode exactly to 13*288 MAP bytes, plus only no-op/alignment endings; no hidden enemy layer after MAP payload.
- LEVxBLX.BIC are tilesets.
- 2X2.BIC is sprite sheet source.
- OPAGE/IPAGE/PLAQ/OKMENU etc. look like compressed screens/UI pages or non-level pages, not obvious enemy coordinate data.
- The strongest position logic currently lives in EXE runtime object/spawn code, not archive MAP data.

This does not prove there is no packed level script in EXE/ENC; it means it is not visible as a simple per-level archive resource parallel to LEVxMAP.
