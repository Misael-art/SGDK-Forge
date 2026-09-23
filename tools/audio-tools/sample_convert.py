#!/usr/bin/env python3
"""Converte um WAV de authoring para o payload PCM 8 bit signed do XGM2.

Encana `audio_core.to_xgm2_pcm` (resample linear + 8bit signed + alinhamento
256). A saida crua (`--out sample.pcm`) e compativel com o payload XGM2, mas
nao declara identidade byte a byte com o resampler interno do ResComp.
`--c-array` gera a forma literal C.

Exemplo:
  python3 tools/audio-tools/sample_convert.py \\
      --input res/audio/chase/chase_hit.wav --out out/hit.pcm --rate 13300

Regras: taxa XGM2 so aceita 6650 (half) ou 13300 (full); payload alinhado a 256.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from audio_core import (
    SCHEMA_VERSION,
    XGM2_RATES,
    XGM2_SAMPLE_ALIGN,
    c_array_format,
    now_iso,
    read_wav,
    sha256_file,
    to_xgm2_pcm,
    wav_info,
    write_wav,
)

TOOL_NAME = "sample_convert"
TOOL_VERSION = "1.0.0"


def convert(input_path: Path, rate: int, out_path: Path | None,
            c_array_name: str | None) -> dict:
    samples = read_wav(input_path)
    payload, metrics = to_xgm2_pcm(samples, wav_info(input_path)["sample_rate"], rate)
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "generated_at": now_iso(),
        "input": str(input_path),
        "input_sha256": sha256_file(input_path),
        "rate": rate,
        "route_classification": "technical_pcm_conversion",
        "metrics": metrics,
        "c_array_name": c_array_name,
    }
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload)
        report["output"] = str(out_path)
        report["output_bytes"] = len(payload)
        report["output_sha256"] = sha256_file(out_path)
    if c_array_name is not None:
        report["c_array"] = c_array_format(payload, c_array_name)
    return report


def _positive_fixtures(tmpdir: Path) -> list[dict]:
    name = "sample_convert_roundtrip"
    fails = []
    wav_path = tmpdir / "tone.wav"
    pcm_path = tmpdir / "tone.pcm"
    try:
        rate = 44100
        samples = [math.sin(2 * math.pi * 440 * i / rate) * 0.5 for i in range(rate)]
        write_wav(wav_path, samples, rate)
        report = convert(wav_path, 13300, pcm_path, None)
        data = pcm_path.read_bytes()
        if not report["metrics"]["256_aligned"]:
            fails.append("saida nao alinhada a 256")
        if len(data) % XGM2_SAMPLE_ALIGN != 0:
            fails.append("ficheiro PCM fora do alinhamento 256")
        if len(data) != report["output_bytes"]:
            fails.append("contagem de bytes divergente")
    except Exception as exc:  # noqa: BLE001
        fails.append(f"excecao: {exc}")
    return [{
        "fixture": name,
        "kind": "positive",
        "passed": not fails,
        "blocker": "audio_self_check_failed:" + name,
        "detail": fails,
    }]


def _negative_fixtures() -> list[dict]:
    fixtures = []
    bad_rate = False
    tmp = Path("/tmp") / "audio_tools_neg.wav"
    try:
        rate = 44100
        write_wav(tmp, [math.sin(2 * math.pi * 220 * i / rate) * 0.5 for i in range(rate // 2)], rate)
        convert(tmp, 8000, None, None)
    except ValueError:
        bad_rate = True
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
    fixtures.append({
        "fixture": "rejects_non_xgm2_rate",
        "kind": "negative",
        "passed": bad_rate,
        "blocker": "audio_self_check_expected_blocker:rejects_non_xgm2_rate",
        "detail": [] if bad_rate else ["aceptou taxa 8000 que nao e 6650/13300"],
    })
    return fixtures


def self_check() -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        fixtures = _positive_fixtures(tmpdir) + _negative_fixtures()
    failed = [f for f in fixtures if not f["passed"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "audio_core (rescomp.txt WAV/XGM2 + xgm2.txt)",
        "limitation": (
            "Prova formato compativel. Nao prova identidade byte a byte com "
            "ResComp, anti-aliasing de alta qualidade ou qualidade artistica."
        ),
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TOOL_NAME + " (WAV -> PCM XGM2).")
    parser.add_argument("--input", dest="input_path", metavar="WAV",
                        help="WAV 16bit monofonte de authoring.")
    parser.add_argument("--out", dest="out_path", metavar="PCM",
                        help="escreve payload PCM 8bit signed.")
    parser.add_argument("--rate", type=int, default=13300,
                        help=f"taxa XGM2 ({sorted(XGM2_RATES)}), default 13300.")
    parser.add_argument("--c-array", dest="c_array", metavar="NAME",
                        help="emite array C literal com este nome.")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    if not args.input_path:
        parser.print_help()
        return 2
    if args.rate not in XGM2_RATES:
        print(f"[ERRO] taxa XGM2 invalida {args.rate}; aceita {sorted(XGM2_RATES)}",
              file=sys.stderr)
        return 2
    report = convert(Path(args.input_path), args.rate,
                     Path(args.out_path) if args.out_path else None,
                     args.c_array)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
