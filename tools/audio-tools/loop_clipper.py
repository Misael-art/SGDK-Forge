#!/usr/bin/env python3
"""Corta um WAV em loop sem clique, deslocando o ponto de corte para um
zero-crossing (proximo de zero) no inicio e no fim do segmento.

Serve para suportar o `seamless_loop_report` do `premium-audio-pipeline`:
BGM/ambience/loop de menu nao podem clicar nem reiniciar de forma abrupta.
O cut nao e matematicamente perfeito (nao faz crossfade), mas reduz o clique
faiscante de um corte aleatorio: escolhe a janela [start, end] de comprimento
mais proximo do alvo onde ambos os limites caiem perto de zero.

Exemplo:
  python3 tools/audio-tools/loop_clipper.py --input loop.wav --out loop_clean.wav \\
      --duration 1.0
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from audio_core import SCHEMA_VERSION, now_iso, read_wav, wav_info, write_wav

TOOL_NAME = "loop_clipper"
TOOL_VERSION = "1.0.0"


def _nearest_zero_crossing(samples: list[float], target: int, radius: int,
                           rising: bool = True) -> int | None:
    """Procura o indice mais proximo de `target` onde a onda cruza o zero.

    `rising=True` escolhe cruzamentos que sobem (negativo->positivo):
    consistencia no sentido deixara o loop mais continuo.
    """
    best = None
    best_dist = None
    lo = max(1, target - radius)
    hi = min(len(samples) - 1, target + radius)
    for index in range(lo, hi):
        prev = samples[index - 1]
        curr = samples[index]
        if rising:
            crosses = prev < 0 <= curr
        else:
            crosses = prev > 0 >= curr
        if not crosses:
            continue
        dist = abs(index - target)
        if best_dist is None or dist < best_dist:
            best = index
            best_dist = dist
    return best


def crop_loop(samples: list[float], target_frames: int, radius: int = 1024) -> tuple[list[float], dict]:
    if target_frames <= 0:
        raise ValueError("target_frames deve ser > 0")
    if target_frames >= len(samples):
        raise ValueError("loop maior que o audio nao faz sentido; alimente mais duracao")
    start = _nearest_zero_crossing(samples, 0, radius) or 0
    end_target = start + target_frames
    end = _nearest_zero_crossing(samples, end_target, radius, rising=True)
    if end is None or end <= start:
        # fallback: corte simples no comprimento pedido (sem snap de fim)
        end = end_target
    cropped = samples[start:end]
    seam_delta = abs(cropped[-1] - cropped[0]) if cropped else 0.0
    report = {
        "start_frame": start,
        "start_value": round(samples[start], 6),
        "end_frame": end,
        "end_value": round(samples[end - 1], 6),
        "seam_amplitude_delta": round(seam_delta, 6),
        "loop_frames": end - start,
        "target_frames": target_frames,
        "frames_error": abs((end - start) - target_frames),
    }
    return cropped, report


def process(input_path: Path, output_path: Path, duration_s: float,
            radius: int = 1024) -> dict:
    info = wav_info(input_path)
    sample_rate = info["sample_rate"]
    samples = read_wav(input_path)
    cropped, report = crop_loop(samples, int(duration_s * sample_rate), radius)
    write_wav(output_path, cropped, sample_rate)
    return {"sample_rate": sample_rate, **report}


def _positive_fixtures(tmpdir: Path) -> list[dict]:
    name = "loop_clipper_cuts_at_zero"
    fails = []
    try:
        sr = 44100
        freq = 440.0
        samples = [math.sin(2 * math.pi * freq * i / sr) for i in range(int(0.5 * sr))]
        target = int(sr * 0.15)
        cropped, report = crop_loop(samples, target)
        if abs(cropped[0]) > 0.08:
            fails.append("inicio longe do zero")
        if abs(cropped[-1]) > 0.08:
            fails.append("fim longe do zero")
        if report["seam_amplitude_delta"] > 0.08:
            fails.append("descontinuidade de amplitude no seam")
        out = tmpdir / "loop.wav"
        write_wav(out, cropped, sr)
        if not out.is_file():
            fails.append("loop nao gravado")
        if report["loop_frames"] < target * 0.9 or report["loop_frames"] > target * 1.1:
            fails.append("comprimento do loop desviou demais do alvo")

        source_22k = tmpdir / "source_22k.wav"
        output_22k = tmpdir / "output_22k.wav"
        rate_22k = 22050
        source_samples = [
            math.sin(2 * math.pi * 220 * i / rate_22k)
            for i in range(rate_22k)
        ]
        write_wav(source_22k, source_samples, rate_22k)
        process_report = process(source_22k, output_22k, 0.25)
        if process_report["sample_rate"] != rate_22k:
            fails.append("process alterou a taxa de entrada")
        if wav_info(output_22k)["sample_rate"] != rate_22k:
            fails.append("arquivo de saida nao preservou a taxa")
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
    # loop maior que o audio deve falhar
    bad = False
    try:
        crop_loop([0.0, 0.1, -0.1], 10)
    except ValueError:
        bad = True
    fixtures.append({
        "fixture": "rejects_loop_exceeding_audio",
        "kind": "negative",
        "passed": bad,
        "blocker": "audio_self_check_expected_blocker:rejects_loop_exceeding_audio",
        "detail": [] if bad else ["aceitou loop maior que o audio"],
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
        "rule_ref": "premium-audio-pipeline (seamless_loop_report) + xgm2.txt loop",
        "exercised": "corte em zero-crossing de senoide; rejeicao de loop > audio.",
        "limitation": "Reduz clique; nao faz crossfade nem prova a nao-fadiga auditiva.",
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TOOL_NAME + " (loop sem clique).")
    parser.add_argument("--input", dest="input", metavar="WAV",
                        help="WAV de authoring.")
    parser.add_argument("--out", dest="out", metavar="WAV",
                        help="WAV de saida (loop recortado).")
    parser.add_argument("--duration", type=float, default=1.0,
                        help="duracao do loop em segundos.")
    parser.add_argument("--radius", type=int, default=1024,
                        help="janela de busca de zero-crossing (frames).")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    if not args.input or not args.out:
        parser.print_help()
        return 2
    try:
        report = process(Path(args.input), Path(args.out), args.duration, args.radius)
    except ValueError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    result = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "generated_at": now_iso(),
        "input": str(args.input),
        "output": str(args.out),
        "sample_rate": report["sample_rate"],
        "duration_s": args.duration,
        "next": "tools/audio-tools/sample_convert.py --input <loop> --rate <13300|6650>",
        **report,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
