# MUGEN SFF Showdown (SFFv1.01) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** extrair `showdown.sff` (SFF v1.01) + `showdown.def`, reconstruir as camadas/frames, otimizar tiles 8×8 (dedup + H/V flip + paleta por tile), exportar BINs SGDK e provar em ROM rodando no BlastEm.

**Architecture:** pipeline Python gera artefatos determinísticos (PCX/PNG/relatórios/BINs). Um viewer SGDK mínimo carrega BINs (tiles/tilemaps/paletas) e renderiza Plane B/A com a animação BG2, validando com evidência BlastEm.

**Tech Stack:** Python 3 + Pillow (PIL), SGDK 2.11 + rescomp, PowerShell wrapper (`capture_blastem_evidence.ps1`).

---

## Estrutura (arquivos/dirs)

**Treino**
- Base: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/`
- Inputs: `rascunho/inputs/` + `rascunho/inputs_manifest.json`
- Work intermediário: `work/`
- Relatórios: `analysis/`
- Viewer: `sgdk_viewer/showdown_viewer/`

**Código Python (criar)**
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/__init__.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/sff_v1.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/def_stage.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/pipeline/run_showdown_pipeline.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/__init__.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/tile_codec.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/tile_dedup.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/palette_plan.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/sgdk_export/export_showdown_bins.py`

**Testes (criar)**
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_sff_v1.py`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_def_stage.py`

**Viewer SGDK (criar por cópia do modelo)**
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/sgdk_viewer/showdown_viewer/` (cópia do `tools/sgdk_wrapper/modelo/`)
- Modificar:
  - `.../res/resources.res`
  - `.../src/scenes/scene_demo.c`
  - `.../inc/scenes/scene_demo.h` (se necessário para hooks)

---

### Task 1: Preparar base do tooling Python

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/__init__.py`
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/__init__.py`
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/__init__.py`

- [ ] **Step 1: Criar os `__init__.py` vazios**

Conteúdo (mesmo para os 3 arquivos):

```python
```

- [ ] **Step 2: Validar dependência Pillow disponível**

Run:

```powershell
python -c "import PIL; print(PIL.__version__)"
```

Expected: imprime uma versão (ex.: `10.4.0`).

---

### Task 2: Implementar parser/extrator SFF v1.01 (ElecbyteSpr)

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/sff_v1.py`
- Test: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_sff_v1.py`

- [ ] **Step 1: Escrever teste que falha (unittest)**

