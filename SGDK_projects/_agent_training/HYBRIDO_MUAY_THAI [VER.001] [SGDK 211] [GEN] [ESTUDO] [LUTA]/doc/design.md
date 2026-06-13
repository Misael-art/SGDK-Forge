# Design — O Híbrido (Muay Thai + Mutação de Pedra/Lava)

Status: `training_design_locked`

## Correcao de rota v002

O personagem v001 produzido por `data/builders/build_hibrido_assets_v001.py` foi
rebaixado para `technical_lab_asset`. Ele usa primitivas locais e nao representa
arte final premium. A solucao final do treino deve partir de fonte visual autoral
ou concept candidate de IA, seguida de traducao/redesenho para pixel art nativa.

## Objetivo do treino

Produzir um personagem em pixel art no estilo Capcom (X-Men vs Street Fighter) respeitando restrições do Mega Drive e registrando contratos para aprendizado e curadoria posterior.

## Contratos travados

- Escala nominal: `48x64` (bbox em múltiplos de 8)
- Pipeline: `lineart_blocking_1px` → color blocking → rampas por material → FX → validação pixel-strict → prova em emulador
- Split de paleta: `PAL2` (corpo/pedra/roupa) + `PAL3` (fogo/lava/glow)
- Formato: PNG indexado, 16 entradas, index 0 transparente, cores no grid 9-bits

## Silhueta e leitura

- Massa imponente (ombros largos, tronco bloco, pernas curtas e pesadas)
- Mãos grandes e antebraços volumosos (leitura “poderoso parado”)
- Faixas nos punhos como ponto de contraste e guia visual do golpe
- Cicatriz no peito como “ponto focal” (glow em PAL3)

## Materiais (cel shading)

- Pedra: 3 tons (sombra/base/luz) + micro textura (rachaduras e ruído controlado)
- Pele: 3 tons (sombra/base/luz) em regiões não petrificadas (rosto/pescoço)
- Bandagens: 2–3 tons com dobras simples (sem AA)
- Fogo/Lava: 3–5 tons (contorno escuro + laranja/amarelo + branco) com borda dura

## Entregas

- Model sheet (pixel): `data/processed/model_sheets/hibrido_fighter_model_sheet_48x64_v002.png`
- Sprites (runtime):
  - `res/sprites/hibrido/*_body_48x64_strip_v002.png` (PAL2)
  - `res/sprites/hibrido/*_fx_48x64_strip_v002.png` (PAL3)
- Contratos:
  - `doc/contracts/palette_role_map_v001.json`
  - `doc/contracts/sprite_sheet_contract_v001.json`

## Prova mínima (existência)

- Build: `out/rom.bin`
- Gate: rodar no BlastEm via `run.bat` e capturar screenshot dedicada

## Acoes minimas v002

- `idle`: guarda respirada com peso e leitura de ombros.
- `walk_step`: passo curto de lutador, mantendo pivo e linha de chao.
- `teep`: golpe simples de Muay Thai com startup, active e recovery.
