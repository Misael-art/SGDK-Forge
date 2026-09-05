"""Generate original FM/PSG VGM music and XGM2 PCM SFX for Celestial Chase."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import wave
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT / "res" / "audio" / "chase"
REPORT = PROJECT / "doc" / "sample_format_audit.json"
RATE = 13300
VGM_RATE = 60
VGM_WAIT_SAMPLES = 735
SN76489_CLOCK = 3579545
YM2612_CLOCK = 7670454


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clamp(value: float) -> int:
    return max(0, min(255, int(round(128 + value))))


def fade(index: int, length: int, edge: int) -> float:
    if index < edge:
        return index / edge
    if index >= length - edge:
        return (length - index - 1) / edge
    return 1.0


def write_wav(path: Path, samples: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(RATE)
        handle.writeframes(bytes(samples))


def ym_write(register: int, value: int, port: int = 0) -> bytes:
    return bytes((0x52 if port == 0 else 0x53, register & 0xFF, value & 0xFF))


def psg_write(value: int) -> bytes:
    return bytes((0x50, value & 0xFF))


def ym_instrument(channel: int, multipliers: tuple[int, int, int, int], levels: tuple[int, int, int, int]) -> bytes:
    data = bytearray()
    operator_offsets = (0, 4, 8, 12)
    for operator, offset in enumerate(operator_offsets):
        register_offset = offset + channel
        data += ym_write(0x30 + register_offset, multipliers[operator] & 0x0F)
        data += ym_write(0x40 + register_offset, levels[operator] & 0x7F)
        data += ym_write(0x50 + register_offset, 0x1F)
        data += ym_write(0x60 + register_offset, 0x0A)
        data += ym_write(0x70 + register_offset, 0x04)
        data += ym_write(0x80 + register_offset, 0x26)
        data += ym_write(0x90 + register_offset, 0x00)
    data += ym_write(0xB0 + channel, 0x07)
    data += ym_write(0xB4 + channel, 0xC0)
    return bytes(data)


def ym_note(channel: int, block: int, fnum: int, key_on: bool) -> bytes:
    data = bytearray()
    data += ym_write(0x28, channel)
    data += ym_write(0xA0 + channel, fnum & 0xFF)
    data += ym_write(0xA4 + channel, ((block & 0x07) << 3) | ((fnum >> 8) & 0x07))
    if key_on:
        data += ym_write(0x28, 0xF0 | channel)
    return bytes(data)


def psg_tone(channel: int, period: int, attenuation: int) -> bytes:
    latch = 0x80 | ((channel & 0x03) << 5) | (period & 0x0F)
    high = (period >> 4) & 0x3F
    volume = 0x90 | ((channel & 0x03) << 5) | (attenuation & 0x0F)
    return psg_write(latch) + psg_write(high) + psg_write(volume)


def build_chase_vgm() -> bytes:
    """Build an original 8-second NTSC loop using two FM voices and PSG pulse."""
    commands = bytearray()
    commands += ym_instrument(0, (1, 2, 3, 4), (0x24, 0x2C, 0x34, 0x18))
    commands += ym_instrument(1, (2, 1, 2, 6), (0x30, 0x26, 0x34, 0x14))
    commands += psg_write(0x9F) + psg_write(0xBF) + psg_write(0xDF) + psg_write(0xFF)

    loop_command_offset = 0x40 + len(commands)
    fm_notes = (644, 722, 810, 858, 722, 810, 964, 858)
    bass_notes = (644, 574, 644, 541, 644, 574, 510, 541)
    psg_periods = (508, 453, 404, 381, 453, 404, 339, 381)

    for step in range(16):
        note_index = step % len(fm_notes)
        commands += ym_note(0, 3, bass_notes[note_index], True)
        commands += ym_note(1, 4, fm_notes[note_index], True)
        commands += psg_tone(0, psg_periods[note_index], 8 if (step & 1) else 6)
        for frame in range(30):
            if frame == 24:
                commands += ym_write(0x28, 0x00)
                commands += ym_write(0x28, 0x01)
                commands += psg_write(0x9E)
            commands.append(0x62)

    commands += ym_write(0x28, 0x00)
    commands += ym_write(0x28, 0x01)
    commands += psg_write(0x9F)
    commands.append(0x66)

    total_samples = 16 * 30 * VGM_WAIT_SAMPLES
    header = bytearray(0x40)
    header[0:4] = b"Vgm "
    struct.pack_into("<I", header, 0x08, 0x00000150)
    struct.pack_into("<I", header, 0x0C, SN76489_CLOCK)
    struct.pack_into("<I", header, 0x18, total_samples)
    struct.pack_into("<I", header, 0x1C, loop_command_offset - 0x1C)
    struct.pack_into("<I", header, 0x20, total_samples)
    struct.pack_into("<I", header, 0x24, VGM_RATE)
    struct.pack_into("<H", header, 0x28, 0x0009)
    header[0x2A] = 16
    struct.pack_into("<I", header, 0x2C, YM2612_CLOCK)
    struct.pack_into("<I", header, 0x34, 0x0C)

    result = header + commands
    struct.pack_into("<I", result, 0x04, len(result) - 4)
    return bytes(result)


def audit_vgm_bytes(data: bytes) -> dict:
    if data[:4] != b"Vgm ":
        raise ValueError("invalid VGM signature")
    data_offset = 0x34 + struct.unpack_from("<I", data, 0x34)[0]
    command_data = data[data_offset:]
    position = 0
    uses_fm = False
    uses_psg = False
    waits = 0
    while position < len(command_data):
        command = command_data[position]
        if command in (0x52, 0x53):
            uses_fm = True
            position += 3
        elif command == 0x50:
            uses_psg = True
            position += 2
        elif command == 0x62:
            waits += 1
            position += 1
        elif command == 0x66:
            break
        else:
            raise ValueError(f"unsupported generated VGM command 0x{command:02X}")
    return {
        "format": "VGM",
        "version": "1.50",
        "rate_hz": struct.unpack_from("<I", data, 0x24)[0],
        "total_samples": struct.unpack_from("<I", data, 0x18)[0],
        "duration_seconds": round(struct.unpack_from("<I", data, 0x18)[0] / 44100.0, 3),
        "loop_samples": struct.unpack_from("<I", data, 0x20)[0],
        "sn76489_clock_hz": struct.unpack_from("<I", data, 0x0C)[0],
        "ym2612_clock_hz": struct.unpack_from("<I", data, 0x2C)[0],
        "uses_fm": uses_fm,
        "uses_psg": uses_psg,
        "wait_60hz_commands": waits,
    }


def build_tone(
    seconds: float,
    frequencies: tuple[float, ...],
    amplitude: float,
    noise: float = 0.0,
    descend: bool = False,
) -> list[int]:
    length = int(RATE * seconds)
    edge = max(1, int(RATE * min(0.025, seconds / 5.0)))
    result: list[int] = []
    seed = 0x4A31
    for index in range(length):
        time_s = index / RATE
        progress = index / max(1, length - 1)
        value = 0.0
        for frequency in frequencies:
            current = frequency * (1.0 - (0.35 * progress if descend else 0.0))
            value += math.sin(math.tau * current * time_s) * (amplitude / len(frequencies))
        if noise:
            seed = ((seed * 1103515245) + 12345) & 0x7FFFFFFF
            value += (((seed >> 16) & 0xFF) - 128) * noise
        envelope = (1.0 - progress) * fade(index, length, edge)
        result.append(clamp(value * envelope))
    result[0] = 128
    result[-1] = 128
    return result


def audit(path: Path) -> dict:
    with wave.open(str(path), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
        duration = handle.getnframes() / handle.getframerate()
    centered = [value - 128 for value in frames]
    return {
        "path": path.relative_to(PROJECT).as_posix(),
        "sha256": sha256(path),
        "channels": 1,
        "bits_per_sample": 8,
        "sample_rate_hz": RATE,
        "duration_seconds": round(duration, 3),
        "dc_offset": round(sum(centered) / max(1, len(centered)), 3),
        "peak": max(abs(value) for value in centered),
        "first_sample": frames[0],
        "last_sample": frames[-1],
        "loop_boundary_silent": frames[0] == 128 and frames[-1] == 128,
    }


def main() -> None:
    assets = {
        "chase_menu.wav": build_tone(0.12, (440.0, 660.0), 72.0),
        "chase_jump.wav": build_tone(0.18, (520.0, 780.0), 68.0),
        "chase_land.wav": build_tone(0.14, (130.0,), 62.0, noise=0.18, descend=True),
        "chase_hit.wav": build_tone(0.24, (92.0, 184.0), 76.0, noise=0.32, descend=True),
        "chase_pulse.wav": build_tone(0.46, (220.0, 440.0, 880.0), 72.0),
        "chase_pickup.wav": build_tone(0.16, (660.0, 990.0), 65.0),
        "chase_victory.wav": build_tone(0.72, (329.63, 493.88, 659.25), 64.0),
        "chase_failure.wav": build_tone(0.72, (196.0, 146.83, 98.0), 64.0, descend=True),
        "chase_pressure.wav": build_tone(0.20, (82.41, 164.81), 54.0, descend=True),
    }
    for name, samples in assets.items():
        write_wav(OUTPUT / name, samples)

    music_path = OUTPUT / "chase_core_fm_psg.vgm"
    music_data = build_chase_vgm()
    music_path.write_bytes(music_data)
    music_audit = audit_vgm_bytes(music_data)
    music_audit.update({
        "path": music_path.relative_to(PROJECT).as_posix(),
        "sha256": sha256(music_path),
        "source_size_bytes": len(music_data),
        "composition_basis": "project_local_original_fm_psg_sequence",
    })

    report = {
        "schema": "audio_source_audit_v2",
        "status": "generated_pending_validate_audio_and_blastem_listen",
        "generation_basis": "project_local_original_synthesis",
        "driver": "XGM2",
        "music": music_audit,
        "pcm_sfx": [audit(OUTPUT / name) for name in assets],
        "delivery_findings": [
            "The score is an original loop with YM2612 FM and SN76489 PSG commands.",
            "All SFX sources are mono PCM WAV at 13.3 kHz and 8-bit.",
            "Every PCM sample begins and ends at unsigned PCM center 128.",
            "The ResComp XGM2 conversion and human headphone review remain runtime gates.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