```python
import unittest
from pathlib import Path

from mugen_sff.sff_v1 import read_sff_v1_header, iter_sff_v1_entries


class TestSffV1(unittest.TestCase):
    def test_showdown_header(self) -> None:
        sff = Path(__file__).resolve().parents[2] / "rascunho" / "inputs" / "showdown.sff"
        header = read_sff_v1_header(sff)
        self.assertEqual(header.version, (1, 0, 1, 0))
        self.assertEqual(header.groups, 4)
        self.assertEqual(header.images, 6)
        self.assertEqual(header.first_offset, 512)
        self.assertEqual(header.subheader_size, 32)

    def test_showdown_entries_count(self) -> None:
        sff = Path(__file__).resolve().parents[2] / "rascunho" / "inputs" / "showdown.sff"
        entries = list(iter_sff_v1_entries(sff))
        self.assertEqual(len(entries), 6)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar teste e ver falhar**

Run:

```powershell
python -m unittest SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_sff_v1.py -v
```

Expected: FAIL com `ModuleNotFoundError` ou `ImportError`.

- [ ] **Step 3: Implementar `sff_v1.py` mínimo para passar**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Iterator


@dataclass(frozen=True)
class SffV1Header:
    version: tuple[int, int, int, int]
    groups: int
    images: int
    first_offset: int
    subheader_size: int
    palette_type: int


@dataclass(frozen=True)
class SffV1Entry:
    next_offset: int
    data_len: int
    axis_x: int
    axis_y: int
    group: int
    index: int
    linked_index: int
    same_palette_as_previous: int
    data_offset: int


MAGIC = b"ElecbyteSpr\x00"
HEADER_SIZE = 512
SUBHEADER_SIZE = 32


def read_sff_v1_header(path: Path) -> SffV1Header:
    raw = Path(path).read_bytes()
    if len(raw) < HEADER_SIZE:
        raise ValueError("SFF muito pequeno para conter header v1")
    if raw[:12] != MAGIC:
        raise ValueError("assinatura ElecbyteSpr inválida")

    ver = raw[12:16]
    verhi = ver[3]
    verlo = ver[2]
    verlo2 = ver[1]
    verlo3 = ver[0]
    groups, images, first_offset, subheader_size = struct.unpack_from("<IIII", raw, 16)
    palette_type = raw[32]
    return SffV1Header(
        version=(verhi, verlo, verlo2, verlo3),
        groups=groups,
        images=images,
        first_offset=first_offset,
        subheader_size=subheader_size,
        palette_type=palette_type,
    )


def iter_sff_v1_entries(path: Path) -> Iterator[SffV1Entry]:
    raw = Path(path).read_bytes()
    header = read_sff_v1_header(path)
    if header.subheader_size != SUBHEADER_SIZE:
        raise ValueError(f"subheader_size inesperado: {header.subheader_size}")

    offset = header.first_offset
    for _ in range(header.images):
        if offset <= 0 or (offset + SUBHEADER_SIZE) > len(raw):
            raise ValueError("offset de subfile inválido")

        next_offset, data_len = struct.unpack_from("<II", raw, offset + 0)
        axis_x, axis_y, group, index, linked_index = struct.unpack_from("<hhHHH", raw, offset + 8)
        same_palette = raw[offset + 18]
        data_offset = offset + SUBHEADER_SIZE
        yield SffV1Entry(
            next_offset=next_offset,
            data_len=data_len,
            axis_x=axis_x,
            axis_y=axis_y,
            group=group,
            index=index,
            linked_index=linked_index,
            same_palette_as_previous=same_palette,
            data_offset=data_offset,
        )
        offset = next_offset if next_offset != 0 else 0


def extract_sff_v1_pcx(path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = Path(path).read_bytes()
    header = read_sff_v1_header(path)
    entries = list(iter_sff_v1_entries(path))

    meta: list[dict[str, int]] = []
    for i, entry in enumerate(entries):
        if entry.data_len == 0 and entry.linked_index > 0:
            source = entries[entry.linked_index]
            payload = raw[source.data_offset : source.data_offset + source.data_len]
        else:
            payload = raw[entry.data_offset : entry.data_offset + entry.data_len]

        pcx_name = f"{entry.group}_{entry.index}.pcx"
        pcx_path = out_dir / pcx_name
        pcx_path.write_bytes(payload)
        meta.append(
            {
                "seq": i,
                "group": entry.group,
                "index": entry.index,
                "axis_x": entry.axis_x,
                "axis_y": entry.axis_y,
                "linked_index": entry.linked_index,
                "data_len": entry.data_len,
                "palette_type": header.palette_type,
                "same_palette_as_previous": entry.same_palette_as_previous,
            }
        )

    meta_path = out_dir.parent / "meta" / "sprites.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(__import__("json").dumps({"header": header.__dict__, "sprites": meta}, indent=2), encoding="utf-8")
    return meta_path
```

- [ ] **Step 4: Rodar testes novamente**

Run:

```powershell
python -m unittest SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_sff_v1.py -v
```

Expected: PASS.

---

### Task 3: Implementar parser do `showdown.def` (BG + actions)

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/mugen_sff/def_stage.py`
- Test: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_def_stage.py`

- [ ] **Step 1: Escrever teste que falha**

