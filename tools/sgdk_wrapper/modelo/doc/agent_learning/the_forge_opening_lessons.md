# Caderno de aprendizado — abertura The Forge (modelo)

**Para o proximo agente.** Leia isto antes de tocar em
`scene_branding_v2.c`, `res/branding/` ou de declarar status da marca.
Nao e canon. Nao e AAA. `canonical_promotion_performed=false`.

Projeto: `tools/sgdk_wrapper/modelo` (template/engine brand, nao jogo).
`delivery_claim_ceiling=none`. `ready_for_aaa=false`.
ROM vigente ao fechar este caderno:
`661e408694457859da97af6e3afa729be152bcff46b9984efd5eab3f777801a5`.

Hierarquia de verdade: `doc/10-memory-bank.md` > GDD > spec > este caderno.

---

## 0. O que esta sequencia e (e o que nao e)

A marca e a oficina. Quatro atos (~7 s, F0–F420, NTSC):

| Ato | Quadros | O que o espectador deve ler |
| I preludio | 0–84 | void navy, pulso, D-pad = toque da criacao. START salta. A nao salta. |
| II descida | 84–168 | ceu sai por VSCROLL `t²*168/span²`; parede so em F154 |
| III lock | 168–228 | ruinas, bigorna, martelo sobe, fagulhas pairam |
| IV dois golpes | 228 / 312 / 348 | 1o = materia; 2o = identidade; FORGE so depois do 2o |

Fio condutor: **12 fagulhas** do preludio ao nome. O enxame de 56
estilhacos foi medido (ob 20 / cpu 182 / spr 51) e abandonado.

Nao declare: `validado_budget`, `ready_for_aaa`, descida continua de
224 px, sample de estudio, arte final do ceu.

---

## 1. Doutrina operacional medida

1. **Se nao rodou no BlastEm, nao existe.** Intencao nao e validacao.
2. **Bisseccione antes de corrigir.** Um desligamento por ROM.
3. **O screenshot e o beat.** O `frame_counter` do VLAB anda de ~60 em
   60 (91 / 151 / 211 / 331) porque o probe exporta a cada 60 quadros
   e ignora os primeiros 90 (`PROBE_SCENE_WARMUP_FRAMES`).
4. **Atribua o pico a janela certa.** F151 ob=0 e F211 ob=9 significou
   parede em F154–155, nao o slam (F228) nem o FORGE (F348).
5. **O teto do hardware e o alvo; o claim exige medicao.** Empurre o
   que tenta; so afirme o que mediu.
6. **Este projeto e a marca da engine, nao um jogo AAA.** Melhorar a
   apresentacao nao autoriza `ready_for_aaa`.

---

## 2. Falhas medidas (nao repetir)

### 2.1 Hardware que nao faz o que o nome sugere

| Tentativa | O que o VDP fez de verdade | Evidencia |
| `VSCROLL_COLUMN` para levantar so a COIFA | Move o plano inteiro; fogo sobe; preto envolve a bigorna por baixo | memoria 2026-08-18; pres4/pres6 |
| `HSCROLL_LINE` como palco | Rasgou a bigorna | revertido |
| `VDP_setWindowVPos(FALSE, 22)` | WINDOW no **topo**; PRESENTS em y=23 ficou fora | act3_presents |
| `VDP_clearTileMapRect` em y>=64 | Apagou os tiles da bigorna | restore de `img_forge_bg_a_props` |
| Plane wrap de 32 tiles | Nao ha travel continuo de 224 px da parede | descida = scroll do ceu + swap |

### 2.2 APLIB no display

`VDP_setTileMapEx` em IMAGE `BEST` **desempacota o mapa inteiro a cada
chamada** (40×28 = 2240 B origem).

- Uma fileira por quadro = unpack 8× → cpu 196 / MASTER some.
- Dois unpacks cheios em F154–155 → **cpu 160 / over_budget 9**,
  atribuido por engano aos golpes.
- `drawImageEx` do logo no display recarrega tileset por cima do martelo.

Cura medida:

1. `unpackTileMap(src, dest)` com `dest.tilemap` em `static u16[40*28]`.
   Sem `MEM_alloc`. Header: `sdk/sgdk-2.11/inc/tools.h`.
