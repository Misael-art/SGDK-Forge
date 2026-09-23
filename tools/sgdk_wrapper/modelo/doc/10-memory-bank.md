<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-03T11:18:02.8853590-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 5
- Ultimo build versionado: build_v002
- ROM vigente: `22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f` (`262144` bytes)
- Validation summary: errors=0 warnings=5
- Blockers vigentes: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed
- Evidencia de emulador: BlastEm TargetScene=0 observado; runtime_metrics partial com 1 pico de CPU
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=funcional performance=parcial_com_pico_cpu audio=ok hardware_real=blastem_reference_emulator
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker Ã¢â‚¬â€ __PROJECT_NAME__

**Ultima atualizacao:** 2026-08-18
**Fase atual:** abertura The Forge em 4 atos; ceu v02 traduzido para VDP
**Proxima fase:** ceu ainda placeholder; emerge e swap, nao travel de 224 px; pico cpu 83; nao e ready_for_aaa

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- `APP_SCENE_BRANDING` e a primeira cena do modelo canonico.
- A cena usa cinco `IMAGE` reais em `res/branding/` declarados em `res/resources.res`.
- O baseline atual usa BG_A/B, scroll, HScroll line no slot project, palette cycling e skip por START/A.
- O runtime probe canonico existe e foi integrado ao boot/loop para gerar MDRT/READY em SRAM durante captura.
- A rota de audio foi corrigida para WAV XGM2 13300/6650 em vez de PCM bruto 11k.

### O que e placeholder

- A direcao sonora e funcional/sintetica, ainda nao e sample premium final.
- O cursor textual do slot author e efeito temporario em BG_A; nao deve ser vendido como visual AAA isolado.
- Monograma 3D/sprites complexos continuam fora do baseline ate novo asset pass e novo budget.

### O que falta para o slice ser completo

- Gerar `visual_vdp_dump.bin` ou atualizar formalmente o gate para aceitar MDRT+screenshot sem dump VDP.
- Resolver o pico isolado de CPU em `runtime_metrics.json` (`frame_index=128`, `cpu_load_ratio=401`) antes de declarar 60 FPS estavel.
- Resolver ou registrar explicitamente o rework visual apontado para `brand_author_logo.png`.
- Fechar o drift local de `.agent` e o GDD generico se o alvo for `ready_for_aaa`.

### Snapshot dos gates QA

- visual_lab_aprovado: false
- gameplay_rom_aprovada: false
- ready_for_aaa: false
- freshness_audit: ok
- scene_closeout_gate: blocked

### Blockers QA ativos

- `.agent` local teve caminhos ausentes materializados, mas segue com drift em `ARCHITECTURE.md` e `framework_manifest.json`.
- `doc/11-gdd.md` e generico; nao sustenta `ready_for_aaa` de projeto completo.
- `visual_aesthetic_report.json` marca `brand_author_logo.png` como `rework` e outros slots como `needs_review`.
- `visual_vdp_dump.bin` ainda nao existe em `out/evidence/blastem/`.
- Runtime probe registrou cena 0 no BlastEm, mas com captura parcial e um pico de CPU; budget segue nao validado.

### Metricas de codigo

- Branding baseline: 5 `IMAGE`, 5 `WAV XGM2`, 0 sprites runtime no baseline.
- `res_graph_report.json` passou com 10 declaracoes e 0 overlaps VRAM.
- Audio XGM2: maximo planejado de 2 PCM simultaneos, PSG ch0-ch2 como reforco tonal, PSG noise nao usado como canal tonal.
- `validate_audio.ps1` passou com 5 WAV XGM2 e estimativa de 29,97 KB (0,73% de 4096 KB).

### Estado de evidencia canonica

- ROM vigente: `out/rom.bin`, SHA256 `661e408694457859da97af6e3afa729be152bcff46b9984efd5eab3f777801a5`
- BlastEm: `d5_sky` observado (selo recusa void); `d5_lock`/`d5_hit1`/`d5_forge` selados; golpes ob=0 / cpu 83
- Claim maximo: abertura observada. Nao e `validado_budget` nem `ready_for_aaa`

---

## 2. O QUE ACABOU DE ACONTECER

**2026-08-18 — Caderno de aprendizado da abertura**

Tudo o que esta sequencia ensinou (VDP, APLIB, VRAM, probe, audio, ceu)
esta em `doc/agent_learning/the_forge_opening_lessons.md`. O proximo
agente le esse caderno antes de editar a marca. Capture local apenas;
`canonical_promotion_performed=false`.

