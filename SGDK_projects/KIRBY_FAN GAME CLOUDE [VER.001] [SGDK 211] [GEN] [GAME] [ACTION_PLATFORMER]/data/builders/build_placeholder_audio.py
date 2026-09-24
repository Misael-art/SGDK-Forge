#!/usr/bin/env python3
"""Generate PLACEHOLDER audio: one VGM tune + a few 8-bit PCM samples.

This is not the composed soundtrack. doc/17-audio-design.md specifies 8 tracks
authored in Furnace by a composer; this generator exists so the XGM2 pipeline
can be exercised end to end and, above all, so the CPU cost of having audio
running can be MEASURED before anyone writes a note. The boss arena was already
at 90% CPU, and audio competes for the same VBlank.

VGM format reference used: header fields at the offsets below, command stream of
0x52/0x53 (YM2612 port 0/1), 0x50 (SN76489), 0x62 (wait one NTSC frame),
0x66 (end). Sample clock is 44100 Hz.
"""

from pathlib import Path
import struct
import math
import wave

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "res" / "audio"
SFX = ROOT / "res" / "sfx"

YM_CLOCK = 7670454
SN_CLOCK = 3579545
FRAME_SAMPLES = 735          # 44100 / 60


# --------------------------------------------------------------------------
# YM2612 helpers
# --------------------------------------------------------------------------
class Vgm:
    def __init__(self):
        self.data = bytearray()
        self.frames = 0
        self.loop_at = None

    def ym0(self, reg, val):
        self.data += bytes((0x52, reg & 0xFF, val & 0xFF))

    def ym1(self, reg, val):
        self.data += bytes((0x53, reg & 0xFF, val & 0xFF))

    def psg(self, val):
        self.data += bytes((0x50, val & 0xFF))

    def wait_frame(self, n=1):
        for _ in range(n):
            self.data += bytes((0x62,))
        self.frames += n

    def mark_loop(self):
        self.loop_at = len(self.data)

    def build(self) -> bytes:
        body = bytes(self.data) + bytes((0x66,))
        header = bytearray(0x100)
        header[0x00:0x04] = b"Vgm "
        struct.pack_into("<I", header, 0x08, 0x00000150)   # version 1.50
        struct.pack_into("<I", header, 0x0C, SN_CLOCK)
        struct.pack_into("<I", header, 0x2C, YM_CLOCK)
        struct.pack_into("<I", header, 0x24, 60)           # rate
        total = self.frames * FRAME_SAMPLES
        struct.pack_into("<I", header, 0x18, total)
        # data offset is relative to 0x34
        struct.pack_into("<I", header, 0x34, 0x100 - 0x34)
        if self.loop_at is not None:
            loop_abs = 0x100 + self.loop_at
            struct.pack_into("<I", header, 0x1C, loop_abs - 0x1C)
            struct.pack_into("<I", header, 0x20, total)
        # EOF offset relative to 0x04
        struct.pack_into("<I", header, 0x04, (0x100 + len(body)) - 0x04)
        return bytes(header) + body


# Operator register offsets within a channel.
OP = (0x00, 0x08, 0x04, 0x0C)


def patch(v: Vgm, ch: int, algo: int, feedback: int,
          ops):  # ops = list of (mul, tl, ar, d1r, d2r, rr, sl)
    """Program one FM channel. ch is 0..2 (port 0) or 3..5 (port 1)."""
    write = v.ym0 if ch < 3 else v.ym1
    base = ch % 3
    for i, (mul, tl, ar, d1r, d2r, rr, sl) in enumerate(ops):
        o = OP[i]
        write(0x30 + o + base, mul & 0x0F)
        write(0x40 + o + base, tl & 0x7F)
        write(0x50 + o + base, ar & 0x1F)
        write(0x60 + o + base, d1r & 0x1F)
        write(0x70 + o + base, d2r & 0x1F)
        write(0x80 + o + base, ((sl & 0x0F) << 4) | (rr & 0x0F))
    write(0xB0 + base, ((feedback & 7) << 3) | (algo & 7))
    write(0xB4 + base, 0xC0)          # both speakers


# Equal-tempered note -> (block, fnum) for the YM2612.
def ym_note(midi):
    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    block = 4
    while freq < 262.0 and block > 0:
        freq *= 2.0
        block -= 1
    while freq >= 524.0 and block < 7:
        freq /= 2.0
        block += 1
    fnum = int(round((freq * 144.0 * (1 << 21)) / YM_CLOCK)) >> (block)
    fnum = max(0, min(2047, fnum))
    return block, fnum


def note_on(v: Vgm, ch: int, midi):
    write = v.ym0 if ch < 3 else v.ym1
    base = ch % 3
    block, fnum = ym_note(midi)
    write(0xA4 + base, ((block & 7) << 3) | ((fnum >> 8) & 3))
    write(0xA0 + base, fnum & 0xFF)
    key = 0xF0 | (base + (4 if ch >= 3 else 0))
    v.ym0(0x28, key)


def note_off(v: Vgm, ch: int):
    base = ch % 3
    v.ym0(0x28, base + (4 if ch >= 3 else 0))


# PSG: channel 0..2 tone, 3 noise. Attenuation 0 (loud) .. 15 (off).
def psg_note(v: Vgm, ch, midi, atten):
    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    n = int(round(SN_CLOCK / (32.0 * freq)))
    n = max(1, min(1023, n))
    v.psg(0x80 | (ch << 5) | (n & 0x0F))
    v.psg((n >> 4) & 0x3F)
    v.psg(0x90 | (ch << 5) | (atten & 0x0F))


