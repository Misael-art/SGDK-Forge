#!/usr/bin/env python3
"""Nucleo compartilhado do audio toolkit do workspace (mega drive / SGDK).

Eh o "oraculo" numerico de audio na linha do `forge_art/vdp_color.py` do lado
visual: cada regra dura do som do Mega Drive vive aqui como funcao pura,
testavel por `--self-check`, e os demais scripts de `tools/audio-tools/`
apenas encanam essas regras.

Regras duras codificadas (fonte): `sdk/sgdk-2.11/bin/rescomp.txt` e
`sdk/sgdk-2.11/bin/xgm2.txt`, nao invencao:

- XGM2 mixed PCM: payload 8 bit SIGNED, taxa fixa de 13.3 Khz ou 6.65 Khz.
  WAV PCM de 8 bits, por outro lado, usa armazenamento UNSIGNED com centro 128.
  `WAV name wav_file XGM2 [out_rate]`, out_rate so aceita 6650 ou 13300
  (default 13300). Metodos: XGM2_playPCM(..).
- XGM2 suporta 3 canais PCM (CH1 musica, CH2/CH3 FX). Ver xgm2.txt.
- Endereco de sample XGM2 e relativo ao bloco SDAT /256 -> payload de sample
  deve ser alinhado a 256 bytes (pad com 0) para a tabela de IDs fechar limpa.

Limitacao honesta: este modulo prova conformidade numerica/formato. NAO prova
qualidade de mix, identidade de gerero nem reserva de frequencia. Isso vive nas
skills de composicao (Fase 3 do plano de proficiencia em audio).
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import sys
import wave
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "audio_core"
TOOL_VERSION = "1.0.0"

# Regras duras do XGM2 (rescomp.txt + xgm2.txt).
XGM2_RATE_FULL = 13300
XGM2_RATE_HALF = 6650
XGM2_RATES = frozenset({XGM2_RATE_FULL, XGM2_RATE_HALF})
XGM2_SAMPLE_SIZE_BYTES = 1   # 8 bit signed
XGM2_SAMPLE_ALIGN = 256      # enderecos /256 -> alinhar payload
XGM2_PCM_CHANNELS = 3
XGM2_MUSIC_CHANNEL = 1       # reservado a musica; FX em CH2/CH3

XGM2_MAGIC = b"XGM2"
XGM2_VERSION = 0x10

VGM_MAGIC = b"Vgm "


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clamp_long_center(value: float) -> int:
    """Converte float PCM em 8 bit signed (-128..127) saturando nao estourando.

    XGM2 espera 8 bit signed. O dominio de authoring e 16 bit; a reducao a
    8 bit (mitad de resolucao) e o que da o timbre de sample de Mega Drive.
    """
    return max(-128, min(127, round(value)))


# ----------------------------------------------------------------------------
# WAV (16 bit PCM ideal como fonte de authoring) -> XGM2 8 bit signed.
# ----------------------------------------------------------------------------

def wav_info(path: Path) -> dict:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frames = source.getnframes()
        comp = source.getcomptype()
    if channels < 1 or sample_width not in (1, 2) or comp != "NONE":
        raise ValueError("espera WAV PCM (1 ou 2 bytes de ampl.) sem compressao")
    return {
        "path": str(path),
        "channels": channels,
        "sample_width": sample_width,
        "sample_rate": sample_rate,
        "frames": frames,
        "duration_s": (frames / sample_rate) if sample_rate else 0.0,
    }


def read_wav(path: Path) -> list[float]:
    """Le um WAV mono/estereo e devolve PCM float mono (-1..1).

    Aceita authoring PCM de 16 bits e WAV PCM de 8 bits. No container RIFF,
    amostras de 8 bits sao unsigned e usam 128 como silencio; o payload XGM2
    signed so e produzido depois por ``to_xgm2_pcm``.
    """
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        frames = source.getnframes()
        comp = source.getcomptype()
        if channels < 1 or sample_width not in (1, 2) or comp != "NONE":
            raise ValueError("espera WAV PCM (1 ou 2 bytes) sem compressao")
        raw = source.readframes(frames)

    if sample_width == 1:
        values = raw
        norm = 128.0
    else:
        values = array.array("h")
        values.frombytes(raw)
        if sys.byteorder != "little":
            values.byteswap()
        norm = 32768.0
    mixed = []
    for frame in range(frames):
        base = frame * channels
        total = 0.0
        for channel in range(channels):
            value = values[base + channel]
            total += (value - 128) if sample_width == 1 else value
        mixed.append(total / (norm * channels))
    return mixed


def write_wav(path: Path, samples: list[float], sample_rate: int) -> None:
    """Escreve WAV PCM 16 bit mono a partir de float (-1..1), clipando seguro."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        frames = array.array("h")
        for value in samples:
            int_value = max(-32768, min(32767, round(value * 32768.0)))
            frames.append(int_value)
        if sys.byteorder != "little":
            frames.byteswap()
        output.writeframes(frames.tobytes())