**2026-08-18 — Ceu v02 (placeholder, lido no BlastEm)**

Canal: `native_chat_image_generation_callable`. Conceito B persistido em
`data/source_art/branding_v2/raw/starfield_v02b.jpg`. A placa VDP nao e o
JPG: `translate_starfield_v02.py` recorta nearest, monta campo navy,
estrelas nos slots de pulso PAL0[1]/[2] e uma barra de 24 px de calor.
4-bit, PLTE 16, unique 26 (era 125). Ainda `placeholder`.

ROM `661e408694457859da97af6e3afa729be152bcff46b9984efd5eab3f777801a5`

| Beat | Pasta | Selo | ob / cpu / spr |
| ceu | `d5_sky` | recusado (void) | 0 / 27 / 13 |
| lock | `d5_lock` | selado | 0 / 45 / 13 |
| 1o golpe | `d5_hit1` | selado | 0 / 83 / 13 |
| FORGE | `d5_forge` | selado | 0 / 83 / 13 |

O screenshot do ceu mostra navy + constelacoes + fagulhas ouro + barra
violeta. O selo continua recusando campo escuro. Forja nao regressou.

**2026-08-18 — Nametable assado, pico 92→83**

O 92 residual ainda era `VDP_setTileMapEx` percorrendo 1120 celulas com
override + LZ4W dos quadros 1/2 do martelo no lock. Agora o preludio
assa paleta/prioridade/indice no buffer; o reveal escreve quatro metades
com `VDP_setTileMapDataRect` + DMA_QUEUE; o martelo 1 e 2 carregam em
F12-F13 (warmup, sprite oculto).

ROM `ceaa7028bf8fc3a350d4cacc901003f955de55a464f0fea3666a6079b0887fdf`

| Beat | Pasta | ob / cpu / spr / scan |
| emerge | `d4_reveal` | 0 / 45 / 13 / 3 |
| lock | `d4_lock` | 0 / 45 / 13 / 3 |
| 1o golpe | `d4_hit1` | 0 / 83 / 13 / 5 |
| FORGE | `d4_forge` | 0 / 83 / 13 / 14 |

Pico 160→92→83. Ainda abaixo do limiar 100. O 83 que sobra e
provavelmente o slam PCM + quadro 3 do martelo + SPR_update. Nao e
`validado_budget`. Cacar mais CPU agora rende pouco frente ao ceu IA.

**2026-08-18 — Pico cpu 160 era APLIB no display**

A janela F151-F211 (ob=9 / cpu 160) nao era o slam nem o FORGE. O VLAB
exporta a cada 60 quadros: F151 ainda tinha ob=0; F211 ja tinha 9. HIT2
nao somou mais. Causa medida: `VDP_setTileMapEx` em IMAGE BEST desempacota
o APLIB 40x28 inteiro (2240 bytes origem) em F154 e de novo em F155.

Cura: `unpackTileMap` para buffers estaticos nos quadros 8-10 do preludio
(o probe ignora os primeiros 90). O reveal so escreve o nametable ja
aberto. Prefetch do quadro 4 do martelo no lock (slot 0) para o HIT1 nao
descompactar LZ4W no mesmo quadro do slam. Sem malloc. Sem enxame de 56.

ROM `e6437530f7951d404417f278c77fb93135822159a95e6f31075d5bc43756b7e5`

| Beat | Pasta | VLAB | Selo | ob / cpu / spr / scan |
| emerge | `d3_reveal` | 151 | selado | 0 / 45 / 13 / 3 |
| lock | `d3_lock` | 151 | selado | 0 / 45 / 13 / 3 |
| 1o golpe | `d3_hit1` | 211 | selado | 0 / 92 / 13 / 5 |
| FORGE | `d3_forge` | 331 | selado | 0 / 92 / 13 / 14 |

Pico residual 92 (abaixo do limiar 100). Nao e `validado_budget`.
API: `sdk/sgdk-2.11/inc/tools.h` `unpackTileMap` com dest estatico
(`dest->tilemap` apontando para `u16[40*28]`).

**2026-08-18 — Recaptura da ROM de descida (sem enxame de 56)**

