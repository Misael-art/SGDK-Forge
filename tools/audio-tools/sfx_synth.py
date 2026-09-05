#!/usr/bin/env python3
"""Sintetizador de SFX de Mega Drive (som PL/SFX) no estilo de tooling por primitivas.

Gera WAV 16bit mono como fonte de authoring; passe por `sample_convert.py`
para derivar o payload PCM XGM2 (8bit signed, 13.3/6.65kHz alinhado a 256).

Primitivas (os manos da sonaplastia de chip):
  - noise   : burst de ruido (estilo PSG noise) com decaimento -- impacto, terra.
  - thump   : tom grave com queda rapida de frequencia + env AG -- "peso", nao "whoosh".
  - whoosh  : ruido filtrado com varredura e fade in/out -- passagem, arrow.
  - blip    : tom curto quadrado/triangular -- UI, tecla, inflar.
  - bell    : senoide + harmonicos com decaimento tonal -- anel/coleta.

Determinismo: PRNG seedado (default 0) para o ruido, para self-check e jobs
imutaveis.

Exemplo:
  python3 tools/audio-tools/sfx_synth.py --type thump --out hit.wav \\
      --dur 0.22 --freq-start 120 --freq-end 40 --amp 0.9
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

from audio_core import SCHEMA_VERSION, now_iso, write_wav

TOOL_NAME = "sfx_synth"
TOOL_VERSION = "1.0.0"


def render_noise(duration: float, sr: int, amp: float, decay: float,
                 seed: int = 0, color: str = "white") -> list[float]:
    count = int(duration * sr)
    rng = random.Random(seed)
    out = []
    if color not in {"white", "pink"}:
        raise ValueError("color deve ser white ou pink")
    pink_rows = [rng.uniform(-1, 1) for _ in range(16)]
    pink_sum = sum(pink_rows)
    for i in range(count):
        if color == "pink":
            # Voss-McCartney deterministico: atualiza uma oitava por amostra
            # e soma ruido branco para evitar degraus audiveis.
            counter = i + 1
            row = (counter & -counter).bit_length() - 1
            if row < len(pink_rows):
                pink_sum -= pink_rows[row]
                pink_rows[row] = rng.uniform(-1, 1)
                pink_sum += pink_rows[row]
            value = (pink_sum + rng.uniform(-1, 1)) / (len(pink_rows) + 1)
        else:
            value = rng.uniform(-1, 1)
        out.append(value * amp * math.exp(-decay * i / sr))
    return out


def render_thump(duration: float, sr: int, amp: float, freq_start: float,
                 freq_end: float, decay: float) -> list[float]:
    count = int(duration * sr)
    phase = 0.0
    out = []
    for i in range(count):
        t = i / sr
        freq = freq_start + (freq_end - freq_start) * (i / count)
        phase += 2 * math.pi * freq / sr
        out.append(math.sin(phase) * amp * math.exp(-decay * t))
    return out


def render_whoosh(duration: float, sr: int, amp: float, fade: float,
                  seed: int = 0) -> list[float]:
    count = int(duration * sr)
    rng = random.Random(seed)
    out = []
    for i in range(count):
        t = i / count
        value = rng.uniform(-1, 1)
        if t < fade:
            value *= t / fade
        elif t > 1 - fade:
            value *= (1 - t) / fade
        out.append(value * amp)
    return out


def render_blip(duration: float, sr: int, amp: float, freq: float,
                shape: str = "square", decay: float = 8.0) -> list[float]:
    if shape not in {"square", "triangle"}:
        raise ValueError("shape deve ser square ou triangle")
    count = int(duration * sr)
    out = []
    for i in range(count):
        t = i / sr
        phase = (i * freq) / sr
        if shape == "triangle":
            ph = phase - math.floor(phase)
            wave = 4.0 * abs(ph - 0.5) - 1.0
        else:
            ph = phase - math.floor(phase)
            wave = 1.0 if ph < 0.5 else -1.0
        out.append(wave * amp * math.exp(-decay * t))
    return out


def render_bell(duration: float, sr: int, amp: float, freq: float,
                decay: float = 4.0) -> list[float]:
    count = int(duration * sr)
    out = []
    for i in range(count):
        t = i / sr
        value = (math.sin(2 * math.pi * freq * t) * 1.0) + \
                (math.sin(2 * math.pi * freq * 2.76 * t) * 0.4) + \
                (math.sin(2 * math.pi * freq * 5.4 * t) * 0.2)
        out.append(value * amp * math.exp(-decay * t) / 1.6)
    return out


PRIMITIVES = {
    "noise": render_noise,
    "thump": render_thump,
    "whoosh": render_whoosh,
    "blip": render_blip,
    "bell": render_bell,
}


def normalize(samples: list[float], target_peak: float = 0.9) -> list[float]:
    if not 0 < target_peak <= 1:
        raise ValueError("target_peak deve estar em (0, 1]")
    peak = max((abs(v) for v in samples), default=0.0)
    if peak < 1e-9:
        return samples
    factor = target_peak / peak
    return [v * factor for v in samples]


def render(type_key: str, duration: float, sr: int, amp: float,
           normalize_peak: float | None = None, **params) -> dict:
    if type_key not in PRIMITIVES:
        raise ValueError(f"primitiva desconhecida: {type_key}; aceita {sorted(PRIMITIVES)}")
    if duration <= 0 or sr <= 0:
        raise ValueError("duration e sr devem ser > 0")
    if not 0 <= amp <= 1:
        raise ValueError("amp deve estar em [0, 1]")
    if type_key == "whoosh" and not 0 < params.get("fade", 0.3) <= 0.5:
        raise ValueError("fade do whoosh deve estar em (0, 0.5]")
    fn = PRIMITIVES[type_key]
    from inspect import signature
    accepted = signature(fn).parameters
    kwargs = {k: v for k, v in params.items() if k in accepted}
    samples = fn(duration=duration, sr=sr, amp=amp, **kwargs)
    if normalize_peak is not None:
        samples = normalize(samples, normalize_peak)
    peak = max((abs(v) for v in samples), default=0.0)
    return {
        "type": type_key,
        "samples": samples,
        "peak": round(peak, 6),
        "frames": len(samples),
        "duration_s": round(len(samples) / sr, 6),
        "nan_free": all(math.isfinite(v) for v in samples),
    }


def _positive_fixtures(tmpdir: Path) -> list[dict]:
    name = "sfx_synth_renders_audible"
    fails = []
    try:
        hit = render("thump", 0.22, 44100, 0.9, normalize_peak=0.75,
                     freq_start=120, freq_end=40, decay=30)
        noise = render("noise", 0.1, 44100, 0.8, normalize_peak=0.75,
                       decay=60, seed=7, color="pink")
        if not hit["nan_free"] or not noise["nan_free"]:
            fails.append("amostras NaN")
        if hit["peak"] <= 0.0:
            fails.append("thump em silencio")
        if noise["frames"] == 0:
            fails.append("noise vazio")
        if hit["peak"] != 0.75:
            fails.append("normalize_peak nao foi respeitado")
        # escrever wav e re-ler
        wav = tmpdir / "thump.wav"
        write_wav(wav, hit["samples"], 44100)
        if not wav.is_file() or wav.stat().st_size == 0:
            fails.append("wav nao gravado")
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
    bad = False
    try:
        render("bogus", 0.1, 44100, 0.5)
    except ValueError:
        bad = True
    fixtures.append({
        "fixture": "rejects_unknown_primitiva",
        "kind": "negative",
        "passed": bad,
        "blocker": "audio_self_check_expected_blocker:rejects_unknown_primitiva",
        "detail": [] if bad else ["aceptou primitiva inexistente"],
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
        "rule_ref": "SGDK_GLOBAL.md 8.2 (som fotografo transitorio) + primitivas de chip",
        "exercised": "render thump e noise; rejeicao de primitiva desconhecida.",
        "limitation": "Gera fonte de authoring. Nao e mix final nem prova qualidade estetica.",
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TOOL_NAME + " (SFX por primitivas).")
    parser.add_argument("--type", dest="type_key", metavar="KIND",
                        help=f"primitiva: {sorted(PRIMITIVES)}")
    parser.add_argument("--out", dest="out", metavar="WAV",
                        help="escreve WAV 16bit monofonte.")
    parser.add_argument("--sr", type=int, default=44100, help="taxa de authoring.")
    parser.add_argument("--dur", type=float, default=0.2, help="duracao em segundos.")
    parser.add_argument("--amp", type=float, default=0.8, help="amplitude (0..1).")
    parser.add_argument("--seed", type=int, default=0, help="semente do ruido.")
    parser.add_argument("--freq-start", dest="freq_start", type=float, default=120.0)
    parser.add_argument("--freq-end", dest="freq_end", type=float, default=40.0)
    parser.add_argument("--freq", type=float, default=440.0)
    parser.add_argument("--decay", type=float, default=30.0)
    parser.add_argument("--color", default="white")
    parser.add_argument("--shape", default="square")
    parser.add_argument("--fade", type=float, default=0.3)
    parser.add_argument("--normalize-peak", type=float,
                        help="normaliza explicitamente para pico em (0,1]; sem flag, --amp prevalece")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    if not args.type_key or not args.out:
        parser.print_help()
        return 2
    try:
        result = render(
            args.type_key, args.dur, args.sr, args.amp,
            normalize_peak=args.normalize_peak,
            freq_start=args.freq_start, freq_end=args.freq_end, freq=args.freq,
            decay=args.decay, seed=args.seed, color=args.color, shape=args.shape,
            fade=args.fade,
        )
    except ValueError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 2
    write_wav(Path(args.out), result["samples"], args.sr)
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "generated_at": now_iso(),
        "output": str(args.out),
        "sample_rate": args.sr,
        "type": result["type"],
        "frames": result["frames"],
        "duration_s": result["duration_s"],
        "peak": result["peak"],
        "normalize_peak": args.normalize_peak,
        "next": "tools/audio-tools/sample_convert.py --input <wav> --rate <13300|6650>",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
