# P6 — Catalogo de efeitos MD: registro consultivo e aderencia

Status: **consultivo — nada implementado**. Fonte canonica, nao copiada: `doc/05_technical/97_MASTER_TECH_TABLE_180.md` (180 tecnicas, 17 eixos) na raiz do Forge.
Regra: um item daqui so vira trabalho com direcionamento proprio, medicao antes/depois e evidencia BlastEm.

## A. Ja em uso no Mugenesis (visto rodando)
| ID | tecnica | onde | ROM |
|---|---|---|---|
| HU-101 | HUD em WINDOW | P4 `fight_hud.c` | b138fb35 |
| HU-102 | lifebar com tiles graduados | P4, segmentos de 9 variantes | b138fb35 |
| HU-108 | tempo em tiles | P4 | b138fb35 |
| HU-109 / CI-140 | contador de combo | P4 "N HITS" | b138fb35 |
| CI-133 | sparks de colisao | P1, ancorados no contato | 38a67c94 |
| CI-131 | hitstop | runtime (pausetime MUGEN) | da354830 |
| TC-053 | dither como transparencia | P5, sombra | 46a9cd65 |
| TC-051 / RO-078 | index 0 / flip | runtime base | da354830 |
| OM-173 / OM-178 / OM-179 | fila de DMA, pool, FSM | runtime | da354830 |
| OM-180 | profiling de frame | `-DMG_PROFILE` | build de perfil |

## B. Candidatos com aderencia (ordem sugerida, nao aprovada)
| ID | tecnica | por que cabe | risco medido/esperado |
|---|---|---|---|
| CI-135 / CI-138 | camera shake | EnvShake do MUGEN hoje e aproximado | barato (1 scroll/quadro) |
| PC-034 / CI-132 | flash de paleta no impacto | supers/KO; MUGEN usa PalFX/BGPalFX | CRAM DMA de 32 B; respeitar PAL0 do HUD |
| PA-158 / PA-157 | poeira e estilhacos | queda e knockdown do Ken ja referenciam sprites | pressao de linha no chao com a sombra (P5) |
| PM-003 / FB-086 / BA-* | parallax e fundo animado | estagio E4 | PAL0 1..8 reservada; custo de DMA a medir |
| ID-041 | Shadow/Highlight | reabre P5 (sombra S/H) no E4 | conflita com a paleta do HUD; memo P5 |
| CI-139 | sparks com ciclo de paleta | PAL3 e exclusiva de fx | baixo |
| PM-005 / PM-006 | camera com damping e limites | camera atual segue o centro dos lutadores | baixo |

## C. Fora de escopo neste jogo
- **Eixo 02 (pseudo-3D):** 011–015 e 019, estrada e warp.
- **Eixo 07/08:** zoom e rotacao por hardware; ja sao recusas honestas.
- **Eixo 12 (texto narrativo):** exceto TN-120 (legibilidade), ja coberta pelo HUD.
- **Eixo 13 (cutscenes):** so volta se houver modo historia.
- **Itens de plataforma e aventura:**
  - OM-172 slope, OM-175 raycast, HU-104 minimapa e HU-105 retículo;
  - PA-151..155 e PA-160: clima de estagio, reavaliar no E4.
- **OM-176 (interlace 448):** custo de VRAM incompatível com dois lutadores grandes.
- **P3 (multiplex de aneis):** NO-GO, ver `doc/hud/p3_ring_multiplex_memo.md`.
