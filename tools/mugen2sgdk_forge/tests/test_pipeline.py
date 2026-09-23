"""Contrato ponta a ponta com um personagem SINTETICO (sem conteudo de terceiros).

Monta um pacote MUGEN minimo em memoria (def/cmd/cns/air/sff v1 PCX/snd/act) e verifica
parsers, classificacao de fidelidade, conversao de sprites, sons e determinismo do gerador.
"""
import io
import json
import struct
import sys
import wave
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import __main__ as cli  # noqa: E402
from mugen2sgdk_forge import character  # noqa: E402
from mugen2sgdk_forge.converters import sprites  # noqa: E402
from mugen2sgdk_forge.parsers import air, cmd, ini  # noqa: E402
from mugen2sgdk_forge.source import Source  # noqa: E402


def pcx(w, h, fill_idx, pal):
    hdr = bytearray(128)
    hdr[0], hdr[1], hdr[2], hdr[3] = 10, 5, 1, 8
    struct.pack_into("<4H", hdr, 4, 0, 0, w - 1, h - 1)
    hdr[65] = 1
    struct.pack_into("<H", hdr, 66, w)
    body = bytearray()
    for y in range(h):
        row = [fill_idx if 1 <= x < w - 1 else 0 for x in range(w)]
        for v in row:
            if v >= 0xC0:
                body += bytes([0xC1, v])
            else:
                body.append(v)
    return bytes(hdr) + bytes(body) + b"\x0c" + bytes(c for rgb in pal for c in rgb)


def sff(images):
    """images: [(group, image, axisx, axisy, pcxbytes)]"""
    head = bytearray(512)
    head[:12] = b"ElecbyteSpr\0"
    head[12:16] = bytes([0, 1, 0, 1])
    struct.pack_into("<IIII", head, 16, 1, len(images), 512, 32)
    out = bytearray(head)
    pos = 512
    for i, (g, im, ax, ay, data) in enumerate(images):
        nxt = pos + 32 + len(data) if i + 1 < len(images) else 0
        sub = struct.pack("<IIhhHHHB", nxt, len(data), ax, ay, g, im, 0, 0 if i == 0 else 1).ljust(32, b"\0")
        out += sub + data
        pos += 32 + len(data)
    return bytes(out)


