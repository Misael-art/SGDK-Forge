"""Gerador SGDK 2.11: IR compilado -> .res + PNG/WAV + C de dados (const) + mg_ops.h.

Saida deterministica: ordenacao estavel, sem timestamps, sem caminhos absolutos.
Layout no projeto destino:
    res/mugen/<id>/sheets/*.png, res/mugen/<id>/snd/*.wav, res/mgres_<id>.res
    src/mg_gen/mg_<id>.c, inc/mg_gen/mg_<id>.h
"""
from __future__ import annotations

import hashlib
import io
import re
from pathlib import Path

from ..ir import controllers as C
from ..ir import opcodes as O

DIR_CODES = {"F": 1, "B": 2, "U": 3, "D": 4, "DF": 5, "DB": 6, "UF": 7, "UB": 8}


def key_event_mask(k) -> int:
    """Bits das teclas (codigos MG_K_*) cujo evento (mudanca) pode satisfazer a tecla k."""
    if k.key in DIR_CODES:
        if k.four_way:
            comps = set(k.key)
            return sum(1 << c for d, c in DIR_CODES.items() if comps <= set(d))
        return 1 << DIR_CODES[k.key]
    return 1 << KEYMAP[k.key]


KEYMAP = {"F": 1, "B": 2, "U": 3, "D": 4, "DF": 5, "DB": 6, "UF": 7, "UB": 8,
          "a": 9, "b": 10, "c": 11, "x": 12, "y": 13, "z": 14, "s": 15}


def ident(s: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s.lower())
    return s if not s[:1].isdigit() else "_" + s


def ops_header() -> str:
    lines = ["/* mg_ops.h -- GERADO por mugen2sgdk_forge (ir/opcodes.py, ir/controllers.py). Nao editar. */",
             "#ifndef MG_OPS_H", "#define MG_OPS_H", ""]
    lines += [f"#define MG_OP_{n} {i}" for i, n in enumerate(O.OPS)] + [""]
    lines += [f"#define MG_TRG_{n.upper()} {i}" for i, n in enumerate(O.TRIGGERS)]
    lines += [f"#define MG_NUM_TRG {len(O.TRIGGERS)}", ""]
    lines += [f"#define MG_TRGA_{n.upper()} {i}" for i, n in enumerate(O.TRIGGERS_ARG)] + [""]
    lines += [f"#define MG_GHV_{ident(n).upper()} {i}" for i, n in enumerate(O.GETHITVARS)] + [""]
    lines += [f"#define MG_CT_{n.upper()} {i}" for i, n in enumerate(C.SCHEMA)] + [""]
    for n, params in C.SCHEMA.items():
        for i, (p, comp, _) in enumerate(params):
            lines.append(f"#define MG_P_{n.upper()}_{ident(p).upper()}{'_' + 'XYZ'[comp] if comp or sum(1 for q in params if q[0] == p) > 1 else ''} {i}")
    lines += ["", "/* simbolos (syms[]) por tipo de controlador */"]
    for n, keys in SYM_ORDER.items():
        for i, k in enumerate(keys):
            lines.append(f"#define MG_S_{n.upper()}_{ident(k).upper()} {i}")
    lines += ["", "#endif", ""]
    return "\n".join(lines)


# ordem fixa dos simbolos por tipo (syms[] do controlador)
SYM_ORDER = {
    "hitdef": ["attr", "hitflag", "guardflag", "animtype", "air.animtype", "ground.type", "air.type",
               "priority", "hitsound", "guardsound", "sparkno", "guard.sparkno"],
    "playsnd": ["sound"],
    "statetypeset": ["statetype", "movetype", "physics"],
    "nothitby": ["attr"],
    "hitby": ["attr"],
    "varset": ["fvar", "index", "min"],
    "superpause": ["anim", "sound"],
    "helper": ["postype"],
}
SYM_ORDER["projectile"] = SYM_ORDER["hitdef"]
SYM_ORDER["varadd"] = SYM_ORDER["varset"]
SYM_ORDER["varrandom"] = SYM_ORDER["varset"]


class CodePool:
    """Pool de bytecode com deduplicacao (programas identicos compartilham offset)."""

    def __init__(self):
        self.buf = bytearray()
        self.index: dict[bytes, int] = {}

    def add(self, code: bytes | None) -> int:
        if code is None:
            return 0xFFFF
        if code not in self.index:
            self.index[code] = len(self.buf)
            self.buf += code
        return self.index[code]