ROM `e79a9de43b994cd799b4e7b60016672effe6f9cb1cb653778fc52c5761624b82`.
Descida: o ceu sai por VSCROLL `t²*168/span²`; a parede/bigorna entram em
dois quadros a partir de F154; a paleta so aquece depois do tilemap novo.
Climax: sem `brandPrepareShards` / `brandUpdateShards`. As 12 fagulhas
do preludio e que levam o 1o e o 2o golpe.

O `frame_counter` do VLAB nesta captura sai em degraus de ~60 (91 / 151 /
211 / 331). A autoridade do beat e o screenshot, nao esse contador.

| Beat | Warmup | Pasta | VLAB | Selo | O que se le | ob / cpu / spr / scan |
| ceu | 1.0 / 2.0 | `d2_sky`, `d2_sky2` | 91 ou ausente | rejeitado (ceu preto) | campo estelar + fagulhas ouro | 0 / 27 / 13 / 3 |
| queda | 2.4 | `d2_drop` | 91 | rejeitado (ceu preto) | ainda so estrelas e fagulhas | 0 / 27 / 13 / 3 |
| emerge | 2.9 | `d2_reveal` | 151 | selado | parede+bigorna escuras, fogo, fagulhas | 0 / 45 / 13 / 3 |
| lock | 3.3 | `d2_lock` | 151 | selado | forja acesa, martelo no alto, fagulhas | 0 / 45 / 13 / 3 |
| 1o golpe | 4.1 | `d2_hit1` | 211 | selado | martelo na bigorna, fagulhas expulsas, sem 56 estilhacos | 9 / 160 / 13 / 5 |
| FORGE | 6.2 | `d2_forge` | 331 | selado | FORGE carimbado, martelo sumiu, fagulhas sumiram | 9 / 160 / 13 / 14 |

Janela de 32 amostras do probe: os 9 `over_budget` estao nos golpes, nao
na descida. Pico de sprites 13 (12 fagulhas + martelo), nao 51. Cpu 160
nos dois impactos. Nao e `validado_budget`.

Gates desta ROM: tile_residency pico 1216/1740 OK; provenance OK;
brand_comprehension exit 0. Sem aprovacao humana. Ceu continua
`ai_generated` placeholder. A emerge e swap de tilemap, nao travel de
224 px. Slam/BGM continuam sinteticos de laboratorio.

**2026-08-18 — The Forge, quatro atos**

Memorando de direcao virado em ritmo de ~7 s (F0-F420). START salta.
A no preludio e o toque da criacao (D-pad desloca o ceu no mesmo quadro).

| Ato | Quadros | Evidencia | Leitura |
| I | 0-84 | `out/evidence/sky` frame_2 | campo estelar + fagulhas |
| II/III | 168-228 | `drop`/`lock` F211 | ruinas, bigorna, martelo, fagulhas |
| IV-1 | 228 | `hit1` F271 | martelo na bigorna, fagulhas expulsas |
| IV-2 | 312-348 | `forge` F331 | FORGE forjado |

Fio condutor: 12 fagulhas nascem no ceu, explodem no 1o golpe e convergem
no 2o. O nome so existe depois do segundo impacto.

ROM `5c625fe565a6b977dce07853445face0e2bfcf693782f214bcffc8aac4cf23ae`.
Climax F331: over_budget 20 / cpu 182 (56 estilhacos + fagulhas). Nao e
validado_budget. Ceu e `ai_generated` placeholder. A parede emerge por
swap de tilemap no meio da queda, coberta pelas fagulhas — nao e uma
descida continua de 224 px.

**2026-08-18 — Menu legivel + slam + cama FM**

Causa do menu distorcido: `VDP_drawText` herdava PAL0 da forja e HSCROLL/S/H
residual. O front-end agora e cena 2 sobre a oficina: FORGE no bigorna,
barra preta, texto ouro com sombra, fonte recarregada.

Audio do impacto: o contacto do martelo (F120) deixou de tocar
`stamp_whoosh`. Toca `brand_hammer_slam` (PCM 13.3 kHz) + ruido branco +
tom grave PSG, com shake de 10 quadros. A trilha `mus_forge_brand` e VGM
FM original (9 s); o loop do xgm2tool nao colou, o runtime retriga
`XGM2_play`. Nao e sample de estudio nem partitura humana.

ROM `f26ffc9a7eab50813ee35ce53601f042353c1bcb457adb0a28a915de2b832430`:
- F331 `wm4`: MISAEL ouro, bigorna intacta, ob=0
- F451 `ms6`: MASTER ouro, bigorna intacta (preload; cpu 188 / ob 8 no enter)
- F691 `front12`: MENU scene=2, FORGE + "START ENTRAR NA DEMO" / "B REVER A MARCA", ob=0 cpu=6

