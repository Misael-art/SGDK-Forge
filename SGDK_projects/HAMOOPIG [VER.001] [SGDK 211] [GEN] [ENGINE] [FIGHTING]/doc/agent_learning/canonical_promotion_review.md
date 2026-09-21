# Canonical Promotion Review

Use este arquivo para revisar, com cautela, se algum aprendizado local deve ser levado para o framework canonico.

## Politica

Promocao canonica so ocorre quando um humano ordenar explicitamente a assimilacao. Ate la, tudo permanece local e passivo.

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | sim (ROMs + BlastEm d2–d5; Musgo ROM c81fee9f… + screenshot seletor) |
| O padrao funcionou fora de um caso unico? | parcial (marca 2026-08-18; roster Ken+Musgo 2026-09-11 no mesmo engine) |
| Os riscos e limites estao escritos? | sim, em `the_forge_opening_lessons.md` e `musgo_roster_lessons.md` |
| Existe conflito com `SGDK_GLOBAL.md`? | nao — reforca DMA/VBlank, H-Int RTE, bloqueio estetico, teto source_candidate |
| Existe conflito com headers SGDK 2.11? | nao — cita `unpackTileMap`, `HINTERRUPT_CALLBACK`, `SYS_hardReset` |
| Um humano aprovou a promocao? | Sim, em 2026-09-18, para a assimilacao instrucional delimitada abaixo; sem promocao de maturidade |

## Decisoes

| Data | Candidato | Decisao | Justificativa | Autor humano |
|---|---|---|---|---|
| 2026-09-11 | Checklist onboarding lutador (sgdk-runtime-coder / fighting-game-design) | `needs_human_review` | Ken e Musgo repetiram o mesmo buraco; ainda so HAMOOPIG; nao criar skill nova | pendente |
| 2026-09-11 | Harvest video-first (sprite-animation) | `needs_human_review` | ffmpeg `%` + hibrido de impacto; util no workflow de animacao | pendente |
| 2026-09-11 | Downscale direto IA (art-translation-to-vdp) | `needs_human_review` | Ja existe regra no catalogo; Musgo e evidencia nova de luta grande | pendente |
| 2026-09-11 | Bundle sem VLAB (emulator-vdp-evidence-curator) | `needs_human_review` | Screenshot de seletor existe; selo recusado; nao apagar boot | pendente |

Nota de roteamento 2026-09-11: o Capture marcou `create_skill` em onboarding de lutador, harvest video-first e engine sem VLAB porque o `learning_owner_catalog.json` nao tem frase. Isso e falha de roteamento, nao gap puro. Curadoria deve patchar owners existentes (`sgdk-runtime-coder`, `fighting-game-design`, `sprite-animation`, `emulator-vdp-evidence-curator`, `art-translation-to-vdp`). Nao criar skill nova. Downscale IA roteou corretamente para `art-translation-to-vdp`.


## Curadoria canonica autorizada — 2026-09-18

O pedido explicito do usuario nesta data autorizou assimilar o aprendizado do projeto ainda incompleto. Foram incorporados oito principios a uma referencia compartilhada e quatro skills existentes, sem alterar runtime, promover especializacao ou aprovar qualidade AAA. O registro de decisoes e hashes e `doc/curation/2026_09_18/curation_decisions.json`; o diagnostico e plano estao em `doc/curation/2026_09_18/curadoria_aprendizado_canonico.md`. Os candidatos historicos abaixo nao foram todos aprovados: esta autorizacao tem escopo de assimilacao instrucional selecionada.