def write_wav_8bit(path: Path, samples: list[float], sample_rate: int) -> None:
    """Escreve WAV PCM 8 bit mono com o bias unsigned do RIFF/WAVE.

    O sinal de authoring continua em ``-1..1``. O arquivo WAV usa centro 128;
    ``to_xgm2_pcm`` remove esse bias e produz o payload signed do driver.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(1)
        output.setframerate(sample_rate)
        frames = bytearray()
        for value in samples:
            signed = clamp_long_center(value * 127.0)
            frames.append(max(0, min(255, signed + 128)))
        output.writeframes(bytes(frames))


def resample_samplerate(samples: list[float], source_rate: int, target_rate: int) -> list[float]:
    """Reduz/aumenta taxa por interpolacao linear, como rota tecnica basica.

    A funcao nao afirma qualidade perceptiva nem equivalencia ao ResComp. Uma
    rota de entrega deve comparar aliasing e escuta no hardware/emulador.
    """
    if source_rate == target_rate:
        return list(samples)
    if source_rate <= 0 or target_rate <= 0:
        raise ValueError("taxas devem ser > 0")
    ratio = target_rate / source_rate
    out_count = round(len(samples) * ratio)
    if out_count == 0:
        return []
    result = []
    for i in range(out_count):
        source_pos = i / ratio
        index = int(source_pos)
        frac = source_pos - index
        left = samples[index] if index < len(samples) else 0.0
        right = samples[index + 1] if index + 1 < len(samples) else left
        result.append(left + (right - left) * frac)
    return result


def to_xgm2_pcm(samples: list[float], sample_rate: int, target_rate: int) -> tuple[bytes, dict]:
    """Converte PCM float authoring -> bytes 8 bit signed no formato XGM2.

    Retorna (payload_bytes, metrics). O payload e alinhado a 256 bytes com 0
    (regra XGM2: endereco de sample relativo ao SDAT /256).
    """
    if target_rate not in XGM2_RATES:
        raise ValueError(
            f"taxa XGM2 invalida {target_rate}; aceita {sorted(XGM2_RATES)}")
    resampled = resample_samplerate(samples, sample_rate, target_rate)
    signed = []
    peak = 0.0
    for value in resampled:
        byte = clamp_long_center(value * 127.0)
        peak = max(peak, abs(value))
        signed.append(byte)
    padding = (XGM2_SAMPLE_ALIGN - (len(signed) % XGM2_SAMPLE_ALIGN)) % XGM2_SAMPLE_ALIGN
    payload = bytes(b & 0xFF for b in signed) + (b"\x00" * padding)
    peak_signed = max((abs(b) for b in signed), default=0)
    metrics = {
        "source_sample_rate": sample_rate,
        "target_sample_rate": target_rate,
        "source_frames": len(samples),
        "payload_frames": len(signed),
        "payload_bytes": len(payload),
        "align_padding_bytes": padding,
        "256_aligned": (len(payload) % XGM2_SAMPLE_ALIGN == 0),
        "peak_amplitude": round(peak, 6),
        "peak_signed_level": peak_signed,
        "clipped": peak_signed >= 128,
    }
    return bytes(payload), metrics


def c_array_format(data: bytes, name: str, per_line: int = 16) -> str:
    """Formata payload 8 bit signed como array C `const u8 name[] = {...}`."""
    parts = []
    for index, byte in enumerate(data):
        signed = byte - 256 if byte >= 128 else byte
        if index % per_line == 0:
            parts.append("\n    ")
        parts.append(f"{signed:+d},")
    body = "".join(parts).rstrip(",")
    return f"const u8 {name}[{len(data)}] = {{{body}\n}};"


# ----------------------------------------------------------------------------
# VGM header (minimo necessario para reportar/auditar, nao re-implementar o
# conversor; xgm2tool faz o parse completo).
# ----------------------------------------------------------------------------

def vgm_info(data: bytes) -> dict:
    """Le o essencial do header VGM 1.x para reportar taxa/versao/regiao."""
    if len(data) < 0x40 or data[0:4] != VGM_MAGIC:
        raise ValueError("arquivo nao parece um VGM valido (magic 'Vgm ' ausente)")
    eof_relative = int.from_bytes(data[0x04:0x08], "little")
    version = int.from_bytes(data[0x08:0x0C], "little")
    rate = int.from_bytes(data[0x24:0x28], "little")
    if eof_relative and eof_relative + 4 > len(data):
        raise ValueError("header VGM declara EOF alem do tamanho do arquivo")
    return {
        "version": f"{(version >> 8) & 0xff}.{version & 0xff:02x}",
        "raw_version": version,
        "eof_offset_absolute": eof_relative + 4 if eof_relative else None,
        "playback_rate_hz": rate or None,
        "system_hint": "PAL" if rate == 50 else ("NTSC" if rate == 60 else "AUTO"),
        "size_bytes": len(data),
    }


def xgm2_info(data: bytes) -> dict:
    if len(data) < 0x0C or data[0:4] != XGM2_MAGIC:
        raise ValueError("arquivo nao parece um XGM2 valido (magic 'XGM2' ausente)")
    version = data[4]
    fmt = data[5]
    slen = int.from_bytes(data[6:8], "little")
    fmlen = int.from_bytes(data[8:10], "little")
    psglen = int.from_bytes(data[10:12], "little")
    return {
        "magic": "XGM2",
        "version_hex": f"0x{version:02x}",
        "format": {
            "value": fmt,
            "ntsc_vs_pal": "NTSC" if (fmt & 0x01) == 0 else "PAL",
            "multi_track": bool(fmt & 0x02),
            "gd3": bool(fmt & 0x04),
            "packed": bool(fmt & 0x08),
        },
        "sample_block_bytes": slen * 256,
        "fm_block_bytes": fmlen * 256,
        "psg_block_bytes": psglen * 256,
        "size_bytes": len(data),
    }


# ----------------------------------------------------------------------------
# Self-check (positivo + negativo). Convencao do workspace.
# ----------------------------------------------------------------------------

def _positive_fixtures() -> list[dict]:
    name = "audio_core_roundtrip"
    fails = []
    try:
        source = [math.sin(2 * math.pi * 440 * i / 44100) * 0.5 for i in range(44100)]
        payload, metrics = to_xgm2_pcm(source, 44100, XGM2_RATE_FULL)
        if not metrics["256_aligned"]:
            fails.append("payload nao alinhado a 256")
        if len(payload) != metrics["payload_bytes"]:
            fails.append("contagem de bytes divergente")
        if metrics["payload_frames"] <= 0:
            fails.append("payload vazio")
        # seno de amplitude 0.5 nao pode clipar a resolucao de 8 bit
        if metrics["clipped"]:
            fails.append("seno 0.5 clipou a resolucao de 8 bit")
    except Exception as exc:  # noqa: BLE001
        fails.append(f"excecao: {exc}")
    fixtures = [{
        "fixture": name,
        "kind": "positive",
        "passed": not fails,
        "blocker": "audio_self_check_failed:" + name,
        "detail": fails,
    }]

    wav_fails = []
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            wav_path = Path(tmp) / "u8_roundtrip.wav"
            source = [-0.75, -0.25, 0.0, 0.25, 0.75]
            write_wav_8bit(wav_path, source, XGM2_RATE_FULL)
            with wave.open(str(wav_path), "rb") as wav:
                raw = wav.readframes(wav.getnframes())
            if raw[2] != 128:
                wav_fails.append("silencio WAV 8-bit nao foi codificado como 128")
            decoded = read_wav(wav_path)
            if not (decoded[0] < 0 < decoded[-1]):
                wav_fails.append("round-trip WAV 8-bit perdeu o sinal")
    except Exception as exc:  # noqa: BLE001
        wav_fails.append(f"excecao: {exc}")
    fixtures.append({
        "fixture": "wav_u8_bias_roundtrip",
        "kind": "positive",
        "passed": not wav_fails,
        "blocker": "audio_self_check_failed:wav_u8_bias_roundtrip",
        "detail": wav_fails,
    })

    vgm_fails = []
    try:
        header = bytearray(0x40)
        header[0:4] = VGM_MAGIC
        header[4:8] = (0x3C).to_bytes(4, "little")
        header[8:12] = (0x00000171).to_bytes(4, "little")
        header[0x24:0x28] = (60).to_bytes(4, "little")
        parsed = vgm_info(bytes(header))
        if parsed["raw_version"] != 0x171 or parsed["system_hint"] != "NTSC":
            vgm_fails.append("offsets canonicos do header VGM foram interpretados errado")
    except Exception as exc:  # noqa: BLE001
        vgm_fails.append(f"excecao: {exc}")
    fixtures.append({
        "fixture": "vgm_header_offsets",
        "kind": "positive",
        "passed": not vgm_fails,
        "blocker": "audio_self_check_failed:vgm_header_offsets",
        "detail": vgm_fails,
    })
    return fixtures


def _negative_fixtures() -> list[dict]:
    fixtures = []
    # taxa XGM2 invalida
    bad_rate = False
    try:
        to_xgm2_pcm([0.0, 0.1], 44100, 11025)
    except ValueError:
        bad_rate = True
    fixtures.append({
        "fixture": "rejects_non_xgm2_rate",
        "kind": "negative",
        "passed": bad_rate,
        "blocker": "audio_self_check_expected_blocker:rejects_non_xgm2_rate",
        "detail": [] if bad_rate else ["aceptou taxa 11025 que nao e 6650/13300"],
    })
    # wav nao-PCM16 deve falhar
    bad_wav = False
    try:
        wav_info(Path("/dev/null"))
    except (ValueError, wave.Error, EOFError, OSError):
        bad_wav = True
    fixtures.append({
        "fixture": "rejects_missing_or_invalid_wav",
        "kind": "negative",
        "passed": bad_wav,
        "blocker": "audio_self_check_expected_blocker:rejects_missing_or_invalid_wav",
        "detail": [] if bad_wav else ["wav_info nao recusou /dev/null"],
    })
    return fixtures


def self_check() -> dict:
    fixtures = _positive_fixtures() + _negative_fixtures()
    failed = [f for f in fixtures if not f["passed"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "rescomp.txt (WAV/XGM2) e xgm2.txt",
        "sources": {
            "xgm2_rate": "sdk/sgdk-2.11/bin/rescomp.txt:475",
            "xgm2_align": "sdk/sgdk-2.11/bin/xgm2.txt:61 (SID /256)",
        },
        "exercised": (
            "round-trip de PCM 16bit -> resample -> 8bit signed alinhado a 256; "
            "rejeicao de taxa fora de 6650/13300; rejeicao de ficheiro nao-WAV."
        ),
        "limitation": (
            "Prova conformidade de formato e alinhamento de sample. Nao prova "
            "qualidade de mix, identidade sonora nem reserva de frequencia."
        ),
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def _cmd_self_check() -> int:
    report = self_check()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["blocking"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Oraculo numerico de audio do workspace (Mega Drive / SGDK).")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)
    if args.self_check:
        return _cmd_self_check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
