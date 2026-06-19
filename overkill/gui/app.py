from __future__ import annotations

import json
import math
import re
import sys
import traceback
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageTk
except Exception as exc:  # pragma: no cover - GUI helper
    print("This tool requires Pillow. Install with: pip install pillow")
    raise

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from overkill.core import *

class ImageCanvas(ttk.Frame):
    def __init__(self, master, zoom: int = 1):
        super().__init__(master)
        self.canvas = tk.Canvas(self, bg="#202020", highlightthickness=0)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._tk_img = None
        self._pil_img: Optional[Image.Image] = None
        self._display_img: Optional[Image.Image] = None
        self._overlay_items: list[dict] = []
        self.zoom = max(1, int(zoom))

    def set_zoom(self, zoom: int):
        self.zoom = max(1, int(zoom))
        if self._pil_img is not None:
            self.set_image(self._pil_img, self._overlay_items)

    def _tk_color(self, color) -> str:
        if isinstance(color, tuple) and len(color) >= 3:
            return f"#{int(color[0]) & 255:02x}{int(color[1]) & 255:02x}{int(color[2]) & 255:02x}"
        return str(color)

    def _scaled_coords(self, coords):
        return [int(round(float(c) * self.zoom)) for c in coords]

    def draw_overlay(self):
        self.canvas.delete("overlay")
        for item in self._overlay_items:
            kind = item.get("type")
            coords = self._scaled_coords(item.get("coords", ()))
            tags = ("overlay",)
            if kind == "line":
                self.canvas.create_line(
                    *coords,
                    fill=self._tk_color(item.get("fill", "#ffffff")),
                    width=int(item.get("width", 1)),
                    tags=tags,
                )
            elif kind == "rectangle":
                self.canvas.create_rectangle(
                    *coords,
                    outline=self._tk_color(item.get("outline", "#ffffff")),
                    width=int(item.get("width", 1)),
                    tags=tags,
                )
            elif kind == "ellipse":
                self.canvas.create_oval(
                    *coords,
                    outline=self._tk_color(item.get("outline", "#ffffff")),
                    width=int(item.get("width", 1)),
                    tags=tags,
                )
            elif kind == "text" and len(coords) >= 2:
                self.canvas.create_text(
                    coords[0],
                    coords[1],
                    anchor=item.get("anchor", "nw"),
                    text=str(item.get("text", "")),
                    fill=self._tk_color(item.get("fill", "#ffffff")),
                    font=item.get("font", ("TkDefaultFont", 9)),
                    tags=tags,
                )

    def set_image(self, img: Image.Image, overlay_items: Optional[list[dict]] = None):
        self._pil_img = img
        self._overlay_items = list(overlay_items or [])
        if self.zoom > 1:
            self._display_img = img.resize((img.width * self.zoom, img.height * self.zoom), Image.Resampling.NEAREST)
        else:
            self._display_img = img
        self._tk_img = ImageTk.PhotoImage(self._display_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)
        self.draw_overlay()
        self.canvas.configure(scrollregion=(0, 0, self._display_img.width, self._display_img.height))

    def canvas_event_to_image_xy(self, event) -> tuple[int, int]:
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        if self.zoom > 1:
            x //= self.zoom
            y //= self.zoom
        return x, y

    def save_current(self, path: Path):
        if self._pil_img is None:
            raise ValueError("No preview image to save")
        self._pil_img.save(path)