def wav(n=800, rate=22050, ch=2):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack(f"<{n * ch}h", *([1000, -1000] * (n * ch // 2))))
    return buf.getvalue()


def snd(sounds):
    head = bytearray(512)
    head[:12] = b"ElecbyteSnd\0"
    struct.pack_into("<II", head, 16, len(sounds), 512)
    out = bytearray(head)
    pos = 512
    for i, (g, s, data) in enumerate(sounds):
        nxt = pos + 16 + len(data) if i + 1 < len(sounds) else 0
        out += struct.pack("<IIII", nxt, len(data), g, s) + data
        pos += 16 + len(data)
    return bytes(out)


PAL = [(0, 0, 0)] * 256
PAL[5] = (200, 40, 40)
PAL[6] = (40, 200, 40)
PAL[40] = (250, 250, 0)

DEF = """[Info]
name = "Fixture"
author = "forge tests"
pal.defaults = 1
[Files]
cmd = f.cmd
cns = f.cns
stcommon = common1.cns
sprite = f.sff
anim = f.air
sound = f.snd
pal1 = p1.act
"""
CMD = """[Command]
name = "holdfwd"
command = /$F
time = 1
[Command]
name = "hadouken"
command = ~D, DF, F, x
[Command]
name = "x"
command = x
time = 1
[Statedef -1]
[State -1, soco]
type = ChangeState
trigger1 = command = "x" && ctrl
value = 200
[State -1, hadou]
type = ChangeState
triggerall = command = "hadouken"
trigger1 = ctrl
value = 1000
"""
CNS = """[Data]
life = 900
[Size]
ground.front = 16
[Velocity]
walk.fwd = 2.4
[Movement]
yaccel = .44
[Statedef 0]
type = S
physics = S
anim = 0
ctrl = 1
[Statedef 200]
type = S
movetype = A
physics = S
anim = 200
ctrl = 0
[State 200, hit]
type = HitDef
trigger1 = AnimElem = 2
attr = S, NA
damage = 30, 2
animtype = medium
hitsound = S1, 0
sparkno = S700
pausetime = 8, 8
ground.velocity = -4
[State 200, fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1
[State 200, rastro]
type = AfterImage
trigger1 = 1
[Statedef 1000]
type = S
movetype = A
anim = 200
[State 1000, bola]
type = Projectile
trigger1 = AnimElem = 2
projanim = 700
velocity = 5
damage = 60
[State 1000, som]
type = PlaySnd
trigger1 = Time = 0
value = 1, 0
"""
AIR = """[Begin Action 0]
Clsn2Default: 1
 Clsn2[0] = -10,-40, 10, 0
0,0, 0,0, 10
0,1, 0,0, 10
[Begin Action 200]
Clsn2: 1
 Clsn2[0] = -10,-40, 10, 0
0,0, 0,0, 3
Clsn1: 1
 Clsn1[0] = 5,-30, 30,-20
Clsn2: 1
 Clsn2[0] = -10,-40, 10, 0
200,0, 0,0, 4
0,0, 0,0, 3
[Begin Action 700]
700,0, 0,0, 4
"""


def make_pkg(tmp: Path) -> Path:
    p = tmp / "fixture.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("fx/f.def", DEF)
        z.writestr("fx/f.cmd", CMD)
        z.writestr("fx/f.cns", CNS)
        z.writestr("fx/f.air", AIR)
        z.writestr("fx/f.sff", sff([(0, 0, 8, 32, pcx(16, 32, 5, PAL)), (0, 1, 8, 32, pcx(16, 32, 6, PAL)),
                                    (200, 0, 8, 32, pcx(24, 32, 5, PAL)), (700, 0, 8, 8, pcx(16, 16, 40, PAL))]))
        z.writestr("fx/f.snd", snd([(1, 0, wav())]))
        z.writestr("fx/p1.act", bytes(c for rgb in reversed(PAL) for c in rgb))
    return p


def test_air_boxes_and_defaults():
    r = air.parse(AIR)
    a = r.actions[200]
    assert a.frames[0].clsn1 == [] and a.frames[1].clsn1 == [(5, -30, 30, -20)]
    assert r.actions[0].frames[1].clsn2 == [(-10, -40, 10, 0)]   # Clsn2Default herdado


def test_controller_belongs_to_last_statedef_not_label():
    from mugen2sgdk_forge.parsers import cns
    txt = "[Statedef 425]\ntype = C\n[State 261, fim]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = 11\n"
    r = cns.parse(ini.parse(txt), "x")
    assert [c.type for c in r.states[425].controllers] == ["changestate"]
    assert 261 not in r.states


def test_cmd_case_back_vs_button():
    steps, err = cmd.parse_command_string("B, b")
    assert [k.key for s in steps for k in s.keys] == ["B", "b"] and not err


def test_cmd_tokens():
    cmds, _, w = cmd.parse(ini.parse(CMD))
    had = next(c for c in cmds if c.name == "hadouken")
    assert [k.key for s in had.steps for k in s.keys] == ["D", "DF", "F", "x"]
    assert had.steps[0].keys[0].release and not w


def test_character_fidelity_and_missing_common(tmp_path):
    ch = character.load(Source(make_pkg(tmp_path)))
    assert ch.report["missing_refs"][0]["key"] == "stcommon"
    assert 5000 in ch.states and ch.states[5000].origin == "common_forge"
    fid = ch.report["controller_fidelity"]
    assert fid["unsupported"] == 1          # AfterImage declarado, nao escondido
    hd = next(c for c in ch.states[200].controllers if c.type == "hitdef")
    assert hd.sym["sparkno"] == 700 and hd.sym["hitsound"] == 0   # prefixo S = proprio personagem


def test_sprites_palette_and_sheets(tmp_path):
    ch = character.load(Source(make_pkg(tmp_path)))
    r = sprites.convert(ch)
    assert r.body.src_indices == [5, 6]
    assert {s.name for s in r.sheets} >= {"g0", "g200"}
    assert all(s.cell_w % 8 == 0 and s.cell_h % 8 == 0 for s in r.sheets)
    assert r.body_variants[0][1][1] == sprites.vdp_word((200, 40, 40))


def test_generator_is_deterministic(tmp_path):
    pkg = make_pkg(tmp_path)
    outs = []
    for name in ("a", "b"):
        proj = tmp_path / name
        (proj / "doc").mkdir(parents=True)
        rep = cli.convert_char(pkg, "fixture", proj)
        outs.append(rep["outputs"])
        assert "src/mg_gen/mg_fixture.c" in rep["outputs"]
        prov = json.loads((proj / "doc" / "asset_provenance_manifest.json").read_text())
        assert all(e["acceptance_status"] == "technical_candidate" for e in prov["entries"])
    assert outs[0] == outs[1]
    c = (tmp_path / "a" / "src" / "mg_gen" / "mg_fixture.c").read_text()
    assert "float" not in c and "double" not in c and "malloc" not in c
