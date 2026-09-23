# HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]

Status: `lab_not_delivery=true`

Nota operacional v002: os assets v001 gerados por `data/builders/build_hibrido_assets_v001.py`
sao `placeholder`, `technical_lab_asset`, `procedural_renderer` e `not_final_art`.
Eles preservam aprendizado de pipeline, mas nao sao fonte visual premium nem personagem final.

Treino de criação de personagem (model sheet + sprite sheet) com foco em:

- escala `48x64` (metasprite)
- split de paleta: PAL2 corpo/pedra/roupa, PAL3 fogo/lava/glow
- assets finais em PNG indexado (16 cores), grid 9-bits e index 0 transparente

Entradas e decisões ficam em `doc/`. Assets gerados ficam em `res/` (runtime) e `data/processed/` (referências de produção).
A rota visual v002 usa fonte IA apenas como concept/source candidate; a traducao final para
runtime continua classificada como treino/laboratorio ate aprovacao humana e evidencia BlastEm fresca.

Reprovacao humana v002: o source/model sheet e a traducao runtime falharam no gate
visual. A Pose 3 apresenta leitura de membro extra/duplicado, as poses de esforco
mantem face estatica e o runtime 48x64 nao preserva olhos, braco de lava, calcao
e contraste quente. Portanto v002 e `placeholder_rejected_visual_translation`.
Build, PNG indexado e BlastEm comprovam apenas sintaxe tecnica.

Regras locais obrigatorias:

- Antes de converter, rodar input gatekeeper de anatomia: 2 bracos, 2 pernas, 1 cabeca, 1 tronco, articulacoes plausiveis.
- Antes de aceitar animacao, auditar acting facial por estado.
- Nao usar downscale direto ou quantizacao global como sprite final 48x64.
- Validar PAL2/PAL3 por semantica de material, nao so por limite de cores.