Nao ouvi o slam no BlastEm (captura visual). Implementado e ligado ao
contacto. Status de audio: `needs_review`. Sem ready_for_aaa.

**2026-08-18 — Apresentacao da marca do modelo (forja travada)**

A marca e a oficina, nao um slide de creditos. Tres erros de composicao
estavam vestidos de "ato 3":

1. `VSCROLL_COLUMN` nao levanta so a COIFA. Move o plano inteiro: o fogo
   sobe e o topo preto envolve por baixo da bigorna.
2. `VDP_clearTileMapRect` na faixa y>=64 apaga os tiles da bigorna.
   FORGE tem de sair por **restore** de `img_forge_bg_a_props`.
3. Unpack APLIB do tilemap cheio, uma fileira por quadro (8x) + WINDOW
   copiando BG_B, gerou cpu 196 / over_budget 10-17 e o MASTER nao
   sustentava ate F511.

Cura medida, ROM `40fec78b44c36200b2329d26bae7129062b2bba2b9240722700fb3c322ed73f9`:

| Beat | Pasta | Quadro | O que se le | over_budget | cpu |
| F271 | `out/evidence/fin2/` | ato 2 | FORGE sobre bigorna intacta | 0 | 70 |
| F331 | `out/evidence/fin4/` | ato 3 | MISAEL na parede, bigorna inteira | 0 | 70 |
| F451 | `out/evidence/fin6/` | ato 3 | MASTER na parede, bigorna inteira | 0 | 97 |
| F511 | `out/evidence/fin72/` | hold | MASTER + PRESENTS ouro no fogo | 0 | 97 |

Runtime: nomes em y<64 (BG_A transparente); restore unico do FORGE;
PRESENTS carimbado em BG_A y=26 sobre o fogo, sem WINDOW; tilesets
carregados no quadro anterior ao carimbo; CPU no stamp; haze de linha
desligada no ato 3; hold ate F600. Sem `PAL_fadeOutAll`. Sem mexer em
`SHARD_COUNT` 56 / `SHARD_ROWS` 7 / `SHARD_ROW_STAGGER` 6.

Ainda placeholder: iluminacao da bigorna, wordmarks MISAEL/MASTER mais
lamacentos que o FORGE, letterbox preta no topo do bg_b. Sem aprovacao
humana. **Nao e AAA, nao e ready_for_aaa.** E a assinatura de laboratorio
da engine, agora com a oficina no lugar.

Gates: tile_residency OK, provenance OK, brand_comprehension exit 0.
Bundles selados blockers=[].

**2026-08-17 — Bissecção do ato 3 (F451) ANTES da correção**

Seis desligamentos, um por build, warmup 6s → screenshot F451.
Burst delay 0 captura o começo da ROM (ato 1), não o ato 3 — o quadro
de ato 3 é `screenshot.png`. Log: `rascunho/act3_bisect_log.md`.

| Ponto | O que desligou | O que mudou em F451 |
| 1 | cortina `VDP_setVerticalScrollTile` | só tirou a cortina. Wordmarks e bigorna iguais |
| 2 | wordmark projeto `f==430` | MASTER sumiu; MISAEL e FORGE ficaram legíveis; bigorna menos corrompida |
| 3 | presents `f==480` | nada (ainda não executa em F451) |
| 4 | fade `PAL_fadeOutAll` | nada (ainda não executa em F451) |
| 5 | `SPR_reset()` | brasa ficou em cima do MASTER; CPU 136 / over_budget 8; sintomas iguais |
| 6 | `sVramAuthor = sVramBgA` | **bigorna voltou** (chifre, face, argolas). MASTER igual |

Mapa dos três sintomas (medidos, não teorizados):

1. **Magenta nas bordas** — nenhum dos 6 pontos mudou. Em F451 a
   letterbox ficou preta em todas as capturas. Magenta só aparece no
   `animation_frames/frame_1.png` (burst no boot/ato 1), idêntico em
   todos os builds. Não é regressão do ato 3 causada por esses blocos.
2. **Wordmarks ausentes** — o autor ESTAVA desenhado. Em F451 o
   tilemap do projeto cobre o MISAEL (ponto 2 revela isso). A cortina
   (ponto 1) não esconde wordmark. Em F331 o MISAEL já era visível
   no screenshot de `re4/`.
