"""Read actual SpriteDefinition limits from the current SGDK ROM and map file."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def audit(root: Path) -> dict:
    rom_path, symbols_path = root / "out/rom.bin", root / "out/symbol.txt"
    if not rom_path.is_file() or not symbols_path.is_file():
        return {"status": "unavailable", "reason": "current_rom_or_symbol_map_missing", "sprites": {}}
    rom_ns = rom_path.stat().st_mtime_ns
    rom = rom_path.read_bytes()
    stale = []
    if symbols_path.stat().st_mtime_ns > rom_ns:
        stale.append(symbols_path.relative_to(root).as_posix())
    symbols = {}
    for line in symbols_path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if len(fields) == 3:
            try:
                symbols[fields[2]] = int(fields[0], 16)
            except ValueError:
                pass
    rows = {}
    for res in sorted((root / "res").glob("*.res")):
        if res.stat().st_mtime_ns > rom_ns:
            stale.append(res.relative_to(root).as_posix())
        for line in res.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r'^\s*SPRITE\s+(\w+)\s+"([^"]+)"\s+(\d+)\s+(\d+)', line)
            if not match:
                continue
            name, rel, w, h = match.groups()
            image = root / "res" / rel
            if image.is_file() and image.stat().st_mtime_ns > rom_ns:
                stale.append(image.relative_to(root).as_posix())
            address = symbols.get(name)
            if address is None or address + 20 > len(rom):
                rows[name] = {"status": "missing_compiled_definition", "source": res.relative_to(root).as_posix()}
                continue
            rw, rh = (int.from_bytes(rom[address + i:address + i + 2], "big") for i in (0, 2))
            tile_count = int.from_bytes(rom[address + 14:address + 16], "big")
            sprite_count = int.from_bytes(rom[address + 16:address + 18], "big") & 0x7F
            if (rw, rh) != (int(w) * 8, int(h) * 8):
                rows[name] = {"status": "compiled_dimensions_mismatch", "compiled": [rw, rh],
                              "declared_tiles": [int(w), int(h)]}
            else:
                rows[name] = {"status": "proved", "max_internal_sprites": sprite_count,
                              "max_tiles": tile_count, "rom_address": address,
                              "source": res.relative_to(root).as_posix(),
                              "source_sha256": hashlib.sha256(res.read_bytes()).hexdigest()}
    status = "stale" if stale else ("passed" if rows and all(x["status"] == "proved" for x in rows.values()) else "partial")
    return {"schema_version": "compiled_sprite_limits.v1", "status": status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rom": {"path": "out/rom.bin", "sha256": hashlib.sha256(rom).hexdigest(), "bytes": len(rom)},
            "symbol_map": {"path": "out/symbol.txt",
                           "sha256": hashlib.sha256(symbols_path.read_bytes()).hexdigest()},
            "stale_sources": sorted(set(stale)), "sprites": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.project_root.resolve())
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
