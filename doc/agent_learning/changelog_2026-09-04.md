# Changelog de curadoria — 2026-09-04

## Escopo

Curadoria do fluxo visual canônico a partir do estudo Kirby Cloude v11. Nenhum
asset do jogo foi alterado ou promovido.

## Mudanças

- manifesto e validator de workset visual;
- congelamento executável de projeto como estudo de caso;
- reclassificação de rasterização por coordenadas para
  `procedural_code_probe`;
- schema obrigatório no auditor de proveniência;
- diagnóstico `active_only` com histórico opt-in;
- skills de sprite, animação, diagnóstico, excelência e guardian alinhadas ao
  mesmo contrato de elegibilidade.

## Evidência exigida para fechamento

- `forge-art self-check`;
- suíte física `test_native_edit.py`;
- `test_art_pipeline.py`;
- self-check do auditor de proveniência;
- validação do workset congelado e tentativa adversarial de produção;
- `quick_validate.py` nas skills modificadas;
- `git diff --check` escopado.

## Resultado medido

- `forge-art self-check`: 136/136;
- `test_native_edit.py`: 11/11;
- `test_art_pipeline.py`: 133/133;
- auditor de proveniência: self-check aprovado e Kirby `verdict=OK` após a
  reclassificação honesta dos 25 símbolos;
- workset congelado: válido; ataques de edição, conversão e shootout recusados
  com `visual_production_frozen` e sem nova saída;
- cinco skills modificadas: válidas por `quick_validate.py`.
