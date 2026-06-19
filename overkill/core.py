from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from PIL import Image, ImageDraw
except Exception as exc:  # pragma: no cover
    print("This tool requires Pillow. Install with: pip install pillow")
    raise

EGA_PALETTE = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
]

NAME_KIND_HINTS = {
    "1X1.BIC": "small 16x16-ish sprites",
    "2X2.BIC": "larger sprites / powerups / enemies",
    "2X2C.BIC": "larger sprites, alternate sheet",
    "SHIP.BIC": "player/enemy ship graphics, layout not fully solved",
    "G0.BIC": "not a normal BIC sprite sheet yet; RLE/header variant unresolved",
    "G3.BIC": "small 8-byte table/metadata, probably not bitmap graphics",
    "ADLIB.ENC": "audio/music-related data, not graphics",
    "ROLAND.ENC": "audio/music-related data, not graphics",
    "G1.BIC": "32x32 animation frames / level graphics",
    "G2.BIC": "32x32 animation frames / level graphics",
    "G4.BIC": "32x32 animation frames / level graphics",
    "G5.BIC": "32x32 animation frames / level graphics",
    "PANEL.ENC": "right HUD/panel full-screen-ish encoded page",
    "OKMENU.ENC": "menu encoded page",
    "LOGO.BIC": "logo / title-related BIC resource",
}


def ega_image(pixels: Iterable[int], width: int, height: int) -> Image.Image:
    img = Image.new("P", (width, height))
    pal = []
    for r, g, b in EGA_PALETTE:
        pal += [r, g, b]
    pal += [0, 0, 0] * (256 - 16)
    img.putpalette(pal)
    img.putdata([p & 15 for p in pixels])
    return img.convert("RGB")


def scale_nearest(img: Image.Image, scale: int) -> Image.Image:
    if scale <= 1:
        return img
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)


def packbits_decode(src: bytes, expected_size: Optional[int] = None) -> bytes:
    """PackBits-style RLE used by .BIC after the 7-byte header."""
    out = bytearray()
    i = 0
    while i < len(src):
        control = src[i]
        i += 1
        if control <= 127:
            count = control + 1
            out.extend(src[i:i + count])
            i += count
        elif control >= 129:
            count = 257 - control
            if i >= len(src):
                break
            out.extend([src[i]] * count)
            i += 1
        else:  # 128 noop
            pass
        if expected_size is not None and len(out) >= expected_size:
            return bytes(out[:expected_size])
    return bytes(out)


@dataclass
class ResourceEntry:
    index: int
    name: str
    start_rel: int
    start_abs: int
    size: int
    raw_dir_entry: bytes
    data: bytes

    @property
    def ext(self) -> str:
        return self.name.rsplit(".", 1)[-1].upper() if "." in self.name else ""


