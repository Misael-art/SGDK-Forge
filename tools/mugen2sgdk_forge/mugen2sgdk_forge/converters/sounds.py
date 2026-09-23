"""Sons MUGEN (WAV em .snd) -> WAV mono 16-bit 13300 Hz para `WAV ... XGM2` do rescomp.

Conversao deterministica em Python puro (sem audioop): mixdown estereo, reamostragem linear.
O rescomp ainda converte para 8-bit assinado; aqui so padronizamos taxa/canais e medimos ROM.
Sons nao referenciados por nenhum controlador sao omitidos (registrado).
"""
from __future__ import annotations

import io
import struct
import wave
from dataclasses import dataclass

XGM2_RATE = 13300


@dataclass
class SoundOut:
    index: int            # indice no .snd (mesmo usado pelos controladores)
    group: int
    sample: int
    wav: bytes
    rom_bytes: int        # estimativa 8-bit na ROM
    seconds: float


def _to_mono16(snd) -> tuple[list[int], int]:
    with wave.open(io.BytesIO(snd.wav)) as w:
        n, ch, width, rate = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    if width == 1:
        vals = [(b - 128) << 8 for b in raw]
    elif width == 2:
        vals = list(struct.unpack(f"<{len(raw) // 2}h", raw))
    else:
        raise ValueError(f"WAV {width * 8}-bit nao suportado")
    if ch > 1:
        vals = [sum(vals[i:i + ch]) // ch for i in range(0, len(vals) - ch + 1, ch)]
    return vals, rate


def _resample(vals: list[int], src: int, dst: int) -> list[int]:
    if src == dst or not vals:
        return vals
    n_out = max(1, len(vals) * dst // src)
    out = []
    last = len(vals) - 1
    for i in range(n_out):
        num = i * src
        j, frac = divmod(num, dst)
        a = vals[min(j, last)]
        b = vals[min(j + 1, last)]
        out.append(a + (b - a) * frac // dst)
    return out


def convert(ch, used: set[int]) -> tuple[list[SoundOut], dict]:
    outs, rep = [], {"converted": [], "skipped_unused": 0, "errors": []}
    for i, s in enumerate(ch.sounds):
        if i not in used:
            rep["skipped_unused"] += 1
            continue
        if s.error:
            rep["errors"].append({"sound": [s.group, s.sample], "error": s.error})
            continue
        try:
            vals, rate = _to_mono16(s)
        except ValueError as e:
            rep["errors"].append({"sound": [s.group, s.sample], "error": str(e)})
            continue
        vals = _resample(vals, rate, XGM2_RATE)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(XGM2_RATE)
            w.writeframes(struct.pack(f"<{len(vals)}h", *vals))
        o = SoundOut(i, s.group, s.sample, buf.getvalue(), len(vals), len(vals) / XGM2_RATE)
        outs.append(o)
        rep["converted"].append({"sound": [s.group, s.sample], "from": f"{s.channels}ch {s.rate}Hz",
                                 "seconds": round(o.seconds, 3), "rom_bytes": o.rom_bytes})
    rep["rom_bytes_total"] = sum(o.rom_bytes for o in outs)
    return outs, rep
