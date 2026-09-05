# Failure Patterns

Registre aqui falhas, falsos positivos, tentativas ruins e decisoes que nao devem ser repetidas sem nova evidencia.

| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |
|---|---|---|---|---|---|---|
| 2026-08-18 | `promotion_candidate` | VDP | `VSCROLL_COLUMN` usado como cortina da COIFA envolve a bigorna de preto | A tabela de coluna desloca o plano inteiro, nao uma faixa | Nao e cortina local. Owner: shadow-highlight-scroll-fx | pres4/pres6; memoria 2026-08-18 |
| 2026-08-18 | `promotion_candidate` | VRAM | `sVramAuthor = sVramBgA` apaga a bigorna em F451 | Tileset do wordmark sobrescreve tileset vivo do tilemap | Nunca reusar indice sob plano vivo. Bissect ponto 6 | bis_6; ROM 1d432425… |
| 2026-08-18 | `promotion_candidate` | CRAM/cena | Menu distorcido apos a marca | `VDP_drawText` herda PAL0 da forja + scroll/S/H residual | Teardown: fonte, PAL3, barra, handoff para MENU | front12 F691 |
| 2026-08-18 | `local_note` | paleta | Muro-fantasma roxo no ceu | Lerp star→forge com tilemap do ceu ainda visivel | So aquece depois do tilemap da parede pousar | F91 ghost vs d2_reveal |
| 2026-08-18 | `local_note` | H-Int | Crash `0x23080000` no primeiro H-Int | Handler `void` emite RTS; SR vira PC alto | `HINTERRUPT_CALLBACK` (RTE); nao armar no enter | runtime_decision_log h_int_why |
| 2026-08-18 | `local_note` | WINDOW | PRESENTS invisivel em F480 | `VDP_setWindowVPos(FALSE,n)` e topo | TRUE=fundo; ou carimbar em BG_A sem WINDOW | act3_presents vs pres_fix |
| 2026-08-18 | `local_note` | captura | Magenta no frame_1 do burst | Janela BlastEm ainda nao composta | Espera 0.35 s; PAL0[0] no dump e 0x0000 | capture_blastem_evidence_linux.sh |
| 2026-08-18 | `local_note` | roteamento IA | `imagegen_tool.py route` pede ComfyUI | Detector nao ve `image_gen` desta sessao | Se a ferramenta nativa existe, o canal e nativo | generation_channel_decision 2026-08-18 |
| 2026-08-18 | `local_note` | The Forge parede | cpu 160 / ob 9 entre F151 e F211, atribuidos aos golpes | `VDP_setTileMapEx` em IMAGE BEST desempacota o APLIB 40x28 inteiro no display (F154 e F155) | unpackTileMap em buffer estatico no warmup; nametable no reveal | d2_hit1 ob=9 cpu=160; d3_hit1 ob=0 cpu=92 |
| 2026-08-18 | `local_note` | The Forge ceu | Bundle do BlastEm recusa o ato I (`blank_or_low_information_capture`); VLAB `frame_counter` anda de 60 em 60 | Campo estelar e quase preto; SRAM do probe nao e por quadro | Autoridade do beat e o screenshot; nao usar o contador VLAB como relogio fino; nao vender selo do ceu | d2_sky / d2_sky2 / d2_drop rejeitados; d2_reveal/d2_lock ambos reportam F151 e mostram atos diferentes |
| 2026-08-18 | `local_note` | branding ato 3 | Cortina de coluna corta a bigorna; wipe apaga o ferro; unpack APLIB 8x + WINDOW some com o MASTER | VSCROLL_COLUMN move o plano inteiro; clear em y>=64; setTileMapEx descompacta o mapa todo por chamada | Nao usar scroll de coluna como cortina local; restore, nao clear; uma chamada so; PRESENTS em BG_A | pres4/pres6 costura preta; hq6 MASTER ausente cpu 201; fin* over_budget 0 |
| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log/screenshot/hash] |

## Regras

- Falha sem evidencia deve ser marcada como hipotese.
- Solucao nao comprovada nao vira recomendacao.
- Se a falha indicar risco canonico, classifique como `needs_human_review`.