class ShadowArchive:
    def __init__(self, overkill_file: Path):
        self.overkill_file = overkill_file
        self.file_data = overkill_file.read_bytes()
        self.overlay_base = self._find_overlay_base(self.file_data)
        self.overlay = self.file_data[self.overlay_base:]
        self.count = int.from_bytes(self.overlay[0:2], "little")
        self.key = int.from_bytes(self.overlay[2:4], "little")
        self.signature = self.overlay[4:10]
        self.entry_len = int.from_bytes(self.overlay[10:12], "little")
        if self.signature != b"SHADOW":
            raise ValueError(f"SHADOW signature not found at overlay base. Got {self.signature!r}")
        self.dir_size = 12 + self.count * self.entry_len
        self.entries = self._parse_entries()

    @staticmethod
    def _find_overlay_base(data: bytes) -> int:
        sig = data.find(b"SHADOW")
        if sig < 4:
            raise ValueError("Could not find SHADOW signature in OVERKILL data file.")
        return sig - 4

    def _parse_entries(self) -> list[ResourceEntry]:
        entries: list[ResourceEntry] = []
        pos = 12
        ax = self.key
        for idx in range(self.count):
            enc = self.overlay[pos:pos + self.entry_len]
            if len(enc) != self.entry_len:
                raise ValueError("Truncated SHADOW directory")
            al = ax & 0xFF
            ah = (ax >> 8) & 0xFF
            dec = bytearray()
            for c in enc:
                dec.append(c ^ al)
                al = (al + ah) & 0xFF
            ax = (ah << 8) | al
            raw = bytes(dec)
            start = int.from_bytes(raw[5:9], "little")
            size = int.from_bytes(raw[9:13], "little")
            name = raw[13:self.entry_len].split(b"\0", 1)[0].decode("ascii", "replace").strip()
            data = self.overlay[start:start + size]
            entries.append(ResourceEntry(idx, name, start, self.overlay_base + start, size, raw, data))
            pos += self.entry_len
        return entries

    def extract_all(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        for e in self.entries:
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", e.name or f"entry_{e.index}")
            (out_dir / f"{e.index:02d}_{safe}").write_bytes(e.data)

    def directory_json(self) -> dict:
        return {
            "overkill_file": str(self.overkill_file),
            "overlay_base": self.overlay_base,
            "count": self.count,
            "key": self.key,
            "entry_len": self.entry_len,
            "dir_size": self.dir_size,
            "entries": [
                {
                    "index": e.index,
                    "name": e.name,
                    "start_rel": e.start_rel,
                    "start_abs": e.start_abs,
                    "size": e.size,
                    "ext": e.ext,
                }
                for e in self.entries
            ],
        }


@dataclass
class BicDecoded:
    expected_size: int
    fields_or_count_byte: int
    block_size: int
    decoded: bytes
    ok: bool


def decode_bic(data: bytes) -> BicDecoded:
    if len(data) < 7:
        raise ValueError("BIC too small")
    expected = int.from_bytes(data[1:3], "little")
    fields = data[3]
    block_size = int.from_bytes(data[5:7], "little")
    decoded = packbits_decode(data[7:], expected)
    return BicDecoded(expected, fields, block_size, decoded, len(decoded) == expected)


def render_planar_4bpp(raw: bytes, width: int, height: int, row_interleaved: bool = True, bitrev: bool = False) -> Optional[Image.Image]:
    wb = (width + 7) // 8
    needed = wb * height * 4
    if len(raw) < needed:
        return None
    pixels = []
    bit_order = range(8) if bitrev else range(7, -1, -1)
    if row_interleaved:
        for y in range(height):
            base = y * wb * 4
            for xb in range(wb):
                vals = [raw[base + p * wb + xb] for p in range(4)]
                for bit in bit_order:
                    x = xb * 8 + (bit if bitrev else 7 - bit)
                    if x < width:
                        pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
    else:
        plane_size = wb * height
        for y in range(height):
            for xb in range(wb):
                vals = [raw[p * plane_size + y * wb + xb] for p in range(4)]
                for bit in bit_order:
                    x = xb * 8 + (bit if bitrev else 7 - bit)
                    if x < width:
                        pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
    # Generic row-plane renderer must not apply orientation corrections.
    # Orientation is resource-specific. Applying a global vertical flip here made
    # 2X2/G/MANEXPL/THEND previews upside-down while WINDOW.BIC stayed correct
    # only because it uses its own type-3 full-image renderer.
    return ega_image(pixels, width, height)


def render_nibbles(raw: bytes, width: int, height: int, high_first: bool = True) -> Optional[Image.Image]:
    needed = (width * height + 1) // 2
    if len(raw) < needed:
        return None
    pixels = []
    for b in raw[:needed]:
        if high_first:
            pixels.extend([(b >> 4) & 15, b & 15])
        else:
            pixels.extend([b & 15, (b >> 4) & 15])
    return ega_image(pixels[:width * height], width, height)


def transposed_records(raw: bytes, record_size: int, item_count: int) -> list[bytes]:
    if record_size <= 0 or item_count <= 0:
        return []
    max_len = record_size * item_count
    raw = raw[:max_len]
    return [bytes(raw[field * item_count + i] for field in range(record_size)) for i in range(item_count)]


def render_sprite_record(rec: bytes, mode: str = "row", bitrev: bool = False, force_size: Optional[int] = None) -> Optional[Image.Image]:
    if len(rec) < 8:
        return None
    width = force_size or (rec[0] if rec[0] else 16)
    if width <= 0 or width > 128:
        width = force_size or 16
    wb = rec[2] if rec[2] else (width + 7) // 8
    if wb <= 0 or wb > 32:
        wb = (width + 7) // 8
    # The known sheets are square-ish; header byte 0 is a good height hint.
    height = force_size or (rec[0] if rec[0] in (8, 16, 24, 32, 40, 48, 64) else max(1, (len(rec) - 4) // (wb * 4)))
    data = rec[4:]
    return render_planar_4bpp(data, width, height, row_interleaved=(mode == "row"), bitrev=bitrev)


def make_sprite_sheet(decoded: BicDecoded, name: str, max_items: int = 300) -> Image.Image:
    record_size = decoded.fields_or_count_byte
    item_count = decoded.block_size
    records = transposed_records(decoded.decoded, record_size, item_count)
    # The row/non-bitrev interpretation is currently the best confirmed one for 1X1/2X2/2X2C.
    images: list[tuple[int, Image.Image]] = []
    for i, rec in enumerate(records[:max_items]):
        img = render_sprite_record(rec, mode="row", bitrev=False)
        if img:
            images.append((i, img))
    if not images:
        raise ValueError("Could not render transposed sprite records")
    scale = 5 if "1X1" in name.upper() else 4
    cell_w = max(40, max(img.width for _, img in images) * scale + 10)
    cell_h = max(42, max(img.height for _, img in images) * scale + 18)
    cols = 16 if "1X1" in name.upper() else 12
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for j, (idx, img) in enumerate(images):
        x = (j % cols) * cell_w
        y = (j // cols) * cell_h
        scaled = scale_nearest(key_known_transparency_colors(key_dominant_corner_color(img)), scale)
        sheet.paste(scaled, (x, y))
        draw.text((x + 2, y + scaled.height + 1), str(idx), fill=(230, 230, 230))
    return sheet


def make_fixed_record_sheet(decoded: BicDecoded, name: str, record_size: int, width: int, height: int, skip: int = 4, transposed: bool = True, scale: int = 4, cols: int = 8) -> Image.Image:
    raw = decoded.decoded
    if len(raw) % record_size != 0:
        raise ValueError(f"Decoded size {len(raw)} is not divisible by record size {record_size}")
    item_count = len(raw) // record_size
    records = transposed_records(raw, record_size, item_count) if transposed else [raw[i * record_size:(i + 1) * record_size] for i in range(item_count)]
    images: list[tuple[int, Image.Image]] = []
    for i, rec in enumerate(records):
        img = render_planar_4bpp(rec[skip:], width, height, row_interleaved=True, bitrev=False)
        if img:
            images.append((i, img))
    if not images:
        raise ValueError("Could not render fixed-size records")
    cell_w = max(56, width * scale + 16)
    cell_h = max(60, height * scale + 22)
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for j, (idx, img) in enumerate(images):
        x = (j % cols) * cell_w
        y = (j // cols) * cell_h
        scaled = scale_nearest(img, scale)
        sheet.paste(scaled, (x + 4, y + 4))
        draw.text((x + 4, y + scaled.height + 5), str(idx), fill=(230, 230, 230))
    return sheet



def decode_map_rows(decoded: BicDecoded) -> list[bytes]:
    """Decode LEVxMAP type-4 transposed records into rows.

    Important pass29 correction:
    LEVxMAP.BIC has BIC type=4, field/record size 13 and count 288.
    The decoded payload is still transposed by field, just like BLX resources.
    Correct row_i is:

        row_i = bytes(decoded.decoded[field * 288 + i] for field in range(13))

    The previous direct row-major interpretation caused nonsense placement.
    """
    raw = decoded.decoded
    width = int(getattr(decoded, "fields_or_count_byte", 0) or 13)
    height = int(getattr(decoded, "block_size", 0) or (len(raw) // max(1, width)))
    if width <= 0 or height <= 0 or len(raw) < width * height:
        width = 13 if len(raw) % 13 == 0 else max(1, int(math.sqrt(len(raw))))
        height = len(raw) // width
        return [raw[i * width:(i + 1) * width] for i in range(height)]

    # Type-4 transposed records.
    return [bytes(raw[field * height + row] for field in range(width)) for row in range(height)]



def is_map_metadata_row(row: bytes) -> bool:
    """Heuristic for non-playfield MAP metadata/header row.

    Several LEVxMAP resources have canonical row 0 starting with 0x00 and then
    a small set of values that do not behave like normal level cells. When the
    map is reversed for gameplay display this row appears as the very last row.

    Keep this rule deliberately narrow: row[0] == 0. LEV0 currently does not
    match and is left untouched.
    """
    return bool(row) and row[0] == 0


def playable_map_rows_with_indices(decoded: BicDecoded) -> list[tuple[int, bytes]]:
    """Return canonical row index + row for rows considered part of the level."""
    rows = decode_map_rows(decoded)
    start = 1 if rows and is_map_metadata_row(rows[0]) else 0
    return list(enumerate(rows[start:], start=start))


def map_rows_for_display_with_indices(decoded: BicDecoded) -> list[tuple[int, bytes]]:
    """Gameplay-oriented MAP row order, preserving canonical row indices."""
    return list(reversed(playable_map_rows_with_indices(decoded)))


def map_rows_for_display(decoded: BicDecoded) -> list[bytes]:
    """Gameplay-oriented MAP row order for display, excluding metadata rows."""
    return [row for _, row in map_rows_for_display_with_indices(decoded)]





def decode_bic_type3_stream(source_data: bytes) -> bytes:
    """Decode type=3 full-image payload.

    Type=3 full-image streams start at source_data[5], not source_data[7].
    The first decoded byte is an alignment/padding byte for the row-plane image.
    """
    decoded = packbits_decode(source_data[5:], None)
    if decoded:
        decoded = decoded[1:]
    return decoded


def render_bic_type3_image(decoded: BicDecoded, source_data: bytes) -> Optional[Image.Image]:
    """Render BIC type=3 full/image-like row-plane resources.

    Dimensions:
        height     = source_data[2]
        widthBytes = source_data[4]

    Payload:
        PackBits(source_data[5:])[1:]
    """
    if len(source_data) < 7 or source_data[0] != 3:
        return None

    height = source_data[2]
    width_bytes = source_data[4]
    if width_bytes <= 0 or height <= 0:
        return None

    need = width_bytes * height * 4
    raw = decode_bic_type3_stream(source_data)
    if len(raw) < need:
        raw = raw + bytes(need - len(raw))
    else:
        raw = raw[:need]

    pixels: list[int] = []
    for y in range(height):
        row = raw[y * width_bytes * 4:(y + 1) * width_bytes * 4]
        for xb in range(width_bytes):
            vals = [row[p * width_bytes + xb] for p in range(4)]
            for bit in range(7, -1, -1):
                pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
    return ega_image(pixels, width_bytes * 8, height)







def make_bluebits_diagnostic(decoded: BicDecoded, source_data: bytes, scale: int = 3) -> Image.Image:
    """Diagnostic preview for BLUEBITS.BIC.

    BLUEBITS is type=3 and appears to contain:
      1) one visible 96x79 source image,
      2) several embedded image-like chunks of varying dimensions,
      3) additional non-image/reveal/blitter data.

    The extra chunks shown here are data-derived candidates from scanning the
    corrected stream after the visible bitmap for embedded headers:

        word height
        word widthBytes

    This is still a diagnostic, not a final animation parser.
    """
    base = render_bic_type3_image(decoded, source_data)
    if base is None:
        return Image.new("RGB", (320, 120), (24, 24, 24))

    raw = decode_bic_type3_stream(source_data)
    visible_len = source_data[4] * source_data[2] * 4
    extra = raw[visible_len:]

    labelled: list[tuple[str, Image.Image]] = [("source 96x79", base)]

    def render_rowplane_bytes(data: bytes, width_bytes: int, height: int) -> Optional[Image.Image]:
        need = width_bytes * height * 4
        if len(data) < need:
            return None
        pixels: list[int] = []
        for y in range(height):
            row = data[y * width_bytes * 4:(y + 1) * width_bytes * 4]
            for xb in range(width_bytes):
                vals = [row[p * width_bytes + xb] for p in range(4)]
                for bit in range(7, -1, -1):
                    pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
        return ega_image(pixels, width_bytes * 8, height)

    # Pass46 selected non-overlapping candidates. The first two are very likely
    # the large outline ship views; some later ones are UI/reveal/text/strip data.
    candidates = [
        (0, 93, 16),       # 128x93 outline/ship-like
        (5956, 113, 18),   # 144x113 outline/ship-like
        (15200, 35, 12),   # 96x35 small cyan object
        (16884, 44, 15),   # 120x44 cyan object
        (20732, 36, 16),   # 128x36 cyan object
        (23040, 44, 18),   # 144x44 cyan object
        (26212, 45, 16),   # text/panel-like
        (29096, 45, 16),   # text/panel-like
        (36472, 10, 40),   # 320x10 strip
        (38076, 10, 40),   # 320x10 strip
    ]

    for off, h, wb in candidates:
        if off + 4 + wb * h * 4 <= len(extra):
            img = render_rowplane_bytes(extra[off + 4:], wb, h)
            if img:
                labelled.append((f"extra@{off} {wb*8}x{h}", img))

    sheet = make_labelled_sheet(labelled, scale=scale, cols=3)
    note_h = 72
    out = Image.new("RGB", (sheet.width, sheet.height + note_h), (24, 24, 24))
    out.paste(sheet, (0, 0))
    draw = ImageDraw.Draw(out)
    draw.text((8, sheet.height + 8), f"BLUEBITS corrected stream len={len(raw)}, visible={visible_len}, extra={len(extra)} bytes.", fill=(255, 255, 0))
    draw.text((8, sheet.height + 26), "Visible image + multiple embedded candidates. Real animation/reveal still needs EXE blitter trace.", fill=(220, 220, 220))
    draw.text((8, sheet.height + 44), "Likely not simple frame sequence; contains outlines, strips, and command/reveal-like data.", fill=(220, 220, 220))
    return out






def decode_logo_type0_escape_rle(source_data: bytes) -> tuple[bytes, int, int, int]:
    """Decode LOGO.BIC type=0 escape-RLE.

    Header:
        byte 0 = type = 0
        byte 1 = escape marker
        word 2 = height
        byte 4 = widthBytes

    Payload starts at byte 5.

    RLE rule:
        if byte == escape:
            count = next byte
            value = next byte
            emit value repeated count times
        else:
            emit byte literally

    Important alignment rule:
        Like type=3 full-image streams, LOGO.BIC produces one leading decoded
        alignment/padding byte before the actual row-plane image data.

        Decode widthBytes * height * 4 + 1 bytes, then drop decoded[0].

    For LOGO.BIC:
        escape = 0x36
        height = 0x0040 = 64
        widthBytes = 0x22 = 34
        image bytes = 34 * 64 * 4 = 8704
        decoded stream bytes used = 8705 including alignment byte
    """
    if len(source_data) < 5 or source_data[0] != 0:
        return b"", 0, 0, 0

    escape = source_data[1]
    height = int.from_bytes(source_data[2:4], "little")
    width_bytes = source_data[4]
    image_size = width_bytes * height * 4
    expected_stream_size = image_size + 1

    out = bytearray()
    i = 5
    while i < len(source_data) and len(out) < expected_stream_size:
        b = source_data[i]
        i += 1
        if b == escape and i + 1 < len(source_data):
            count = source_data[i]
            value = source_data[i + 1]
            i += 2
            out.extend([value] * count)
        else:
            out.append(b)

    if len(out) < expected_stream_size:
        out.extend([0] * (expected_stream_size - len(out)))

    # Drop the leading decoded alignment byte. This is what fixes the 8px shift.
    image_data = bytes(out[1:1 + image_size])
    return image_data, width_bytes, height, escape




def render_logo_bic(source_data: bytes) -> Optional[Image.Image]:
    """Render solved LOGO.BIC image."""
    decoded, width_bytes, height, escape = decode_logo_type0_escape_rle(source_data)
    if not decoded or width_bytes <= 0 or height <= 0:
        return None

    pixels: list[int] = []
    for y in range(height):
        row = decoded[y * width_bytes * 4:(y + 1) * width_bytes * 4]
        for xb in range(width_bytes):
            vals = [row[p * width_bytes + xb] for p in range(4)]
            for bit in range(7, -1, -1):
                pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
    return ega_image(pixels, width_bytes * 8, height)


def make_logo_solved_preview(source_data: bytes, archive: Optional[ShadowArchive] = None) -> Image.Image:
    """Show solved LOGO.BIC and optionally overlay it on WINDOW.BIC."""
    logo_img = render_logo_bic(source_data)
    if logo_img is None:
        return make_logo_probe_image(source_data)

    panels: list[tuple[str, Image.Image]] = [("LOGO solved 272x64", logo_img)]

    # Helpful context: overlay the logo onto WINDOW.BIC at 0,0.
    if archive is not None:
        try:
            window_entry = next((e for e in archive.entries if e.name.upper() == "WINDOW.BIC"), None)
            if window_entry:
                window_dec = decode_bic(window_entry.data)
                bg = render_bic_type3_image(window_dec, window_entry.data)
                if bg:
                    composite = bg.copy()
                    # Treat black as transparent for title overlay preview.
                    mask = Image.new("L", logo_img.size, 0)
                    pix = logo_img.convert("RGB").load()
                    mp = mask.load()
                    for y in range(logo_img.height):
                        for x in range(logo_img.width):
                            if pix[x, y] != (0, 0, 0):
                                mp[x, y] = 255
                    composite.paste(logo_img, (0, 0), mask)
                    panels.append(("LOGO over WINDOW @0,0", composite))
        except Exception:
            pass

    sheet = make_labelled_sheet(panels, scale=2, cols=1)

    decoded, width_bytes, height, escape = decode_logo_type0_escape_rle(source_data)
    note_h = 72
    out = Image.new("RGB", (max(sheet.width, 760), sheet.height + note_h), (24, 24, 24))
    out.paste(sheet, (0, 0))
    draw = ImageDraw.Draw(out)
    draw.text((8, sheet.height + 8), f"LOGO type=0 solved: escape=0x{escape:02X}, widthBytes={width_bytes}, height={height}, image={len(decoded)} bytes (+1 alignment byte).", fill=(255, 255, 0))
    draw.text((8, sheet.height + 26), "RLE: escape count value -> repeat value count times; other bytes are literals.", fill=(220, 220, 220))
    draw.text((8, sheet.height + 44), "Leading decoded alignment byte is dropped; this fixes the 8px image shift.", fill=(220, 220, 220))
    return out


def render_type0_logo_probe_images(source_data: bytes) -> list[tuple[str, Image.Image]]:
    """Diagnostic probes for unresolved LOGO.BIC type=0."""
    probes: list[tuple[str, Image.Image]] = []
    if len(source_data) < 8:
        return probes

    def rowplane(raw: bytes, width_bytes: int, height: int, label: str):
        need = width_bytes * height * 4
        if len(raw) < need or width_bytes <= 0 or height <= 0:
            return
        pixels: list[int] = []
        data = raw[:need]
        for y in range(height):
            row = data[y * width_bytes * 4:(y + 1) * width_bytes * 4]
            for xb in range(width_bytes):
                vals = [row[p * width_bytes + xb] for p in range(4)]
                for bit in range(7, -1, -1):
                    pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
        probes.append((label, ega_image(pixels, width_bytes * 8, height)))

    header_width_bytes = source_data[4] or 34
    candidate_heights = []
    for value, label in [
        (source_data[1], "h=byte1"),
        (source_data[2], "h=byte2"),
        (source_data[5], "h=byte5"),
        (54, "h=54"),
        (64, "h=64"),
    ]:
        if value and (value, label) not in candidate_heights:
            candidate_heights.append((value, label))

    candidates: list[tuple[int, int, str]] = []
    seen = set()
    for h, hlabel in candidate_heights:
        for wb, wlabel in [(header_width_bytes, f"wb={header_width_bytes}"), (40, "wb=40/320px")]:
            key = (wb, h)
            if key not in seen:
                seen.add(key)
                candidates.append((wb, h, f"{wlabel} {hlabel}"))

    for off in (0, 6, 7, 16, 32):
        for wb, h, desc in candidates[:8]:
            rowplane(source_data[off:], wb, h, f"raw off {off} {desc}")

    for start in (5, 6, 7):
        try:
            dec = packbits_decode(source_data[start:], None)
            for wb, h, desc in candidates[:8]:
                rowplane(dec, wb, h, f"packbits {start} {desc}")
        except Exception:
            pass

    return probes



def key_dominant_corner_color(img: Image.Image, key_to: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    rgb = img.convert("RGB")
    px = rgb.load()
    coords = [(0, 0), (rgb.width - 1, 0), (0, rgb.height - 1), (rgb.width - 1, rgb.height - 1)]
    counts: dict[tuple[int, int, int], int] = {}
    for x, y in coords:
        c = px[x, y]
        counts[c] = counts.get(c, 0) + 1
    if not counts:
        return rgb
    key = max(counts.items(), key=lambda kv: kv[1])[0]
    if key in {(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)}:
        return rgb
    data = [key_to if p == key else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb


def key_known_transparency_colors(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    key_colors = {
        (170, 0, 170),
        (255, 85, 255),
    }
    data = [(0, 0, 0) if p in key_colors else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb


def make_logo_probe_image(source_data: bytes) -> Image.Image:
    """LOGO.BIC type=0 diagnostic preview.

    This does not pretend the logo is solved. It shows header info plus several
    systematic raw/PackBits probes so type-0 work can continue without crashing.
    """
    probes = render_type0_logo_probe_images(source_data)
    info = Image.new("RGB", (760, 170), (24, 24, 24))
    draw = ImageDraw.Draw(info)
    if len(source_data) >= 7:
        lines = [
            "LOGO.BIC: type=0 unresolved custom/sparse/compiled blitter format.",
            f"header bytes: {' '.join(f'{b:02X}' for b in source_data[:16])}",
            f"candidate dimensions from header: widthBytes={source_data[4]} height={source_data[5]}",
            "Ordinary raw/PackBits row-plane probes, including 320px candidates, still look noisy.",
            "Next real fix needs tracing the EXE routine that draws type=0 LOGO.",
        ]
    else:
        lines = ["LOGO.BIC: too small"]
    y = 12
    for line in lines:
        draw.text((12, y), line, fill=(255, 255, 0) if y == 12 else (220, 220, 220))
        y += 24

    if not probes:
        return info

    probe_sheet = make_labelled_sheet(probes[:8], scale=1, cols=2)
    out = Image.new("RGB", (max(info.width, probe_sheet.width), info.height + probe_sheet.height + 8), (24, 24, 24))
    out.paste(info, (0, 0))
    out.paste(probe_sheet, (0, info.height + 8))
    return out




def key_transparent_corner_color(img: Image.Image, key_to: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    """Replace the dominant corner color with black for G0 preview."""
    rgb = img.convert("RGB")
    px = rgb.load()
    coords = [(0, 0), (rgb.width - 1, 0), (0, rgb.height - 1), (rgb.width - 1, rgb.height - 1)]
    counts: dict[tuple[int, int, int], int] = {}
    for x, y in coords:
        counts[px[x, y]] = counts.get(px[x, y], 0) + 1
    if not counts:
        return rgb
    key = max(counts.items(), key=lambda kv: kv[1])[0]
    data = [key_to if p == key else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb


def render_1bpp_image(data: bytes, width_bytes: int, height: int) -> Image.Image:
    pixels: list[int] = []
    for b in data[:width_bytes * height]:
        for bit in range(7, -1, -1):
            pixels.append(15 if ((b >> bit) & 1) else 0)
    return ega_image(pixels, width_bytes * 8, height)


def make_g0_leftover_mask_sheet(decoded: BicDecoded, scale: int = 2) -> Image.Image:
    """Diagnostic render for the 504-byte G0 tail."""
    chunk = 516
    tail = decoded.decoded[(len(decoded.decoded) // chunk) * chunk:]
    if not tail:
        return Image.new("RGB", (320, 80), (24, 24, 24))

    variants: list[tuple[str, Image.Image]] = []
    for width_bytes in (2, 4, 8, 16, 24, 32):
        if len(tail) >= width_bytes:
            h = len(tail) // width_bytes
            if 1 <= h <= 256:
                variants.append((f"tail 1bpp {width_bytes*8}x{h}", render_1bpp_image(tail, width_bytes, h)))
    return make_labelled_sheet(variants, scale=scale, cols=3)



def make_g3_sheet(decoded: BicDecoded, scale: int = 4) -> Image.Image:
    """Decode G3.BIC.

    Pass45 correction:
    G3 is type=4 with 129 records of 8 bytes.

    After reconstructing those 8-byte records, the correct payload is simply:

        data = concat(records)
        frame0 = data[0:516]
        frame1 = data[516:1032]

    Each frame is a normal 32x32 EGA record with embedded header 20 00 04 00.

    The previous parser split each 8-byte record into record[:4] and record[4:8],
    which produced two visually wrong/interleaved images.
    """
    records = decode_type4_records(decoded.decoded, bic_record_size(decoded), bic_record_count(decoded))
    if not records:
        return make_logo_probe_image(b"G3 decode failed")

    data = b"".join(records)
    imgs: list[tuple[str, Image.Image]] = []
    bad_headers: list[tuple[int, bytes]] = []

    for i in range(len(data) // 516):
        rec = data[i * 516:(i + 1) * 516]
        if rec[:4] != b"\x20\x00\x04\x00":
            bad_headers.append((i, rec[:4]))
        img = render_record_from_embedded_header(rec)
        if img:
            imgs.append((f"G3 frame {i}", img))

    sheet = make_labelled_sheet(imgs, scale=scale, cols=4)
    note_h = 34
    out = Image.new("RGB", (sheet.width, sheet.height + note_h), (24, 24, 24))
    out.paste(sheet, (0, 0))
    draw = ImageDraw.Draw(out)
    draw.text((8, sheet.height + 8), "G3: concat 129×8 type4 records -> two direct 516-byte frames.", fill=(255, 255, 0))
    if bad_headers:
        draw.text((8, sheet.height + 22), f"Warning: {len(bad_headers)} unexpected headers.", fill=(255, 96, 96))
    else:
        draw.text((8, sheet.height + 22), "Both frames start with 20 00 04 00.", fill=(180, 220, 180))
    return out




def compose_g0_final_boss_from_parts(part_images: list[Image.Image]) -> Optional[Image.Image]:
    """Compose G0 final boss from parts 4,5,6,7.

    User/game observation:
        G0 is one large final boss object made from pieces 4,5,6,7.

    Layout:
        4 5
        6 7
    """
    if len(part_images) <= 7 or any(part_images[i] is None for i in (4, 5, 6, 7)):
        return None
    out = Image.new("RGB", (64, 64), (0, 0, 0))
    out.paste(part_images[4], (0, 0))
    out.paste(part_images[5], (32, 0))
    out.paste(part_images[6], (0, 32))
    out.paste(part_images[7], (32, 32))
    return out


def key_g0_fill_colors_for_composite(img: Image.Image) -> Image.Image:
    """Preview-only keying for assembled G0 boss.

    This is not a palette remap. It removes the obvious background/fill colors
    that the game likely ignores through a blitter mask or transparent key.
    """
    rgb = img.convert("RGB")
    # Be conservative: remove only common fill colors seen in corners/backgrounds.
    fill_colors = {
        (0, 255, 0),       # bright green
        (0, 170, 0),       # dark green
        (170, 0, 170),     # magenta
        (255, 85, 255),    # bright magenta
    }
    data = [(0, 0, 0) if p in fill_colors else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb





def find_g0_header_aligned_records(decoded: BicDecoded) -> list[bytes]:
    """Find true G0 516-byte records by their embedded 32x32 header.

    Systematic pass37 fix:
    G0 decoded payload does not start with the first 516-byte record.
    The normal 32x32 EGA record header is:

        20 00 04 00

    In G0 it appears at offset 504 and then every 516 bytes.
    So the first 504 bytes are a prefix/preamble, not a tail after records.
    """
    header = b"\x20\x00\x04\x00"
    records: list[bytes] = []
    start = 0
    while True:
        pos = decoded.decoded.find(header, start)
        if pos < 0:
            break
        if pos + 516 <= len(decoded.decoded):
            records.append(decoded.decoded[pos:pos + 516])
        start = pos + 1
    return records


def g0_prefix_bytes(decoded: BicDecoded) -> bytes:
    """Return bytes before the first true G0 32x32 record."""
    header = b"\x20\x00\x04\x00"
    pos = decoded.decoded.find(header)
    if pos < 0:
        return b""
    return decoded.decoded[:pos]


def compose_g0_boss_header_aligned(records: list[bytes]) -> Optional[Image.Image]:
    """Compose the header-aligned final boss.

    Header-aligned records are shifted relative to the older wrong chunk view.
    The main boss body is records 3,4,5,6:

        3 4
        5 6
    """
    if len(records) <= 6:
        return None
    top = merge_g0_pair_as_64x32(records[3], records[4])
    bottom = merge_g0_pair_as_64x32(records[5], records[6])
    if top is None or bottom is None:
        return None
    out = Image.new("RGB", (64, 64), (0, 0, 0))
    out.paste(top, (0, 0))
    out.paste(bottom, (0, 32))
    return out


def key_g0_magenta_background(img: Image.Image) -> Image.Image:
    """Preview-only keying for the header-aligned G0 boss.

    After correct record alignment, the background/fill is mainly magenta.
    This keying is display-only; the real game likely uses a mask/blitter rule.
    """
    rgb = img.convert("RGB")
    data = [(0, 0, 0) if p in {(170, 0, 170), (255, 85, 255)} else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb


def merge_g0_pair_as_64x32(left_rec: bytes, right_rec: bytes) -> Optional[Image.Image]:
    """Merge two G0 32x32 records into one 64x32 row-plane EGA image.

    A simple image paste is visually misleading because the source records are
    EGA row-plane data. To form a 64px-wide object, each row/plane must become:

        left plane bytes + right plane bytes

    for plane0..plane3.
    """
    if len(left_rec) < 516 or len(right_rec) < 516:
        return None
    left = left_rec[4:516]
    right = right_rec[4:516]
    width_bytes_32 = 4
    height = 32
    merged = bytearray()
    for y in range(height):
        row_l = left[y * width_bytes_32 * 4:(y + 1) * width_bytes_32 * 4]
        row_r = right[y * width_bytes_32 * 4:(y + 1) * width_bytes_32 * 4]
        for plane in range(4):
            merged.extend(row_l[plane * width_bytes_32:(plane + 1) * width_bytes_32])
            merged.extend(row_r[plane * width_bytes_32:(plane + 1) * width_bytes_32])
    return render_planar_4bpp(bytes(merged), 64, 32, row_interleaved=True)


def compose_g0_final_boss_merged(records: list[bytes]) -> Optional[Image.Image]:
    """Compose final boss from G0 records 4,5,6,7 using row/plane merging."""
    if len(records) <= 7:
        return None
    top = merge_g0_pair_as_64x32(records[4], records[5])
    bottom = merge_g0_pair_as_64x32(records[6], records[7])
    if top is None or bottom is None:
        return None
    out = Image.new("RGB", (64, 64), (0, 0, 0))
    out.paste(top, (0, 0))
    out.paste(bottom, (0, 32))
    return out


def key_g0_background_colors(img: Image.Image) -> Image.Image:
    """Preview-only keying for G0 background/fill colors.

    The final boss should be drawn on black/transparent background.
    Bright green/magenta areas in decoded G0 chunks behave like fill/key areas,
    not intended metal colors.
    """
    rgb = img.convert("RGB")
    fill_colors = {
        (0, 255, 0),
        (0, 170, 0),
        (85, 255, 85),
        (170, 0, 170),
        (255, 85, 255),
    }
    data = [(0, 0, 0) if p in fill_colors else p for p in rgb.getdata()]
    rgb.putdata(data)
    return rgb



def g0_complete_records(decoded: BicDecoded) -> list[bytes]:
    """Return true header-aligned G0 32x32 records."""
    return find_g0_header_aligned_records(decoded)





def type4_records_by_header(decoded: BicDecoded) -> list[bytes]:
    """Return raw type-4 records using header byte size and count."""
    return decode_type4_records(decoded.decoded, bic_record_size(decoded), bic_record_count(decoded))



def flip_resource_if_needed(img: Optional[Image.Image], *, flip_vertical: bool = False) -> Optional[Image.Image]:
    """Apply explicit resource-specific orientation only when a parser knows it is needed."""
    if img is None:
        return None
    if flip_vertical:
        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return img


def render_record_from_embedded_header(rec: bytes, max_width_bytes: int = 80) -> Optional[Image.Image]:
    """Render a row-plane EGA bitmap record whose first 4 bytes are height,widthBytes."""
    if len(rec) < 4:
        return None
    height = int.from_bytes(rec[0:2], "little")
    width_bytes = int.from_bytes(rec[2:4], "little")
    if not (1 <= height <= 256 and 1 <= width_bytes <= max_width_bytes):
        return None
    return render_planar_4bpp(rec[4:], width_bytes * 8, height, row_interleaved=True)


def make_ship_sheet(decoded: BicDecoded, scale: int = 4) -> Image.Image:
    """Decode SHIP.BIC.

    SHIP is type=4 with 4-byte records and count 1452.
    Group every 33 small records:
        33 * 4 = 132 bytes
    yielding 44 normal 16x16 records with header 10 00 02 00.
    """
    small = type4_records_by_header(decoded)
    grouped = [b"".join(small[i * 33:(i + 1) * 33]) for i in range(len(small) // 33)]
    imgs: list[tuple[str, Image.Image]] = []
    for i, rec in enumerate(grouped):
        img = render_record_from_embedded_header(rec)
        if img:
            imgs.append((str(i), img))
    return make_labelled_sheet(imgs, scale=scale, cols=11)



def make_manexpl_sheet(decoded: BicDecoded, scale: int = 3) -> Image.Image:
    """Decode MANEXPL.BIC.

    Pass43 correction:
    MANEXPL has no 7-record prefix. After type-4 transposition, concatenating all
    16-byte small records yields exactly:

        28 * 516 bytes

    and each 516-byte record already starts with the normal 32x32 header:

        20 00 04 00

    So do not skip 7 records and do not synthesize headers.
    """
    small = type4_records_by_header(decoded)
    data = b"".join(small)

    imgs: list[tuple[str, Image.Image]] = []
    bad_headers: list[tuple[int, bytes]] = []
    for i in range(len(data) // 516):
        rec = data[i * 516:(i + 1) * 516]
        if rec[:4] != b"\x20\x00\x04\x00":
            bad_headers.append((i, rec[:4]))
        img = render_record_from_embedded_header(rec)
        if img:
            imgs.append((str(i), img))

    sheet = make_labelled_sheet(imgs, scale=scale, cols=7)

    note_h = 40
    out = Image.new("RGB", (sheet.width, sheet.height + note_h), (24, 24, 24))
    out.paste(sheet, (0, 0))
    draw = ImageDraw.Draw(out)
    draw.text((8, sheet.height + 8), f"MANEXPL: {len(imgs)} direct 516-byte records; no prefix skipped.", fill=(255, 255, 0))
    if bad_headers:
        draw.text((8, sheet.height + 24), f"Warning: {len(bad_headers)} records have unexpected headers.", fill=(255, 96, 96))
    else:
        draw.text((8, sheet.height + 24), "All records start with 20 00 04 00.", fill=(180, 220, 180))
    return out




def make_thend_image(decoded: BicDecoded) -> Optional[Image.Image]:
    """Decode THEND.BIC as one full row-plane image.

    THEND is type=4 with 2-byte small records and count 3522.
    Concatenating all small records gives one 7044-byte image record:
        2c 00 28 00 -> height 44, widthBytes 40 = 320 px
    """
    small = type4_records_by_header(decoded)
    rec = b"".join(small)
    return render_record_from_embedded_header(rec, max_width_bytes=80)


def make_g0_sheet(decoded: BicDecoded, scale: int = 4) -> Image.Image:
    """Decode G0.BIC using true header-aligned records.

    Pass37:
    The first 504 decoded bytes are a prefix/preamble before the first real 516-byte
    record. True records start at embedded headers 20 00 04 00.
    """
    records = find_g0_header_aligned_records(decoded)

    sections: list[tuple[str, Image.Image]] = []

    boss_raw = compose_g0_boss_header_aligned(records)
    if boss_raw:
        sections.append(("G0 boss header-aligned raw 3+4 / 5+6", boss_raw))
        sections.append(("G0 boss magenta-key preview", key_g0_magenta_background(boss_raw)))

    # Individual true records.
    for i, rec in enumerate(records):
        img = render_planar_4bpp(rec[4:], 32, 32, row_interleaved=True)
        if img:
            sections.append((f"G0 true record {i}", img))

    if not sections:
        img = Image.new("RGB", (720, 160), (24, 24, 24))
        draw = ImageDraw.Draw(img)
        draw.text((12, 20), "G0.BIC: no true 20 00 04 00 record headers found", fill=(255, 255, 0))
        draw.text((12, 45), f"decoded={len(decoded.decoded)} expected={decoded.expected_size}", fill=(220, 220, 220))
        return img

    sheet = make_labelled_sheet(sections, scale=scale, cols=4)

    prefix_len = len(g0_prefix_bytes(decoded))
    note_h = 42
    out = Image.new("RGB", (sheet.width, sheet.height + note_h), (24, 24, 24))
    out.paste(sheet, (0, 0))
    draw = ImageDraw.Draw(out)
    draw.text((8, sheet.height + 8), f"G0 prefix/preamble before first true record: {prefix_len} bytes.", fill=(255, 255, 0))
    draw.text((8, sheet.height + 24), "No magic plane order: colors fix because records are aligned to 20 00 04 00 headers.", fill=(220, 220, 220))
    return out


def make_labelled_sheet(labelled_images: list[tuple[str, Image.Image]], scale: int = 4, cols: int = 8) -> Image.Image:
    if not labelled_images:
        return Image.new("RGB", (320, 120), (24, 24, 24))
    cell_w = max(img.width for _, img in labelled_images) * scale + 12
    cell_h = max(img.height for _, img in labelled_images) * scale + 18
    rows = math.ceil(len(labelled_images) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(labelled_images):
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h
        sheet.paste(scale_nearest(key_known_transparency_colors(key_dominant_corner_color(img)), scale), (x + 2, y + 2))
        draw.text((x + 2, y + img.height * scale + 3), label, fill=(230, 230, 0))
    return sheet


def make_map_index_image(decoded: BicDecoded, scale: int = 4) -> Image.Image:
    rows = map_rows_for_display(decoded)
    height = len(rows)
    width = len(rows[0]) if rows else 0
    flat = [v for row in rows for v in row]
    pixels = [b & 15 for b in flat[:width * height]]
    img = ega_image(pixels, width, height)
    img = scale_nearest(img, scale)
    draw = ImageDraw.Draw(img)
    if width == 13:
        for y in range(0, height + 1, 16):
            yy = y * scale
            draw.line((0, yy, img.width, yy), fill=(255, 255, 255))
    return img





def make_map_highbit_overlay(decoded: BicDecoded, cell: int = 16, sprite_count: int = 250, show_grid: bool = True, tile_count: int | None = None) -> Image.Image:
    """Render optional MAP diagnostic overlay.

    Pass54: red no longer means enemy. It means special/out-of-range MAP value.

    Colors:
    - red/orange: value is not a normal 1-based BLX tile ID
    - black: tile 1 / empty background
    - gray: ordinary BLX tile value
    - subtle blue grid if enabled
    """
    rows = map_rows_for_display(decoded)
    height = len(rows)
    width = len(rows[0]) if rows else 0
    if tile_count is None:
        tile_count = 255
    img = Image.new("RGB", (width * cell, height * cell), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, v in enumerate(row):
            if map_value_is_special(v, tile_count):
                col = (255, 96, 32)
            elif v == 1:
                col = (0, 0, 0)
            else:
                b = 50 + (min(v, 255) * 180) // 255
                col = (b, b, b)
            draw.rectangle((x * cell, y * cell, (x + 1) * cell - 1, (y + 1) * cell - 1), fill=col)
    if show_grid:
        for y in range(0, height + 1):
            yy = y * cell
            draw.line((0, yy, img.width, yy), fill=(60, 60, 220))
        for x in range(0, width + 1):
            xx = x * cell
            draw.line((xx, 0, xx, img.height), fill=(60, 60, 220))
    return img


def combine_map_render_and_overlay(rendered: Image.Image, overlay: Optional[Image.Image] = None, title: str = "") -> Image.Image:
    """Render level image, optionally with side-by-side debug overlay."""
    gap = 12
    label_h = 18

    if overlay is None:
        out = Image.new("RGB", (rendered.width, rendered.height + label_h), (24, 24, 24))
        draw = ImageDraw.Draw(out)
        draw.text((4, 2), title or "level render", fill=(255, 255, 0))
        out.paste(rendered, (0, label_h))
        return out

    h = max(rendered.height, overlay.height) + label_h
    w = rendered.width + gap + overlay.width
    out = Image.new("RGB", (w, h), (24, 24, 24))
    draw = ImageDraw.Draw(out)
    draw.text((4, 2), title or "level render", fill=(255, 255, 0))
    draw.text((rendered.width + gap + 4, 2), "debug MAP overlay: red/orange=special or out-of-range MAP value", fill=(255, 96, 96))
    out.paste(rendered, (0, label_h))
    out.paste(overlay, (rendered.width + gap, label_h))
    return out


def decode_type4_records(raw: bytes, record_size: int, count: int) -> list[bytes]:
    """Type-4 BIC stores records transposed by field.

    record_i = raw[0*count+i], raw[1*count+i], ...
    """
    if record_size <= 0 or count <= 0 or len(raw) < record_size * count:
        return []
    return [bytes(raw[field * count + i] for field in range(record_size)) for i in range(count)]




def bic_record_size(decoded: BicDecoded) -> int:
    """Return BIC type-4 record size / field count.

    In this GUI's BicDecoded:
        fields_or_count_byte = header byte at offset 3
        block_size           = header word at offset 5

    For LEV0BLX this must return 4, not 7392.
    """
    if hasattr(decoded, "fields_or_count_byte"):
        return int(decoded.fields_or_count_byte)
    if hasattr(decoded, "fields_or_count_word"):
        return int(decoded.fields_or_count_word)
    if hasattr(decoded, "record_size"):
        return int(decoded.record_size)
    return 0


def bic_record_count(decoded: BicDecoded) -> int:
    """Return BIC type-4 record count.

    In this GUI's BicDecoded this is `block_size`.
    For LEV0BLX this must return 7392.
    """
    if hasattr(decoded, "block_size"):
        return int(decoded.block_size)
    if hasattr(decoded, "block_or_record_count"):
        return int(decoded.block_or_record_count)
    if hasattr(decoded, "record_count"):
        return int(decoded.record_count)
    return 0




def decode_blx_tile_records(decoded: BicDecoded) -> list[bytes]:
    """Decode LEVxBLX into 132-byte tile records.

    Generalized pass19 model:
    Type-4 BIC transpose gives `record_count` records of `record_size` bytes.

    Most BLX:
        record_size=4, group 33 records -> 132-byte tile

    LEV3BLX:
        record_size=2, group 66 records -> 132-byte tile

    LEV5BLX:
        record_size=8, group 33 records -> 264 bytes -> two 132-byte tiles
    """
    raw = decoded.decoded
    record_size = bic_record_size(decoded)
    record_count = bic_record_count(decoded)
    records = decode_type4_records(raw, record_size, record_count)

    # General case when a whole number of records forms one 132-byte tile.
    if record_size > 0 and 132 % record_size == 0:
        group = 132 // record_size
        if record_count % group == 0:
            return [b"".join(records[i * group:(i + 1) * group]) for i in range(record_count // group)]

    # LEV5-like case: 33 records × 8 bytes = 264 bytes = two 132-byte tiles.
    if record_size == 8 and record_count % 33 == 0:
        out: list[bytes] = []
        for i in range(record_count // 33):
            block = b"".join(records[i * 33:(i + 1) * 33])
            if len(block) >= 264:
                out.append(block[:132])
                out.append(block[132:264])
        return out

    if record_size == 132:
        return records

    return []


def render_blx_tile_record(tile_record: bytes, bitrev: bool = False, plane_order: tuple[int, int, int, int] = (0, 1, 2, 3)) -> Optional[Image.Image]:
    """Render a corrected LEVxBLX 132-byte row-plane-grouped tile record.

    Layout:
        word height      usually 16
        word widthBytes  usually 2 for 16 px
        for each row:
            plane0: widthBytes
            plane1: widthBytes
            plane2: widthBytes
            plane3: widthBytes
    """
    if len(tile_record) < 4:
        return None
    height = int.from_bytes(tile_record[0:2], "little")
    width_bytes = int.from_bytes(tile_record[2:4], "little")
    if height <= 0 or height > 64 or width_bytes <= 0 or width_bytes > 16:
        return None
    data = tile_record[4:]
    row_stride = width_bytes * 4
    if len(data) < height * row_stride:
        return None

    pixels: list[int] = []
    bits = range(8) if bitrev else range(7, -1, -1)
    for y in range(height):
        row = data[y * row_stride:(y + 1) * row_stride]
        for xb in range(width_bytes):
            vals = [row[p * width_bytes + xb] for p in plane_order]
            for bit in bits:
                pixels.append(sum(((vals[p] >> bit) & 1) << p for p in range(4)))
    return ega_image(pixels, width_bytes * 8, height)


def make_tile_record_sheet(decoded: BicDecoded, name: str, record_size: int = 132, scale: int = 4, cols: int = 16) -> Image.Image:
    """Render corrected LEVxBLX tile sheet."""
    records = decode_blx_tile_records(decoded)
    images: list[tuple[int, Image.Image]] = []
    for i, rec in enumerate(records):
        img = render_blx_tile_record(rec)
        if img:
            images.append((i, img))

    if not images:
        img = Image.new("RGB", (720, 160), (24, 24, 24))
        draw = ImageDraw.Draw(img)
        draw.text((12, 20), f"{name}: this BLX uses a different subformat not decoded yet", fill=(255, 255, 0))
        draw.text((12, 45), f"decoded={len(decoded.decoded)} record_size={bic_record_size(decoded)} count={bic_record_count(decoded)}", fill=(220, 220, 220))
        return img

    max_w = max(im.width for _, im in images)
    max_h = max(im.height for _, im in images)
    cell_w = max_w * scale + 12
    cell_h = max_h * scale + 18
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for j, (idx, img) in enumerate(images):
        x = (j % cols) * cell_w
        y = (j // cols) * cell_h
        scaled = scale_nearest(img, scale)
        sheet.paste(scaled, (x + 2, y + 2))
        draw.text((x + 2, y + scaled.height + 3), str(idx), fill=(230, 230, 0))
    return sheet


# Tentative mapping discovered by comparing corrected BLX sheets to screenshots:
# resource LEV1BLX matches EDRAX / game level 1 visual style.
# User noted resource LEV0BLX appears to be game level 5 style.
# Resource MAP/BLX numbering is not guaranteed to equal game level numbering.
# Use same-number pairing as a neutral default; compare manually in the GUI.
DEFAULT_MAP_TO_BLX: dict[int, int] = {i: i for i in range(6)}


MOVING_ENEMY_STREAM_STARTS = [0x12D7D, 0x12DF7, 0x12F23, 0x13157, 0x131A1, 0x131CB]
MOVING_ENEMY_DESCRIPTOR_START = 0x13249
MOVING_ENEMY_DESCRIPTOR_END = 0x136DD
MOVING_ENEMY_RAW_FROM_PTR_DELTA = 0x6521


def _read_u16(data: bytes, off: int) -> int:
    if off < 0 or off + 2 > len(data):
        raise ValueError("u16 read outside data")
    return int.from_bytes(data[off:off + 2], "little")


def _read_s16(data: bytes, off: int) -> int:
    if off < 0 or off + 2 > len(data):
        raise ValueError("s16 read outside data")
    return int.from_bytes(data[off:off + 2], "little", signed=True)


def lzexe_decompress_load_module(exe_data: bytes) -> bytes | None:
    """Return the LZEXE decompressed load module when the EXE stub matches.

    The shipped Overkill binaries use an LZEXE-style depacker. This helper is
    deliberately conservative: it only exposes the decompressed load image for
    parser probes and returns None if the stream does not decode cleanly.
    """
    try:
        if len(exe_data) < 0x40 or exe_data[:2] not in (b"MZ", b"ZM"):
            return None
        header_paragraphs = _read_u16(exe_data, 0x08)
        initial_ip = _read_u16(exe_data, 0x14)
        initial_cs = _read_u16(exe_data, 0x16)
        lz_header = header_paragraphs * 16 + initial_cs * 16
        if initial_ip != 0x000E or lz_header + 16 > len(exe_data):
            return None
        info = [_read_u16(exe_data, lz_header + i) for i in range(0, 16, 2)]
        compressed_paragraphs = info[4]
        source_offset = (initial_cs - compressed_paragraphs + header_paragraphs) * 16
        if source_offset < 0 or source_offset >= len(exe_data):
            return None
        src = exe_data[source_offset:]
        si = 0
        out = bytearray()

        def read_byte() -> int:
            nonlocal si
            if si >= len(src):
                raise ValueError("truncated LZEXE stream")
            value = src[si]
            si += 1
            return value

        def read_word() -> int:
            return read_byte() | (read_byte() << 8)

        bit_buffer = read_word()
        bit_count = 16

        def read_bit() -> int:
            nonlocal bit_buffer, bit_count
            bit = bit_buffer & 1
            bit_count -= 1
            if bit_count == 0:
                bit_buffer = read_word()
                bit_count = 16
            else:
                bit_buffer >>= 1
            return bit

        def signed16(value: int) -> int:
            value &= 0xFFFF
            return value - 0x10000 if value & 0x8000 else value

        while True:
            if read_bit():
                out.append(read_byte())
                continue

            if not read_bit():
                length = (read_bit() << 1) | read_bit()
                length += 2
                span = signed16(0xFF00 | read_byte())
            else:
                span = read_byte()
                length_byte = read_byte()
                span = signed16(span | ((length_byte & ~0x07) << 5) | 0xE000)
                length = (length_byte & 0x07) + 2
                if length == 2:
                    length = read_byte()
                    if length == 0:
                        break
                    if length == 1:
                        continue
                    length += 1

            for _ in range(length):
                source = len(out) + span
                if source < 0:
                    raise ValueError("LZEXE back-reference before output")
                out.append(out[source])
        return bytes(out)
    except Exception:
        return None


def parse_moving_enemy_descriptors(data: bytes) -> list[dict]:
    """Parse the shared moving-enemy formation descriptor table."""
    if len(data) < MOVING_ENEMY_DESCRIPTOR_END:
        raise ValueError("data is too short for moving enemy descriptor table")
    descriptors: list[dict] = []
    off = MOVING_ENEMY_DESCRIPTOR_START
    while off < MOVING_ENEMY_DESCRIPTOR_END:
        start = off
        field_14 = _read_u16(data, off)
        field_0a = _read_u16(data, off + 2)
        behavior = _read_u16(data, off + 4)
        count = _read_u16(data, off + 6)
        if count > 64:
            raise ValueError(f"implausible moving enemy descriptor count {count} at 0x{off:05X}")
        off += 8
        if off + count * 4 > MOVING_ENEMY_DESCRIPTOR_END:
            raise ValueError(f"moving enemy descriptor at 0x{start:05X} overruns table")
        offsets = []
        for _ in range(count):
            offsets.append({"dx": _read_s16(data, off), "dy": _read_s16(data, off + 2)})
            off += 4
        ptr = start - MOVING_ENEMY_RAW_FROM_PTR_DELTA
        descriptors.append({
            "descriptor_ptr": ptr,
            "descriptor_ptr_hex": f"0x{ptr:04X}",
            "raw_file_offset": start,
            "raw_file_offset_hex": f"0x{start:05X}",
            "field_14": field_14,
            "field_0A": field_0a,
            "behavior": behavior,
            "behavior_hex": f"0x{behavior:02X}",
            "count": count,
            "offsets": offsets,
        })
    if off != MOVING_ENEMY_DESCRIPTOR_END or len(descriptors) < 40:
        raise ValueError("moving enemy descriptor table did not parse cleanly")
    return descriptors


def parse_moving_enemy_stream(data: bytes, start: int) -> tuple[list[dict], int]:
    """Parse one scrolling-level moving-enemy spawn stream."""
    off = start
    records: list[dict] = []
    for _ in range(256):
        rec_start = off
        trigger = _read_u16(data, off)
        off += 2
        if trigger == 0xFFFF:
            return records, off
        if trigger > 320:
            raise ValueError(f"implausible moving enemy trigger {trigger} at 0x{rec_start:05X}")
        descriptor_ptr = _read_u16(data, off)
        off += 2
        marker = False
        if descriptor_ptr == 0xFFFF:
            marker = True
            descriptor_ptr = _read_u16(data, off)
            off += 2
        base_x = _read_u16(data, off)
        base_y = _read_s16(data, off + 2)
        off += 4
        if base_x > 1024 or not -512 <= base_y <= 512:
            raise ValueError(f"implausible moving enemy anchor at 0x{rec_start:05X}")
        records.append({
            "raw_record_start": rec_start,
            "raw_record_start_hex": f"0x{rec_start:05X}",
            "trigger": trigger,
            "approx_canonical_row_inferred_288_minus_trigger": 288 - trigger,
            "descriptor_ptr": descriptor_ptr,
            "descriptor_ptr_hex": f"0x{descriptor_ptr:04X}",
            "base_x": base_x,
            "base_y": base_y,
            "special_marker_FFFF_before_descriptor_ptr": marker,
        })
    raise ValueError(f"unterminated moving enemy stream at 0x{start:05X}")


def decode_moving_enemy_spawn_streams(data: bytes) -> dict:
    """Decode all moving-enemy spawn streams from an unpacked executable image."""
    descriptors = parse_moving_enemy_descriptors(data)
    desc_by_ptr = {d["descriptor_ptr"]: d for d in descriptors}
    streams = []
    for index, start in enumerate(MOVING_ENEMY_STREAM_STARTS):
        records, end = parse_moving_enemy_stream(data, start)
        for rec in records:
            desc = desc_by_ptr.get(rec["descriptor_ptr"])
            if not desc:
                continue
            rec["descriptor_behavior"] = desc["behavior"]
            rec["descriptor_behavior_hex"] = desc["behavior_hex"]
            rec["descriptor_count"] = desc["count"]
            rec["descriptor_offsets"] = desc["offsets"]
            rec["spawn_points_at_event_anchor_screen_space"] = [
                {"x": rec["base_x"] + p["dx"], "y": rec["base_y"] + p["dy"]}
                for p in desc["offsets"]
            ]
        streams.append({
            "stream_index": index,
            "raw_stream_start": start,
            "raw_stream_start_hex": f"0x{start:05X}",
            "raw_stream_end_exclusive": end,
            "raw_stream_end_exclusive_hex": f"0x{end:05X}",
            "record_count": len(records),
            "records": records,
        })
    return {
        "status": "decoded from executable bytes",
        "streams": streams,
        "formation_descriptors": descriptors,
    }


def moving_enemy_spawn_stream_sources(archive: ShadowArchive) -> list[tuple[str, bytes]]:
    """Candidate executable byte sources near the loaded game archive."""
    sources = [("game_data/OVERKILL raw", archive.file_data)]
    unpacked = lzexe_decompress_load_module(archive.file_data)
    if unpacked:
        sources.append(("game_data/OVERKILL LZEXE load module", unpacked))
    exe_path = archive.overkill_file.parent / "OVERKILL.EXE"
    if exe_path.exists():
        try:
            exe_data = exe_path.read_bytes()
            sources.append(("game_data/OVERKILL.EXE raw", exe_data))
            unpacked_exe = lzexe_decompress_load_module(exe_data)
            if unpacked_exe:
                sources.append(("game_data/OVERKILL.EXE LZEXE load module", unpacked_exe))
        except Exception:
            pass
    return sources


def decode_moving_enemy_spawn_streams_from_archive(archive: ShadowArchive) -> tuple[dict | None, str]:
    """Try to decode moving enemy streams from game-file executable sources."""
    errors = []
    for label, data in moving_enemy_spawn_stream_sources(archive):
        try:
            decoded = decode_moving_enemy_spawn_streams(data)
            decoded["source"] = label
            return decoded, label
        except Exception as exc:
            errors.append(f"{label}: {exc}")
    return None, "; ".join(errors)




# Pass54: do not map MAP values directly to enemy sprites.
#
# Disassembly and in-game checks show that values such as 0x92 can be object
# behavior/type codes in runtime object structs, but the same numeric values in
# LEVxMAP may also be valid terrain tile IDs. Therefore broad rules like
# "raw - 0x26 -> 2X2 sprite" create many false enemies.

OBJECT_SPRITE_BASE_OFFSET = 0x26  # historical diagnostic only; not used for rendering.
KNOWN_OBJECT_SPRITE_MAP: dict[int, int] = {}


def map_value_to_object_sprite_index(value: int, sprite_count: int = 250) -> int | None:
    """Return a candidate sprite for MAP value.

    Disabled in pass54.

    Enemy sprites are very likely runtime objects created from EXE tables/state
    machines, not direct replacements for MAP bytes. Keep this function for API
    compatibility but return None so the level viewer does not paint false enemy
    sprites across valid terrain tiles.
    """
    return None


def map_value_is_special(value: int, tile_count: int) -> bool:
    """Return True for MAP bytes that are not normal 1-based BLX tile IDs."""
    return value == 0 or value > tile_count


def describe_object_mapping(value: int, sprite_count: int = 250) -> str:
    """Human-readable object mapping status."""
    return "no direct MAP->2X2 sprite mapping; enemy layer appears runtime/scripted"


def decode_2x2_sprite_records(decoded: BicDecoded) -> list[bytes]:
    """Return direct 2X2/2X2C 16x16 sprite records from a type-4 BIC."""
    return decode_type4_records(decoded.decoded, bic_record_size(decoded), bic_record_count(decoded))


def render_object_sprite_record(rec: bytes) -> Optional[Image.Image]:
    """Render a 2X2 object/enemy sprite frame with magenta transparency keyed."""
    img = render_record_from_embedded_header(rec)
    if img is None:
        return None
    return key_known_transparency_colors(key_dominant_corner_color(img))



def make_nonblack_mask(img: Image.Image) -> Image.Image:
    """Return mask for object sprites keyed to black background.

    Object/enemy sprites should overlay terrain, not replace it with a black box.
    """
    rgb = img.convert("RGB")
    mask = Image.new("L", rgb.size, 0)
    src = rgb.load()
    dst = mask.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            if src[x, y] != (0, 0, 0):
                dst[x, y] = 255
    return mask


def draw_level_grid(img: Image.Image, tile_size: int = 16, color: tuple[int, int, int] = (64, 64, 64)) -> Image.Image:
    """Draw a tile grid over an image."""
    out = img.copy()
    draw = ImageDraw.Draw(out)
    for x in range(0, out.width + 1, tile_size):
        draw.line((x, 0, x, out.height), fill=color)
    for y in range(0, out.height + 1, tile_size):
        draw.line((0, y, out.width, y), fill=color)
    return out


def render_2x2_object_sprites(decoded: BicDecoded) -> list[Optional[Image.Image]]:
    records = decode_2x2_sprite_records(decoded)
    return [render_object_sprite_record(rec) for rec in records]


def map_value_to_tile_index(value: int, tile_count: int) -> int | None:
    """Convert a LEVxMAP byte to a BLX tile index.

    Pass26 correction:
    For EDRAX / LEV1, raw values 1..205 map directly to LEV1BLX tiles 0..204.
    Therefore high-bit values are not automatically low7 flags.

    General safe rule:
        if 1 <= value <= tile_count:
            return value - 1
        else:
            return None  # special/object/trigger/flag or unknown cell data
    """
    if 1 <= value <= tile_count:
        return value - 1
    return None


def render_level_from_map_and_tiles(
    map_decoded: BicDecoded,
    blx_decoded: BicDecoded,
    object_sprites: Optional[list[Optional[Image.Image]]] = None,
    *,
    show_objects: bool = False,
    show_grid: bool = False,
) -> Image.Image:
    """Render LEVxMAP rows with paired BLX tiles.

    Pass54 correction:
    enemies are not drawn from MAP bytes as 2X2 sprites anymore.

    Confirmed/suspected model:
    - LEVxMAP + LEVxBLX is the terrain/background layer.
    - Runtime object/enemy slots are controlled by EXE state machines/tables.
    - Some MAP bytes may be special triggers when outside the valid tile range,
      but values 1..tile_count are background tiles even when >= 0x80.

    The show_objects flag now only draws subtle markers for out-of-range/special
    MAP cells; it does not paste 2X2 sprites.
    """
    display_rows = map_rows_for_display_with_indices(map_decoded)
    map_rows = [row for _, row in display_rows]
    width = len(map_rows[0]) if map_rows else 0
    height = len(map_rows)

    tile_records = decode_blx_tile_records(blx_decoded)
    tiles: list[Image.Image | None] = [render_blx_tile_record(rec) for rec in tile_records]

    img = Image.new("RGB", (width * 16, height * 16), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(map_rows):
        for x, value in enumerate(row):
            idx = map_value_to_tile_index(value, len(tiles))
            if idx is not None and 0 <= idx < len(tiles) and tiles[idx] is not None:
                img.paste(tiles[idx], (x * 16, y * 16))
            elif value != 0:
                draw.rectangle((x * 16, y * 16, x * 16 + 15, y * 16 + 15), fill=(24, 0, 24))

            if show_objects and map_value_is_special(value, len(tiles)):
                # Diagnostic marker only: not a sprite.
                x0, y0 = x * 16, y * 16
                draw.rectangle((x0 + 3, y0 + 3, x0 + 12, y0 + 12), outline=(255, 128, 0))
                draw.line((x0 + 4, y0 + 4, x0 + 11, y0 + 11), fill=(255, 128, 0))
                draw.line((x0 + 11, y0 + 4, x0 + 4, y0 + 11), fill=(255, 128, 0))

    if show_grid:
        img = draw_level_grid(img, tile_size=16)

    return img


def make_blx_probe(decoded: BicDecoded, name: str) -> Image.Image:
    raw = decoded.decoded
    candidates: list[tuple[str, Image.Image]] = []
    # Try the candidate dimensions that have produced useful hints so far.
    for w in (88, 176, 264, 320, 336):
        for mode in ("nib_hi", "nib_lo"):
            h = max(1, (len(raw) * 2) // w)
            if h > 512:
                h = 512
            img = render_nibbles(raw, w, h, high_first=(mode == "nib_hi"))
            if img:
                candidates.append((f"{mode} {w}x{h}", img.crop((0, 0, min(w, img.width), min(h, img.height)))))
    for w in (88, 176, 264, 336):
        wb = (w + 7) // 8
        h = len(raw) // (wb * 4) if wb else 0
        if 4 <= h <= 512:
            for row in (True, False):
                img = render_planar_4bpp(raw, w, h, row_interleaved=row, bitrev=False)
                if img:
                    candidates.append((f"planar {'row' if row else 'contig'} {w}x{h}", img))
    if not candidates:
        raise ValueError("No BLX probe candidates")
    thumb_w, thumb_h = 360, 220
    sheet = Image.new("RGB", (thumb_w * 2, thumb_h * math.ceil(len(candidates) / 2)), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(candidates[:10]):
        x = (i % 2) * thumb_w
        y = (i // 2) * thumb_h
        # scale down/up to fit while preserving nearest-ish look
        factor = min((thumb_w - 8) / img.width, (thumb_h - 24) / img.height)
        new_size = (max(1, int(img.width * factor)), max(1, int(img.height * factor)))
        res = Image.Resampling.NEAREST if factor >= 1 else Image.Resampling.BOX
        thumb = img.resize(new_size, res)
        sheet.paste(thumb, (x + 4, y + 18))
        draw.text((x + 4, y + 2), label, fill=(240, 240, 240))
    return sheet


def make_raw_hex(data: bytes, width: int = 16, max_len: int = 4096) -> str:
    lines = []
    for off in range(0, min(len(data), max_len), width):
        chunk = data[off:off + width]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        ascii_s = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{off:04x}: {hexs:<{width*3}} {ascii_s}")
    if len(data) > max_len:
        lines.append(f"... truncated, total {len(data)} bytes")
    return "\n".join(lines)

