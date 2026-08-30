# Especificação de Cena — neutral_reference

## Identidade

- scene_id: `neutral_reference`
- papel: fixture técnica interativa e determinística
- visual: grid/texto geométrico neutro, sem asset autoral ou licenciado
- owner: `src/scenes/scene_demo.c`
- telemetria owner: `src/system/reference_contract.c`

## Loop

A ROM solicita deslocamento à direita, salto e estabilização. A simulação marca
os bits `moved`, `airborne` e `static_table_skipped` somente depois de observar
os estados reais. Ao completar os três, exporta `completed=1` no bloco `FREF`.

## Budgets proporcionais

- resolução: 320x224;
- CRAM declarada pela fixture: 16 entradas, zero ilegal;
- sprites: nenhum sprite de recurso externo;
- HScroll: modo plane da cena; tabela de referência é payload de teste CPU;
- alocação dinâmica: nenhuma;
- DMA estático redundante permitido: zero.

## Evidência exigida

- `out/rom.bin` e SHA-256;
- screenshot BlastEm da cena `neutral_reference`;
- `save.sram` contendo `FREF` e `MDRT`;
- relatório de `canonical_fixture_gate.py`;
- manifesto selado e gate final com o mesmo SHA-256.

## Limites de claim

O contrato prova apenas sua própria mecânica de fixture. Não prova jogo
completo, arte final, áudio, performance sustentada nem `ready_for_aaa`.