```python
import unittest
from pathlib import Path

from mugen_sff.def_stage import parse_stage_def


class TestStageDef(unittest.TestCase):
    def test_showdown_layers_and_action(self) -> None:
        root = Path(__file__).resolve().parents[2]
        stage_def = root / "rascunho" / "inputs" / "showdown.def"
        stage = parse_stage_def(stage_def)
        self.assertEqual(len(stage.bgs), 4)
        self.assertIn(2, stage.actions)
        self.assertEqual(len(stage.actions[2]), 4)
        self.assertEqual(stage.actions[2][0].group, 2)
        self.assertEqual(stage.actions[2][0].index, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar e ver falhar**

Run:

```powershell
python -m unittest SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_def_stage.py -v
```

Expected: FAIL (module ausente).

- [ ] **Step 3: Implementar `def_stage.py` mínimo**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict


@dataclass(frozen=True)
class BgDef:
    id: int
    kind: str
    sprite_group: int | None
    sprite_index: int | None
    actionno: int | None
    mask: int


@dataclass(frozen=True)
class ActionFrame:
    group: int
    index: int
    offset_x: int
    offset_y: int
    time: int


@dataclass(frozen=True)
class StageDef:
    bgs: list[BgDef]
    actions: dict[int, list[ActionFrame]]


def _parse_key_value(line: str) -> tuple[str, str] | None:
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    return key.strip().lower(), value.strip()


def parse_stage_def(path: Path) -> StageDef:
    text = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    section = None
    current_bg_id: int | None = None
    bgs: list[BgDef] = []
    actions: DefaultDict[int, list[ActionFrame]] = __import__("collections").defaultdict(list)

    bg_accum: dict[str, str] = {}
    for raw in text:
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            if section and section.startswith("bg ") and current_bg_id is not None:
                kind = bg_accum.get("type", "normal").lower()
                spr = bg_accum.get("spriteno")
                actionno = bg_accum.get("actionno")
                mask = int(bg_accum.get("mask", "0"))
                sprite_group = None
                sprite_index = None
                if spr:
                    parts = [p.strip() for p in spr.split(",")]
                    if len(parts) == 2:
                        sprite_group = int(parts[0])
                        sprite_index = int(parts[1])
                bgs.append(
                    BgDef(
                        id=current_bg_id,
                        kind=kind,
                        sprite_group=sprite_group,
                        sprite_index=sprite_index,
                        actionno=int(actionno) if actionno else None,
                        mask=mask,
                    )
                )
            bg_accum = {}
            section = line[1:-1].strip().lower()
            if section.startswith("bg "):
                current_bg_id = int(section.split(" ", 1)[1])
            else:
                current_bg_id = None
            continue

        if section and section.startswith("begin action"):
            action_id = int(section.split(" ", 2)[2])
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                actions[action_id].append(
                    ActionFrame(
                        group=int(parts[0]),
                        index=int(parts[1]),
                        offset_x=int(parts[2]),
                        offset_y=int(parts[3]),
                        time=int(parts[4]),
                    )
                )
            continue

        parsed = _parse_key_value(line)
        if parsed and section and section.startswith("bg "):
            key, value = parsed
            bg_accum[key] = value

    if section and section.startswith("bg ") and current_bg_id is not None:
        kind = bg_accum.get("type", "normal").lower()
        spr = bg_accum.get("spriteno")
        actionno = bg_accum.get("actionno")
        mask = int(bg_accum.get("mask", "0"))
        sprite_group = None
        sprite_index = None
        if spr:
            parts = [p.strip() for p in spr.split(",")]
            if len(parts) == 2:
                sprite_group = int(parts[0])
                sprite_index = int(parts[1])
        bgs.append(
            BgDef(
                id=current_bg_id,
                kind=kind,
                sprite_group=sprite_group,
                sprite_index=sprite_index,
                actionno=int(actionno) if actionno else None,
                mask=mask,
            )
        )

    return StageDef(bgs=bgs, actions=dict(actions))
```

- [ ] **Step 4: Rodar testes**

Run:

```powershell
python -m unittest SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/tests/test_def_stage.py -v
```

Expected: PASS.

---

### Task 4: Orquestrar extração + reconstrução em frames PNG

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/pipeline/run_showdown_pipeline.py`

- [ ] **Step 1: Implementar pipeline até reconstrução**

```python
from __future__ import annotations

from pathlib import Path
import json

from PIL import Image

from mugen_sff.sff_v1 import extract_sff_v1_pcx
from mugen_sff.def_stage import parse_stage_def


TARGET_W = 320
TARGET_H = 224
SOURCE_H = 240
SOURCE_CROP_TOP = SOURCE_H - TARGET_H


def load_pcx(sprite_dir: Path, group: int, index: int) -> Image.Image:
    path = sprite_dir / f"{group}_{index}.pcx"
    with Image.open(path) as img:
        return img.convert("RGBA")


