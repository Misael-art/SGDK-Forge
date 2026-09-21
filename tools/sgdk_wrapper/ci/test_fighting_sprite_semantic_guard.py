#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

from PIL import Image


WRAPPER = Path(__file__).resolve().parents[1]
TOOL = WRAPPER / "validate_fighting_sprite_semantics.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_fighting_sprite_semantics", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sprite(path: Path, width: int, height: int, visible_height: int) -> None:
    image = Image.new("P", (width, height), 0)
    image.putpalette([0, 0, 0, 34, 68, 102] + [0, 0, 0] * 254)
    top = height - visible_height
    for y in range(top, height):
        for x in range(width // 4, width * 3 // 4):
            image.putpixel((x, y), 1)
    image.save(path, "PNG", bits=4, transparency=0)


def strip(path: Path, cell_width: int, cell_height: int, heights: list[int]) -> None:
    image = Image.new("P", (cell_width * len(heights), cell_height), 0)
    image.putpalette([0, 0, 0, 34, 68, 102] + [0, 0, 0] * 254)
    for frame, visible_height in enumerate(heights):
        top = cell_height - visible_height
        x0 = frame * cell_width
        for y in range(top, cell_height):
            for x in range(x0 + cell_width // 4, x0 + cell_width * 3 // 4):
                image.putpixel((x, y), 1)
    image.save(path, "PNG", bits=4, transparency=0)


def source(path: str, digest: str, role: str, *, classification="native_pixel", use="scale_reference", promotable=False):
    return {
        "path": path,
        "sha256": digest,
        "semantic_role": role,
        "classification": classification,
        "allowed_use": use,
        "promotable": promotable,
    }


def contract(project: Path, ref_a: Path, ref_b: Path, candidate: Path) -> dict:
    gdd = project / "doc" / "11-gdd.md"
    return {
        "schema_version": "1.0.0",
        "artifact_kind": "fighting_sprite_semantic_contract",
        "asset_id": "fighter_fixture",
        "profile": "fighting_full_body_sprite",
        "project_identity": {"canonical_directory_name": project.name},
        "source_assets": [
            source("data/ref_a.png", sha(ref_a), "fighter_full_body_frame_or_strip"),
            source("data/ref_b.png", sha(ref_b), "fighter_full_body_frame_or_strip"),
        ],
        "scale_rule": {
            "operator": "gte_ceil_multiplier_of_max_reference_visible_height",
            "multiplier": 1.25,
            "declared_minimum_visible_height_px": 125,
            "gdd_binding": {
                "path": "doc/11-gdd.md",
                "sha256": sha(gdd),
                "rule_id": "fighter_fixture_scale",
                "formula_marker": "fighter_fixture_scale:minimum_visible_height=ceil(1.25*max(full_body_reference_visible_height))",
            },
            "references": [
                {"path": "data/ref_a.png", "sha256": sha(ref_a), "semantic_role": "fighter_full_body_frame_or_strip", "cell_width": 64, "cell_height": 104},
                {"path": "data/ref_b.png", "sha256": sha(ref_b), "semantic_role": "fighter_full_body_frame_or_strip", "cell_width": 48, "cell_height": 80},
            ],
        },
        "candidate": {"path": "data/candidate.png", "sha256": sha(candidate), "declared_width": 88, "declared_height": 136},
        "claim_ceiling": "semantic_scale_gate_only",
    }


def codes(result: dict) -> set[str]:
    return set(result["blockers"])


def main() -> int:
    module = load_module()
    checks: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory(prefix="fighting_sprite_semantics_") as raw:
        workspace = Path(raw)
        projects = workspace / "SGDK_projects"
        project = projects / "FIGHTER [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
        data = project / "data"
        data.mkdir(parents=True)
        gdd = project / "doc" / "11-gdd.md"
        gdd.parent.mkdir(parents=True)
        gdd.write_text(
            "fighter_fixture_scale:minimum_visible_height=ceil(1.25*max(full_body_reference_visible_height))\n",
            encoding="utf-8",
        )
        ref_a = data / "ref_a.png"
        ref_b = data / "ref_b.png"
        candidate = data / "candidate.png"
        strip(ref_a, 64, 104, [98, 100])
        strip(ref_b, 48, 80, [74, 76])
        sprite(candidate, 88, 136, 125)
        base = contract(project, ref_a, ref_b, candidate)
        contract_path = project / "contract.json"

        def run(value: dict) -> dict:
            contract_path.write_text(json.dumps(value), encoding="utf-8")
            return module.validate_contract(project, contract_path)

        result = run(base)
        checks.append(("accepts_full_body_references_and_matching_candidate", result["status"] == "passed", str(result)))
        checks.append(("rederives_formula_from_frame_bboxes", result["measurements"]["computed_minimum_visible_height_px"] == 125, str(result)))

        portrait = json.loads(json.dumps(base))
        portrait["source_assets"][0]["semantic_role"] = "portrait"
        portrait["scale_rule"]["references"][0]["semantic_role"] = "portrait"
        result = run(portrait)
        checks.append(("rejects_portrait_as_scale_reference", any("invalid_fighter_scale_reference_role" in code for code in codes(result)), str(result)))

        wrong_formula = json.loads(json.dumps(base))
        wrong_formula["scale_rule"]["declared_minimum_visible_height_px"] = 99
        result = run(wrong_formula)
        checks.append(("rejects_declared_formula_mismatch", "declared_scale_formula_result_mismatch" in codes(result), str(result)))

        gdd_drift = json.loads(json.dumps(base))
        gdd_drift["scale_rule"]["gdd_binding"]["formula_marker"] = (
            "fighter_fixture_scale:minimum_visible_height=ceil(0.5*max(full_body_reference_visible_height))"
        )
        result = run(gdd_drift)
        checks.append(("rejects_contract_formula_divergent_from_gdd", "gdd_scale_formula_contract_mismatch" in codes(result), str(result)))

        small = data / "small.png"
        sprite(small, 88, 136, 80)
        too_small = json.loads(json.dumps(base))
        too_small["candidate"] = {"path": "data/small.png", "sha256": sha(small), "declared_width": 88, "declared_height": 136}
        result = run(too_small)
        checks.append(("rejects_platform_scale_fighter", "fighting_full_body_sprite_below_gdd_scale" in codes(result), str(result)))

        xpm = data / "native_matrix.xpm"
        xpm.write_text("/* XPM */\nstatic char *x[]={\"1 1 1 1\",\". c #000000\",\".\"};\n", encoding="utf-8")
        xpm_claim = json.loads(json.dumps(base))
        xpm_claim["source_assets"].append(source(
            "data/native_matrix.xpm", sha(xpm), "visual_translation_source",
            classification="hand_authored_pixel", use="visual_translation", promotable=True,
        ))
        result = run(xpm_claim)
        checks.append(("classifies_textual_matrix_as_procedural_probe", any("textual_pixel_matrix_requires_procedural_code_probe" in code for code in codes(result)), str(result)))

        duplicate = projects / "FIGHTER [VER.001] [SGDK 211] [SGDK 211] [GEN] [GAME] [FIGHTING]"
        duplicate.mkdir(parents=True)
        result = run(base)
        checks.append(("rejects_duplicate_project_identity_even_empty", "duplicate_project_identity_detected" in codes(result), str(result)))
        duplicate.rmdir()

        stale = json.loads(json.dumps(base))
        stale["candidate"]["sha256"] = "f" * 64
        result = run(stale)
        checks.append(("rejects_stale_candidate_hash", "candidate_hash_mismatch" in codes(result), str(result)))

    failed = [(name, detail) for name, passed, detail in checks if not passed]
    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}" + (f" -- {detail}" if not passed else ""))
    print(f"fighting_sprite_semantic_guard: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
