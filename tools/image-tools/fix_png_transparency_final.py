#!/usr/bin/env python3
"""DEPRECATED — removido do caminho canonico pelo P0.2 do plano forge-art.

Defeito lido no proprio codigo antes da substituicao (git mostra a versao
anterior): `fix_png()` convertia para RGBA, compunha sobre um fundo **preto**
(`Image.new("RGB", size, (0, 0, 0))` + `paste(..., mask=alpha)`), requantizava
com median-cut e entao fazia `quantized.info.pop("transparency", None)`.

Ou seja: a ferramenta chamada de "fix de transparencia" **removia** a
transparencia por construcao, e ainda pintava de preto todo pixel que era
transparente. Depois salvava por cima do arquivo original.

O nome dizia o oposto do que o codigo fazia. Foi por isso que
`test_art_pipeline.py` conseguia chamar isso de "pipeline completo" e ficar
verde: o teste media que o modo virou `P`, e nunca que o index 0 sobreviveu.

O que usar no lugar
-------------------

- PNG que JA e indexado e so tem PLTE inflada ou index 0 no papel errado:
    python3 tools/image-tools/normalize_indexed_sgdk_png.py transparent0 <arquivo.png>
    python3 tools/image-tools/normalize_indexed_sgdk_png.py unused0      <arquivo.png>
- PNG que ainda nao e indexado: a indexacao pertence a `forge-art convert`
  (rota `technical_conversion`), com index 0 declarado por papel do asset e
  saida imutavel + hash + report. Nao existe atalho aprovado.

Nunca componha sobre preto (nem sobre magenta) para "resolver" transparencia.
Transparencia vem de indice e papel declarado.

Referencia: doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md
"""

from __future__ import annotations

import sys

DEPRECATION_BLOCKER = "deprecated_transparency_destroyer"

MESSAGE = """\
[BLOQUEADO] fix_png_transparency_final.py foi removido do caminho canonico (forge-art P0.2).

Motivo (medido no codigo anterior, nao suposto):
  - compunha a imagem sobre PRETO usando o alpha como mascara
  - requantizava com median-cut e entao removia o marcador `transparency`
  - salvava por cima do arquivo original

O nome prometia consertar transparencia; o codigo a destruia.

Proxima acao causal:
  * PNG ja indexado com PLTE inflada ou index 0 no papel errado:
      python3 tools/image-tools/normalize_indexed_sgdk_png.py transparent0 <arquivo.png>
    (use `unused0` quando o contrato do asset reservar o index 0 como nao visivel)
  * PNG ainda nao indexado:
      a indexacao pertence a `forge-art convert`. Ela precisa declarar o papel do
      index 0 antes de escolher a paleta. Nao ha atalho aprovado.

Este script falha fechado de proposito. Nenhuma flag o reabilita.
"""


def main() -> int:
    sys.stderr.write(MESSAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