def composite_frame(stage, sprite_dir: Path, bg2_frame: tuple[int, int] | None) -> Image.Image:
    layers = []
    for bg in stage.bgs:
        if bg.kind == "anim":
            if bg2_frame is None:
                continue
            g, i = bg2_frame
            layers.append(load_pcx(sprite_dir, g, i))
        else:
            if bg.sprite_group is None or bg.sprite_index is None:
                continue
            layers.append(load_pcx(sprite_dir, bg.sprite_group, bg.sprite_index))

    base = Image.new("RGBA", layers[0].size, (0, 0, 0, 0))
    for layer in layers:
        base = Image.alpha_composite(base, layer)

    w, h = base.size
    crop_top = max(0, min(h, SOURCE_CROP_TOP))
    base = base.crop((0, crop_top, min(w, TARGET_W), crop_top + TARGET_H))
    if base.size != (TARGET_W, TARGET_H):
        base = base.resize((TARGET_W, TARGET_H), Image.Resampling.NEAREST)
    return base


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    sff_path = root / "rascunho" / "inputs" / "showdown.sff"
    def_path = root / "rascunho" / "inputs" / "showdown.def"

    extracted_dir = root / "work" / "extracted_pcx"
    extract_sff_v1_pcx(sff_path, extracted_dir)

    stage = parse_stage_def(def_path)
    frames_dir = root / "work" / "reconstructed_layers"
    frames_dir.mkdir(parents=True, exist_ok=True)

    action = stage.actions.get(2, [])
    bg2_frames = [(f.group, f.index) for f in action] if action else [None]

    written = []
    for idx, bg2 in enumerate(bg2_frames):
        frame = composite_frame(stage, extracted_dir, bg2)
        out = frames_dir / f"frame_{idx:04d}.png"
        frame.save(out)
        written.append(str(out))

    report = {"frames": written, "target": {"w": TARGET_W, "h": TARGET_H}, "crop_top": SOURCE_CROP_TOP}
    (root / "analysis").mkdir(parents=True, exist_ok=True)
    (root / "analysis" / "reconstruction.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Executar pipeline e verificar frames gerados**

Run:

```powershell
python SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/pipeline/run_showdown_pipeline.py
```

Expected:
- `work/extracted_pcx/*.pcx` existe
- `work/reconstructed_layers/frame_0000.png ... frame_0003.png` existe
- `analysis/reconstruction.json` existe

---

### Task 5: Implementar dedup + flips + planejamento de sub-paletas por tile

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/palette_plan.py`
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/tile_dedup.py`

- [ ] **Step 1: Implementar `palette_plan.py` (greedy 4×16 por tile)**

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PalettePlanResult:
    tile_palette_id: list[int]
    palettes: list[list[int]]
    violations: list[dict[str, int]]


def plan_4palettes_for_tiles(tile_color_sets: list[set[int]]) -> PalettePlanResult:
    palettes: list[set[int]] = [set() for _ in range(4)]
    tile_palette_id: list[int] = []
    violations: list[dict[str, int]] = []

    for tile_index, colors in enumerate(tile_color_sets):
        if len(colors) > 16:
            violations.append({"tile_index": tile_index, "reason": 1, "color_count": len(colors)})
            tile_palette_id.append(0)
            continue

        placed = False
        for pid in range(4):
            merged = palettes[pid] | colors
            if len(merged) <= 16:
                palettes[pid] = merged
                tile_palette_id.append(pid)
                placed = True
                break

        if not placed:
            violations.append({"tile_index": tile_index, "reason": 2, "color_count": len(colors)})
            tile_palette_id.append(0)

    ordered_palettes = [sorted(p) for p in palettes]
    return PalettePlanResult(tile_palette_id=tile_palette_id, palettes=ordered_palettes, violations=violations)
```

- [ ] **Step 2: Implementar `tile_dedup.py` (dedup + H/V flip + geração de tilemap words)**

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class TileMatch:
    tile_index: int
    hflip: int
    vflip: int


def _hflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        out[y * 8 : (y + 1) * 8] = row[::-1]
    return bytes(out)


def _vflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[(7 - y) * 8 : (8 - y) * 8]
        out[y * 8 : (y + 1) * 8] = row
    return bytes(out)


def _hvflip(tile: bytes) -> bytes:
    return _hflip(_vflip(tile))


def dedup_tiles_with_flips(tiles: list[bytes]) -> tuple[list[bytes], list[TileMatch]]:
    dictionary: Dict[bytes, TileMatch] = {}
    unique: list[bytes] = []
    matches: list[TileMatch] = []

    for t in tiles:
        variants: list[Tuple[bytes, int, int]] = [
            (t, 0, 0),
            (_hflip(t), 1, 0),
            (_vflip(t), 0, 1),
            (_hvflip(t), 1, 1),
        ]
        found: TileMatch | None = None
        for data, h, v in variants:
            if data in dictionary:
                base = dictionary[data]
                found = TileMatch(tile_index=base.tile_index, hflip=h, vflip=v)
                break

        if found is None:
            index = len(unique)
            unique.append(t)
            dictionary[t] = TileMatch(tile_index=index, hflip=0, vflip=0)
            found = TileMatch(tile_index=index, hflip=0, vflip=0)

        matches.append(found)

    return unique, matches


def build_vdp_tile_word(tile_index: int, palette_id: int, priority: int, hflip: int, vflip: int) -> int:
    value = tile_index & 0x7FF
    if hflip:
        value |= 1 << 11
    if vflip:
        value |= 1 << 12
    value |= (palette_id & 0x3) << 13
    if priority:
        value |= 1 << 15
    return value
```

---

### Task 6: Exportar BINs (tiles 4bpp + tilemaps + paletas) para o viewer SGDK

**Files:**
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/vdp_tiles/tile_codec.py`
- Create: `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/sgdk_export/export_showdown_bins.py`

- [ ] **Step 1: Implementar codec de tile 4bpp (8×8 → 32 bytes)**

```python
from __future__ import annotations


def tile_8x8_indices_to_md4bpp(tile: bytes) -> bytes:
    if len(tile) != 64:
        raise ValueError("tile deve ter 64 bytes (8×8 índices)")
    out = bytearray(32)
    dst = 0
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        for x in range(0, 8, 2):
            a = row[x] & 0x0F
            b = row[x + 1] & 0x0F
            out[dst] = (a << 4) | b
            dst += 1
    return bytes(out)
```

- [ ] **Step 2: Implementar exportador (frames → tiles/tilemaps/paletas)**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from PIL import Image

from vdp_tiles.palette_plan import plan_4palettes_for_tiles
from vdp_tiles.tile_codec import tile_8x8_indices_to_md4bpp
from vdp_tiles.tile_dedup import dedup_tiles_with_flips, build_vdp_tile_word


TARGET_W = 320
TARGET_H = 224
TILES_W = TARGET_W // 8
TILES_H = TARGET_H // 8


def _quantize_master(image: Image.Image, colors: int = 64) -> Image.Image:
    rgba = image.convert("RGBA")
    p = rgba.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return p.convert("P")


def _extract_tile_indices(pimg: Image.Image, left: int, top: int) -> bytes:
    px = pimg.load()
    out = bytearray(64)
    k = 0
    for y in range(8):
        for x in range(8):
            out[k] = int(px[left + x, top + y])
            k += 1
    return bytes(out)


def _tile_color_set(tile: bytes) -> set[int]:
    return set(tile)


def _palette_from_pimg(pimg: Image.Image, colors: list[int]) -> list[int]:
    pal = pimg.getpalette() or []
    out: list[int] = []
    for idx in colors:
        base = idx * 3
        if base + 2 >= len(pal):
            r, g, b = 0, 0, 0
        else:
            r, g, b = pal[base], pal[base + 1], pal[base + 2]
        rr = (r >> 5) & 0x7
        gg = (g >> 5) & 0x7
        bb = (b >> 5) & 0x7
        out.append((bb << 9) | (gg << 5) | (rr << 1))
    while len(out) < 16:
        out.append(0)
    return out[:16]


def export_showdown_bins(frames_dir: Path, out_root: Path) -> dict:
    frames = sorted(frames_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError("nenhum frame_*.png encontrado")

    out_root.mkdir(parents=True, exist_ok=True)
    all_unique_tiles_md: list[bytes] = []
    frame_maps: list[list[int]] = []
    frame_meta: list[dict] = []

    for frame_index, frame_path in enumerate(frames):
        with Image.open(frame_path) as src:
            pimg = _quantize_master(src, colors=64)
        tiles: list[bytes] = []
        tile_sets: list[set[int]] = []
        for ty in range(TILES_H):
            for tx in range(TILES_W):
                t = _extract_tile_indices(pimg, tx * 8, ty * 8)
                tiles.append(t)
                tile_sets.append(_tile_color_set(t))

        plan = plan_4palettes_for_tiles(tile_sets)

        priority = 0
        unique_tiles, matches = dedup_tiles_with_flips(tiles)

        base_index = len(all_unique_tiles_md)
        for ut in unique_tiles:
            all_unique_tiles_md.append(tile_8x8_indices_to_md4bpp(ut))

        tile_words: list[int] = []
        for tile_idx, match in enumerate(matches):
            palette_id = plan.tile_palette_id[tile_idx]
            word = build_vdp_tile_word(
                tile_index=base_index + match.tile_index,
                palette_id=palette_id,
                priority=priority,
                hflip=match.hflip,
                vflip=match.vflip,
            )
            tile_words.append(word)

        frame_maps.append(tile_words)
        frame_meta.append(
            {
                "frame": frame_index,
                "path": str(frame_path),
                "unique_tiles": len(unique_tiles),
                "violations": plan.violations,
                "palettes": plan.palettes,
            }
        )

    tiles_bin = out_root / "showdown_tiles_4bpp.bin"
    tiles_bin.write_bytes(b"".join(all_unique_tiles_md))

    maps_bin = out_root / "showdown_maps_u16.bin"
    maps_bytes = bytearray()
    for tile_words in frame_maps:
        for w in tile_words:
            maps_bytes.extend(int(w).to_bytes(2, "little"))
    maps_bin.write_bytes(bytes(maps_bytes))

    meta_path = out_root / "showdown_export_meta.json"
    meta = {
        "tiles_bin": str(tiles_bin),
        "maps_bin": str(maps_bin),
        "frames": len(frame_maps),
        "tiles_w": TILES_W,
        "tiles_h": TILES_H,
        "frame_meta": frame_meta,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    frames_dir = root / "work" / "reconstructed_layers"
    out_dir = root / "work" / "sgdk_bins"
    export_showdown_bins(frames_dir, out_dir)
    (root / "analysis").mkdir(parents=True, exist_ok=True)
    (root / "analysis" / "tile_stats.json").write_text((out_dir / "showdown_export_meta.json").read_text(encoding="utf-8"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Executar export e verificar BINs**

Run:

```powershell
python SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/tools/sgdk_export/export_showdown_bins.py
```

Expected:
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/work/sgdk_bins/showdown_tiles_4bpp.bin`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/work/sgdk_bins/showdown_maps_u16.bin`
- `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/analysis/tile_stats.json`

---

### Task 7: Criar viewer SGDK e integrar BINs via rescomp

**Files:**
- Create (by copy): `SGDK_projects/_agent_training/[ESTUDO]_mugen_sff_showdown_v1/sgdk_viewer/showdown_viewer/**`
- Modify: `.../res/resources.res`
- Modify: `.../src/scenes/scene_demo.c`

- [ ] **Step 1: Copiar o template canônico do wrapper**

Run:

```powershell
$src = "F:\Projects\Sgdk Forge\tools\sgdk_wrapper\modelo"
$dst = "F:\Projects\Sgdk Forge\SGDK_projects\_agent_training\[ESTUDO]_mugen_sff_showdown_v1\sgdk_viewer\showdown_viewer"
Copy-Item -Recurse -Force -LiteralPath $src -Destination $dst
```

Expected: diretório `$dst` criado com `build.bat`, `src/`, `res/`, `inc/`.

- [ ] **Step 2: Copiar BINs gerados para dentro do viewer**

Run:

```powershell
$viewer = "F:\Projects\Sgdk Forge\SGDK_projects\_agent_training\[ESTUDO]_mugen_sff_showdown_v1\sgdk_viewer\showdown_viewer"
$bins = "F:\Projects\Sgdk Forge\SGDK_projects\_agent_training\[ESTUDO]_mugen_sff_showdown_v1\work\sgdk_bins"
New-Item -ItemType Directory -Force -Path "$viewer\res\data\showdown" | Out-Null
Copy-Item -Force -LiteralPath "$bins\showdown_tiles_4bpp.bin" -Destination "$viewer\res\data\showdown\showdown_tiles_4bpp.bin"
Copy-Item -Force -LiteralPath "$bins\showdown_maps_u16.bin" -Destination "$viewer\res\data\showdown\showdown_maps_u16.bin"
```

Expected: arquivos `.bin` presentes em `res/data/showdown/`.

- [ ] **Step 3: Escrever `resources.res` mínimo com BIN**

Set content of `.../res/resources.res` para:

```text
BIN bin_showdown_tiles "data/showdown/showdown_tiles_4bpp.bin" 2 2 0 NONE FALSE
BIN bin_showdown_maps "data/showdown/showdown_maps_u16.bin" 2 2 0 NONE FALSE
```

- [ ] **Step 4: Modificar `scene_demo.c` para renderizar o tilemap e animar BG2**

Objetivo mínimo do código:
- Carregar tiles em `TILE_USER_INDEX`
- Aplicar tilemap no `BG_A`
- Alternar frame do tilemap a cada ~16 frames de VBlank

Substituir o corpo do `scene_demo.c` por uma implementação mínima (mantendo includes existentes do projeto):

```c
#include <genesis.h>

#include "resources.h"

static const u16 kTilesW = 40;
static const u16 kTilesH = 28;
static const u16 kFrames = 4;

static u16 frameIndex = 0;
static u16 tick = 0;

static const u16* getFrameMap(const u16* maps, u16 frame)
{
    return maps + (frame * kTilesW * kTilesH);
}

void scene_demo_init(void)
{
    VDP_setTextPlane(WINDOW);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    const u16 tileCount = (u16)(bin_showdown_tiles_size / 32);
    VDP_loadTileData((const u32*)bin_showdown_tiles, TILE_USER_INDEX, tileCount, DMA);

    const u16* maps = (const u16*)bin_showdown_maps;
    const u16* map0 = getFrameMap(maps, 0);
    VDP_setTileMapDataRect(BG_A, map0, 0, 0, kTilesW, kTilesH, kTilesW, DMA);
}

void scene_demo_update(void)
{
    tick++;
    if ((tick & 0x0F) == 0)
    {
        frameIndex = (frameIndex + 1) % kFrames;
        const u16* maps = (const u16*)bin_showdown_maps;
        const u16* map = getFrameMap(maps, frameIndex);
        VDP_setTileMapDataRect(BG_A, map, 0, 0, kTilesW, kTilesH, kTilesW, DMA);
    }
}

void scene_demo_release(void)
{
}
```

- [ ] **Step 5: Build do viewer**

Run:

```powershell
cd "F:\Projects\Sgdk Forge\SGDK_projects\_agent_training\[ESTUDO]_mugen_sff_showdown_v1\sgdk_viewer\showdown_viewer"
.\build.bat
```

Expected:
- `out\rom.bin` existe
- build sem erros

---

### Task 8: Capturar evidência BlastEm (gate do workspace)

**Files:**
- Output: `.../sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`
- Output: `.../sgdk_viewer/showdown_viewer/out/evidence/blastem/*`

- [ ] **Step 1: Rodar captura mínima de evidência**

Run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "F:\Projects\Sgdk Forge\tools\sgdk_wrapper\capture_blastem_evidence.ps1" -ProjectRoot "F:\Projects\Sgdk Forge\SGDK_projects\_agent_training\[ESTUDO]_mugen_sff_showdown_v1\sgdk_viewer\showdown_viewer" -CaptureMode minimal
```

Expected:
- `out\logs\blastem_evidence.json` com `evidence_status = ok` (ou `warn` se WarnOnly usado)
- `out\evidence\blastem\screenshot.png` presente

---

## Self-review (feito ao executar)

- Após Task 4: abrir `work/reconstructed_layers/frame_*.png` e validar coerência visual.
- Após Task 6: checar `analysis/tile_stats.json` por violações de paleta (motivos 1 e 2).
- Após Task 7: se tiles “quebrarem” visualmente, reduzir `colors` de 64→32 e reexportar para estabilizar o plano de 4 paletas.

