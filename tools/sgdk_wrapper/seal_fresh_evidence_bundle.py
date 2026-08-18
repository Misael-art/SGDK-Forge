#!/usr/bin/env python3
"""Seal a same-session BlastEm bundle with conservative identity/freshness checks."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"
TEXT_TIME_TOLERANCE_SECONDS = 5.0
WRAPPER_ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso_utc(timestamp: float | None = None) -> str:
    moment = datetime.fromtimestamp(timestamp, timezone.utc) if timestamp is not None else datetime.now(timezone.utc)
    return moment.isoformat()


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_without_timezone")
    return parsed.astimezone(timezone.utc)


def load_screenshot_gate() -> Any:
    tool = WRAPPER_ROOT / "screenshot_semantic_gate.py"
    spec = importlib.util.spec_from_file_location("screenshot_semantic_gate", tool)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable_to_import:{tool}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Espelha PROBE_VLAB_PALETTE_WORDS em system/runtime_probe.c. Se mudar la, muda aqui.
PROBE_VLAB_PALETTE_WORDS = 64


def extract_vlab(sram_path: Path, dump_path: Path) -> dict[str, Any]:
    raw = sram_path.read_bytes()
    offset = raw.find(b"VLAB")
    if offset < 0 or offset + 8 > len(raw):
        raise ValueError("vlab_block_missing")
    schema_version, total_bytes = struct.unpack_from(">HH", raw, offset + 4)
    if total_bytes < 8 or offset + total_bytes > len(raw):
        raise ValueError("vlab_block_size_invalid")
    payload = raw[offset : offset + total_bytes]
    dump_path.write_bytes(payload)
    word_count = (total_bytes - 8) // 2
    words = list(struct.unpack_from(f">{word_count}H", payload, 8)) if word_count else []
    if len(words) < 24:
        raise ValueError("vlab_metrics_incomplete")
    # A paleta tem tamanho FIXO (PROBE_VLAB_PALETTE_WORDS = 64) e vive no fim do
    # bloco; o que sobra na frente e metrica. Derivar assim faz a leitura
    # acompanhar a probe sozinha.
    #
    # A versao anterior cortava em `words[:24]` com 24 escrito na mao, enquanto a
    # probe ja emitia 26 palavras. Os dois campos extras — spawned e failed do
    # contador de alocacao — caiam no balde da paleta e nunca chegavam ao report.
    # Quando a probe passou a 32, os seis quadros de pico sumiram do mesmo jeito,
    # e o sintoma foi campo `None` num bundle cuja SRAM tinha o dado.
    metric_count = max(24, len(words) - PROBE_VLAB_PALETTE_WORDS)
    return {
        "schema_version": schema_version,
        "offset": offset,
        "total_bytes": total_bytes,
        "metric_word_count": metric_count,
        "metric_words": words[:metric_count],
        "palette_words": words[metric_count:],
    }


def build_runtime_metrics(
    *,
    session_id: str,
    rom_sha256: str,
    vlab: dict[str, Any],
    sram_path: Path,
    dump_path: Path,
    window_title: str,
    generated_at: str,
) -> dict[str, Any]:
    words = vlab["metric_words"]
    fps_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s+fps", window_title, re.IGNORECASE)
    return {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "tool_name": "seal_fresh_evidence_bundle",
        "session_id": session_id,
        "rom_sha256": rom_sha256,
        "scope": "single_capture_snapshot",
        "performance_claim": "unproven",
        "window_title": window_title or None,
        "window_fps_snapshot": float(fps_match.group(1)) if fps_match else None,
        "vlab": {
            "schema_version": vlab["schema_version"],
            "source_sram_sha256": sha256(sram_path),
            "visual_vdp_dump_sha256": sha256(dump_path),
            "scene_id": words[0],
            "frame_counter": (words[1] << 16) | words[2],
            "screen_width": words[3],
            "screen_height": words[4],
            "plane_width": words[5],
            "plane_height": words[6],
            "hscroll_mode": words[7],
            "vscroll_mode": words[8],
            "frame_counter_snapshot": words[15],
            "sample_count": words[16],
            "over_budget_frames": words[17],
            "max_cpu_load": words[18],
            "max_cpu_jitter": words[19],
            "max_scanline_sprites": words[20],
            # [16] instantaneo no quadro do export, [17] maximo acumulado na cena.
            # Os nomes antigos (max_sprite_links / active_sprite_count) descreviam
            # o que os campos NAO faziam: [17] era a constante 1.
            "active_sprite_count_at_export": words[21],
            "max_active_sprites": words[22],
            "target_fps": words[23],
            # words[26..31]: quadro em que cada pico ocorreu, hi/lo.
            # Maximo sem quadro diz que o teto foi violado e nao diz por quem.
            # Ausentes em ROM com probe anterior a 2026-08-18: fica None.
            "max_scanline_sprites_at_frame": _peak_frame(words, 26),
            "max_cpu_load_at_frame": _peak_frame(words, 28),
            "max_active_sprites_at_frame": _peak_frame(words, 30),
            # words[24..25]: contador de alocacao de sprite. Existiam na probe
            # desde sempre e nunca chegavam aqui por causa do corte em 24.
            "sprite_alloc_spawned": words[24] if len(words) > 24 else None,
            "sprite_alloc_failed": words[25] if len(words) > 25 else None,
        },
        "claim_limit": "A single window-title and VLAB snapshot does not prove sustained performance.",
    }


def _peak_frame(words, index):
    """Le um par hi/lo. Devolve None quando a ROM foi compilada com a probe
    antiga, que nao emite estas palavras — declarar ausencia e melhor que
    devolver 0 e deixar parecer que o pico foi no quadro zero."""
    if len(words) <= index + 1:
        return None
    return (words[index] << 16) | words[index + 1]


def seal_bundle(
    *,
    session_root: Path,
    session_id: str,
    rom_path: Path,
    screenshot_path: Path,
    sram_path: Path,
    expected_rom_sha256: str,
    started_at: str,
    completed_at: str,
    emulator_ref: str,
    emulator_commit: str,
    window_title: str = "",
) -> dict[str, Any]:
    session_root = session_root.resolve()
    session_root.mkdir(parents=True, exist_ok=True)
    rom_path = rom_path.resolve()
    screenshot_path = screenshot_path.resolve()
    sram_path = sram_path.resolve()
    dump_path = session_root / "visual_vdp_dump.bin"
    metrics_path = session_root / "runtime_metrics.json"
    semantic_path = session_root / "screenshot_semantic_gate_report.json"
    manifest_path = session_root / "evidence_manifest.json"
    freshness_path = session_root / "freshness_report.json"
    blockers: list[str] = []
    started = parse_time(started_at)
    completed = parse_time(completed_at)
    if completed < started:
        raise ValueError("session_completed_before_start")

    required_inputs = {"rom": rom_path, "screenshot": screenshot_path, "sram": sram_path}
    for name, path in required_inputs.items():
        if not path.is_file():
            blockers.append(f"artifact_missing:{name}")

    current_rom_sha256 = sha256(rom_path) if rom_path.is_file() else None
    if current_rom_sha256 != expected_rom_sha256.lower():
        blockers.append("rom_identity_mismatch")

    vlab: dict[str, Any] | None = None
    if sram_path.is_file():
        try:
            vlab = extract_vlab(sram_path, dump_path)
        except ValueError as exc:
            blockers.append(str(exc))

    generated_at = iso_utc()
    if vlab and current_rom_sha256:
        metrics = build_runtime_metrics(
            session_id=session_id,
            rom_sha256=current_rom_sha256,
            vlab=vlab,
            sram_path=sram_path,
            dump_path=dump_path,
            window_title=window_title,
            generated_at=generated_at,
        )
        metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    semantic_report: dict[str, Any] | None = None
    if screenshot_path.is_file():
        semantic_report = load_screenshot_gate().analyze_screenshot(
            screenshot_path,
            rom_path=rom_path if rom_path.is_file() else None,
            evidence_session_id=session_id,
        )
        semantic_path.write_text(json.dumps(semantic_report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        if not semantic_report.get("semantic_capture_valid"):
            blockers.append(str(semantic_report.get("blocker_code") or "screenshot_semantic_gate_failed"))

    artifact_paths = {
        "rom": rom_path,
        "screenshot": screenshot_path,
        "sram": sram_path,
        "vdp_dump": dump_path,
        "runtime_metrics": metrics_path,
    }
    artifact_records: list[dict[str, Any]] = []
    min_epoch = started.timestamp() - TEXT_TIME_TOLERANCE_SECONDS
    max_epoch = max(completed.timestamp(), datetime.now(timezone.utc).timestamp()) + TEXT_TIME_TOLERANCE_SECONDS
    for name, path in artifact_paths.items():
        if not path.is_file():
            blockers.append(f"artifact_missing:{name}")
            continue
        modified = path.stat().st_mtime
        if modified < min_epoch or modified > max_epoch:
            blockers.append(f"artifact_stale:{name}")
        artifact_records.append({
            "name": name,
            "path": os.path.relpath(path, session_root).replace(os.sep, "/"),
            "session_id": session_id,
            "rom_sha256": current_rom_sha256,
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "captured_at": iso_utc(modified),
        })

    blockers = list(dict.fromkeys(blockers))
    sealed = not blockers
    manifest = {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "tool_name": "seal_fresh_evidence_bundle",
        "tool_version": TOOL_VERSION,
        "status": "sealed" if sealed else "rejected",
        "session_id": session_id,
        "session_started_at": started_at,
        "session_completed_at": completed_at,
        "rom_sha256": current_rom_sha256,
        "expected_rom_sha256": expected_rom_sha256.lower(),
        "emulator": {"ref": emulator_ref, "commit": emulator_commit},
        "artifacts": artifact_records,
        "semantic_capture_valid": bool(semantic_report and semantic_report.get("semantic_capture_valid")),
        "blockers": blockers,
        "claim_limit": "Bundle identity and freshness only; no broad gameplay, audio, performance or AAA claim is inferred.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    freshness = {
        "schema_version": "1.0.0",
        "generated_at": iso_utc(),
        "tool_name": "fresh_evidence_bundle_audit",
        "tool_version": TOOL_VERSION,
        "status": "ok" if sealed else "blocked",
        "session_id": session_id,
        "rom_sha256": current_rom_sha256,
        "same_session": sealed,
        "artifact_count": len(artifact_records),
        "required_artifact_count": len(artifact_paths),
        "blockers": blockers,
        "manifest_path": manifest_path.name,
    }
    freshness_path.write_text(json.dumps(freshness, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"sealed": sealed, "manifest": manifest, "freshness": freshness}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--rom", required=True)
    parser.add_argument("--screenshot", required=True)
    parser.add_argument("--sram", required=True)
    parser.add_argument("--expected-rom-sha256", required=True)
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--completed-at", required=True)
    parser.add_argument("--emulator-ref", required=True)
    parser.add_argument("--emulator-commit", required=True)
    parser.add_argument("--window-title", default="")
    args = parser.parse_args()
    result = seal_bundle(
        session_root=Path(args.session_root),
        session_id=args.session_id,
        rom_path=Path(args.rom),
        screenshot_path=Path(args.screenshot),
        sram_path=Path(args.sram),
        expected_rom_sha256=args.expected_rom_sha256,
        started_at=args.started_at,
        completed_at=args.completed_at,
        emulator_ref=args.emulator_ref,
        emulator_commit=args.emulator_commit,
        window_title=args.window_title,
    )
    print(json.dumps({"status": result["freshness"]["status"], "blockers": result["freshness"]["blockers"]}))
    return 0 if result["sealed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
