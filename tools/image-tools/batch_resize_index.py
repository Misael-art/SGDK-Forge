#!/usr/bin/env python3
"""DEPRECATED — removido do caminho canonico pelo P0.2 do plano forge-art.

Este script NAO foi apenas aposentado por gosto. Ele violava tres restricoes
duras ao mesmo tempo, e as tres foram lidas no proprio codigo antes da
substituicao (git mostra a versao anterior):

1. `_resample()` devolvia `Image.Resampling.LANCZOS` e essa funcao era usada no
   caminho de producao. Interpolacao suave em pixel nativo cria halo e pixel
   intermediario. Blocker canonico: `non_nearest_downscale` /
   `fake_pixel_art_artifact` (`megadrive-pixel-strict-rules`).
2. Com `transparency: true` ele salvava **RGBA** por cima do proprio arquivo de
   entrada (`png_path`). Isso e saida nao indexada E sobrescrita da fonte. O
   contrato manda PNG modo P, PLTE <= 16, e fonte read-only.
3. `to_indexed_bmp()` compunha a imagem sobre branco, destruindo o slot
   transparente. O index 0 e reservado por contrato e precisa sobreviver ponta
   a ponta.

Alem disso ele nao tinha oraculo unico de cor, job imutavel, hash, cache,
`--dry-run`, `--resume` nem rollback.

O que usar no lugar
-------------------

- conversao de cor: `tools/sgdk_wrapper/forge_art/vdp_color.py` (oraculo unico,
  com `--self-check` positivo e negativo);
- normalizacao de PNG **ja indexado**: `tools/image-tools/normalize_indexed_sgdk_png.py`;
- conversao completa: `forge-art convert` (rota `technical_conversion`), que
  nasce como `technical_candidate` e nunca se declara asset final.

Ate `forge-art convert` existir, nao ha rota automatica aprovada para gerar
asset final a partir de fonte high-res. Isso e o estado real, nao uma lacuna a
contornar: conversao automatica resolve conformidade, nao qualidade artistica.

Referencia: doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md
"""

from __future__ import annotations

import sys

DEPRECATION_BLOCKER = "deprecated_destructive_converter"

MESSAGE = """\
[BLOQUEADO] batch_resize_index.py foi removido do caminho canonico (forge-art P0.2).

Motivo (medido no codigo anterior, nao suposto):
  - usava LANCZOS em caminho de pixel nativo   -> non_nearest_downscale
  - salvava RGBA por cima do arquivo de origem -> sobrescrita de fonte + saida nao indexada
  - compunha BMP sobre branco                  -> destruia o index 0 transparente

Proxima acao causal, conforme a natureza da sua fonte:
  * fonte JA indexada e so precisa normalizar PLTE/index 0:
      python3 tools/image-tools/normalize_indexed_sgdk_png.py transparent0 <arquivo.png>
  * precisa converter cor para a grade do VDP:
      python3 tools/sgdk_wrapper/forge_art/vdp_color.py --convert R,G,B
  * fonte high-res / concept / render de personagem ou cenario de identidade:
      NAO existe rota automatica aprovada. A rota e `assisted_native_translation`
      (skill art/art-translation-to-vdp): construcao no canvas nativo, paleta por
      material, aprovacao humana registrada. Um resize+quantize nao e asset final.

Este script falha fechado de proposito. Nenhuma flag o reabilita.
"""


def main() -> int:
    sys.stderr.write(MESSAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