2. Pagar o unpack no preludio F8–F10 (dentro do warmup do probe).
3. Assar `TILE_ATTR_FULL(pal, prio, 0, 0, vram) + cell` no buffer.
4. Reveal: `VDP_setTileMapDataRect` + `DMA_QUEUE` em metades de 14 fileiras.
5. Fatiar so **depois** de descompactar. Fatiar IMAGE BEST re-descompacta.

Serie de budget nos golpes: **160 → 92 → 83**, `over_budget` **9 → 0**.
Limiar do probe = 100. Pico 83 residual (slam PCM / quadro 3 do martelo /
`SPR_update`). Nao e `validado_budget`.

### 2.3 VRAM: nao reusar tileset vivo

Bissect Act 3 (F451, um ponto por ROM):

| Ponto | Desligou | O que mudou |
| 1 | cortina `VSCROLL_COLUMN` | so tirou a cortina |
| 2 | wordmark projeto | MASTER sumiu; MISAEL ficou visivel (estava coberto) |
| 3 | PRESENTS | nada (ainda nao executa em F451) |
| 4 | `PAL_fadeOutAll` | nada (ainda nao executa) |
| 5 | `SPR_reset` | brasa em cima do MASTER; sintomas iguais |
| 6 | `sVramAuthor = sVramBgA` | **bigorna voltou** |

Causa da bigorna: o tileset do wordmark sobrescreveu o tileset vivo de
`img_forge_bg_a_props`. O tilemap da bigorna apontava para indices
errados. Wordmarks carregam **depois** da janela do martelo
(`sVramHammer + 72`).

Magenta nas bordas: so no `animation_frames/frame_1.png` (janela do
BlastEm ainda nao composta). PAL0[0] no dump e 0x0000. Nao e regressao
do ato 3. O script Linux espera 0.35 s antes do burst.

### 2.4 H-Int e APIs

- Handler `void` emite RTS. H-Int e excecao: RTS deixa SR `0x2308` como
  word alta do PC → `0x23080000`. Use `HINTERRUPT_CALLBACK` (RTE).
- Nao ligar H-Int em `enter()`: DMA da carga ainda nao flushou.
- `PAL_fadeOutAll` mediu over_budget 8. Nao usar no closer.
- `int` no GCC 68000 e 32 bits. Use `u16`/`s16`.
- `VDP_drawText` herda a paleta corrente. Depois da forja (PAL0 quente)
  o menu sai distorcido. Cura: recarregar fonte + PAL3 ouro + barra preta.
- Handoff da marca vai para `APP_SCENE_MENU`, nao para o boot de debug.

### 2.5 Audio

- Whoosh no contacto do martelo mata o impacto. Slam = WAV XGM2 13.3 kHz
  em PCM CH2 pri 15 + ruido branco PSG + tom grave. Nao parar a BGM.
- Loop do `xgm2tool` saiu 0 frames. `AUDIO_update` retriga `XGM2_play`
  se `sBgmWanted && !XGM2_isPlaying()`. Nao e partitura humana.

### 2.6 Probe e evidencia

- Warmup 90 quadros nao conta CPU. Amostras: as primeiras 32 depois do
  warmup. `over_budget` e `max_cpu` acumulam a cena toda e exportam
  a cada 60 quadros.
- Dois captures com o mesmo `frame_counter` VLAB (ex. 151) podem ser
  atos diferentes. Autoridade = screenshot.
- `blank_or_low_information_capture` recusa o Ato I mesmo quando o ceu
  e valido (void navy). Nao venda selo do ceu. O PNG do BlastEm ainda
  e evidencia de que o ato existiu.
- Burst em delay 0 pega o boot, nao o beat pedido.

### 2.7 Arte

- Pixel de primitiva em disco **nao** satisfaz o bloqueio estetico.
  `source_kind: procedural_primitive` nunca e `final`.
- Lerp de paleta do ceu para a forja **com o tilemap do ceu ainda
  visivel** produz muro-fantasma roxo. So aquece depois do tilemap novo.
- Dump de nebula IA no `res/` explode tiles unicos. Conceito IA = composicao;
  placa VDP = reconstrucao 9-bit com campo liso + estrelas carimbadas.
- `imagegen_tool.py route` neste host pode dizer `local_install_required`
  e ignorar `image_gen` nativo da sessao. Se a ferramenta callable existe,
  o canal e `native_chat_image_generation_callable`.
- PLTE tem de ter 16 entradas e IHDR bitdepth 4. PLTE 256 faz o rescomp
  tratar indices iguais como tiles diferentes.
- PAL0[1] e PAL0[2] sao o pulso organico do Ato I. Nao gaste esses
  indices no campo navy.

