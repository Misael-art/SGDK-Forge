"""Reproducible, non-promoting MUGEN stage colour candidate.

The source is composited at a declared camera position; each MUGEN layer's
delta must still be implemented in the final runtime. This tool never claims
that a flattened view is the finished stage or that tile counts equal ResComp.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

from .converters.sprites import vdp_rgb, vdp_word
from .parsers import sff, stage
from .stage_measure import _canon, compose
from .vdp_authoring import png_palette_for_words

PLANES = {
    "back": ("BG 0a", "BG 0b", "BG 1", "BG 2"),
    "front": ("BG 3", "BG 4a", "BG 4b"),
}


def _tiles(data: bytes, width: int, height: int) -> set:
    unique = set()
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            tile = tuple(tuple(data[(y + j) * width + x:(y + j) * width + x + 8]) for j in range(8))
            unique.add(_canon(tile))
    return unique


def _viewport_tiles(data: bytes, width: int, height: int, viewport: int = 320) -> dict:
    """Count resident patterns for every tile-aligned visible camera position."""
    positions = []
    for left in range(0, width - viewport + 1, 8):
        view = b"".join(data[y * width + left:y * width + left + viewport]
                        for y in range(height))
        positions.append({"left": left, "tiles_with_flip": len(_tiles(view, viewport, height))})
    return {"minimum": min(p["tiles_with_flip"] for p in positions),
            "maximum": max(p["tiles_with_flip"] for p in positions),
            "positions": positions}


def _view_width(camera_span: float, delta: float) -> int:
    """Cover the 320 px viewport at both camera bounds, rounded to tile grid."""
    return (320 + round(camera_span * delta) + 7) // 8 * 8


def _rgb(word: int) -> tuple[int, int, int]:
    """Decode CRAM with the converter's authoritative R-G-B ordering and grid."""
    return vdp_rgb(word)


def _palette(source_palette: list, frequency: Counter, fixed_hud: list[int]) -> list[int]:
    """Pick eight stage words that reduce source error alongside seven HUD words.

    This is an offline estimate for candidate selection, not aesthetic approval.
    """
    if len(fixed_hud) != 7:
        raise ValueError("expected the seven owned HUD words 9..15")
    counts = Counter()
    for i, n in frequency.items():
        if i:
            counts[vdp_word(source_palette[i])] += n
    words = list(counts)
    src = np.asarray([_rgb(w) for w in words], dtype=np.int32)
    weights = np.asarray([counts[w] for w in words], dtype=np.int64)
    fixed = np.asarray([_rgb(w) for w in fixed_hud], dtype=np.int32)
    best = np.min(np.sum((src[:, None, :] - fixed[None, :, :]) ** 2, axis=2), axis=1)
    chosen = []
    for _ in range(8):
        winner, gain = None, -1
        for i, word in enumerate(words):
            if word in chosen or word in fixed_hud:
                continue
            err = np.sum((src - src[i]) ** 2, axis=1)
            improvement = int(np.dot(weights, np.maximum(0, best - err)))
            if improvement > gain:
                winner, gain = i, improvement
        if winner is None:
            break
        chosen.append(words[winner])
        best = np.minimum(best, np.sum((src - src[winner]) ** 2, axis=1))
    if len(chosen) != 8:
        raise ValueError("source needs fewer than eight distinct stage words")
    return [0] + chosen + fixed_hud


def _source_planes(source_zip: Path, def_name: str, sff_name: str,
                   crop_top: int) -> tuple[stage.Stage, list, dict[str, tuple[int, bytes]]]:
    with zipfile.ZipFile(source_zip) as z:
        st = stage.parse(z.read(def_name).decode("latin-1"), def_name)
        sprites, warnings = sff.parse(z.read(sff_name))
    if warnings or st.warnings:
        raise ValueError("source warnings require adjudication: " + repr(warnings + st.warnings))
    lookup = {(s.group, s.image): s for s in sprites}
    for name in {n for group in PLANES.values() for n in group}:
        layer = next((la for la in st.layers if la.name == name), None)
        if not layer or not layer.spriteno or tuple(layer.spriteno) not in lookup:
            raise ValueError(f"missing source layer {name}")
    if any(s.palette != sprites[0].palette for s in sprites):
        raise ValueError("source has per-sprite palettes; cannot share index lookup")
    # A declaration for two design views only. Individual deltas are in report;
    # these composite deltas do not preserve their independent scrolling.
    deltas = {"back": 0.43, "front": 0.67}
    planes = {}
    span = st.camera["boundright"] - st.camera["boundleft"]
    for name, layers in PLANES.items():
        width = _view_width(span, deltas[name])
        buf = compose(st, lookup, list(layers), deltas[name], width, crop_top)
        planes[name] = (width, bytes(i for row in buf for i in row))
    return st, sprites[0].palette, planes


