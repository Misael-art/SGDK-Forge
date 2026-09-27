# Escopo vigente da revisao — 2026-09-25

O usuario autorizou explicitamente a curadoria MUGEN nesta sessao. O parecer
por ID esta no workspace em `doc/curation/2026_09_25_mugen_coordination/`.
Foram promovidas instrucoes delimitadas; nenhuma ROM, arte ou qualidade AAA.
O ledger local contem aprendizado herdado de The Forge. Sua presenca ou schema
valido nao comprova ocorrencia local; nao promover em lote. A tabela abaixo
sobre branding pertence ao material legado do template e fica preservada
como historico, nao como estado de autorizacao ou evidencia do Mugenesis.

---

# Canonical Promotion Review

Use este arquivo para revisar, com cautela, se algum aprendizado local deve ser levado para o framework canonico.

## Politica

Promocao canonica so ocorre quando um humano ordenar explicitamente a assimilacao. Ate la, tudo permanece local e passivo.

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | sim (ROMs + BlastEm d2–d5) |
| O padrao funcionou fora de um caso unico? | parcial (so modelo/branding) |
| Os riscos e limites estao escritos? | sim, em `the_forge_opening_lessons.md` |
| Existe conflito com `SGDK_GLOBAL.md`? | nao — reforca DMA/VBlank, H-Int RTE, bloqueio estetico |
| Existe conflito com headers SGDK 2.11? | nao — cita `unpackTileMap` e `HINTERRUPT_CALLBACK` |
| Um humano aprovou a promocao? | **nao** |

## Decisoes

| Data | Candidato | Decisao | Justificativa | Autor humano |
|---|---|---|---|---|
| [DATA] | [candidato] | `needs_human_review` | [motivo] | [nome/handle] |
| 2026-09-27 | Diagnostico de VRAM fisica, primeiro guard, paleta de atlas e uniao de tiles | `instrucoes_canonicas_aplicadas` | Pedido humano explicito nesta conversa; testes host e ROM diagnostica sustentam o metodo. O caso continua sem aprovacao de streaming, piso ou FPS. Owners existentes atualizados; ver `tools/sgdk_wrapper/.agent/references/mugen_suzaku_vram_diagnostic_2026_09_27.md`. | usuario desta sessao |