def psg_off(v: Vgm, ch):
    v.psg(0x90 | (ch << 5) | 0x0F)


# --------------------------------------------------------------------------
# The tune: Vegetable Valley, G major, 138 BPM (doc/17-audio-design.md 1.3).
# Bass on FM1, lead on FM3, PSG1 doubles the lead an octave up.
# --------------------------------------------------------------------------
def build_stage_theme() -> bytes:
    v = Vgm()
    v.ym0(0x22, 0x00)     # LFO off
    v.ym0(0x27, 0x00)     # normal mode
    v.ym0(0x2B, 0x00)     # DAC off

    # SILENCE ALL FOUR PSG CHANNELS FIRST.
    # The PSG powers up at attenuation 0 (maximum) on every channel, so any
    # channel the tune does not use would sing a tone forever. Silencing unused
    # channels is correct practice on this chip.
    #
    # HONEST NOTE: this was added on 2026-08-06 to fix a "full-scale square
    # wave" that turned out NOT to exist -- I had misread audio.raw as int16
    # when BlastEm writes 32-bit float, and my dB figures were garbage. The real
    # level was -18.5 dBFS peak all along. The change is kept because it is
    # right, NOT because it fixed the imagined problem.
    for _ch in range(4):
        v.psg(0x90 | (_ch << 5) | 0x0F)

    # Key everything off so a warm reset cannot leave a note sustaining.
    for _c in range(3):
        v.ym0(0x28, _c)
        v.ym0(0x28, _c + 4)

    # Bass: algorithm 4, punchy short decay.
    patch(v, 0, algo=4, feedback=5,
          ops=[(1, 30, 31, 12, 6, 8, 2), (1, 18, 31, 10, 5, 8, 2),
               (2, 40, 31, 14, 7, 8, 3), (1, 20, 31, 12, 6, 9, 2)])
    # Lead: algorithm 2, brighter.
    patch(v, 2, algo=2, feedback=4,
          ops=[(2, 36, 31, 10, 4, 7, 1), (1, 26, 31, 9, 4, 7, 1),
               (1, 34, 31, 10, 4, 7, 1), (1, 16, 31, 8, 3, 7, 1)])

    # 138 BPM -> an eighth note is about 13 frames at 60 Hz.
    E = 13
    G3, A3, B3, D4, G4 = 55, 57, 59, 62, 67
    lead = [G4, B3 + 12, D4 + 12, B3 + 12, G4, D4 + 12, B3 + 12, G4]
    bass = [G3, G3, D4 - 12, D4 - 12, A3, A3, B3, B3]

    v.mark_loop()
    for bar in range(4):
        for i in range(8):
            note_on(v, 0, bass[i] - 12)
            note_on(v, 2, lead[(i + bar) % 8])
            psg_note(v, 0, lead[(i + bar) % 8] + 12, 9)
            v.wait_frame(E - 3)
            note_off(v, 0)
            note_off(v, 2)
            psg_off(v, 0)
            v.wait_frame(3)
    return v.build()


# --------------------------------------------------------------------------
# PCM samples, 8-bit unsigned. doc/SOUNDMAP.md 4: 13300 Hz or 6650 Hz.
# Normalised to -3 dBFS peak so two simultaneous PCM channels cannot clip.
# --------------------------------------------------------------------------
PEAK = 0.707      # -3 dBFS


def write_wav(path: Path, rate: int, samples):
    peak = max(1e-6, max(abs(s) for s in samples))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(bytes(
            max(0, min(255, int(128 + 127 * PEAK * (s / peak))))
            for s in samples
        ))


def noise_sweep(rate, seconds, f0, f1):
    n = int(rate * seconds)
    out = []
    state = 0x1234
    for i in range(n):
        t = i / n
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        noise = ((state >> 16) & 0xFF) / 128.0 - 1.0
        env = (1.0 - t) ** 2
        cut = f0 + (f1 - f0) * t
        out.append(noise * env * math.sin(2 * math.pi * cut * i / rate) * 0.5
                   + noise * env * 0.5)
    return out


def thump(rate, seconds, f0, f1):
    n = int(rate * seconds)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        phase += 2 * math.pi * f / rate
        out.append(math.sin(phase) * ((1.0 - t) ** 3))
    return out


def main():
    AUDIO.mkdir(parents=True, exist_ok=True)
    SFX.mkdir(parents=True, exist_ok=True)

    vgm = build_stage_theme()
    (AUDIO / "mus_stage_valley.vgm").write_bytes(vgm)
    print(f"  res/audio/mus_stage_valley.vgm  {len(vgm)} bytes")

    # Inhale: long airy noise, half rate to halve the ROM cost (SOUNDMAP 4.1).
    write_wav(SFX / "sfx_inhale.wav", 6650, noise_sweep(6650, 0.55, 300, 1400))
    # Swallow and damage: short transients that must cut through the music.
    write_wav(SFX / "sfx_swallow.wav", 13300, thump(13300, 0.18, 420, 90))
    write_wav(SFX / "sfx_hurt.wav", 13300, thump(13300, 0.22, 700, 120))

    total = 0
    for p in sorted(SFX.glob("*.wav")):
        total += p.stat().st_size
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size} bytes")
    print(f"  PCM total: {total} bytes ({total / 1024:.1f} KB) "
          f"de 384 KB de orcamento")


if __name__ == "__main__":
    main()
