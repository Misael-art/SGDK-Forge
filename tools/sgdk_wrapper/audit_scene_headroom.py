#!/usr/bin/env python3
"""Sweep contracted scenes and apply the audacity doctrine to declared sprite pressure.

`vdp_scanline_simulator.py` needs a sprite layout (x/y/w/h per sprite). Contracted
scenes in this workspace declare pressure as prose or as a single number, so the
simulator cannot be pointed at them directly. That gap is the first finding this
sweep reports.

What it can do: classify every declaration and, where a real number exists,
compute utilisation against the VDP limit and apply SGDK_GLOBAL section 30 —
unmeasured headroom is timidity. Below 60% utilisation without a declared
justification the scene is leaving hardware on the table.

Three states a scene can be in:

  measured        a number exists; utilisation computed, doctrine applied
  declared_zero   the scene declares zero sprites; the hardware is idle by design
                  or by neglect, and the contract should say which
  unmeasured      `nao_medido` or prose; nothing can be computed, and no claim of
                  sprite budget is supportable
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPRITE_LIMIT_H40 = 20
UNEXPLOITED_BELOW = 0.60
PRESSURE_KEYS = ("scanline_sprite_pressure", "max_scanline_sprites", "sprite_peak_per_scanline")
NUMBER_RE = re.compile(r"(\d+)\s*/\s*(\d+)|^\s*(\d+)\s*$|(\d+)\s+sprites?")
UNMEASURED_RE = re.compile(r"(?i)nao[_ ]medido|not[_ ]measured|unknown")


def extract(node: Any, out: list[tuple[str, Any]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in PRESSURE_KEYS:
                out.append((key, value))
            extract(value, out)
    elif isinstance(node, list):
        for item in node:
            extract(item, out)


def interpret(value: Any) -> tuple[str, int | None]:
    """Return (state, peak). state in measured | declared_zero | unmeasured."""
    if isinstance(value, (int, float)):
        n = int(value)
        return ("declared_zero", 0) if n == 0 else ("measured", n)
    text = str(value).strip()
    if UNMEASURED_RE.search(text):
        return ("unmeasured", None)
    match = NUMBER_RE.search(text)
    if not match:
        return ("unmeasured", None)
    groups = [g for g in match.groups() if g is not None]
    n = int(groups[0])
    return ("declared_zero", 0) if n == 0 else ("measured", n)


def audit(root: Path) -> dict[str, Any]:
    scenes: list[dict[str, Any]] = []
    for path in sorted(root.rglob("doc/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        hits: list[tuple[str, Any]] = []
        extract(data, hits)
        if not hits:
            continue
        justified = bool(str(data.get("headroom_justification", "")).strip())
        for key, value in hits:
            state, peak = interpret(value)
            try:
                project = path.relative_to(root).parts[0]
            except ValueError:
                project = path.parent.parent.name
            entry: dict[str, Any] = {
                "project": project,
                "file": path.name,
                "field": key,
                "declared": str(value)[:120],
                "state": state,
                "peak_sprites_per_scanline": peak,
                "headroom_justification": justified or None,
            }
            if state == "measured" and peak is not None:
                util = peak / SPRITE_LIMIT_H40
                entry["utilization"] = round(util, 3)
                if util < UNEXPLOITED_BELOW and not justified:
                    entry["finding"] = "unexploited_headroom"
            elif state == "declared_zero":
                entry["utilization"] = 0.0
                if not justified:
                    entry["finding"] = "hardware_idle_undeclared"
            else:
                entry["finding"] = "sprite_pressure_unmeasured"
            scenes.append(entry)

    by_state: dict[str, int] = {}
    for s in scenes:
        by_state[s["state"]] = by_state.get(s["state"], 0) + 1

    return {
        "schema_version": "1.0.0",
        "tool": "audit_scene_headroom",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "doctrine_ref": "SGDK_GLOBAL.md secao 30",
        "sprite_limit_assumed": SPRITE_LIMIT_H40,
        "limitation": "vdp_scanline_simulator.py exige layout de sprites (x/y/w/h). Nenhuma "
                      "cena contratada declara layout, entao o simulador nao pode ser apontado "
                      "para elas. Esta varredura le a pressao declarada; nao a substitui por "
                      "medicao real.",
        "declarations": scenes,
        "summary": {
            "declarations_found": len(scenes),
            "by_state": by_state,
            "unexploited_headroom": len([s for s in scenes if s.get("finding") == "unexploited_headroom"]),
            "hardware_idle_undeclared": len([s for s in scenes if s.get("finding") == "hardware_idle_undeclared"]),
            "unmeasured": len([s for s in scenes if s.get("finding") == "sprite_pressure_unmeasured"]),
        },
    }


def self_check() -> int:
    """Classifica measured, declared_zero e unmeasured; sinaliza folga nao explorada."""
    cases = {"9": ("measured", "unexploited_headroom"),
             "19": ("measured", None),
             "0": ("declared_zero", "hardware_idle_undeclared"),
             "nao_medido": ("unmeasured", "sprite_pressure_unmeasured"),
             "runtime observado 9/20": ("measured", "unexploited_headroom")}
    for value, (want_state, want_finding) in cases.items():
        state, peak = interpret(value)
        if state != want_state:
            print(f"self-check failed: '{value}' -> {state}, esperado {want_state}", file=sys.stderr)
            return 1
        if want_finding == "unexploited_headroom" and peak is not None:
            if (peak / SPRITE_LIMIT_H40) >= UNEXPLOITED_BELOW:
                print(f"self-check failed: '{value}' deveria acusar folga", file=sys.stderr); return 1
        if want_finding is None and peak is not None:
            if (peak / SPRITE_LIMIT_H40) < UNEXPLOITED_BELOW:
                print(f"self-check failed: '{value}' nao deveria acusar folga", file=sys.stderr); return 1
    print("audit_scene_headroom self-check passed (3 estados + limiar de folga)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="SGDK_projects")
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"[scene-headroom] ERROR: diretorio nao encontrado: {root}")
        return 2

    report = audit(root)
    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        s = report["summary"]
        print(f"[scene-headroom] declaracoes encontradas: {s['declarations_found']}")
        for state, n in sorted(s["by_state"].items()):
            print(f"    {state:16} {n}")
        print(f"[scene-headroom] unexploited_headroom={s['unexploited_headroom']} "
              f"hardware_idle_undeclared={s['hardware_idle_undeclared']} "
              f"unmeasured={s['unmeasured']}")
        seen: set[tuple[str, str]] = set()
        for d in report["declarations"]:
            key = (d["project"][:28], d["declared"][:40])
            if key in seen:
                continue
            seen.add(key)
            util = f"{d['utilization']:.0%}" if d.get("utilization") is not None else "  - "
            print(f"  {d['project'][:28]:30} {util:>5}  {d.get('finding','ok'):28} {d['declared'][:44]}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