---

## 3. Padroes que funcionaram (com limite)

| Padrao | Quando usar | Nao use para |
| Forja travada; FORGE por **restore** unico de props | Sair do nome sem apagar a bigorna | Wipe/clear em y>=64 |
| Nomes na parede y<64; PRESENTS em BG_A y=26 | Sem WINDOW no closer | WINDOW copiando BG_B |
| 12 fagulhas do ceu ao nome | Fio condutor barato (spr 13) | Reabrir 56 estilhacos sem resim |
| Descida = VSCROLL do ceu + reveal em 2–4 quadros | Unico travel honesto no wrap de 32 tiles | Prometer 224 px continuos |
| Prefetch do martelo (quadros 1/2 em F12–13; quadro 4 no lock t==21) | HIT1 sem unpack LZ4W no slam | Prefetch no slot que esta na tela |
| Janela dupla do martelo 36+36 | `dma_queue_contract` | Residencia dos 7 quadros (252 tiles) |
| START skip; A = toque da criacao | Memorando The Forge | A como skip |
| Traducao VDP do ceu (navy + 26 unique) | Ato I legivel, budget baixo | Arte final / selo do void |

---

## 4. Mapa de arquivos

| Papel | Caminho |
| Runtime 4 atos | `src/scenes/scene_branding_v2.c` + `inc/scenes/branding_v2.h` |
| Menu (PAL3, fonte, barra) | `src/scenes/scene_menu.c` |
| Slam + BGM | `src/system/audio.c` (`AUDIO_CUE_BRAND_HAMMER_SLAM`, `AUDIO_startBrandBgm`) |
| Probe | `src/system/runtime_probe.c` (warmup 90, export 60, threshold 100) |
| Memorando | `doc/the_forge_direction.md` |
| Decisoes de runtime | `doc/runtime_decision_log.json` |
| Proveniencia | `doc/asset_provenance_manifest.json` |
| Traducao do ceu | `data/source_art/branding_v2/translate_starfield_v02.py` |
| Captura Linux | `tools/sgdk_wrapper/capture_blastem_evidence_linux.sh` |
| Build Linux | `build_sgdk_wine_bridge.sh` (nunca `.bat` neste host) |

Nao retune sem resim: `SHARD_COUNT` 56 / `SHARD_ROWS` 7 /
`SHARD_ROW_STAGGER` 6 / `sector=(index*5)&15`. O climax atual **nao
chama** `brandPrepareShards` / `brandUpdateShards`. Deixar o codigo
morto e honesto; reativar e regressao de budget.

---

## 5. Como capturar um beat

```
warmup-seconds ≈ tempo de tela desejado
--target-scene 0 --burst-count 0
```

O ROM ja esta em `APP_SCENE_BRANDING`. Burst antes do warmup atrasa o
screenshot e o frame_1 pode sair magenta.

Beats uteis desta ROM: ceu ~2.0 s, emerge ~2.9 s, lock ~3.3 s,
hit1 ~4.1 s, forge ~6.2 s. Confira sempre o PNG, nao o VLAB.

---

## 6. Status honesto ao fechar este caderno

| Eixo | Estado |
| ROM / BlastEm | 4 atos observados; lock/hit1/forge selados |
| Budget | ob=0 nos golpes; pico cpu 83; **nao** validado_budget |
| Ceu | placeholder composto de conceito IA; unique 26; selo recusa void |
| Audio | slam+BGM ligados; sintetico de laboratorio; `needs_review` |
| Arte | sem aprovacao humana; primitivas de brand_* continuam placeholder |
| Claim | marca da engine do template. Nao e jogo AAA. Nao e ready_for_aaa |

---

## 7. O que o proximo agente deve fazer (e o que nao deve)

Faca, se o humano pedir:

- revisao humana do ceu/forja antes de qualquer promocao;
- sample real de martelo / trilha composta (o peso sonoro ainda e lab);
- travel verdadeiro da parede so com prova de wrap/VRAM, nao por desejo.

Nao faca por inercia:

- reabrir o enxame de 56;
- `PAL_fadeOutAll`, `VSCROLL_COLUMN` como cortina, wipe da bigorna;
- unpack APLIB no display;
- `sVramX = sVramY` em tileset que ainda esta no plano;
- declarar AAA, `validado_budget` ou ceu final;
- caçar o cpu 83 enquanto o teto visual da marca for outro.
