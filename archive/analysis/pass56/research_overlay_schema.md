# Research overlay schema

File:

    research_overlays/level_observations.json

Example:

```json
{
  "LEV1": [
    {
      "canonical_row": 125,
      "col": 2,
      "label": "reported enemy: 2X2 68-70, drop 71",
      "sprites": [68, 69, 70],
      "drop_sprite": 71,
      "source": "user report",
      "notes": "Clicked cell raw MAP value is 0x01; enemy must be runtime/scripted or visually overlapping from another layer."
    }
  ]
}
```

Fields:
- `canonical_row`: MAP storage/canonical row.
- `col`: tile column.
- `label`: text drawn next to marker.
- `sprites`: optional observed 2X2 sprite indices.
- `drop_sprite`: optional observed dropped 2X2 sprite index.
- `source`: optional provenance.
- `notes`: optional longer explanation.

These observations are not parsed enemy data.
They are verification markers used during reverse engineering.
