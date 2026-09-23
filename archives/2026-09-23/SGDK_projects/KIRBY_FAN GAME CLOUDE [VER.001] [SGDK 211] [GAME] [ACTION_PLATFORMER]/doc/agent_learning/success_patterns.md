# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| 2026-08-18 | `promotion_candidate` | IMAGE BEST no display | unpackTileMap em buffer estatico no warmup + TILE_ATTR assado + DataRect/DMA_QUEUE. Serie cpu 160→92→83, ob 9→0 | ROM e6437530 / ceaa7028 / 661e4086; d3/d4/d5 | Dest sem malloc. Fatiar so depois de unpack. Owner: sgdk-runtime-coder |
| 2026-08-18 | `promotion_candidate` | evidencia VLAB | Screenshot e o beat; frame_counter VLAB anda de 60 em 60 e atrasa o SRAM. Dois F151 podem ser atos diferentes | d2_reveal vs d2_lock; probe export 60 / warmup 90 | Nao e relogio fino. Owner: emulator-vdp-evidence-curator |
| 2026-08-18 | `local_note` | The Forge fio | 12 fagulhas do preludio ao nome no lugar de 56 estilhacos: spr 51→13, climax sem +ob | ROM e79a9de4…; d2_hit1 spr=13 | Nao reabrir enxame sem resim de scanline |
| 2026-08-18 | `local_note` | The Forge martelo | Prefetch quadro 4 no slot livre (lock t==21) e 1/2 em F12–13 com sprite oculto | ROM ceaa7028…; d4_hit1 | Nao evictar o quadro que esta na tela |
| 2026-08-18 | `local_note` | The Forge ceu | Conceito IA so para composicao; placa VDP reconstruida em 16 cores 9-bit. Unique 125→26. Ato I fica navy+estrelas | ROM 661e4086…; d5_sky | Ainda placeholder. Selo BlastEm recusa void |
| 2026-08-18 | `local_note` | The Forge nametable | Assar TILE_ATTR no preludio e escrever metades com DataRect+DMA_QUEUE. cpu 92→83, ob=0 | ROM ceaa7028…; d4_hit1/d4_forge | Pico 83 residual. Nao e validado_budget |
| 2026-08-18 | `local_note` | The Forge parede | Unpack APLIB 40x28 no preludio (probe warmup) e nametable no reveal. ob 9→0, cpu 160→92 | ROM e6437530…; d3_hit1/d3_forge | Pico 92 residual. Dest estatico, sem malloc |
| 2026-08-18 | `local_note` | The Forge descida | Paleta da forja so depois do tilemap da parede: emerge escura, nao muro fantasma no ceu. 12 fagulhas no lugar de 56 estilhacos: spr 51→13 | ROM e79a9de4…; d2_reveal/d2_lock/d2_hit1/d2_forge | Golpes ainda cpu 160 / ob 9. Nao e validado_budget |
| 2026-08-18 | `local_note` | branding_sequence_v2 ato 3 | Forja travada + restore unico de props + nomes na parede (y<64) + PRESENTS no fogo. over_budget 0 em F271/331/451/511 | ROM 40fec78b…; fin2/fin4/fin6/fin72 | Nao e licenca para arte final nem ready_for_aaa |
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.