class OverkillBrowserApp(tk.Tk):
    def __init__(self, start_dir: Path):
        super().__init__()
        self.title("Overkill RE Editor")
        self.geometry("1180x760")
        self.project_dir = start_dir
        self.game_dir = start_dir / "game_data"
        self.archive: Optional[ShadowArchive] = None
        self.filtered_entries: list[ResourceEntry] = []
        self.current_entry: Optional[ResourceEntry] = None
        self.current_decoded: Optional[BicDecoded] = None
        self.current_map_context: Optional[dict] = None
        self.level_show_enemies_var = tk.BooleanVar(value=False)
        self.level_show_debug_var = tk.BooleanVar(value=False)
        self.level_show_grid_var = tk.BooleanVar(value=False)
        self.level_show_runtime_candidates_var = tk.BooleanVar(value=False)
        self.level_show_decoded_map_events_var = tk.BooleanVar(value=True)
        self.level_show_moving_enemy_spawns_var = tk.BooleanVar(value=True)
        self.level_show_row_ruler_var = tk.BooleanVar(value=True)
        self._object_sprites_cache: Optional[list[Optional[Image.Image]]] = None
        self._moving_enemy_streams_cache: Optional[dict] = None
        self._moving_enemy_streams_status: str = ""
        self.level_zoom_var = tk.StringVar(value="3x")
        self._build_ui()
        self.load_default_archive()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.grid(row=0, column=0, sticky="nsew")

        self.graphics_tab = ttk.Frame(self.main_notebook)
        self.level_tab = ttk.Frame(self.main_notebook)
        self.runtime_objects_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.graphics_tab, text="Graphics Browser")
        self.main_notebook.add(self.level_tab, text="Level Viewer")
        self.main_notebook.add(self.runtime_objects_tab, text="Runtime Objects")

        self.graphics_tab.columnconfigure(0, weight=0)
        self.graphics_tab.columnconfigure(1, weight=1)
        self.graphics_tab.rowconfigure(1, weight=1)

        top = ttk.Frame(self.graphics_tab, padding=6)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(4, weight=1)

        ttk.Button(top, text="Open game_data...", command=self.open_game_dir).grid(row=0, column=0, padx=3)
        ttk.Button(top, text="Extract resources", command=self.extract_resources).grid(row=0, column=1, padx=3)
        ttk.Button(top, text="Save preview PNG", command=self.save_preview).grid(row=0, column=2, padx=3)
        ttk.Label(top, text="Filter:").grid(row=0, column=3, padx=(12, 3))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self.apply_filter())
        ttk.Entry(top, textvariable=self.filter_var).grid(row=0, column=4, sticky="ew")

        left = ttk.Frame(self.graphics_tab, padding=(6, 0, 3, 6))
        left.grid(row=1, column=0, sticky="ns")
        left.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(left, columns=("idx", "name", "size", "ext"), show="headings", height=30)
        for col, text, w in [("idx", "#", 42), ("name", "Resource", 150), ("size", "Size", 72), ("ext", "Type", 50)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, stretch=False)
        self.tree.grid(row=0, column=0, sticky="ns")
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right = ttk.Frame(self.graphics_tab, padding=(3, 0, 6, 6))
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        self.info_label = ttk.Label(right, text="", anchor="w")
        self.info_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.notebook = ttk.Notebook(right)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.preview = ImageCanvas(self.notebook)
        self.notebook.add(self.preview, text="Preview")
        self.hex_text = tk.Text(self.notebook, wrap="none", font=("Courier", 10))
        self.notebook.add(self.hex_text, text="Hex / decode info")
        self.inspector_text = tk.Text(self.notebook, wrap="word", font=("Courier", 10))
        self.notebook.add(self.inspector_text, text="Inspector")
        self.notes_text = self.inspector_text
        self.preview.canvas.bind("<Button-1>", self.on_preview_click)

        self._build_level_viewer()
        self._build_runtime_objects_view()


    def _build_level_viewer(self):
        """Build the dedicated level viewer tab with layer toggles."""
        self.level_tab.columnconfigure(0, weight=1)
        self.level_tab.columnconfigure(1, weight=0)
        self.level_tab.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.level_tab, padding=6)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(controls, text="Level:").grid(row=0, column=0, padx=(0, 4))
        self.level_var = tk.StringVar(value="LEV1")
        self.level_combo = ttk.Combobox(
            controls,
            textvariable=self.level_var,
            width=12,
            state="readonly",
            values=[f"LEV{i}" for i in range(6)],
        )
        self.level_combo.grid(row=0, column=1, padx=4)
        ttk.Button(controls, text="Render level", command=self.render_selected_level).grid(row=0, column=2, padx=4)
        ttk.Label(controls, text="Zoom:").grid(row=0, column=3, padx=(16, 4))
        self.level_zoom_combo = ttk.Combobox(
            controls,
            textvariable=self.level_zoom_var,
            width=5,
            state="readonly",
            values=["1x", "2x", "3x", "4x", "5x"],
        )
        self.level_zoom_combo.grid(row=0, column=4, padx=4)
        self.level_zoom_combo.bind("<<ComboboxSelected>>", lambda _event: self.apply_level_zoom())
        ttk.Label(controls, text="LEVxMAP + paired LEVxBLX").grid(row=0, column=5, padx=(12, 4))

        self.level_canvas = ImageCanvas(self.level_tab, zoom=3)
        self.level_canvas.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=(0, 6))
        self.level_canvas.canvas.bind("<Button-1>", self.on_level_canvas_click)

        side = ttk.LabelFrame(self.level_tab, text="Level overlays", padding=8)
        side.grid(row=1, column=1, sticky="ns", padx=(3, 6), pady=(0, 6))

        ttk.Checkbutton(
            side,
            text="Show MAP special markers",
            variable=self.level_show_enemies_var,
            command=self.render_selected_level,
        ).grid(row=0, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show red debug overlay",
            variable=self.level_show_debug_var,
            command=self.render_selected_level,
        ).grid(row=1, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show grid",
            variable=self.level_show_grid_var,
            command=self.render_selected_level,
        ).grid(row=2, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show suspected runtime formations",
            variable=self.level_show_runtime_candidates_var,
            command=self.render_selected_level,
        ).grid(row=3, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show decoded map events",
            variable=self.level_show_decoded_map_events_var,
            command=self.render_selected_level,
        ).grid(row=4, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show moving enemy spawns",
            variable=self.level_show_moving_enemy_spawns_var,
            command=self.render_selected_level,
        ).grid(row=5, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            side,
            text="Show canonical row ruler",
            variable=self.level_show_row_ruler_var,
            command=self.render_selected_level,
        ).grid(row=6, column=0, sticky="w", pady=2)

        ttk.Separator(side, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=8)

        info = (
            "Notes:\n"
            "• Base layer is MAP/BLX terrain.\n"
            "• Static MAP events are decoded\n"
            "  directly from LEVxMAP.BIC.\n"
            "• Moving formations are executable\n"
            "  stream data when available.\n"
            "• Default zoom is 3×."
        )
        ttk.Label(side, text=info, justify="left", wraplength=240).grid(row=8, column=0, sticky="w")

    def apply_level_zoom(self):
        m = re.match(r"(\d+)x", self.level_zoom_var.get())
        zoom = int(m.group(1)) if m else 3
        self.level_canvas.set_zoom(zoom)


    def level_zoom_value(self) -> int:
        m = re.match(r"(\d+)x", self.level_zoom_var.get())
        return int(m.group(1)) if m else 3

    def load_research_observations(self, level_name: str) -> list[dict]:
        """Load user-verifiable manual research markers.

        These are intentionally separate from parsers. They are observations we
        can overlay, verify, correct, or delete as reverse engineering progresses.
        """
        path = self.project_dir / "research_overlays" / "level_observations.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return list(data.get(level_name.upper(), []))
        except Exception:
            return []






    def load_moving_enemy_sprite_hints(self) -> dict:
        path = self.project_dir / "research_overlays" / "moving_enemy_sprite_family_hints.json"
        hints: dict = {}
        if not path.exists():
            hints = {}
        else:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                hints = dict(data.get("behaviors", {}))
            except Exception:
                hints = {}

        evidence_path = self.project_dir / "research_overlays" / "moving_enemy_behavior_handler_sprite_evidence.json"
        if not evidence_path.exists():
            return hints
        try:
            data = json.loads(evidence_path.read_text(encoding="utf-8"))
            for rec in data.get("handler_evidence", []):
                key = self.normalize_behavior_key(rec.get("behavior_hex", rec.get("behavior", "?")))
                if key in hints:
                    continue
                frames: list[int] = []
                for ev in rec.get("sprite_evidence", []) or []:
                    candidate = ev.get("frame_family_candidate")
                    if candidate:
                        frames.extend(int(x) for x in candidate)
                    exact = ev.get("exact_sprite")
                    if exact is not None:
                        frames.append(int(exact))
                frames = sorted(dict.fromkeys(frames))
                if frames:
                    if len(frames) == 1:
                        display = f"2X2:{frames[0]}"
                    elif frames == list(range(frames[0], frames[-1] + 1)):
                        display = f"2X2:{frames[0]}-{frames[-1]}"
                    else:
                        display = "2X2:" + ",".join(str(frame) for frame in frames)
                    hints[key] = {
                        "status": "static_evidence",
                        "display": display,
                        "sprite_frames": frames,
                    }
            return hints
        except Exception:
            return hints

    def object_sprites(self) -> list[Optional[Image.Image]]:
        """Return decoded 2X2 object/enemy sprites for overlay drawing."""
        if self._object_sprites_cache is not None:
            return self._object_sprites_cache
        if not self.archive:
            self._object_sprites_cache = []
            return self._object_sprites_cache
        sprite_entry = next((e for e in self.archive.entries if e.name.upper() == "2X2.BIC"), None)
        if sprite_entry is None:
            self._object_sprites_cache = []
            return self._object_sprites_cache
        try:
            self._object_sprites_cache = render_2x2_object_sprites(decode_bic(sprite_entry.data))
        except Exception:
            self._object_sprites_cache = []
        return self._object_sprites_cache

    def normalize_behavior_key(self, value) -> str:
        if isinstance(value, int):
            return f"0x{value:02X}"
        text = str(value).strip()
        try:
            return f"0x{int(text, 16 if text.lower().startswith('0x') else 10):02X}"
        except Exception:
            return text.upper()

    def sprite_index_for_behavior(self, behavior, sequence_index: int = 0) -> int | None:
        """Choose a representative sprite frame for a decoded behavior."""
        key = self.normalize_behavior_key(behavior)
        hints = self.load_moving_enemy_sprite_hints()
        hint = hints.get(key) or hints.get(key.upper())
        if not hint:
            return None
        frames = hint.get("sprite_frames") or hint.get("observed_snapshot_sprites") or []
        if not frames:
            return None
        try:
            return int(frames[sequence_index % len(frames)])
        except Exception:
            return None

    def paste_object_sprite(self, out: Image.Image, sprite_index: int | None, x: int, y: int) -> bool:
        """Paste a 2X2 sprite at top-left map coordinates, clipped to the image."""
        if sprite_index is None:
            return False
        sprites = self.object_sprites()
        if sprite_index < 0 or sprite_index >= len(sprites):
            return False
        sprite = sprites[sprite_index]
        if sprite is None:
            return False
        x = int(x)
        y = int(y)
        if x >= out.width or y >= out.height or x + sprite.width <= 0 or y + sprite.height <= 0:
            return False
        left = max(0, x)
        top = max(0, y)
        right = min(out.width, x + sprite.width)
        bottom = min(out.height, y + sprite.height)
        crop_box = (left - x, top - y, right - x, bottom - y)
        sprite_crop = sprite.crop(crop_box)
        mask_crop = make_nonblack_mask(sprite).crop(crop_box)
        out.paste(sprite_crop, (left, top), mask_crop)
        return True

    def add_overlay_rect(self, items: list[dict], coords, outline, width: int = 2) -> None:
        items.append({"type": "rectangle", "coords": tuple(coords), "outline": outline, "width": width})

    def add_overlay_line(self, items: list[dict], coords, fill, width: int = 1) -> None:
        items.append({"type": "line", "coords": tuple(coords), "fill": fill, "width": width})

    def add_overlay_text(self, items: list[dict], x: int, y: int, text: str, fill) -> None:
        items.append({"type": "text", "coords": (x, y), "text": text, "fill": fill})

    def shift_overlay_items(self, items: list[dict], dx: int = 0, dy: int = 0) -> list[dict]:
        shifted = []
        for item in items:
            copy = dict(item)
            coords = list(copy.get("coords", ()))
            for i in range(0, len(coords), 2):
                coords[i] += dx
                if i + 1 < len(coords):
                    coords[i + 1] += dy
            copy["coords"] = tuple(coords)
            shifted.append(copy)
        return shifted

    def static_map_event_defs(self) -> dict[int, dict]:
        return {
            0x04: {"initializer": "0x78D4", "behavior": "0x8B", "label": "static enemy 8B"},
            0x07: {"initializer": "0x78E0", "behavior": "0x8C", "label": "static enemy 8C"},
            0x6C: {"initializer": "0x7914", "behavior": "0x24", "label": "static event 24"},
            0x6D: {"initializer": "0x792A", "behavior": "0x25", "label": "static event 25"},
            0xAC: {"initializer": "0x7940", "behavior": "0x90", "label": "static event 90"},
            0xB1: {"initializer": "0x7956", "behavior": "0x91", "label": "static event 91"},
            0xC9: {"initializer": "0x7877", "behavior": "0x28", "label": "static event 28"},
        }

    def load_moving_enemy_spawns(self, level_name: str) -> list[dict]:
        if not self.archive:
            return []
        if self._moving_enemy_streams_cache is None:
            data, status = decode_moving_enemy_spawn_streams_from_archive(self.archive)
            if data is None:
                # Compatibility fallback while the packed executable image is
                # being mapped back to the pass75 unpacked runtime artifact.
                path = self.project_dir / "research_overlays" / "moving_enemy_spawn_streams_all_levels.json"
                if path.exists():
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                        status = "fallback research artifact: " + status
                    except Exception:
                        data = {"streams": []}
                else:
                    data = {"streams": []}
            self._moving_enemy_streams_cache = data
            self._moving_enemy_streams_status = status if len(status) <= 260 else status[:257] + "..."
        try:
            m = re.search(r"LEV(\d+)", level_name.upper())
            if not m:
                return []
            stream_index = int(m.group(1))
            for stream in self._moving_enemy_streams_cache.get("streams", []):
                if int(stream.get("stream_index", -1)) == stream_index:
                    return list(stream.get("records", []))
            return []
        except Exception:
            return []

    def draw_moving_enemy_spawns(
        self,
        img: Image.Image,
        display_rows: list,
        level_name: str,
        overlay_items: Optional[list[dict]] = None,
    ) -> Image.Image:
        records = self.load_moving_enemy_spawns(level_name)
        if not records:
            return img

        out = img.copy()
        overlay_items = overlay_items if overlay_items is not None else []
        sprite_hints = self.load_moving_enemy_sprite_hints()
        canon_to_display = {canonical: i for i, (canonical, _row) in enumerate(display_rows)}

        for rec in records:
            canonical = int(rec.get("approx_canonical_row_inferred_288_minus_trigger", -1))
            display_row = canon_to_display.get(canonical)
            if display_row is None:
                continue

            anchor_y = display_row * 16
            behavior = self.normalize_behavior_key(rec.get("descriptor_behavior_hex", rec.get("descriptor_behavior", "?")))
            count = int(rec.get("descriptor_count") or 0)
            trigger = int(rec.get("trigger", -1))
            confirmed_blue = (
                behavior.upper() == "0X2D"
                and trigger == 130
                and int(rec.get("base_x", -999)) == 64
            )
            outline = (0, 255, 96) if confirmed_blue else (255, 128, 0)
            text = (0, 255, 160) if confirmed_blue else (255, 220, 0)

            pts = rec.get("spawn_points_at_event_anchor_screen_space") or []
            points = []
            for p in pts:
                try:
                    points.append((int(p.get("x", rec.get("base_x", 0))), int(p.get("y", rec.get("base_y", 0)))))
                except Exception:
                    pass
            if not points:
                points = [(int(rec.get("base_x", 0)), int(rec.get("base_y", 0)))]

            min_py = min((py for _x, py in points), default=0)
            drawn_points = []
            for i, (x, py) in enumerate(points):
                draw_y = anchor_y + 4 + (py - min_py)
                sprite_index = self.sprite_index_for_behavior(behavior, i)
                sprite_drawn = self.paste_object_sprite(out, sprite_index, x, draw_y)
                self.add_overlay_rect(overlay_items, (x - 3, draw_y - 3, x + 3, draw_y + 3), outline, width=2)
                if sprite_drawn:
                    self.add_overlay_rect(overlay_items, (x, draw_y, x + 15, draw_y + 15), outline, width=1)
                drawn_points.append((x, draw_y))

            if len(drawn_points) > 1:
                coords = []
                for x, y in drawn_points:
                    coords.extend((x + 8, y + 8))
                self.add_overlay_line(overlay_items, coords, outline, width=1)

            hint = sprite_hints.get(behavior.upper()) or sprite_hints.get(behavior)
            hint_text = ""
            if hint:
                hint_text = " " + str(hint.get("display", ""))
            label = f"{behavior}×{count} t{trigger}{hint_text}"
            xs = [x for x, _y in drawn_points]
            ys = [y for _x, y in drawn_points]
            lx = max(0, min(out.width - 190, (min(xs) if xs else 0) + 5))
            self.add_overlay_text(overlay_items, lx, max(0, (min(ys) if ys else anchor_y) - 11), label, text)

        return out


    def load_decoded_map_events(self, level_name: str, map_decoded: Optional[BicDecoded] = None) -> list[dict]:
        if map_decoded is None:
            return []

        event_defs = self.static_map_event_defs()
        events = []
        for canonical, row in playable_map_rows_with_indices(map_decoded):
            for col, raw in enumerate(row):
                evdef = event_defs.get(raw)
                if not evdef:
                    continue
                events.append({
                    "level": level_name.upper(),
                    "canonical_row": canonical,
                    "col": col,
                    "raw": raw,
                    "raw_hex": f"0x{raw:02X}",
                    "spawn_x": col * 16,
                    "initializer": evdef["initializer"],
                    "behavior": evdef["behavior"],
                    "label": evdef["label"],
                    "confidence": "generic static MAP event candidate",
                })
        return events

    def draw_decoded_map_events(
        self,
        img: Image.Image,
        display_rows: list,
        level_name: str,
        map_decoded: Optional[BicDecoded] = None,
        overlay_items: Optional[list[dict]] = None,
    ) -> Image.Image:
        events = self.load_decoded_map_events(level_name, map_decoded)
        if not events:
            return img
        out = img.copy()
        overlay_items = overlay_items if overlay_items is not None else []
        canon_to_display = {canonical: i for i, (canonical, _row) in enumerate(display_rows)}

        for ev in events:
            canonical = int(ev.get("canonical_row", -1))
            col = int(ev.get("col", -1))
            display_row = canon_to_display.get(canonical)
            if display_row is None or col < 0:
                continue

            x0 = col * 16
            y0 = display_row * 16
            raw = int(ev.get("raw", 0))
            behavior = self.normalize_behavior_key(ev.get("behavior", "?"))
            confidence = str(ev.get("confidence", "static"))
            confirmed = "confirmed" in confidence.lower()
            outline = (0, 255, 64) if confirmed else (255, 128, 0)
            text = (0, 255, 128) if confirmed else (255, 220, 0)

            sprite_index = self.sprite_index_for_behavior(behavior)
            sprite_drawn = self.paste_object_sprite(out, sprite_index, x0, y0)
            self.add_overlay_rect(overlay_items, (x0, y0, x0 + 15, y0 + 15), outline, width=2)
            if not sprite_drawn:
                self.add_overlay_text(overlay_items, x0 + 1, y0 + 1, f"{raw:02X}", text)
            self.add_overlay_text(overlay_items, x0 + 18, max(0, y0 - 1), f"b{behavior}", text)

        return out

    def load_runtime_object_dump(self, level_name: str) -> list[dict]:
        path = self.project_dir / "research_overlays" / "runtime_object_slots.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if level_name.upper() in data:
                return list(data.get(level_name.upper(), []))
            return list(data.get("objects", []))
        except Exception:
            return []

    def draw_runtime_object_dump(self, img: Image.Image, level_name: str) -> Image.Image:
        """Draw actual runtime object slots if user provides a memory-dump-derived JSON.

        Expected file:
            research_overlays/runtime_object_slots.json

        Each object should have at least x, y, sprite, behavior, pool, slot.
        """
        objects = self.load_runtime_object_dump(level_name)
        if not objects:
            return img

        out = img.copy()
        draw = ImageDraw.Draw(out)
        for obj in objects:
            if int(obj.get("active", 0)) == 0:
                continue
            x = int(obj.get("x", obj.get("field_04", 0)))
            y = int(obj.get("y", obj.get("field_02", 0)))
            sprite = int(obj.get("sprite", obj.get("field_08", -1)))
            behavior = int(obj.get("behavior", obj.get("field_18", -1)))
            label = obj.get("label") or f"{obj.get('pool','?')}{obj.get('slot','?')} s{sprite} b{behavior:02X}"

            # Runtime object coords are game-space; draw watched sprites more strongly.
            watched = bool(obj.get("watched_sprite")) or sprite in {147, 148, 149, 150, 71}
            r = 7 if watched else 5
            outline = (255, 64, 0) if watched else (0, 255, 64)
            cross = (255, 255, 0) if watched else (0, 255, 255)
            text_color = (255, 220, 0) if watched else (0, 255, 128)
            self.paste_object_sprite(out, sprite, x, y)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=outline, width=3 if watched else 2)
            draw.line((x-r-2, y, x+r+2, y), fill=cross)
            draw.line((x, y-r-2, x, y+r+2), fill=cross)
            draw.text((x + r + 2, max(0, y - r)), str(label), fill=text_color)

        return out

    def load_runtime_formation_candidates(self, level_name: str) -> list[dict]:
        path = self.project_dir / "research_overlays" / "runtime_formation_candidates.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return list(data.get(level_name.upper(), []))
        except Exception:
            return []

    def draw_runtime_formation_candidates(
        self,
        img: Image.Image,
        display_rows: list,
        level_name: str,
        overlay_items: Optional[list[dict]] = None,
    ) -> Image.Image:
        """Draw suspected runtime formations/trigger lines.

        These are not decoded enemies yet. They are disassembly-derived candidates:
        trigger rows, table pointers, object counts, and known formula groups.
        """
        candidates = self.load_runtime_formation_candidates(level_name)
        if not candidates:
            return img

        out = img.copy()
        overlay_items = overlay_items if overlay_items is not None else []
        level_h = out.height

        for cand in candidates:
            cid = str(cand.get("id", "candidate"))
            kind = str(cand.get("kind", "runtime"))
            confidence = str(cand.get("confidence", "?"))
            trigger = cand.get("trigger") or {}

            # If we only know a scroll trigger, draw a horizontal band at its row16 estimate.
            if "row16" in trigger:
                row16 = float(trigger.get("row16", 0.0))
                y = int(row16 * 16)
                if 0 <= y < level_h:
                    self.add_overlay_line(overlay_items, (0, y, out.width, y), (255, 64, 255), width=2)
                    self.add_overlay_text(overlay_items, 2, min(level_h - 14, y + 2), f"{cid}: trigger {trigger.get('equals')} / {kind}", (255, 128, 255))

                    # For object-count formations with unknown table contents, draw placeholder slots at top center.
                    count = cand.get("object_count")
                    try:
                        count_int = int(count)
                    except Exception:
                        count_int = 0
                    if count_int > 0 and "table contents not decoded" in str(cand.get("position_status", "")):
                        spacing = 20
                        start_x = max(8, (out.width - (count_int - 1) * spacing) // 2)
                        yy = max(8, y - 26)
                        for i in range(count_int):
                            x = start_x + i * spacing
                            self.add_overlay_rect(overlay_items, (x - 5, yy - 5, x + 5, yy + 5), (255, 64, 255), width=2)
                            self.add_overlay_line(overlay_items, (x - 7, yy, x + 7, yy), (255, 255, 0), width=1)
                            self.add_overlay_line(overlay_items, (x, yy - 7, x, yy + 7), (255, 255, 0), width=1)
                        self.add_overlay_text(overlay_items, start_x, max(0, yy - 18), f"{count_int} objects @ {cand.get('data_pointer', 'table?')} ?", (255, 220, 0))

            # If a candidate has explicit approximate points later, support them too.
            for point in cand.get("estimated_points", []) or []:
                x = int(point.get("level_x", 0))
                y = int(point.get("level_y", 0))
                label = str(point.get("label", cid))
                r = int(point.get("radius", 5))
                self.add_overlay_rect(overlay_items, (x - r, y - r, x + r, y + r), (255, 0, 255), width=2)
                self.add_overlay_text(overlay_items, x + r + 2, max(0, y - r), label, (255, 128, 255))

        return out

    def draw_research_observations(self, img: Image.Image, display_rows: list, level_name: str) -> Image.Image:
        observations = self.load_research_observations(level_name)
        if not observations:
            return img
        out = img.copy()
        draw = ImageDraw.Draw(out)
        canon_to_display = {canonical: i for i, (canonical, _row) in enumerate(display_rows)}

        for obs in observations:
            label = str(obs.get("label", "observation"))

            # Off-grid/runtime observation: use exact level-image pixel coordinates.
            # This is useful for enemies that are not aligned to MAP cells.
            if "level_x" in obs and "level_y" in obs:
                x = int(obs.get("level_x", 0))
                y = int(obs.get("level_y", 0))
                r = int(obs.get("radius", 6))
                sprite_index = None
                sprites = obs.get("sprites") or []
                if sprites:
                    try:
                        sprite_index = int(sprites[0])
                    except Exception:
                        sprite_index = None
                self.paste_object_sprite(out, sprite_index, x - 8, y - 8)
                draw.ellipse((x - r, y - r, x + r, y + r), outline=(255, 160, 0), width=2)
                draw.line((x - r, y, x + r, y), fill=(255, 255, 0))
                draw.line((x, y - r, x, y + r), fill=(255, 255, 0))
                draw.text((x + r + 2, max(0, y - r)), label, fill=(255, 220, 0))
                continue

            # Grid/canonical observation: mark a MAP tile cell.
            canonical = int(obs.get("canonical_row", -1))
            col = int(obs.get("col", obs.get("display_col", -1)))
            display_row = canon_to_display.get(canonical)
            if display_row is None or col < 0:
                continue
            x0 = col * 16
            y0 = display_row * 16
            sprite_index = None
            sprites = obs.get("sprites") or []
            if sprites:
                try:
                    sprite_index = int(sprites[0])
                except Exception:
                    sprite_index = None
            self.paste_object_sprite(out, sprite_index, x0, y0)
            draw.rectangle((x0, y0, x0 + 15, y0 + 15), outline=(0, 255, 255), width=2)
            draw.line((x0, y0, x0 + 15, y0 + 15), fill=(255, 255, 0))
            draw.line((x0 + 15, y0, x0, y0 + 15), fill=(255, 255, 0))
            draw.text((x0 + 18, max(0, y0 - 1)), label, fill=(255, 255, 0))

        return out

    def draw_canonical_row_ruler(self, img: Image.Image, display_rows: list, step: int = 16) -> Image.Image:
        """Overlay canonical row numbers for orientation while debugging scrolling levels."""
        out = img.copy()
        draw = ImageDraw.Draw(out)
        for display_row, (canonical, _row) in enumerate(display_rows):
            if canonical % step != 0:
                continue
            y = display_row * 16
            draw.line((0, y, out.width, y), fill=(0, 128, 255))
            draw.text((2, y + 2), f"c{canonical}", fill=(0, 255, 255))
        return out

    def add_grid_overlay(self, items: list[dict], img: Image.Image, tile_size: int = 16) -> None:
        for x in range(0, img.width + 1, tile_size):
            self.add_overlay_line(items, (x, 0, x, img.height), (64, 64, 64), width=1)
        for y in range(0, img.height + 1, tile_size):
            self.add_overlay_line(items, (0, y, img.width, y), (64, 64, 64), width=1)

    def add_map_special_marker_overlay(self, items: list[dict], display_rows: list, tile_count: int) -> None:
        for y, (_canonical, row) in enumerate(display_rows):
            for x, value in enumerate(row):
                if not map_value_is_special(value, tile_count):
                    continue
                x0, y0 = x * 16, y * 16
                self.add_overlay_rect(items, (x0 + 3, y0 + 3, x0 + 12, y0 + 12), (255, 128, 0), width=1)
                self.add_overlay_line(items, (x0 + 4, y0 + 4, x0 + 11, y0 + 11), (255, 128, 0), width=1)
                self.add_overlay_line(items, (x0 + 11, y0 + 4, x0 + 4, y0 + 11), (255, 128, 0), width=1)

    def add_canonical_row_ruler_overlay(self, items: list[dict], img: Image.Image, display_rows: list, step: int = 16) -> None:
        for display_row, (canonical, _row) in enumerate(display_rows):
            if canonical % step != 0:
                continue
            y = display_row * 16
            self.add_overlay_line(items, (0, y, img.width, y), (0, 128, 255), width=1)
            self.add_overlay_text(items, 2, y + 2, f"c{canonical}", (0, 255, 255))

    def render_selected_level(self):
        if not self.archive:
            messagebox.showinfo("No archive", "Load game_data/OVERKILL first.")
            return
        m = re.match(r"LEV(\d+)", self.level_var.get().upper())
        if not m:
            return
        level_index = int(m.group(1))
        level_name = f"LEV{level_index}"
        map_entry = next((e for e in self.archive.entries if e.name.upper() == f"LEV{level_index}MAP.BIC"), None)
        if map_entry is None:
            messagebox.showerror("Missing resource", f"LEV{level_index}MAP.BIC not found.")
            return

        map_bic = decode_bic(map_entry.data)
        blx_index = DEFAULT_MAP_TO_BLX.get(level_index, level_index)
        blx_entry = next((e for e in self.archive.entries if e.name.upper() == f"LEV{blx_index}BLX.BIC"), None)
        if blx_entry is None:
            messagebox.showerror("Missing resource", f"LEV{blx_index}BLX.BIC not found.")
            return

        show_markers = bool(self.level_show_enemies_var.get())
        show_debug = bool(self.level_show_debug_var.get())
        show_grid = bool(self.level_show_grid_var.get())
        show_runtime_candidates = bool(self.level_show_runtime_candidates_var.get())
        show_decoded_map_events = bool(self.level_show_decoded_map_events_var.get())
        show_moving_enemy_spawns = bool(self.level_show_moving_enemy_spawns_var.get())
        show_ruler = bool(self.level_show_row_ruler_var.get())

        blx_bic = decode_bic(blx_entry.data)
        tile_records = decode_blx_tile_records(blx_bic)
        object_sprites = self.object_sprites()

        rendered = render_level_from_map_and_tiles(
            map_bic,
            blx_bic,
            object_sprites=None,
            show_objects=False,
            show_grid=False,
        )

        display_rows = map_rows_for_display_with_indices(map_bic)
        overlay_items: list[dict] = []
        if show_grid:
            self.add_grid_overlay(overlay_items, rendered)
        if show_markers:
            self.add_map_special_marker_overlay(overlay_items, display_rows, len(tile_records))
        if show_ruler:
            self.add_canonical_row_ruler_overlay(overlay_items, rendered, display_rows)
        if show_runtime_candidates:
            rendered = self.draw_runtime_formation_candidates(rendered, display_rows, level_name, overlay_items)
        if show_decoded_map_events:
            rendered = self.draw_decoded_map_events(rendered, display_rows, level_name, map_bic, overlay_items)
        if show_moving_enemy_spawns:
            rendered = self.draw_moving_enemy_spawns(rendered, display_rows, level_name, overlay_items)

        overlay = None
        if show_debug:
            overlay = make_map_highbit_overlay(
                map_bic,
                cell=16,
                sprite_count=0,
                show_grid=show_grid,
                tile_count=len(tile_records),
            )

        title_bits = ["level render", "terrain"]
        if show_markers:
            title_bits.append("MAP special markers")
        if show_grid:
            title_bits.append("grid")
        if show_runtime_candidates:
            title_bits.append("runtime candidates")
        if show_decoded_map_events:
            title_bits.append("decoded map events")
        if show_moving_enemy_spawns:
            title_bits.append("moving enemy spawns")
        if show_ruler:
            title_bits.append("row ruler")
        if overlay is None:
            combined = rendered
            label_h = 0
        else:
            combined = combine_map_render_and_overlay(rendered, overlay, title=" + ".join(title_bits))
            label_h = 18
        combined_overlay_items = self.shift_overlay_items(overlay_items, dy=label_h)

        self.current_map_context = {
            "map_name": map_entry.name.upper(),
            "blx_name": blx_entry.name.upper(),
            "map_rows": [row for _, row in display_rows],
            "display_canonical_indices": [idx for idx, _ in display_rows],
            "canonical_rows": decode_map_rows(map_bic),
            "tile_records": tile_records,
            "object_sprite_count": len(object_sprites),
            "metadata_row_skipped": bool(decode_map_rows(map_bic) and is_map_metadata_row(decode_map_rows(map_bic)[0])),
            "rendered_width": rendered.width,
            "label_h": label_h,
            "gap": 12,
            "tile_size": 16,
            "show_enemies": show_markers,
            "show_debug": show_debug,
            "show_grid": show_grid,
            "show_runtime_candidates": show_runtime_candidates,
            "show_decoded_map_events": show_decoded_map_events,
            "show_moving_enemy_spawns": show_moving_enemy_spawns,
            "show_ruler": show_ruler,
            "zoom": self.level_zoom_value(),
        }
        self.level_canvas.set_zoom(self.level_zoom_value())
        self.level_canvas.set_image(combined, combined_overlay_items)
        self.inspector_text.delete("1.0", "end")
        self.inspector_text.insert(
            "end",
            f"Rendered {map_entry.name} with {blx_entry.name}. "
            f"markers={'on' if show_markers else 'off'}, "
            f"debug={'on' if show_debug else 'off'}, "
            f"grid={'on' if show_grid else 'off'}, "
            f"runtime_candidates={'on' if show_runtime_candidates else 'off'}, "
            f"decoded_map_events={'on' if show_decoded_map_events else 'off'}, "
            f"moving_enemy_spawns={'on' if show_moving_enemy_spawns else 'off'}, "
            f"ruler={'on' if show_ruler else 'off'}, "
            f"zoom={self.level_zoom_value()}x. "
            f"moving stream source: {self._moving_enemy_streams_status or 'not probed'}. "
            "Click a cell in Level Viewer for details.\n",
        )
        self.main_notebook.select(self.level_tab)

    def on_level_canvas_click(self, event):
        ctx = getattr(self, "current_map_context", None)
        if not ctx:
            return
        x, y = self.level_canvas.canvas_event_to_image_xy(event)
        info = self.describe_map_click(x, y, ctx)
        self.inspector_text.delete("1.0", "end")
        self.inspector_text.insert("end", info)


    def _build_runtime_objects_view(self):
        """Screen-space viewer for runtime object-pool dumps."""
        self.runtime_objects_tab.columnconfigure(0, weight=1)
        self.runtime_objects_tab.columnconfigure(1, weight=0)
        self.runtime_objects_tab.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.runtime_objects_tab, padding=6)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(controls, text="Runtime object dump:").grid(row=0, column=0, padx=(0, 6))
        ttk.Button(controls, text="Reload JSON", command=self.render_runtime_objects_dump).grid(row=0, column=1, padx=4)
        ttk.Label(controls, text="Coordinates are screen/playfield pixels, not full-level map pixels.").grid(row=0, column=2, padx=(12, 4))

        self.runtime_objects_canvas = ImageCanvas(self.runtime_objects_tab, zoom=3)
        self.runtime_objects_canvas.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=(0, 6))

        side = ttk.LabelFrame(self.runtime_objects_tab, text="Active runtime objects", padding=8)
        side.grid(row=1, column=1, sticky="ns", padx=(3, 6), pady=(0, 6))
        self.runtime_objects_text = tk.Text(side, width=58, height=36, wrap="none")
        self.runtime_objects_text.grid(row=0, column=0, sticky="nsew")
        ybar = ttk.Scrollbar(side, orient="vertical", command=self.runtime_objects_text.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        self.runtime_objects_text.configure(yscrollcommand=ybar.set)
        side.rowconfigure(0, weight=1)
        side.columnconfigure(0, weight=1)

    def runtime_dump_objects_for_level(self, level_name: str = "LEV1") -> list[dict]:
        path = self.project_dir / "research_overlays" / "runtime_object_slots.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return list(data.get(level_name.upper(), []))
        except Exception:
            return []

    def render_runtime_objects_dump(self):
        objects = self.runtime_dump_objects_for_level("LEV1")
        w, h = 208, 200
        img = Image.new("RGB", (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, w - 1, h - 1), outline=(80, 80, 80))

        active = [obj for obj in objects if int(obj.get("active", 0))]
        active.sort(key=lambda obj: (0 if obj.get("watched_sprite") else 1, str(obj.get("pool", "")), int(obj.get("slot", 0))))

        for obj in active:
            x = int(obj.get("x", obj.get("field_04", 0)))
            y = int(obj.get("y", obj.get("field_02", 0)))
            sprite = int(obj.get("sprite", obj.get("field_08", -1)))
            behavior = int(obj.get("behavior", obj.get("field_18", -1)))
            watched = bool(obj.get("watched_sprite")) or sprite in {147, 148, 149, 150, 71}
            r = 7 if watched else 5
            outline = (255, 96, 0) if watched else (0, 255, 96)
            cross = (255, 255, 0) if watched else (0, 255, 255)
            text_color = (255, 220, 0) if watched else (0, 255, 160)

            self.paste_object_sprite(img, sprite, x, y)
            draw.ellipse((x - r, y - r, x + r, y + r), outline=outline, width=2)
            draw.line((x - r - 2, y, x + r + 2, y), fill=cross)
            draw.line((x, y - r - 2, x, y + r + 2), fill=cross)
            label = f"{obj.get('pool','?')}{int(obj.get('slot',0)):02d} s{sprite} b{behavior:02X}"
            draw.text((min(w - 86, x + r + 2), max(0, y - r - 10)), label, fill=text_color)

        self.runtime_objects_canvas.set_image(img)

        self.runtime_objects_text.delete("1.0", "end")
        if not active:
            self.runtime_objects_text.insert("end", "No active runtime objects loaded.\n")
            return

        self.runtime_objects_text.insert("end", "Active runtime objects from research_overlays/runtime_object_slots.json\n")
        self.runtime_objects_text.insert("end", "Coordinates: screen/playfield pixels\n\n")
        self.runtime_objects_text.insert("end", "pool slot  x    y   sprite behavior state class  watched\n")
        self.runtime_objects_text.insert("end", "---- ---- ---- ---- ------ -------- ----- ----- -------\n")
        for obj in active:
            pool = str(obj.get("pool", "?"))
            slot = int(obj.get("slot", 0))
            x = int(obj.get("x", 0))
            y = int(obj.get("y", 0))
            sprite = int(obj.get("sprite", 0))
            behavior = int(obj.get("behavior", 0))
            state = int(obj.get("state_or_drop_type", obj.get("field_06", 0)))
            cls = int(obj.get("class_or_layer", obj.get("field_16", 0)))
            watched = "YES" if obj.get("watched_sprite") else ""
            self.runtime_objects_text.insert(
                "end",
                f"{pool:>4} {slot:>4} {x:>4} {y:>4} {sprite:>6} 0x{behavior:02X}     {state:>5} {cls:>5} {watched}\n"
            )

    def load_default_archive(self):
        path = self.game_dir / "OVERKILL"
        if path.exists():
            self.load_archive(path)
        else:
            self.info_label.config(text="No game_data/OVERKILL found. Use Open game_data...")

    def open_game_dir(self):
        d = filedialog.askdirectory(initialdir=str(self.project_dir), title="Select folder containing OVERKILL data file")
        if not d:
            return
        dpath = Path(d)
        # accept either the game_data folder or project root
        path = dpath / "OVERKILL"
        if not path.exists() and (dpath / "game_data" / "OVERKILL").exists():
            path = dpath / "game_data" / "OVERKILL"
        if not path.exists():
            messagebox.showerror("Not found", "Could not find OVERKILL in selected folder.")
            return
        self.game_dir = path.parent
        self.load_archive(path)

    def load_archive(self, path: Path):
        try:
            self.archive = ShadowArchive(path)
            self._object_sprites_cache = None
            self._moving_enemy_streams_cache = None
            self._moving_enemy_streams_status = ""
            self.info_label.config(text=f"Loaded {path} | SHADOW at 0x{self.archive.overlay_base:05x}, {self.archive.count} resources")
            self.apply_filter()
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("end", self.make_notes())
            try:
                self.render_selected_level()
            except Exception:
                pass
            try:
                self.render_runtime_objects_dump()
            except Exception:
                pass
        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror("Load failed", str(exc))

    def apply_filter(self):
        if not self.archive:
            return
        q = self.filter_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        self.filtered_entries = []
        for e in self.archive.entries:
            text = f"{e.index} {e.name} {e.ext} {NAME_KIND_HINTS.get(e.name.upper(), '')}".lower()
            if q and q not in text:
                continue
            self.filtered_entries.append(e)
            self.tree.insert("", "end", iid=str(len(self.filtered_entries) - 1), values=(e.index, e.name, e.size, e.ext))

    def selected_entry(self) -> Optional[ResourceEntry]:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.filtered_entries[int(sel[0])]

    def on_select(self, _event=None):
        e = self.selected_entry()
        if not e:
            return
        self.current_entry = e
        self.current_decoded = None
        self.current_map_context = None
        self.render_entry(e)

    def render_entry(self, e: ResourceEntry):
        self.hex_text.delete("1.0", "end")
        self.hex_text.insert("end", self.entry_info_text(e))
        try:
            img = self.make_preview(e)
            self.preview.set_image(img)
            self.notebook.select(self.preview)
        except Exception as exc:
            self.preview.set_image(self.make_message_image(f"No decoded preview yet\n\n{e.name}\n\n{exc}"))


    def on_preview_click(self, event):
        """Inspector for MAP previews."""
        ctx = getattr(self, "current_map_context", None)
        if not ctx:
            return
        x, y = self.preview.canvas_event_to_image_xy(event)
        info = self.describe_map_click(x, y, ctx)
        self.inspector_text.delete("1.0", "end")
        self.inspector_text.insert("end", info)
        try:
            self.notebook.select(self.inspector_text)
        except Exception:
            pass

    def describe_nearby_object_candidates(self, col: int, display_row: int, rows: list, sprite_count: int, radius: int = 3) -> str:
        """Return nearby special/out-of-range MAP cells around clicked cell.

        This is no longer treated as an enemy-sprite detector. It is a terrain/MAP
        diagnostic helper.
        """
        tile_count = sprite_count  # backwards-compatible parameter name in old calls
        found = []
        for rr in range(max(0, display_row - radius), min(len(rows), display_row + radius + 1)):
            row = rows[rr]
            for cc in range(max(0, col - radius), min(len(row), col + radius + 1)):
                raw = row[cc]
                if map_value_is_special(raw, tile_count):
                    found.append((rr, cc, raw))

        if not found:
            return "Nearby special/out-of-range MAP cells: none within radius 3.\n"

        lines = ["Nearby special/out-of-range MAP cells within radius 3:\n"]
        for rr, cc, raw in found[:30]:
            marker = " <-- clicked row/col" if rr == display_row and cc == col else ""
            lines.append(f"  display row={rr}, col={cc}, raw=0x{raw:02X}{marker}\n")
        if len(found) > 30:
            lines.append(f"  ... {len(found) - 30} more\n")
        return "".join(lines) + "\n"

    def describe_map_click(self, x: int, y: int, ctx: dict) -> str:
        label_h = ctx.get("label_h", 18)
        gap = ctx.get("gap", 12)
        rendered_width = ctx.get("rendered_width", 13 * 16)
        tile_size = ctx.get("tile_size", 16)
        rows = ctx.get("map_rows", [])
        canonical_rows = ctx.get("canonical_rows", [])
        display_canonical_indices = ctx.get("display_canonical_indices", [])
        tile_records = ctx.get("tile_records", [])
        object_sprite_count = ctx.get("object_sprite_count", 250)
        blx_name = ctx.get("blx_name", "?")
        map_name = ctx.get("map_name", "?")

        if y < label_h:
            return "Clicked preview label area, not a MAP cell.\n"

        panel = "background render"
        cell_x_px = x
        if x >= rendered_width + gap:
            panel = "diagnostic overlay"
            cell_x_px = x - rendered_width - gap
        elif x >= rendered_width:
            return "Clicked gap between background render and diagnostic overlay.\n"

        col = cell_x_px // tile_size
        display_row = (y - label_h) // tile_size
        in_tile_x = cell_x_px % tile_size
        in_tile_y = (y - label_h) % tile_size

        if not rows or display_row < 0 or display_row >= len(rows) or col < 0 or col >= len(rows[0]):
            return f"Clicked outside MAP cells.\nimage x={x}, y={y}\n"

        raw = rows[display_row][col]
        if display_canonical_indices and 0 <= display_row < len(display_canonical_indices):
            canonical_row = display_canonical_indices[display_row]
        else:
            canonical_row = len(rows) - 1 - display_row if canonical_rows else display_row
        tile_index = map_value_to_tile_index(raw, len(tile_records))
        object_sprite_index = map_value_to_object_sprite_index(raw, object_sprite_count)
        nearby_object_text = self.describe_nearby_object_candidates(col, display_row, rows, object_sprite_count, radius=3)

        out = []
        out.append(f"MAP inspector\n")
        out.append(f"Panel: {panel}\n")
        out.append(f"Map resource: {map_name}\n")
        out.append(f"BLX tileset: {blx_name}\n\n")
        out.append(f"Display cell: col={col}, row={display_row}\n")
        out.append(f"Canonical/storage row: {canonical_row} (display rows are reversed for gameplay preview)\n")
        out.append(f"Pixel in tile: x={in_tile_x}, y={in_tile_y}\n\n")
        out.append(f"Raw MAP value: {raw} / 0x{raw:02X}\n")
        out.append(f"High bit: {'yes' if raw & 0x80 else 'no'}\n")
        out.append(f"Tile count in paired BLX: {len(tile_records)}\n")
        if tile_index is None:
            out.append("Tile index: SPECIAL / OUT OF RANGE / unknown gameplay cell\n")
        else:
            out.append(f"Tile index: {tile_index} (MAP raw is 1-based)\n")
            if 0 <= tile_index < len(tile_records):
                rec = tile_records[tile_index]
                out.append(f"Tile record length: {len(rec)} bytes\n")
                if len(rec) >= 4:
                    h = int.from_bytes(rec[0:2], "little")
                    wb = int.from_bytes(rec[2:4], "little")
                    out.append(f"Tile header: height={h}, widthBytes={wb}, pixelWidth={wb * 8}\n")
                    out.append(f"Tile header bytes: {rec[:8].hex(' ')}\n")

        if object_sprite_index is not None:
            out.append("\nDirect enemy sprite mapping on clicked cell: disabled\n")
            out.append(f"")
            out.append(f"Mapping note: {describe_object_mapping(raw, object_sprite_count)}\n")
        else:
            out.append("\nDirect enemy sprite mapping on clicked cell: disabled\n")

        out.append("\n")
        out.append(nearby_object_text)
        out.append("Use this to report suspicious cells: map resource, display row/col, raw value, tile index.\n")
        return "".join(out)

    def entry_info_text(self, e: ResourceEntry) -> str:
        out = []
        out.append(f"Resource #{e.index}: {e.name}\n")
        out.append(f"Type: {e.ext}\n")
        out.append(f"Size: {e.size} bytes / 0x{e.size:x}\n")
        out.append(f"Start relative to SHADOW overlay: 0x{e.start_rel:x}\n")
        out.append(f"Absolute file offset: 0x{e.start_abs:x}\n")
        out.append(f"Directory raw decoded entry: {e.raw_dir_entry.hex(' ')}\n")
        if e.ext == "BIC":
            try:
                bic = decode_bic(e.data)
                self.current_decoded = bic
                out.append("\nBIC header / decode:\n")
                out.append(f"  byte0 flags/type: 0x{e.data[0]:02x}\n")
                out.append(f"  expected decoded size: {bic.expected_size}\n")
                out.append(f"  byte3 fields/count hint: {bic.fields_or_count_byte}\n")
                out.append(f"  word5 block/item count hint: {bic.block_size}\n")
                out.append(f"  RLE decoded size: {len(bic.decoded)} {'OK' if bic.ok else 'MISMATCH'}\n")
            except Exception as exc:
                out.append(f"\nBIC decode failed: {exc}\n")
        elif e.ext == "ENC":
            out.append("\nENC: full-screen/menu/page resource. Compression/command stream not solved yet.\n")
            if len(e.data) >= 8:
                out.append(f"First bytes: {e.data[:32].hex(' ')}\n")
        out.append("\nHex dump:\n")
        out.append(make_raw_hex(e.data))
        return "".join(out)

    def make_preview(self, e: ResourceEntry) -> Image.Image:
        name = e.name.upper()
        if e.ext == "BIC":
            bic = decode_bic(e.data)
            self.current_decoded = bic
            if name in ("1X1.BIC", "2X2.BIC", "2X2C.BIC"):
                return make_sprite_sheet(bic, name)
            if name == "G0.BIC":
                return make_g0_sheet(bic, scale=4)
            if name == "G3.BIC":
                return make_g3_sheet(bic, scale=4)
            if name in ("G1.BIC", "G2.BIC", "G4.BIC", "G5.BIC"):
                # These decode as transposed 32x32 EGA records: 4-byte per-frame header + 512 bytes bitmap.
                return make_fixed_record_sheet(bic, name, record_size=516, width=32, height=32, skip=4, transposed=True, scale=4, cols=8)
            if re.match(r"LEV\dMAP\.BIC", name):
                # Render with a BLX tileset. Resource numbering is not proven to equal game-level numbering.
                # For now this uses same-number pairing unless DEFAULT_MAP_TO_BLX says otherwise.
                m = re.match(r"LEV(\d)MAP\.BIC", name)
                if m and self.archive:
                    map_lev = int(m.group(1))
                    blx_lev = DEFAULT_MAP_TO_BLX.get(map_lev, map_lev)
                    blx_names = [f"LEV{blx_lev}BLX.BIC", f"LEV{map_lev}BLX.BIC"]
                    for blx_name in blx_names:
                        blx_entry = next((x for x in self.archive.entries if x.name.upper() == blx_name), None)
                        if blx_entry is not None:
                            try:
                                blx_bic = decode_bic(blx_entry.data)
                                tile_records = decode_blx_tile_records(blx_bic)
                                object_sprites = None
                                sprite_entry = next((e for e in self.archive.entries if e.name.upper() == "2X2.BIC"), None)
                                if sprite_entry is not None:
                                    object_sprites = render_2x2_object_sprites(decode_bic(sprite_entry.data))
                                rendered = render_level_from_map_and_tiles(bic, blx_bic, object_sprites=object_sprites, show_objects=True, show_grid=False)
                                overlay = make_map_highbit_overlay(bic, cell=16, sprite_count=len(object_sprites or []), show_grid=True, tile_count=len(tile_records))
                                display_rows = map_rows_for_display_with_indices(bic)
                                self.current_map_context = {
                                    "map_name": name,
                                    "blx_name": blx_name,
                                    "map_rows": [row for _, row in display_rows],
                                    "display_canonical_indices": [idx for idx, _ in display_rows],
                                    "canonical_rows": decode_map_rows(bic),
                                    "tile_records": tile_records,
                                    "object_sprite_count": len(object_sprites or []),
                                    "metadata_row_skipped": bool(decode_map_rows(bic) and is_map_metadata_row(decode_map_rows(bic)[0])),
                                    "rendered_width": rendered.width,
                                    "label_h": 18,
                                    "gap": 12,
                                    "tile_size": 16,
                                }
                                return combine_map_render_and_overlay(rendered, overlay)
                            except Exception:
                                pass
                return make_map_highbit_overlay(bic, cell=16)
            if re.match(r"LEV\dBLX\.BIC", name):
                # Pass12: LEVxBLX decodes as four plane-grouped blocks; each tile uses 4 × (1 header + 32 plane bytes).
                return make_tile_record_sheet(bic, name)
            if name == "BLUEBITS.BIC":
                return make_bluebits_diagnostic(bic, e.data, scale=3)
            if e.data and e.data[0] == 3:
                img = render_bic_type3_image(bic, e.data)
                if img:
                    return img
            if name == "LOGO.BIC":
                return make_logo_solved_preview(e.data, self.archive)
            if name == "SHIP.BIC":
                return make_ship_sheet(bic, scale=4)
            if name == "MANEXPL.BIC":
                return make_manexpl_sheet(bic, scale=3)
            if name == "THEND.BIC":
                img = make_thend_image(bic)
                if img:
                    return img
            # fallback probes for other BICs
            return make_blx_probe(bic, name)
        if name in ("ADLIB.ENC", "ROLAND.ENC"):
            return self.make_message_image(f"{e.name}\n\nLikely audio/music data, not graphics.\nKept in the browser for archive completeness.")
        if e.ext == "ENC":
            return self.make_enc_probe(e.data, e.name)
        return self.make_message_image(f"Raw resource\n{e.name}\n{e.size} bytes")

    def make_enc_probe(self, data: bytes, name: str) -> Image.Image:
        # ENC is still unsolved, but show several direct guesses for fast visual inspection.
        imgs = []
        for off in (0, 4, 8, 16, 32):
            raw = data[off:]
            img = render_planar_4bpp(raw, 320, min(200, len(raw) // 160), row_interleaved=True)
            if img:
                imgs.append((f"planar row 320x? off {off}", img))
            img = render_nibbles(raw, 320, min(200, (len(raw) * 2) // 320), high_first=True)
            if img:
                imgs.append((f"nibble hi 320x? off {off}", img))
        if not imgs:
            return self.make_message_image(f"ENC probe unavailable\n{name}")
        return self.contact_sheet(imgs[:8])

    def contact_sheet(self, labelled_images: list[tuple[str, Image.Image]]) -> Image.Image:
        cell_w, cell_h = 430, 260
        cols = 2
        rows = math.ceil(len(labelled_images) / cols)
        sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (28, 28, 28))
        draw = ImageDraw.Draw(sheet)
        for i, (label, img) in enumerate(labelled_images):
            x = (i % cols) * cell_w
            y = (i // cols) * cell_h
            draw.text((x + 6, y + 4), label, fill=(240, 240, 240))
            factor = min((cell_w - 12) / img.width, (cell_h - 28) / img.height)
            resized = img.resize((max(1, int(img.width * factor)), max(1, int(img.height * factor))), Image.Resampling.NEAREST if factor >= 1 else Image.Resampling.BOX)
            sheet.paste(resized, (x + 6, y + 24))
        return sheet

    def make_message_image(self, text: str) -> Image.Image:
        img = Image.new("RGB", (760, 420), (32, 32, 32))
        draw = ImageDraw.Draw(img)
        draw.multiline_text((20, 20), text, fill=(235, 235, 235), spacing=6)
        return img

    def extract_resources(self):
        if not self.archive:
            return
        out = self.project_dir / "resources_extracted"
        self.archive.extract_all(out)
        (out / "shadow_directory.json").write_text(json.dumps(self.archive.directory_json(), indent=2), encoding="utf-8")
        messagebox.showinfo("Extracted", f"Resources written to:\n{out}")

    def save_preview(self):
        e = self.current_entry
        if not e:
            return
        suggested = re.sub(r"[^A-Za-z0-9_.-]+", "_", e.name) + ".png"
        path = filedialog.asksaveasfilename(initialdir=str(self.project_dir), initialfile=suggested, defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        try:
            self.preview.save_current(Path(path))
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def make_notes(self) -> str:
        return """Current reverse-engineering status bundled in this browser

Confirmed:
- game_data/OVERKILL contains a SHADOW resource archive after the executable part.
- SHADOW directory has 58 resources and a rolling XOR-encrypted directory.
- .BIC resources use PackBits-style RLE after a 7-byte header.
- 1X1.BIC, 2X2.BIC and 2X2C.BIC are transposed sprite sheets and are now mostly readable.
- G1.BIC, G2.BIC, G4.BIC and G5.BIC are transposed 32x32 frame sheets.
- LEVxMAP.BIC decodes to 3744 bytes = 13 x 288 tile/object indices. This matches the 208px gameplay width: 13 tiles * 16px.
- LEVxBLX.BIC is now decoded as four plane-grouped blocks. Each tile has four 33-byte plane records; the first byte is skipped and the next 32 bytes are a 16x16 1bpp plane.

Still unresolved / experimental:
- LEVxMAP.BIC tile indices are rendered as 1-based indices into LEVxBLX: map value 1 = BLX tile 0. This removes the old stripe/noise background. Palette/flags still need cleanup.
- G0.BIC and G3.BIC are not normal G1/G2/G4/G5 32x32 frame sheets.
- SHIP.BIC is decoded but likely has a different record layout.
- .ENC pages are not solved yet; ADLIB.ENC and ROLAND.ENC are probably audio/music-related, not graphics.

Useful filters:
- type BIC to show compressed graphics/resources
- type MAP for level maps
- type BLX for level block graphics
- type 2X2 for large sprite sheets / upgrades / enemies
- type G1/G2/G4/G5 for 32x32 animation sheets
- type ENC for menus/full-screen encoded pages
"""



def find_project_root() -> Path:
    """Return project root whether run from source tree or package module."""
    here = Path(__file__).resolve()
    for candidate in [Path.cwd(), here.parents[2], here.parent]:
        if (candidate / "game_data" / "OVERKILL").exists():
            return candidate
    return here.parents[2]


def main():
    app = OverkillBrowserApp(find_project_root())
    app.mainloop()


if __name__ == "__main__":
    main()
