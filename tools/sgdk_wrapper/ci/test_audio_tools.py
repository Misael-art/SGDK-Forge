#!/usr/bin/env python3
# ruff: noqa: I001
"""Regressao externa das ferramentas de audio; nao confia apenas em self-check."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import wave
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[3]
AUDIO_TOOLS = ROOT / "tools" / "audio-tools"
sys.path.insert(0, str(AUDIO_TOOLS))

import audio_core
import audit_audio_provenance
import loop_clipper
import sample_convert
import sfx_synth
import vgm_to_xgm2


PROJECT = ROOT / "SGDK_projects" / (
    "Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
)


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    modules = [
        audio_core,
        vgm_to_xgm2,
        sample_convert,
        sfx_synth,
        loop_clipper,
        audit_audio_provenance,
    ]
    for module in modules:
        report = module.self_check()
        checks.append((
            f"{module.TOOL_NAME}_self_check",
            not report["blocking"],
            str(report.get("blocking_statuses", [])),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)

        wav8 = temp / "bias.wav"
        audio_core.write_wav_8bit(wav8, [-0.5, 0.0, 0.5], 13300)
        with wave.open(str(wav8), "rb") as handle:
            raw = handle.readframes(handle.getnframes())
        checks.append(("wav_u8_silence_is_128", raw[1] == 128, str(list(raw))))

        header = bytearray(0x40)
        header[:4] = b"Vgm "
        header[4:8] = (0x3C).to_bytes(4, "little")
        header[8:12] = (0x171).to_bytes(4, "little")
        header[0x24:0x28] = (50).to_bytes(4, "little")
        vgm = audio_core.vgm_info(bytes(header))
        checks.append((
            "vgm_offsets_are_canonical",
            vgm["raw_version"] == 0x171 and vgm["system_hint"] == "PAL",
            json.dumps(vgm, sort_keys=True),
        ))

        source = temp / "source_22050.wav"
        output = temp / "loop_22050.wav"
        samples = [math.sin(2 * math.pi * 220 * i / 22050) for i in range(22050)]
        audio_core.write_wav(source, samples, 22050)
        loop_clipper.process(source, output, 0.25)
        checks.append((
            "loop_preserves_input_rate",
            audio_core.wav_info(output)["sample_rate"] == 22050,
            str(audio_core.wav_info(output)),
        ))

        synth = sfx_synth.render(
            "thump", 0.1, 13300, 0.4, normalize_peak=0.75,
            freq_start=140.0, freq_end=42.0, decay=35.0,
        )
        checks.append(("synth_respects_explicit_peak", synth["peak"] == 0.75, str(synth["peak"])))

        source_vgm = PROJECT / "res" / "audio" / "chase" / "chase_core_fm_psg.vgm"
        xgm_report = vgm_to_xgm2.convert(
            source_vgm, temp / "music.xgm", packed=False, timing="auto", silent=True,
        )
        checks.append((
            "real_vgm_to_xgm2",
            xgm_report["xgm2"]["magic"] == "XGM2" and bool(xgm_report["output_sha256"]),
            json.dumps(xgm_report["xgm2"], sort_keys=True),
        ))

        xgc_report = vgm_to_xgm2.convert(
            source_vgm, temp / "music.xgc", packed=True, timing="auto", silent=True,
        )
        checks.append((
            "real_vgm_to_xgc",
            xgc_report["xgm2"]["plausible"] and bool(xgc_report["output_sha256"]),
            json.dumps(xgc_report["xgm2"], sort_keys=True),
        ))

    schema = json.loads((
        ROOT / "tools" / "sgdk_wrapper" / "schemas" / "sfx_bank_manifest.schema.json"
    ).read_text(encoding="utf-8"))
    manifest_path = PROJECT / "doc" / "sfx_bank_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema_errors = list(Draft7Validator(schema).iter_errors(manifest))
    checks.append(("real_manifest_matches_schema", not schema_errors, str(schema_errors)))

    provenance = audit_audio_provenance.audit(manifest_path, PROJECT, verify_hashes=True)
    checks.append((
        "real_manifest_hash_and_res_binding",
        not provenance["blocking"],
        str(provenance["blockers"]),
    ))

    hit = PROJECT / "res" / "audio" / "chase" / "chase_hit.wav"
    with wave.open(str(hit), "rb") as handle:
        hit_raw = handle.readframes(handle.getnframes())
    dc_offset = sum(value - 128 for value in hit_raw) / len(hit_raw)
    checks.append((
        "chase_hit_has_valid_unsigned_center",
        abs(dc_offset) < 2.0 and hit_raw[-1] == 128,
        f"dc_offset={dc_offset:.4f}, last={hit_raw[-1]}",
    ))

    failed = [(name, detail) for name, passed, detail in checks if not passed]
    if failed:
        for name, detail in failed:
            print(f"[FAIL] {name}: {detail}")
    print(f"audio tools validation: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