3. **Bigorna sumiu** — ponto 6. `sVramAuthor = sVramBgA` carregava
   os tiles do wordmark por cima do tileset vivo de `img_forge_bg_a_props`.
   O tilemap da bigorna continuava apontando para esses índices. Ponto 2
   piora (mais 143 tiles), mas não é a causa primeira.

Correção aplicada: só a causa medida. Wordmarks passam a carregar
depois da janela do martelo (`sVramHammer + 72`). Sem mexer em
`SHARD_COUNT` 56 / `SHARD_ROWS` 7 / `SHARD_ROW_STAGGER` 6 /
`sector = (index*5)&15`.

Prova na mesma ROM `1d43242533bd853d185660e29b7eabb6f1924f7c7d579eb5ae457908665819c1`:
- F271 ato 2 (`out/evidence/act2_noregress/`): FORGE limpo, bigorna inteira, over_budget 0
- F331 ato 3 (`out/evidence/act3_author/`): MISAEL + bigorna + FORGE, over_budget 0
- F451 ato 3 (`out/evidence/act3_fix/`): MASTER + bigorna restaurada, over_budget 0, cpu 96, sealed blockers=[]

Gates exit 0: tile_residency, brand_comprehension, asset_provenance.

**2026-08-17 — Ato 3: presents, contraste, contador**

Medido em F480 na ROM anterior: `VDP_setWindowVPos(FALSE, 22)` cobriu as
22 fileiras de cima (tela preta) e o draw do PRESENTS em y=23 ficou fora
da WINDOW. Cura: `VDP_setWindowVPos(TRUE, 22)` (fileiras 22-27).

MASTER escuro em F451: wordmarks estavam com prioridade baixa e o
Shadow/Highlight do ato 1 ainda ligado. Cura: prioridade alta nos tres
wordmarks. Nao desliguei S/H.

`brandEnsureShard` agora reporta spawned/failed em `g_mdRuntimeProbe[18/19]`.
SRAM: **spawned=56 failed=0**. O silencio nao estava escondendo NULL.
O pico 6 vs modelo 16 nao e falha de alocacao.

ROM `a5aec70049fcc9f96f8bd28feffea02f14772da7fe656d2498d03511d4771413`:
- F271 `out/evidence/act2_v2/`: FORGE + bigorna, sem regressao
- F331 `out/evidence/act3_author_v2/`: MISAEL + bigorna
- F451 `out/evidence/act3_master/`: MASTER mais legivel + bigorna, over_budget 0
- F480 `out/evidence/act3_pres_fix/`: MASTER + faixa WINDOW com PRESENTS

Gates exit 0. Bundles sealed blockers=[].

**2026-08-17 — H-Int WHY + bg_b 644**

- Bisseccao ja tinha provado o *quê*: ligar o H-Int salta para `0x23080000`.
- O *porquê*: `brandHIntHandler` era `void` (RTS). H-Int empilha SR+PC; RTS
  trata `0x2308` como word alta do PC. Cura: `HINTERRUPT_CALLBACK` (RTE).
  Segundo risco: H-Int no meio do DMA de enter/VBlank. V-Int mascara, VBlank
  callback (depois do flush) escreve a banda 0 e rearma.
- `img_forge_bg_b` re-autorado de `forge_bg_b_v02.jpg` + compose de crops 8x8
  autorados: 870 → 642 unique com flip (alvo 644). Status: placeholder.
- Runtime carrega todos os quadros de brasa/estilhaço e deriva offsets do ato 3.
- ROM `da5843354459c42329f5f6f4d6bfe9d49ba4d0fc630edcd8c81c6cbebc4f1d82` rodou
  no BlastEm. Bundle selado em `out/evidence/v7_aaa/` com screenshot, SRAM,
  `visual_vdp_dump.bin` e `runtime_metrics.json`.
- Martelo bate na bigorna (smear visivel). FORGE le mas ainda tem ghost e
  sujeira a esquerda. 32 estilhacos, scanline 11, 60.2 fps, over_budget=12.
- `testado_em_emulador` para a abertura. Nao e `validado_budget` nem AAA.

---

**2026-05-24 Ã¢â‚¬â€ Branding intro AAA v1 com assets nativos e VDP**

