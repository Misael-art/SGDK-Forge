from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
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
        raise ValueError("sff header ausente")
    if raw[:12] != MAGIC:
        raise ValueError("assinatura sff inválida")

    ver = raw[12:16]
    verhi = int(ver[3])
    verlo = int(ver[2])
    verlo2 = int(ver[1])
    verlo3 = int(ver[0])
    groups, images, first_offset, subheader_size = struct.unpack_from("<IIII", raw, 16)
    palette_type = int(raw[32])
    return SffV1Header(
        version=(verhi, verlo, verlo2, verlo3),
        groups=int(groups),
        images=int(images),
        first_offset=int(first_offset),
        subheader_size=int(subheader_size),
        palette_type=palette_type,
    )


def iter_sff_v1_entries(path: Path) -> Iterator[SffV1Entry]:
    raw = Path(path).read_bytes()
    header = read_sff_v1_header(path)
    if header.subheader_size != SUBHEADER_SIZE:
        raise ValueError("subheader_size inesperado")

    offset = header.first_offset
    for _ in range(header.images):
        if offset <= 0 or (offset + SUBHEADER_SIZE) > len(raw):
            raise ValueError("offset de subfile inválido")

        next_offset, data_len = struct.unpack_from("<II", raw, offset + 0)
        axis_x, axis_y, group, index, linked_index = struct.unpack_from("<hhHHH", raw, offset + 8)
        same_palette = int(raw[offset + 18])
        data_offset = offset + SUBHEADER_SIZE
        yield SffV1Entry(
            next_offset=int(next_offset),
            data_len=int(data_len),
            axis_x=int(axis_x),
            axis_y=int(axis_y),
            group=int(group),
            index=int(index),
            linked_index=int(linked_index),
            same_palette_as_previous=same_palette,
            data_offset=int(data_offset),
        )
        offset = int(next_offset) if int(next_offset) != 0 else 0


def extract_sff_v1_pcx(path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = Path(path).read_bytes()
    header = read_sff_v1_header(path)
    entries = list(iter_sff_v1_entries(path))

    meta: list[dict[str, int]] = []
    for seq, entry in enumerate(entries):
        payload: bytes
        if entry.data_len == 0 and entry.linked_index > 0 and entry.linked_index < len(entries):
            source = entries[entry.linked_index]
            payload = raw[source.data_offset : source.data_offset + source.data_len]
        else:
            payload = raw[entry.data_offset : entry.data_offset + entry.data_len]

        pcx_path = out_dir / f"{entry.group}_{entry.index}.pcx"
        pcx_path.write_bytes(payload)
        meta.append(
            {
                "seq": int(seq),
                "group": int(entry.group),
                "index": int(entry.index),
                "axis_x": int(entry.axis_x),
                "axis_y": int(entry.axis_y),
                "linked_index": int(entry.linked_index),
                "data_len": int(entry.data_len),
                "palette_type": int(header.palette_type),
                "same_palette_as_previous": int(entry.same_palette_as_previous),
            }
        )

    meta_path = out_dir.parent / "meta" / "sprites.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps({"header": header.__dict__, "sprites": meta}, indent=2), encoding="utf-8")
    return meta_path

