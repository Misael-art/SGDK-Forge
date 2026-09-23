#!/usr/bin/env python3
"""Measure VRAM tile residency from the assets, before any runtime exists.

The workspace already has `res_graph_audit.ps1` for VRAM, but it reads a built
project: it cannot answer anything until the runtime references the assets. That
leaves a window where the art is finished, the budget is already broken, and
nobody can tell — which is exactly what happened to `branding_sequence_v2`, where
a full-screen background deduplicated 2% and blew its contract line by 118%.

This gate closes that window. It reads `res/*.res`, opens each visual asset and
counts unique 8x8 tiles with H/V flip deduplication, which is what actually
occupies VRAM. No runtime needed.

Two things it reports, and the difference matters:

  residency   how many unique tiles must be resident at once. Over the ceiling is
              a hardware fact and blocks.
  dedup ratio how much of the art collapses into shared tiles. A low ratio on a
              large background is the fingerprint of art composed as a photographic
              image and quantised, rather than authored as tiles. It is a smell,
              not a violation, so it warns and names the suspect.

Residency groups come from a scene residency plan when one exists
(`cutscene_resource_plan.states[].resident` in a cinematic storyboard). Without a
plan the tool assumes every asset is simultaneously resident and says so — the
honest worst case, not a silent pass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("[tile-residency] ERROR: Pillow nao disponivel")
    sys.exit(2)

VRAM_TILES_TOTAL = 2048          # 64KB / 32 bytes por tile
NAMETABLE_TILE_EQUIV = 256       # BG_A + BG_B a 64x32, 4KB cada
SAT_TILE_EQUIV = 20              # 640 bytes
SCROLL_TABLE_TILE_EQUIV = 32     # tabela de HScroll por linha, ~1KB
USABLE_CEILING = VRAM_TILES_TOTAL - NAMETABLE_TILE_EQUIV - SAT_TILE_EQUIV - SCROLL_TABLE_TILE_EQUIV

# Fundo grande que quase nao deduplica foi composto como imagem, nao como tiles.
LARGE_ASSET_RAW_TILES = 512
LOW_DEDUP_RATIO = 0.30
# Simetria com a doutrina de audacia: VRAM sobrando tambem e decisao que ninguem tomou.
UNEXPLOITED_VRAM_BELOW = 0.40

RES_ENTRY_RE = re.compile(
    r"^\s*(?P<kind>[A-Z][A-Z0-9_]*)\s+(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s+"
    r'(?:"(?P<qpath>[^"]+)"|(?P<upath>\S+))',
)
PIXEL_KINDS = {"IMAGE", "SPRITE", "TILESET", "TILEMAP", "MAP", "BITMAP"}


def tile_stats(path: Path) -> tuple[int, int]:
    """(raw tiles, unique tiles after H/V flip dedup)."""
    img = Image.open(path)
    if img.mode != "P":
        img = img.convert("P", palette=Image.ADAPTIVE)
    px = img.load()
    w, h = img.size
    seen: set[tuple[int, ...]] = set()
    raw = 0
    for ty in range(h // 8):
        for tx in range(w // 8):
            tile = tuple(px[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8))
            raw += 1
            rows = [tile[i * 8 : (i + 1) * 8] for i in range(8)]
            hflip = tuple(v for r in rows for v in reversed(r))
            vflip = tuple(v for r in reversed(rows) for v in r)
            hvflip = tuple(v for r in reversed(rows) for v in reversed(r))
            seen.add(min(tile, hflip, vflip, hvflip))
    return raw, len(seen)


def parse_res(project_root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    res_dir = project_root / "res"
    if not res_dir.is_dir():
        return out
    for res_file in sorted(res_dir.rglob("*.res")):
        for raw_line in res_file.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = raw_line.split("//", 1)[0].strip()
            if not line:
                continue
            m = RES_ENTRY_RE.match(line)
            if not m or m.group("kind").upper() not in PIXEL_KINDS:
                continue
            rel = (m.group("qpath") or m.group("upath") or "").strip()
            out.append({
                "res_symbol": m.group("symbol"),
                "res_kind": m.group("kind").upper(),
                "asset_path": rel,
                "resolved": (res_dir / rel),
            })
    return out


def load_streaming_slots(project_root: Path) -> dict[str, dict[str, Any]]:
    """Assets com streaming ocupam a janela declarada, nao o conjunto inteiro.

    Sem isto o gate cobra o custo total de um asset cuja decisao de streaming ja
    foi tomada e documentada — e a diferenca decide se a cena estoura ou cabe.
    """
    slots: dict[str, dict[str, Any]] = {}
    for candidate in sorted(project_root.glob("doc/*dma_queue*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        for slot in data.get("vram_slots") or []:
            res = slot.get("resource")
            tiles = slot.get("tiles")
            if isinstance(res, str) and isinstance(tiles, int):
                slots[res] = {"tiles": tiles, "slot_id": slot.get("slot_id"),
                              "source": candidate.name}
    return slots


def load_residency_plan(project_root: Path) -> tuple[list[dict[str, Any]], str | None]:
    for candidate in sorted(project_root.glob("doc/*storyboard*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        states = (data.get("cutscene_resource_plan") or {}).get("states")
        if isinstance(states, list) and states:
            return states, candidate.name
    return [], None


def audit(project_root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    def add(code: str, severity: str, subject: str, message: str) -> None:
        findings.append({"code": code, "severity": severity, "subject": subject, "message": message})

    symbols = parse_res(project_root)
    streaming = load_streaming_slots(project_root)
    assets: list[dict[str, Any]] = []
    by_symbol: dict[str, int] = {}

    for sym in symbols:
        path: Path = sym["resolved"]
        if not path.is_file():
            add("tile_residency_unmeasurable", "blocking", sym["res_symbol"],
                f"arquivo nao encontrado: {sym['asset_path']}")
            continue
        raw, uniq = tile_stats(path)
        ratio = 1 - (uniq / raw) if raw else 0.0
        entry = {
            "res_symbol": sym["res_symbol"],
            "res_kind": sym["res_kind"],
            "asset_path": sym["asset_path"],
            "raw_tiles": raw,
            "unique_tiles": uniq,
            "dedup_ratio": round(ratio, 3),
            "bytes_resident": uniq * 32,
        }
        slot = streaming.get(sym["res_symbol"])
        if slot:
            entry["streamed"] = True
            entry["resident_tiles"] = slot["tiles"]
            entry["streaming_slot"] = slot["slot_id"]
            entry["streaming_source"] = slot["source"]
            entry["bytes_resident"] = slot["tiles"] * 32
            by_symbol[sym["res_symbol"]] = slot["tiles"]
        else:
            entry["streamed"] = False
            entry["resident_tiles"] = uniq
            by_symbol[sym["res_symbol"]] = uniq
        assets.append(entry)

        if raw >= LARGE_ASSET_RAW_TILES and ratio < LOW_DEDUP_RATIO:
            add("low_tile_dedup_ratio", "warning", sym["res_symbol"],
                f"{raw} tiles brutos e apenas {ratio:.0%} de deduplicacao ({uniq} unicos). "
                "Fundo grande que quase nao deduplica foi composto como imagem fotografica e "
                "quantizado, nao autorado como conjunto de tiles. Custa como arte unica e "
                "costuma ainda parecer repetitivo.")

    plan, plan_source = load_residency_plan(project_root)
    states: list[dict[str, Any]] = []
    peak = 0
    peak_state = None

    if plan:
        for st in plan:
            names = [n for n in (st.get("resident") or []) if isinstance(n, str)]
            known = {n: by_symbol[n] for n in names if n in by_symbol}
            missing = [n for n in names if n not in by_symbol]
            total = sum(known.values())
            states.append({
                "state": st.get("id", "?"),
                "resident_symbols": names,
                "unresolved_symbols": missing,
                "resident_tiles": total,
                "margin": round((USABLE_CEILING - total) / USABLE_CEILING, 3),
            })
            if total > peak:
                peak, peak_state = total, st.get("id", "?")
        residency_basis = f"plano de residencia de {plan_source}"
    else:
        peak = sum(by_symbol.values())
        peak_state = "todos_simultaneos"
        states.append({
            "state": "todos_simultaneos",
            "resident_symbols": sorted(by_symbol),
            "unresolved_symbols": [],
            "resident_tiles": peak,
            "margin": round((USABLE_CEILING - peak) / USABLE_CEILING, 3),
        })
        residency_basis = ("nenhum plano de residencia encontrado; assumido pior caso com todos "
                           "os assets simultaneos")

    utilization = peak / USABLE_CEILING if USABLE_CEILING else 0.0
    if peak > USABLE_CEILING:
        add("tile_residency_over_ceiling", "blocking", peak_state or "?",
            f"{peak} tiles residentes contra teto util de {USABLE_CEILING}. "
            "Excesso de VRAM e fato de hardware: reduza tiles unicos re-autorando o asset como "
            "conjunto de tiles, ou tire assets da residencia simultanea.")
    elif utilization < UNEXPLOITED_VRAM_BELOW:
        add("unexploited_vram_headroom", "warning", peak_state or "?",
            f"pico de {peak} tiles usa {utilization:.0%} do teto. Folga nao medida e timidez "
            "(SGDK_GLOBAL secao 30): ou a arte pode ser mais densa, ou declare por que a "
            "direcao pede menos.")

    blocking = sorted({f["code"] for f in findings if f["severity"] == "blocking"})
    return {
        "schema_version": "1.0.0",
        "tool": "audit_tile_residency",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": project_root.as_posix(),
        "ceiling": {
            "vram_tiles_total": VRAM_TILES_TOTAL,
            "nametable_tile_equiv": NAMETABLE_TILE_EQUIV,
            "sat_tile_equiv": SAT_TILE_EQUIV,
            "scroll_table_tile_equiv": SCROLL_TABLE_TILE_EQUIV,
            "usable_ceiling": USABLE_CEILING,
            "derivation": "2048 tiles de 32B, menos nametables de BG_A/BG_B a 64x32, menos SAT, "
                          "menos tabela de scroll por linha",
        },
        "residency_basis": residency_basis,
        "streamed_symbols": sorted(streaming),
        "assets": assets,
        "states": states,
        "peak_resident_tiles": peak,
        "peak_state": peak_state,
        "vram_utilization": round(utilization, 3),
        "findings": findings,
        "limitation": "Mede o asset, nao o runtime. Nao substitui res_graph_report, que confere "
                      "o mapa real de VRAM depois que a cena existe.",
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


def self_check() -> int:
    """Fixture limpa passa; fixture de ruido estoura o teto e reprova."""
    import random, tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "res" / "gfx").mkdir(parents=True)

        def png(name, w, h, noise):
            im = Image.new("P", (w, h))
            im.putpalette([(i * 37) % 256 for i in range(768)])
            px = im.load()
            rnd = random.Random(11)
            for y in range(h):
                for x in range(w):
                    px[x, y] = rnd.randrange(1, 16) if noise else ((x // 8 + y // 8) % 2) + 1
            im.save(root / "res" / "gfx" / name)

        png("clean.png", 256, 64, False)
        (root / "res" / "resources.res").write_text('IMAGE img_clean "gfx/clean.png" BEST\n')
        ok = audit(root)

        png("noise_a.png", 320, 240, True)
        png("noise_b.png", 320, 240, True)
        (root / "res" / "resources.res").write_text(
            'IMAGE img_clean "gfx/clean.png" BEST\n'
            'IMAGE img_noise_a "gfx/noise_a.png" BEST\n'
            'IMAGE img_noise_b "gfx/noise_b.png" BEST\n')
        bad = audit(root)

    if ok["blocking"]:
        print("self-check failed: fixture limpa reprovada", file=sys.stderr); return 1
    clean = [a for a in ok["assets"] if a["res_symbol"] == "img_clean"][0]
    if clean["dedup_ratio"] < 0.9:
        print("self-check failed: dedup nao reconheceu tileset repetido", file=sys.stderr); return 1
    if not bad["blocking"] or "tile_residency_over_ceiling" not in bad["blocking_statuses"]:
        print("self-check failed: estouro de teto nao detectado", file=sys.stderr); return 1
    if not any(f["code"] == "low_tile_dedup_ratio" for f in bad["findings"]):
        print("self-check failed: dedup baixo nao sinalizado", file=sys.stderr); return 1
    print("audit_tile_residency self-check passed (passa, estoura teto, sinaliza dedup baixo)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", default="")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.project_root:
        print("[tile-residency] ERROR: passe --project-root ou --self-check"); return 2
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"[tile-residency] ERROR: projeto nao encontrado: {root}")
        return 2

    report = audit(root)
    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        c = report["ceiling"]
        print(f"[tile-residency] teto util {c['usable_ceiling']} tiles "
              f"({c['vram_tiles_total']} - {c['nametable_tile_equiv']} nametables "
              f"- {c['sat_tile_equiv']} SAT - {c['scroll_table_tile_equiv']} scroll)")
        print(f"[tile-residency] base de residencia: {report['residency_basis']}")
        print()
        print(f"  {'asset':30}{'bruto':>7}{'unico':>7}{'dedup':>8}  residencia")
        for a in report["assets"]:
            tag = f"  stream {a['resident_tiles']}" if a.get("streamed") else ""
            print(f"  {a['res_symbol'][:28]:30}{a['raw_tiles']:7}{a['unique_tiles']:7}"
                  f"{a['dedup_ratio']:7.0%}{tag}")
        print()
        for st in report["states"]:
            flag = " ESTOURA" if st["resident_tiles"] > c["usable_ceiling"] else ""
            print(f"  {st['state'][:26]:28}{st['resident_tiles']:6} tiles"
                  f"  margem {st['margin']:5.0%}{flag}")
            if st["unresolved_symbols"]:
                print(f"      simbolos do plano sem asset: {st['unresolved_symbols']}")
        print()
        for f in report["findings"]:
            print(f"[{f['severity'].upper()}] {f['code']} :: {f['subject']} :: {f['message']}")
        verdict = "BLOCKED" if report["blocking"] else "OK"
        print(f"[tile-residency] pico={report['peak_resident_tiles']} "
              f"utilizacao={report['vram_utilization']:.0%} verdict={verdict}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