- Criado builder deterministico `tools/image-tools/build_branding_intro_assets.py` para transformar fontes nativas em PNGs SGDK-safe: `brand_engine_logo`, `brand_author_logo`, `brand_project_logo`, `brand_presents_text` e `brand_fx_tiles`.
- `SCENE_branding` deixou de ser placeholder textual e passou a usar `IMAGE` real via `VDP_drawImageEx`, fundo de tiles FX, shimmer/pulse de paleta, PSG procedural e FSM engine/author/project.
- ROM direta SGDK buildada em `tools/sgdk_wrapper/modelo/out/rom.bin`; SHA256 `D012A842ADE368E25AE739F1DBB8A87F1DEAEDBE3799F407D24C2C4B170FD734`.
- Evidencia visual capturada no BlastEm para a mesma ROM final:
  - engine: `out/evidence/blastem_brand_intro_engine_final_rom/screenshot.png`
  - author: `out/evidence/blastem_brand_intro_author_final_rom/screenshot.png`
  - project/presents: `out/evidence/blastem_brand_intro_project_present_final/screenshot.png`
- `res_graph_audit.ps1` passou com status `warn` apenas por exigir evidencia VDP runtime para tiles carregados por codigo. O wrapper canonico ainda fica preso em `validate_resources.ps1`/gate `.agent` degradado; nao promover para closeout final ate corrigir esse gate.

**2026-06-03 Ã¢â‚¬â€ Fase 0 branding, XGM2 e runtime probe**

- Validado que os 5 PNGs atuais de `res/branding/` nao sao vazios e devem ser preservados como baseline.
- `branding_sequence_contract.json` foi expandido com `resource_plan_by_slot`, `palette_script`, `audio_cue_map`, `budget_summary`, teardown e `evidence_plan`.
- `scene-regression.json` e `doc/13-spec-cenas.md` passaram a registrar `branding_sequence` como cena formal com `app_scene_id=0`.
- `runtime_probe` foi integrado ao boot/loop para permitir `save.sram` com MDRT e heartbeat READY.
- Audio de branding passou a usar WAV XGM2 declarado em `.res`; PCM bruto 11k foi rejeitado como rota.
- Build wrapper gerou `out/rom.bin` build_v002, SHA256 `22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f`.
- Captura BlastEm `TargetScene=0` gerou `screenshot.png`, `save.sram`, `runtime_metrics.json` e `emulator_session.json`.
- `runtime_metrics.json` confirmou cena 0, 32 amostras, p95=6, 0 sprites, mas manteve 1 pico de CPU; performance segue bloqueada.
- `scene_closeout_gate_report.json` fechou como `blocked`, nao como pronto.

---

## 3. DECISOES PENDENTES

- Decidir se o drift local de `.agent/ARCHITECTURE.md` e `.agent/framework_manifest.json` deve ser substituido pela canonica ou mantido como copia local auditada.
- Fazer novo art pass em `brand_author_logo.png` se o objetivo for remover `visual_gate_blocked`.
- Decidir se `visual_vdp_dump.bin` sera obrigatorio para este template ou se MDRT+screenshot sera aceito como evidencia canonica V2.

---

## 4. DECISION LOG CONSERVADOR

Registre aqui escolhas que evitaram tentativa-e-erro ou mudanca de rota.

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-06-03 | Branding baseline | Preservar `brand_*` atuais e adicionar audio XGM2 funcional | Apagar PNGs por suposicao; PCM bruto 11k | `res/resources.res`, `branding_sequence_contract.json` | build + validate_audio |
| 2026-06-03 | Runtime evidence | Integrar `MDRuntimeProbe` em boot/loop | Prometer runtime_metrics sem fonte ROM-side | `src/core/app.c`, `src/main.c` | BlastEm TargetScene=0 |
| 2026-08-17 | Ato 3 bigorna | Wordmarks depois da janela do martelo | Reusar sVramBgA; culpar cortina/SPR_reset/fade | bis_6 vs re6 em F451 | presents F480 |
| 2026-06-03 | Runtime budget | Manter status bloqueado apesar de BlastEm OK | Declarar 60 FPS com `capture_status=partial` e pico CPU | `out/logs/runtime_metrics.json` | investigar frame_index 128 |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok (`out/rom.bin`, build_v002)
- contratos recompilados: ok
- grafo de recursos: ok
- validator: ok com warnings/bloqueios
- captura BlastEm: ok para boot/cena 0, parcial para performance
- regressao de cena: nao executada nesta rodada
- freshness audit: ok
- closeout gate: blocked

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`
