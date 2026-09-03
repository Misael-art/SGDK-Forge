#!/usr/bin/env python3
"""Contrato pixel-strict executavel do forge-art (P0.3).

Este modulo existe porque a regra ja estava escrita em prosa em varios lugares
e nao era medida em nenhum (SGDK_GLOBAL.md secao 37, corolario da secao 15).
Ele mede, sobre o arquivo em disco:

  - PNG modo P (color type 3), nunca RGBA;
  - PLTE compacta (<= 16 entradas REAIS no chunk, nao cores unicas);
  - bit depth compativel com 4 bpp;
  - ate 15 cores visiveis;
  - index 0 conforme o papel declarado do asset;
  - toda cor da paleta na grade do VDP, pelo oraculo canonico;
  - dimensoes multiplas de 8;
  - hash de conteudo canonico, para provar determinismo.

Limite declarado: isto aprova **sintaxe de hardware**. Nao aprova silhueta,
anatomia, material, identidade nem leitura. Um asset pode passar aqui inteiro e
ainda ser `technical_pass_visual_fail`
(`megadrive-pixel-strict-rules`, secao "Limite do gate pixel-strict").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Sequence

try:
    from forge_art import vdp_color
except ImportError:  # execucao direta pelo caminho do arquivo
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from forge_art import vdp_color

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "forge_art.pixel_contract"
TOOL_VERSION = "1.2.0"

MAX_PLTE_ENTRIES = 16
MAX_VISIBLE_COLORS = 15
TILE_SIZE = 8

#: Papeis validos do index 0. O papel e declarado pelo contrato do asset; a
#: ferramenta nunca escolhe sozinha.
ROLE_TRANSPARENT0 = "transparent0"   # index 0 e o slot transparente do sprite
ROLE_UNUSED0 = "unused0"             # index 0 reservado e nao usado por pixel visivel
INDEX0_ROLES = (ROLE_TRANSPARENT0, ROLE_UNUSED0)

#: Metodos de reamostragem permitidos em caminho de pixel nativo/final.
ALLOWED_RESAMPLE = frozenset({"NEAREST"})
#: Proibidos por criarem pixel intermediario. Blocker: `non_nearest_downscale`.
FORBIDDEN_RESAMPLE = frozenset({"LANCZOS", "BILINEAR", "BICUBIC", "BOX", "HAMMING", "ANTIALIAS"})


class PixelContractError(ValueError):
    def __init__(self, blocker: str, message: str, next_action: str) -> None:
        super().__init__(f"[{blocker}] {message} | proxima acao: {next_action}")
        self.blocker = blocker
        self.next_action = next_action


def assert_nearest_resample(method_name: str) -> str:
    """Guarda de API: so nearest-neighbor entra em caminho de pixel nativo.

    Chamada por qualquer codigo do forge-art antes de reamostrar. O nome vem do
    chamador, entao a proibicao e verificavel por leitura estatica tambem.
    """
    name = str(method_name).upper().split(".")[-1]
    if name in FORBIDDEN_RESAMPLE:
        raise PixelContractError(
            "non_nearest_downscale",
            f"reamostragem {name} cria pixel intermediario e halo em pixel nativo",
            "use NEAREST; downsample interpolado so e admissivel para fonte "
            "classificada como foto/render/concept, e o resultado nasce "
            "technical_candidate, nunca asset final",
        )
    if name not in ALLOWED_RESAMPLE:
        raise PixelContractError(
            "unknown_resample_method",
            f"metodo de reamostragem {name!r} desconhecido",
            "declare o metodo explicitamente; a ferramenta nao adivinha default",
        )
    return name


# ---------------------------------------------------------------------------
# Leitura do PNG no nivel de chunk — Pillow nao expoe PLTE real
# ---------------------------------------------------------------------------

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_chunks(path: Path | str) -> dict:
    """Le IHDR/PLTE/tRNS direto dos bytes.

    Por que nao usar `Image.getpalette()`: Pillow devolve a paleta expandida e
    padded. Uma imagem com 11 cores unicas pode carregar PLTE de 256 entradas,
    e o ResComp trata indice de paleta como identidade de tile — cores iguais
    em indices diferentes viram tiles "unicos" falsos. E exatamente o caso
    `PALETTE_INFLATED`, e ele so aparece lendo o chunk.
    """
    path = Path(path)
    data = path.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise PixelContractError(
            "not_a_png",
            f"{path} nao comeca com a assinatura PNG",
            "confirme que o arquivo e um PNG valido e nao foi truncado",
        )
    info: dict = {"plte_entries": 0, "has_trns": False, "trns": b""}
    offset = len(PNG_MAGIC)
    while offset + 8 <= len(data):
        (length,) = struct.unpack(">I", data[offset:offset + 4])
        ctype = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        if ctype == b"IHDR":
            w, h, depth, color_type = struct.unpack(">IIBB", payload[:10])
            info.update(width=w, height=h, bit_depth=depth, color_type=color_type)
        elif ctype == b"PLTE":
            info["plte_entries"] = length // 3
            info["plte"] = [tuple(payload[i:i + 3]) for i in range(0, length, 3)]
        elif ctype == b"tRNS":
            info["has_trns"] = True
            info["trns"] = payload
        elif ctype == b"IEND":
            break
        offset += 12 + length
    if "width" not in info:
        raise PixelContractError(
            "png_missing_ihdr", f"{path} sem chunk IHDR",
            "arquivo corrompido; falhe fechado em vez de adivinhar dimensoes",
        )
    return info


def canonical_content_hash(path: Path) -> str:
    """SHA-256 sobre bytes canonicos: dimensoes + depth + PLTE + indices.

    Nunca `hash()` do Python (nao e estavel entre processos). O hash ignora
    metadata volatil do PNG, entao dois salvamentos do mesmo conteudo casam.
    """
    from PIL import Image

    path = Path(path)
    info = read_png_chunks(path)
    with Image.open(path) as img:
        if img.mode != "P":
            raise PixelContractError(
                "output_not_indexed",
                f"{path} esta em modo {img.mode}; hash canonico exige PNG indexado",
                "converta para modo P antes de exigir determinismo de indices",
            )
        indices = bytes(img.tobytes())
    digest = hashlib.sha256()
    digest.update(struct.pack(">IIB", info["width"], info["height"], info["bit_depth"]))
    for entry in info.get("plte", []):
        digest.update(bytes(entry))
    digest.update(info["trns"])
    digest.update(indices)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Validacao
# ---------------------------------------------------------------------------

def validate_png(
    path: Path,
    index0_role: str,
    oracle: str = vdp_color.ORACLE_RESCOMP,
    require_multiple_of_8: bool = True,
) -> dict:
    """Mede um PNG contra o contrato pixel-strict. Nunca escreve nada."""
    from PIL import Image

    if index0_role not in INDEX0_ROLES:
        raise PixelContractError(
            "index0_role_undeclared",
            f"papel do index 0 {index0_role!r} invalido; validos: {list(INDEX0_ROLES)}",
            "declare o papel do index 0 no contrato do asset; a ferramenta nao escolhe",
        )

    path = Path(path)
    blockers: list[dict] = []

    def block(code: str, detail: str, next_action: str) -> None:
        blockers.append({"code": code, "detail": detail, "next_action": next_action})

    info = read_png_chunks(path)

    if info["color_type"] != 3:
        block("output_not_indexed",
              f"color type {info['color_type']} (esperado 3 = indexado); "
              f"{'RGBA' if info['color_type'] == 6 else 'nao-P'} nao e saida final",
              "saida final e PNG modo P; RGBA intermediario nao e estado valido do contrato")

    if info["plte_entries"] > MAX_PLTE_ENTRIES:
        block("plte_inflated",
              f"PLTE com {info['plte_entries']} entradas (teto {MAX_PLTE_ENTRIES})",
              "compacte a PLTE; o ResComp usa indice como identidade de tile e "
              "PLTE inflada gera tiles unicos falsos")

    if info["bit_depth"] > 4:
        block("bitdepth_not_4bpp_compatible",
              f"bit depth {info['bit_depth']} (o VDP e 4 bpp)",
              "salve com bit depth <= 4 apos compactar a PLTE")

    if require_multiple_of_8 and (info["width"] % TILE_SIZE or info["height"] % TILE_SIZE):
        block("dimensions_not_multiple_of_8",
              f"{info['width']}x{info['height']} nao e multiplo de {TILE_SIZE}",
              "ajuste por padding/crop declarado preservando pivot e baseline; "
              "nunca por resize interpolado")

    used_indices: set[int] = set()
    if info["color_type"] == 3:
        with Image.open(path) as img:
            used_indices = set(img.tobytes())

    visible = {i for i in used_indices if i != 0}
    if len(visible) > MAX_VISIBLE_COLORS:
        block("too_many_visible_colors",
              f"{len(visible)} cores visiveis (teto {MAX_VISIBLE_COLORS} + index 0)",
              "recure a paleta por material, nao por frequencia estatistica")

    # Indices diferentes com o mesmo RGB continuam diferentes para o ResComp.
    # Sem esta guarda, uma paleta visualmente de 9 cores pode consumir 15
    # identidades de tile e produzir um falso verde de budget.
    if info["color_type"] == 3:
        aliases: dict[tuple[int, int, int], list[int]] = {}
        for idx in sorted(visible):
            if idx < len(info.get("plte", [])):
                aliases.setdefault(tuple(info["plte"][idx]), []).append(idx)
        duplicate_groups = {rgb: ids for rgb, ids in aliases.items() if len(ids) > 1}
        if duplicate_groups:
            detail = [f"#{r:02X}{g:02X}{b:02X}:{ids}"
                      for (r, g, b), ids in sorted(duplicate_groups.items())]
            block("palette_alias_indices",
                  f"indices visiveis distintos compartilham RGB: {detail[:6]}",
                  "deduplique a paleta depois do snap VDP e remapeie os pixels; "
                  "o ResComp trata indice, nao aparencia RGB, como identidade")

    if index0_role == ROLE_TRANSPARENT0:
        if not info["has_trns"] or not info["trns"] or info["trns"][0] != 0:
            block("index0_contract_violation",
                  "papel transparent0 exige chunk tRNS marcando o indice 0 como transparente",
                  "reindexe com normalize_indexed_sgdk_png.py modo transparent0; "
                  "nunca componha sobre preto para 'resolver' transparencia")
    else:  # ROLE_UNUSED0
        if 0 in used_indices:
            block("index0_contract_violation",
                  "papel unused0 exige que nenhum pixel visivel use o indice 0",
                  "reindexe com normalize_indexed_sgdk_png.py modo unused0")

    # --- alpha e binario, e so o index 0 pode ser transparente ---------------
    # O VDP nao tem alpha por pixel: um pixel esta no slot transparente ou nao
    # esta. tRNS com valor intermediario e sintoma de composicao RGBA vazando
    # para o caminho final, e um segundo indice transparente quebra a premissa
    # de que index 0 e o unico slot reservado.
    partial = [(i, a) for i, a in enumerate(info["trns"]) if a not in (0, 255)]
    if partial:
        block("partial_alpha_rejected",
              f"tRNS com alpha parcial em {partial[:6]} (validos: 0 ou 255)",
              "o VDP nao tem alpha por pixel; achate a mascara para binaria na "
              "origem em vez de deixar alpha intermediario chegar ao PNG final")
    extra_transparent = [i for i, a in enumerate(info["trns"]) if a == 0 and i != 0]
    if extra_transparent:
        block("extra_transparent_index",
              f"indices transparentes alem do 0: {extra_transparent[:6]}",
              "so o indice 0 e o slot transparente por contrato; reindexe "
              "colapsando os demais no 0 com normalize_indexed_sgdk_png.py")

    off_grid: list[str] = []
    for idx, entry in enumerate(info.get("plte", [])):
        if idx not in used_indices and idx != 0:
            continue  # entrada nao usada nao carrega cor de tela
        if not vdp_color.is_on_grid(entry, vdp_color.GRID_AUTHORING):
            snapped = vdp_color.snap_rgb_to_vdp_grid(entry, oracle=oracle)
            off_grid.append(
                f"idx{idx} #{entry[0]:02X}{entry[1]:02X}{entry[2]:02X}"
                f" -> #{snapped[0]:02X}{snapped[1]:02X}{snapped[2]:02X}"
            )
    if off_grid:
        block("color_off_vdp_grid",
              f"{len(off_grid)} cores fora da grade de autoria: {off_grid[:6]}",
              "snap pela biblioteca canonica (forge_art/vdp_color.py); "
              "microvariacao da mesma cor apos quantizacao e sintoma de "
              "interpolacao proibida na origem")

    content_hash = canonical_content_hash(path) if info["color_type"] == 3 else None

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "file": str(path),
        "index0_role": index0_role,
        "oracle": oracle,
        "width": info["width"],
        "height": info["height"],
        "bit_depth": info["bit_depth"],
        "color_type": info["color_type"],
        "plte_entries": info["plte_entries"],
        "visible_colors": len(visible),
        "content_sha256": content_hash,
        "scope": "static_contract",
        "limitation": (
            "Aprova sintaxe de hardware. Nao aprova silhueta, anatomia, material, "
            "identidade nem leitura; `technical_pass` nao implica `visual_pass`."
        ),
        "status": "technical_candidate" if not blockers else "rejected",
        "blocking": bool(blockers),
        "blocking_statuses": sorted({b["code"] for b in blockers}),
        "blockers": blockers,
    }


# ---------------------------------------------------------------------------
# Self-check: fixture positiva e uma fixture negativa por blocker
# ---------------------------------------------------------------------------

def _write_ok_sprite(path: Path, w: int = 16, h: int = 16) -> None:
    from PIL import Image

    img = Image.new("P", (w, h))
    palette = [0x00, 0x00, 0x00,   # 0: transparente
               0x22, 0x22, 0x22,
               0x44, 0x66, 0xAA,
               0xEE, 0xCC, 0x88]
    img.putpalette(palette)
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = 0 if (x == 0 or y == 0) else 1 + ((x + y) % 3)
    img.info["transparency"] = 0
    img.save(path, "PNG", bits=4, transparency=0)


def _fixture(name: str, kind: str, passed: bool, detail: str) -> dict:
    return {"fixture": name, "kind": kind,
            "status": "passed" if passed else "failed", "detail": detail}


def self_check() -> dict:
    from PIL import Image

    fixtures: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="forge_art_pixel_") as tmp:
        tmpdir = Path(tmp)

        # --- POSITIVA: asset conforme passa e nasce technical_candidate ---
        ok_png = tmpdir / "ok.png"
        _write_ok_sprite(ok_png)
        rep = validate_png(ok_png, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "conforming_asset_passes", "positive",
            not rep["blocking"] and rep["status"] == "technical_candidate",
            f"status={rep['status']} blockers={rep['blocking_statuses']}",
        ))

        # --- POSITIVA: status maximo e technical_candidate, nunca aprovado ---
        fixtures.append(_fixture(
            "pass_never_claims_visually_approved", "positive",
            rep["status"] != "visually_approved",
            "saida de maquina nunca se declara visually_approved",
        ))

        # --- POSITIVA: determinismo. Mesmo conteudo, mesmo SHA. ---
        twin = tmpdir / "ok_twin.png"
        _write_ok_sprite(twin)
        same = canonical_content_hash(ok_png) == canonical_content_hash(twin)
        fixtures.append(_fixture(
            "same_content_same_sha256", "positive", same,
            f"sha={canonical_content_hash(ok_png)[:16]}...",
        ))

        # --- POSITIVA: conteudo diferente muda o SHA (o hash mede algo) ---
        other = tmpdir / "other.png"
        _write_ok_sprite(other, w=24, h=16)
        fixtures.append(_fixture(
            "different_content_different_sha256", "positive",
            canonical_content_hash(ok_png) != canonical_content_hash(other),
            "hash reage a mudanca de conteudo",
        ))

        # --- NEGATIVA: RGBA reprova ---
        rgba = tmpdir / "rgba.png"
        Image.new("RGBA", (16, 16), (255, 0, 0, 128)).save(rgba, "PNG")
        rep_rgba = validate_png(rgba, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_rgba_output", "negative",
            "output_not_indexed" in rep_rgba["blocking_statuses"],
            f"blockers={rep_rgba['blocking_statuses']}",
        ))

        # --- NEGATIVA: PLTE inflada reprova ---
        inflated = tmpdir / "inflated.png"
        img = Image.new("P", (16, 16))
        img.putpalette([0x22] * 768)  # 256 entradas
        img.save(inflated, "PNG")
        rep_inf = validate_png(inflated, ROLE_UNUSED0)
        fixtures.append(_fixture(
            "rejects_inflated_plte", "negative",
            "plte_inflated" in rep_inf["blocking_statuses"],
            f"PLTE={rep_inf['plte_entries']} blockers={rep_inf['blocking_statuses']}",
        ))

        # --- NEGATIVA: bit depth 8 reprova ---
        fixtures.append(_fixture(
            "rejects_bitdepth_above_4", "negative",
            "bitdepth_not_4bpp_compatible" in rep_inf["blocking_statuses"],
            f"bit_depth={rep_inf['bit_depth']}",
        ))

        # --- NEGATIVA: mais de 15 cores visiveis reprova ---
        many = tmpdir / "many.png"
        img = Image.new("P", (16, 16))
        img.putpalette([v for i in range(20) for v in (i * 0x22 % 256, 0x22, 0x44)])
        px = img.load()
        for y in range(16):
            for x in range(16):
                px[x, y] = 1 + ((y * 16 + x) % 19)
        img.save(many, "PNG")
        rep_many = validate_png(many, ROLE_UNUSED0)
        fixtures.append(_fixture(
            "rejects_more_than_15_visible_colors", "negative",
            "too_many_visible_colors" in rep_many["blocking_statuses"],
            f"visiveis={rep_many['visible_colors']}",
        ))

        # --- NEGATIVA: dois indices usados com o mesmo RGB reprova ---
        aliases = tmpdir / "palette_aliases.png"
        img = Image.new("P", (16, 16), 0)
        img.putpalette([0x00, 0x00, 0x00,
                        0x22, 0x44, 0x66,
                        0x22, 0x44, 0x66] + [0] * 759)
        px = img.load()
        for y in range(1, 15):
            for x in range(1, 15):
                px[x, y] = 1 if (x + y) % 2 else 2
        img.save(aliases, "PNG", bits=4, transparency=0)
        rep_alias = validate_png(aliases, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_palette_alias_indices", "negative",
            "palette_alias_indices" in rep_alias["blocking_statuses"],
            f"blockers={rep_alias['blocking_statuses']}",
        ))

        # --- NEGATIVA: index 0 sem tRNS reprova em papel transparent0 ---
        no_trns = tmpdir / "no_trns.png"
        img = Image.new("P", (16, 16))
        img.putpalette([0x00, 0x00, 0x00, 0x22, 0x22, 0x22] + [0] * 762)
        img.save(no_trns, "PNG")
        rep_trns = validate_png(no_trns, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_index0_without_transparency", "negative",
            "index0_contract_violation" in rep_trns["blocking_statuses"],
            f"blockers={rep_trns['blocking_statuses']}",
        ))

        # --- NEGATIVA: index 0 usado por pixel visivel reprova em unused0 ---
        rep_unused = validate_png(ok_png, ROLE_UNUSED0)
        fixtures.append(_fixture(
            "rejects_index0_used_in_unused0_role", "negative",
            "index0_contract_violation" in rep_unused["blocking_statuses"],
            f"blockers={rep_unused['blocking_statuses']}",
        ))

        # --- NEGATIVA: alpha parcial reprova (o VDP nao tem alpha por pixel) ---
        pa = tmpdir / "partial_alpha.png"
        img = Image.new("P", (16, 16))
        img.putpalette([0x00, 0x00, 0x00, 0x22, 0x22, 0x22, 0x44, 0x66, 0xAA])
        px = img.load()
        for y in range(16):
            for x in range(16):
                px[x, y] = 0 if (x == 0 or y == 0) else 1 + ((x + y) % 2)
        img.save(pa, "PNG", bits=4, transparency=bytes([0, 128, 255]))
        rep_pa = validate_png(pa, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_partial_alpha", "negative",
            "partial_alpha_rejected" in rep_pa["blocking_statuses"],
            f"blockers={rep_pa['blocking_statuses']}",
        ))

        # --- NEGATIVA: segundo indice transparente reprova ---
        xt = tmpdir / "extra_transparent.png"
        img.save(xt, "PNG", bits=4, transparency=bytes([0, 0, 255]))
        rep_xt = validate_png(xt, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_extra_transparent_index", "negative",
            "extra_transparent_index" in rep_xt["blocking_statuses"],
            f"blockers={rep_xt['blocking_statuses']}",
        ))

        # --- POSITIVA: alpha binario (0/255) continua passando ---
        bin_alpha = tmpdir / "binary_alpha.png"
        img.save(bin_alpha, "PNG", bits=4, transparency=bytes([0, 255, 255]))
        rep_bin = validate_png(bin_alpha, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "binary_alpha_still_passes", "positive",
            "partial_alpha_rejected" not in rep_bin["blocking_statuses"]
            and "extra_transparent_index" not in rep_bin["blocking_statuses"],
            f"blockers={rep_bin['blocking_statuses']}",
        ))

        # --- NEGATIVA: cor fora da grade do VDP reprova ---
        off = tmpdir / "off_grid.png"
        img = Image.new("P", (16, 16))
        img.putpalette([0x00, 0x00, 0x00, 0xFF, 0x80, 0x00] + [0] * 762)
        px = img.load()
        for y in range(16):
            for x in range(16):
                px[x, y] = 1
        img.save(off, "PNG", transparency=0)
        rep_off = validate_png(off, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_color_off_vdp_grid", "negative",
            "color_off_vdp_grid" in rep_off["blocking_statuses"],
            f"blockers={rep_off['blocking_statuses']}",
        ))

        # --- NEGATIVA: dimensao nao multipla de 8 reprova ---
        odd = tmpdir / "odd.png"
        _write_ok_sprite(odd, w=15, h=13)
        rep_odd = validate_png(odd, ROLE_TRANSPARENT0)
        fixtures.append(_fixture(
            "rejects_dimensions_not_multiple_of_8", "negative",
            "dimensions_not_multiple_of_8" in rep_odd["blocking_statuses"],
            f"{rep_odd['width']}x{rep_odd['height']} blockers={rep_odd['blocking_statuses']}",
        ))

        # --- NEGATIVA: interpolacao proibida e recusada pela guarda de API ---
        forbidden_caught = []
        for method in sorted(FORBIDDEN_RESAMPLE):
            try:
                assert_nearest_resample(method)
            except PixelContractError as exc:
                if exc.blocker == "non_nearest_downscale":
                    forbidden_caught.append(method)
        fixtures.append(_fixture(
            "rejects_forbidden_interpolation", "negative",
            len(forbidden_caught) == len(FORBIDDEN_RESAMPLE),
            f"{len(forbidden_caught)}/{len(FORBIDDEN_RESAMPLE)} metodos bloqueados: "
            f"{forbidden_caught}",
        ))

        # --- NEGATIVA: NEAREST continua permitido (calibracao anti-falso-positivo) ---
        try:
            allowed = assert_nearest_resample("Image.Resampling.NEAREST") == "NEAREST"
        except PixelContractError as exc:
            allowed = False
            forbidden_caught.append(f"FALSO POSITIVO: {exc}")
        fixtures.append(_fixture(
            "nearest_is_not_false_flagged", "positive", allowed,
            "gate que reprova o caminho correto treina o time a ignorar o vermelho "
            "(SGDK_GLOBAL.md secao 37)",
        ))

        # --- NEGATIVA: papel do index 0 nao declarado falha fechado ---
        try:
            validate_png(ok_png, "whatever")
            role_ok, role_detail = False, "NAO levantou nada (falso verde)"
        except PixelContractError as exc:
            role_ok = exc.blocker == "index0_role_undeclared"
            role_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture(
            "rejects_undeclared_index0_role", "negative", role_ok, role_detail))

        # --- NEGATIVA: arquivo corrompido falha fechado, sem excecao silenciosa ---
        corrupt = tmpdir / "corrupt.png"
        corrupt.write_bytes(b"not a png at all")
        try:
            validate_png(corrupt, ROLE_TRANSPARENT0)
            corrupt_ok, corrupt_detail = False, "NAO levantou nada (falso verde)"
        except PixelContractError as exc:
            corrupt_ok = exc.blocker == "not_a_png"
            corrupt_detail = f"levantou {exc.blocker}"
        fixtures.append(_fixture(
            "rejects_corrupt_file_closed", "negative", corrupt_ok, corrupt_detail))

    failed = [f for f in fixtures if f["status"] != "passed"]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "SGDK_GLOBAL.md secoes 34 e 37; megadrive-pixel-strict-rules",
        "exercised": (
            "fixture positiva conforme; determinismo de SHA nos dois sentidos; "
            "8 blockers disparados por fixture negativa dedicada; calibracao "
            "anti-falso-positivo do NEAREST; papel de index 0 nao declarado e "
            "arquivo corrompido falham fechado."
        ),
        "limitation": (
            "Mede sintaxe de hardware sobre o arquivo. Nao mede semantica visual, "
            "nem prova proveniencia dos pixels."
        ),
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f"pixel_contract_self_check_failed:{f['fixture']}"
                                     for f in failed}),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Contrato pixel-strict executavel do forge-art.")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--validate", metavar="PNG")
    parser.add_argument("--index0-role", choices=INDEX0_ROLES, default=None)
    args = parser.parse_args(argv)

    if args.validate:
        if not args.index0_role:
            print("[index0_role_undeclared] --validate exige --index0-role; "
                  "proxima acao: declare o papel do index 0 no contrato do asset",
                  file=sys.stderr)
            return 2
        report = validate_png(Path(args.validate), args.index0_role)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["blocking"]:
            print("[FAIL] self-check do contrato pixel reprovou; proxima acao: "
                  "corrija a fixture listada em blocking_statuses", file=sys.stderr)
            return 1
        print(f"[OK] {report['fixtures_passed']}/{report['fixtures_total']} fixtures "
              "(positivas e negativas) passaram", file=sys.stderr)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