def generate(source_zip: Path, out: Path, fixed_hud: list[int], budget_tiles: int,
             def_name: str = "ssf2-01-ryu.def", sff_name: str = "ssf2-01-ryu.sff",
             crop_top: int = 16) -> dict:
    if budget_tiles <= 0:
        raise ValueError("measured resident tile budget must be positive")
    st, pal, planes = _source_planes(source_zip, def_name, sff_name, crop_top)
    frequency = Counter(b"".join(data for _, data in planes.values()))
    words = _palette(pal, frequency, fixed_hud)
    targets = np.asarray([_rgb(w) for w in words], dtype=np.int32)
    lookup = np.zeros(256, dtype=np.uint8)
    for src_index in frequency:
        if src_index:
            colour = np.asarray(_rgb(vdp_word(pal[src_index])), dtype=np.int32)
            distance = np.sum((targets[1:] - colour) ** 2, axis=1)
            lookup[src_index] = int(np.argmin(distance)) + 1
    out.mkdir(parents=True, exist_ok=True)
    per_plane = {}
    common_tiles = set()
    source_tiles = set()
    mapped_planes = {}
    palette_rgb = png_palette_for_words(words)
    for name, (width, data) in planes.items():
        mapped = lookup[np.frombuffer(data, dtype=np.uint8)].tobytes()
        mapped_planes[name] = (width, mapped)
        im = Image.frombytes("P", (width, 224), mapped)
        im.putpalette(palette_rgb)
        im.info["transparency"] = 0
        buffer = io.BytesIO()
        im.save(buffer, format="PNG", bits=4, optimize=False)
        encoded = buffer.getvalue()
        (out / f"{name}_candidate.png").write_bytes(encoded)
        src_tiles = _tiles(data, width, 224)
        dst_tiles = _tiles(mapped, width, 224)
        source_tiles |= src_tiles
        common_tiles |= dst_tiles
        per_plane[name] = {
            "width": width,
            "source_tiles_with_flip": len(src_tiles),
            "candidate_tiles_with_flip": len(dst_tiles),
            "candidate_visible_320": _viewport_tiles(mapped, width, 224),
            "source_indices": len(set(data) - {0}),
            "candidate_indices": len(set(mapped) - {0}),
            "recoloured_visible_pixels": sum(n for idx, n in Counter(data).items()
                                             if idx and vdp_word(pal[idx]) != words[lookup[idx]]),
            "visible_pixels": len(data) - data.count(0),
            "png_sha256": hashlib.sha256(encoded).hexdigest(),
        }
    # A pair of planes can have different parallax offsets. These are same-offset
    # bounds, not a substitute for the full joint camera/DMA residency schedule.
    joint_positions = []
    for camera in range(0, 449, 8):
        joint = set()
        for name, delta in (("back", 0.43), ("front", 0.67)):
            width, data = mapped_planes[name]
            left = min((round(camera * delta) // 8) * 8, width - 320)
            view = b"".join(data[y * width + left:y * width + left + 320] for y in range(224))
            joint |= _tiles(view, 320, 224)
        joint_positions.append({"camera": camera, "tiles_with_flip": len(joint)})
    report = {
        "status": "blocked_budget" if len(common_tiles) > budget_tiles else "technical_candidate_requires_rescomp_and_rom",
        "source_sha256": hashlib.sha256(source_zip.read_bytes()).hexdigest(),
        "source_stage": st.name,
        "source_localcoord": list(st.localcoord),
        "source_camera_bounds": [st.camera["boundleft"], st.camera["boundright"]],
        "source_layers": [
            {"name": la.name, "type": la.type, "delta": list(la.delta),
             "velocity": list(la.velocity), "source_image": list(la.spriteno) if la.spriteno else None}
            for la in st.layers
        ],
        "candidate_view": {"height": 224, "crop_top": crop_top,
                           "composite_deltas": {"back": 0.43, "front": 0.67}},
        "palette_words": [f"0x{w:03X}" for w in words],
        "reserved_hud_words_9_15": [f"0x{w:03X}" for w in fixed_hud],
        "planes": per_plane,
        "source_union_tiles_with_flip": len(source_tiles),
        "candidate_union_tiles_with_flip": len(common_tiles),
        "joint_visible_320": {"minimum": min(x["tiles_with_flip"] for x in joint_positions),
                              "maximum": max(x["tiles_with_flip"] for x in joint_positions),
                              "positions": joint_positions},
        "budget_tiles": budget_tiles,
        "over_budget_by_at_least": max(0, len(common_tiles) - budget_tiles),
        "limits": ["flattened design views, independent layer deltas pending",
                   "tile counts are source-pattern estimates, not ResComp or resident-set cost",
                   "PAL0 colour union is a candidate; scene in ROM not observed"],
    }
    (out / "candidate_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