def _arr(ctype: str, name: str, items: list[str], per_line: int = 8) -> str:
    if not items:
        items = ["0"]
    rows = [", ".join(items[i:i + per_line]) for i in range(0, len(items), per_line)]
    return f"static const {ctype} {name}[] = {{\n    " + ",\n    ".join(rows) + "\n};\n"


def _fxc(v: float | None) -> str:
    return str(int(round((v or 0) * O.FX)))


def _const_num(consts, sec, key, comp=0, default=0.0):
    raw = consts.get(sec, {}).get(key)
    if raw is None:
        return default
    try:
        return float(C.split_top(raw)[comp])
    except (ValueError, IndexError):
        return default


def generate(ch, spr, sounds, char_id: str, project: Path, bgfx=()) -> dict:
    cid = ident(char_id)
    res_dir = project / "res" / "mugen" / cid
    (res_dir / "sheets").mkdir(parents=True, exist_ok=True)
    (res_dir / "snd").mkdir(parents=True, exist_ok=True)
    (project / "src" / "mg_gen").mkdir(parents=True, exist_ok=True)
    (project / "inc" / "mg_gen").mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}

    def write(path: Path, data: bytes):
        path.write_bytes(data)
        outputs[path.relative_to(project).as_posix()] = hashlib.sha256(data).hexdigest()

    # ---------------------------------------------------------------- .res
    res = [f"// GERADO por mugen2sgdk_forge para '{ch.name}' ({ch.author}). Nao editar.",
           f"// Conteudo derivado de terceiros: NAO redistribuir sem licenca do autor.", ""]
    for sh in spr.sheets:
        buf = io.BytesIO()
        sh.png.save(buf, format="PNG", optimize=False)
        write(res_dir / "sheets" / f"{sh.name}.png", buf.getvalue())
        res.append(f'SPRITE mg_{cid}_{sh.name} "mugen/{cid}/sheets/{sh.name}.png" '
                   f"{sh.cell_w // 8} {sh.cell_h // 8} FAST 0 NONE BALANCED")
    res.append("")
    snd_names = {}
    for so in sounds:
        n = f"mg_{cid}_snd_{so.group}_{so.sample}"
        write(res_dir / "snd" / f"{so.group}_{so.sample}.wav", so.wav)
        res.append(f'WAV {n} "mugen/{cid}/snd/{so.group}_{so.sample}.wav" XGM2 13300 FALSE')
        snd_names[so.index] = n
    for fx in bgfx:
        buf = io.BytesIO()
        fx.png.save(buf, format="PNG", optimize=False)
        write(res_dir / f"bgfx_{fx.group}.png", buf.getvalue())
        res.append(f'IMAGE mg_{cid}_bgfx_{fx.group} "mugen/{cid}/bgfx_{fx.group}.png" NONE ALL')
    write(project / "res" / f"mgres_{cid}.res", ("\n".join(res) + "\n").encode())

    # ---------------------------------------------------------------- C
    pool = CodePool()
    c: list[str] = [f"/* GERADO por mugen2sgdk_forge -- {ch.name} ({ch.author}). Nao editar. */",
                    '#include "mg/mg_types.h"', f'#include "mgres_{cid}.h"', ""]

    # sheets
    rows = [f"{{ &mg_{cid}_{sh.name}, {sh.axis_x}, {sh.axis_y}, {sh.cell_w}, {sh.cell_h}, "
            f"{0 if sh.palette == 'body' else 1}, 0 }}" for sh in spr.sheets]
    c.append(_arr("MgSheet", "sheets", rows, 1))

    # anims / frames / boxes
    anim_rows, frame_rows, boxes, part_rows = [], [], [], []
    miss = 0
    for aid in sorted(ch.anims):
        a = ch.anims[aid]
        first = len(frame_rows)
        total = 0
        for f in a.frames[:255]:
            loc = spr.locate.get((f.group, f.image))
            if not loc and f.group >= 0:
                miss += 1
            sheet, frame = loc[0] if loc else (-1, 0)
            pidx = len(part_rows)
            for extra in (loc[1:] if loc else []):
                part_rows.append(f"{{ {extra[0]}, {extra[1]}, 0 }}")
            nparts = len(loc) if loc else 1
            flags = (1 if f.hflip else 0) | (2 if f.vflip else 0) | (4 if f.blend else 0)
            bi = len(boxes)
            boxes += [b for b in f.clsn1] + [b for b in f.clsn2]
            frame_rows.append(f"{{ {sheet}, {frame}, {flags}, {f.x}, {f.y}, {f.time}, "
                              f"{len(f.clsn1)}, {len(f.clsn2)}, {bi}, {nparts}, 0, {pidx} }}")
            total = -1 if (f.time < 0 or total < 0) else total + f.time
        anim_rows.append(f"{{ {aid}, {first}, {min(len(a.frames), 255)}, {min(a.loopstart, 254)}, {max(-1, min(total, 32767))} }}")
    c.append(_arr("MgAnimFrame", "frames", frame_rows, 1))
    c.append(_arr("MgFramePart", "parts", part_rows or ["{ -1, 0, 0 }"], 4))
    c.append(_arr("MgBox", "boxes", [f"{{ {b[0]}, {b[1]}, {b[2]}, {b[3]} }}" for b in boxes], 4))
    c.append(_arr("MgAnim", "anims", anim_rows, 1))

    # commands
    step_rows, key_rows, cmd_rows = [], [], []
    for cm in ch.commands:
        fs = len(step_rows)
        for st in cm.steps[:255]:
            fk = len(key_rows)
            for k in st.keys:
                mods = (1 if k.release else 0) | (2 if k.hold else 0) | (4 if k.four_way else 0)
                key_rows.append(f"{{ {KEYMAP[k.key]}, {mods}, {min(k.release_time, 255)}, 0 }}")
            flags = (1 if st.strict else 0) | (2 if st.keys and all(k.hold for k in st.keys) else 0)
            kmask = 0
            for k in st.keys:
                kmask |= key_event_mask(k)
            step_rows.append(f"{{ {fk}, {len(st.keys)}, {flags}, 0x{kmask:04X} }}")
        hold_only = 1 if cm.steps and all(k.hold for k in cm.steps[-1].keys) else 0
        cmd_rows.append(f"{{ {fs}, {min(len(cm.steps), 255)}, {min(cm.time, 255)}, {min(cm.buffer_time, 255)}, {hold_only} }} /* {cm.name} */")
    # indice por evento de tecla (1o passo) e comandos de "segurar"
    buckets = {code: [] for code in range(16)}
    hold_cmds = []
    for i, cm in enumerate(ch.commands[:255]):
        if not cm.steps:
            continue
        first = cm.steps[0]
        if first.keys and all(k.hold for k in first.keys):
            hold_cmds.append(i)
            continue
        m = 0
        for k in first.keys:
            m |= key_event_mask(k)
        for code in range(16):
            if m & (1 << code):
                buckets[code].append(i)
    bucket_first, bucket = [], []
    for code in range(16):
        bucket_first.append(len(bucket))
        bucket += buckets[code]
    bucket_first.append(len(bucket))
    c.append(_arr("MgCmdKey", "keys", key_rows, 4))
    c.append(_arr("u16", "cmd_bucket_first", [str(x) for x in bucket_first], 17))
    c.append(_arr("u8", "cmd_bucket", [str(x) for x in bucket], 24))
    c.append(_arr("u8", "hold_cmds", [str(x) for x in hold_cmds], 24))
    c.append(_arr("MgCmdStep", "steps", step_rows, 4))
    c.append(_arr("MgCommand", "cmds", cmd_rows, 1))

    # states / controllers
    ctrl_rows, param_offs, syms, state_rows = [], [], [], []
    gates = bytearray([0])            # offset 0 = portao vazio (nunca usado)
    gate_idx: dict[tuple, int] = {}
    snd_remap = {so.index: i for i, so in enumerate(sounds)}   # indice .snd -> indice na tabela MgSound
    for sid in sorted(ch.states):
        s = ch.states[sid]
        fc = len(ctrl_rows)
        for cc in s.controllers:
            pidx = len(param_offs)
            for p in cc.params:
                param_offs.append(str(pool.add(p.code)))
            order = SYM_ORDER.get(cc.type, [])
            sidx = len(syms)
            for k in order:
                v = cc.sym.get(k, -1 if k in ("hitsound", "guardsound", "sound", "sparkno", "guard.sparkno", "anim") else 0)
                if k in ("hitsound", "guardsound", "sound") and v >= 0:
                    v = snd_remap.get(v, -1)
                syms.append(str(v))
            goff = 0xFFFF
            if cc.gate:
                key = tuple(cc.gate)
                if key not in gate_idx:
                    gate_idx[key] = len(gates)
                    gates.extend(bytes([len(key)]) + bytes(key))
                goff = gate_idx[key]
            ctrl_rows.append(f"{{ {C.CONTROLLER_IDS[cc.type]}, {len(cc.params)}, {len(order)}, 0, "
                             f"{pool.add(cc.cond)}, {pidx}, {sidx}, {goff}, {cc.tgate[0] if cc.tgate else 0}, {cc.tgate[1] if cc.tgate else 0} }} /* {cc.source_type} L{cc.line} */")
        g = lambda k: pool.add(s.params.get(k))
        flags = (s.flags.get("facep2", 0) and 1) | (s.flags.get("hitdefpersist", 0) and 2) | \
                (s.flags.get("movehitpersist", 0) and 4) | (s.flags.get("hitcountpersist", 0) and 8)
        state_rows.append(f"{{ {sid}, {s.statetype}, {s.movetype}, {s.physics}, {flags}, "
                          f"{g('anim')}, {g('ctrl')}, {g('poweradd')}, {g('sprpriority')}, {g('juggle')}, "
                          f"{g('velset.x')}, {g('velset.y')}, {fc}, {len(ctrl_rows) - fc} }}")
    c.append(_arr("u8", "code", [str(b) for b in pool.buf], 24))
    c.append(_arr("u16", "param_offs", param_offs, 16))
    c.append(_arr("u8", "gates", [str(b) for b in gates], 24))
    c.append(_arr("s16", "syms", syms, 16))
    c.append(_arr("MgCtrl", "ctrls", ctrl_rows, 1))
    c.append(_arr("MgState", "states", state_rows, 1))

    # estado -1: bitmap de controladores liberados por comando (+ linha final: sem portao)
    neg = ch.states.get(-1)
    words = max(1, -(-len(neg.controllers) // 32)) if neg else 1
    rows = [[0] * words for _ in range(len(ch.commands) + 1)]
    if neg:
        for ci, cc in enumerate(neg.controllers):
            if cc.gate:
                for cmd_i in cc.gate:
                    rows[cmd_i][ci // 32] |= 1 << (ci % 32)
            else:
                rows[-1][ci // 32] |= 1 << (ci % 32)
    c.append(_arr("u32", "neg1_masks", [f"0x{w:08X}" for r in rows for w in r], 8))

    # paletas
    pal_rows = ["{ " + ", ".join(f"0x{w:03X}" for w in words) + " } /* " + name + " */"
                for name, words in spr.body_variants]
    c.append(f"static const u16 pals[][16] = {{\n    " + ",\n    ".join(pal_rows) + "\n};\n")
    c.append(_arr("u16", "fxpal", [f"0x{w:03X}" for w in spr.fx_palette], 16))

    # sons (indice = posicao no .snd; ausentes = NULL)
    snd_rows = [f"{{ {snd_names[so.index]}, sizeof({snd_names[so.index]}) }}" for so in sounds]
    c.append(_arr("MgSound", "sounds", snd_rows, 1))

    # efeitos de fundo animados por paleta
    bg_rows = []
    for fi, fx in enumerate(bgfx):
        prow = ["{ " + ", ".join(f"0x{w:03X}" for w in words) + " }" for words in fx.pals]
        c.append(f"static const u16 bgfx{fi}_pals[][16] = {{\n    " + ",\n    ".join(prow) + "\n};\n")
        for a in fx.anims:
            c.append(_arr("u8", f"bgfx{fi}_elem_{a}", [str(x) for x in fx.elem_img[a][:255]], 24))
            bg_rows.append(f"{{ {a}, &mg_{cid}_bgfx_{fx.group}, bgfx{fi}_pals, {len(fx.pals)}, "
                           f"{min(len(fx.elem_img[a]), 255)}, bgfx{fi}_elem_{a} }}")
    if bg_rows:
        c.append("static const MgBgFx bgfx[] = {\n    " + ",\n    ".join(bg_rows) + "\n};\n")

    # constantes
    k = ch.constants
    consts = [
        _const_num(k, "data", "life", 0, 1000), _const_num(k, "data", "attack", 0, 100),
        _const_num(k, "data", "defence", 0, 100), _const_num(k, "data", "liedown.time", 0, 60),
        _const_num(k, "data", "airjuggle", 0, 15),
        _const_num(k, "size", "ground.back", 0, 15), _const_num(k, "size", "ground.front", 0, 16),
        _const_num(k, "size", "air.back", 0, 12), _const_num(k, "size", "air.front", 0, 12),
        _const_num(k, "size", "height", 0, 60),
        _const_num(k, "velocity", "walk.fwd", 0, 2.4), _const_num(k, "velocity", "walk.back", 0, -2.2),
        _const_num(k, "velocity", "run.fwd", 0, 4.6), _const_num(k, "velocity", "run.fwd", 1, 0),
        _const_num(k, "velocity", "run.back", 0, -4.5), _const_num(k, "velocity", "run.back", 1, -3.8),
        _const_num(k, "velocity", "jump.neu", 0, 0), _const_num(k, "velocity", "jump.neu", 1, -8.4),
        _const_num(k, "velocity", "jump.back", 0, -2.55), _const_num(k, "velocity", "jump.fwd", 0, 2.5),
        _const_num(k, "movement", "yaccel", 0, 0.44), _const_num(k, "movement", "stand.friction", 0, 0.85),
        _const_num(k, "movement", "crouch.friction", 0, 0.82),
    ]

    def spark(key, default):
        ref = C.self_anim_ref(k.get("data", {}).get(key, "")) if k.get("data", {}).get(key) else None
        if ref and ref[0] and ref[1] in ch.anims:
            return ref[1]
        return default
    fallback_spark = min((a for a in ch.anims if 700 <= a < 800), default=-1)
    c.append("static const MgConsts consts = {\n    " + ", ".join(_fxc(v) for v in consts) +
             f", {spark('sparkno', fallback_spark)}, {spark('guard.sparkno', fallback_spark)}\n}};\n")

    sidx = {sid: i for i, sid in enumerate(sorted(ch.states))}
    cmd_idx = {cm.name.lower(): i for i, cm in enumerate(ch.commands)}
    hold = lambda n: cmd_idx.get(n, 0xFFFF)
    default_pal = 0
    pd = ch.info.get("pal.defaults")
    if pd:
        try:
            default_pal = max(0, min(len(spr.body_variants) - 1, int(pd.split(",")[0]) - 1))
        except ValueError:
            pass
    c.append(f"const MgCharDef mg_char_{cid} = {{\n"
             f'    "{ch.name}",\n'
             f"    sheets, {len(spr.sheets)}, anims, {len(anim_rows)}, frames, parts, boxes, code, param_offs, syms, ctrls,\n"
             f"    states, {len(state_rows)}, cmds, {len(cmd_rows)}, steps, keys, gates,\n"
             f"    cmd_bucket_first, cmd_bucket, hold_cmds, {len(hold_cmds)}, neg1_masks, {words},\n"
             f"    pals, {len(pal_rows)}, {default_pal}, fxpal, sounds, {len(snd_rows)}, "
             f"{'bgfx' if bg_rows else '0'}, {len(bg_rows)}, &consts,\n"
             f"    {sidx.get(-1, -1)}, {sidx.get(-2, -1)}, {sidx.get(-3, -1)},\n"
             f"    {hold('holdfwd')}, {hold('holdback')}, {hold('holdup')}, {hold('holddown')}\n}};\n")
    write(project / "src" / "mg_gen" / f"mg_{cid}.c", "\n".join(c).encode())
    write(project / "inc" / "mg_gen" / f"mg_{cid}.h",
          (f"/* GERADO por mugen2sgdk_forge. Nao editar. */\n#ifndef MG_GEN_{cid.upper()}_H\n"
           f"#define MG_GEN_{cid.upper()}_H\n#include \"mg/mg_types.h\"\n"
           f"extern const MgCharDef mg_char_{cid};\n#endif\n").encode())

    return {"outputs": outputs, "bytecode_bytes": len(pool.buf), "gated_controllers": sum(1 for r in ctrl_rows if ", 65535 }" not in r), "frames": len(frame_rows),
            "boxes": len(boxes), "controllers": len(ctrl_rows), "missing_frame_sprites": miss}
