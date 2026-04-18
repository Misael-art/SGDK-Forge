# 13 - Especificacao Tecnica por Cena — BENCHMARK_VISUAL_LAB

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: fx_line_scroll_water_lab

Scene ID: `8`

Intencao da cena: provar HSCROLL_LINE (line scroll) em BG_B com camera em BG_A, com overlay de leitura humana.

Signature moment: water-like wobble em 224 linhas, com drift controlavel.

Causa de gameplay: camera lateral simulando correnteza/vento que afeta leitura e timing.

Tecnicas cobertas:

- `vdp_hscroll_line`
- `dma_queue_scroll_table`

Secondary FX pairings:

- `parallax_plane_scroll`
- `overlay_text_hud`

Operational policy: `default_safe`

hint_owner: `none`

hint_callback_contract: `na`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | nao_medido | nao_medido |
| DMA por frame | nao_medido | nao_medido |
| Sprites SAT | 0 | 0 |
| Paletas | 3 | 3 |
| Efeito dominante | line scroll | line scroll |

### Validation axes

- `boot_emulador`: nao_testado
- `gameplay_basico`: nao_testado
- `performance`: nao_testado
- `visual_elite`: nao_testado
- `audio`: nao_testado

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `fx_raster`

### Observacoes

- usa `DMA_QUEUE` para a tabela de scroll por linha
- evita sprites para isolar custo e estabilidade do scroll

---

## Cena: boss_kinematics_lab

Scene ID: `9`

Intencao da cena: demonstrar cadeia de forward kinematics 2D em fix16, dirigindo sprites em runtime.

Signature moment: cadeia de 4 segmentos com fase oscilante e root movido por input.

Causa de gameplay: telegraph/ataque de boss com membros articulados e hitboxes dependentes da pose.

Tecnicas cobertas:

- `fix16_fk_chain`
- `sprite_pose_driver`

Secondary FX pairings:

- `debug_overlay_text`

Operational policy: `default_safe`

hint_owner: `none`

hint_callback_contract: `na`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | nao_medido | nao_medido |
| DMA por frame | nao_medido | nao_medido |
| Sprites SAT | nao_medido | nao_medido |
| Paletas | 3 | 3 |
| Efeito dominante | nenhum | nenhum |

### Validation axes

- `boot_emulador`: nao_testado
- `gameplay_basico`: nao_testado
- `performance`: nao_testado
- `visual_elite`: nao_testado
- `audio`: nao_testado

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `sprite_engineering`

### Observacoes

- nao usa float/double; todos angulos e offsets via fix16
- pronto para integrar hitboxes AABB por segmento no proximo passo

---

## Cena: pseudo3d_tower_lab

Scene ID: `10`

Intencao da cena: provar VSCROLL_COLUMN com scroll por coluna para leitura pseudo-3D (profundidade por screen-space).

Signature moment: colunas com profundidade crescente + wobble para simular torre/estrada.

Causa de gameplay: deslocamento e leitura de velocidade em corredor/estrada com microajuste de depth.

Tecnicas cobertas:

- `vdp_vscroll_column`
- `depth_profile_columns`

Secondary FX pairings:

- `bg_b_phase_pan`

Operational policy: `default_safe`

hint_owner: `none`

hint_callback_contract: `na`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | nao_medido | nao_medido |
| DMA por frame | nao_medido | nao_medido |
| Sprites SAT | 0 | 0 |
| Paletas | 3 | 3 |
| Efeito dominante | column scroll | column scroll |

### Validation axes

- `boot_emulador`: nao_testado
- `gameplay_basico`: nao_testado
- `performance`: nao_testado
- `visual_elite`: nao_testado
- `audio`: nao_testado

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `pseudo3d`

### Observacoes

- usa 20 colunas (160px) como prova minima do modo `VSCROLL_COLUMN`
- escalona depth por coluna para manter previsibilidade de custo

---

## Cena: masked_light_lab

Scene ID: `11`

Intencao da cena: provar H-Int como control plane (split) para troca de paleta e leitura de "luz" sem blending real.

Signature moment: split line controlavel que alterna paleta (escuro → lit) em runtime.

Causa de gameplay: spotlight/alerta que muda leitura de ambiente e timing do player.

Tecnicas cobertas:

- `hint_palette_split`
- `hilight_shadow_enable`

Secondary FX pairings:

- `mask_marker`
- `overlay_text_hud`

Operational policy: `advanced_tradeoff`

hint_owner: `scene_masked_light_lab`

hint_callback_contract: `SCENE_maskedHintCallback + disable_on_exit`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | nao_medido | nao_medido |
| DMA por frame | 0 words | 0 words |
| Sprites SAT | 0 | 0 |
| Paletas | 3 | 3 |
| Efeito dominante | H-Int | H-Int |

### Validation axes

- `boot_emulador`: nao_testado
- `gameplay_basico`: nao_testado
- `performance`: nao_testado
- `visual_elite`: nao_testado
- `audio`: nao_testado

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `fx_raster`

### Observacoes

- callback H-Int nao faz DMA; apenas CPU writes em CRAM
- reset obrigatorio na saida: desabilitar H-Int + hilight/shadow

---

## Cena: audio_xgm2_lab

Scene ID: `12`

Intencao da cena: validar ownership do driver Z80 XGM2 em runtime e controles basicos (pause/stop/reload).

Signature moment: leitura do driver carregado + estado XGM2 no overlay, com eventos de controle.

Causa de gameplay: runtime audio system precisa garantir driver correto antes de tocar PCM/music.

Tecnicas cobertas:

- `z80_driver_xgm2`
- `xgm2_runtime_controls`

Secondary FX pairings:

- `overlay_text_hud`

Operational policy: `default_safe`

hint_owner: `none`

hint_callback_contract: `na`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | irrelevante | irrelevante |
| DMA por frame | irrelevante | irrelevante |
| Sprites SAT | 0 | 0 |
| Paletas | 1 | 1 |
| Efeito dominante | nenhum | nenhum |

### Validation axes

- `boot_emulador`: nao_testado
- `gameplay_basico`: nao_testado
- `performance`: nao_testado
- `visual_elite`: nao_testado
- `audio`: nao_testado

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `audio`

### Observacoes

- cena inclui playback PCM em runtime (`XGM2_playPCMEx`) com multiplexacao por prioridade em `SOUND_PCM_CH2` e `SOUND_PCM_CH3`
- promocao do eixo `audio: ok` continua exigindo evidencia dedicada de playback em BlastEm (captura orientada a audio)

---

## Cena: [NOME]

Scene ID: `[scene_id]`

Intencao da cena: `[intencao_da_cena]`

Signature moment: `[signature_moment]`

Causa de gameplay: `[causa_de_gameplay]`

Tecnicas cobertas:

- `[technique_id_1]`
- `[technique_id_2]`

Secondary FX pairings:

- `[secondary_fx_1]`
- `[secondary_fx_2]`

Operational policy: `[default_safe / advanced_tradeoff / special_scene_only / hazardous_experimental]`

hint_owner: `[none / system_name]`

hint_callback_contract: `[na / callback_name + reset_policy]`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | [N] | [N] |
| DMA por frame | [N] words | [N] |
| Sprites SAT | [N] | [N] |
| Paletas | [N] | [N] |
| Efeito dominante | [line scroll / column scroll / H-Int / nenhum] | |

### Validation axes

- `boot_emulador`: [ok / falha / nao_testado]
- `gameplay_basico`: [funcional / com_bugs / nao_testado]
- `performance`: [estavel / com_drops / nao_testado]
- `visual_elite`: [ok / alerta / nao_testado]
- `audio`: [ok / com_glitches / nao_testado]

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `[fx_raster / sprite_engineering / pseudo3d / audio / cross_cutting]`

### Observacoes

- [restricao 1]
- [restricao 2]
- [por que a tecnica existe nesta cena]

---

## Cena: [OUTRA]

Scene ID: `[scene_id]`

Intencao da cena: `[intencao_da_cena]`

Signature moment: `[signature_moment]`

Causa de gameplay: `[causa_de_gameplay]`

Operational policy: `[default_safe / advanced_tradeoff / special_scene_only / hazardous_experimental]`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | [N] | [N] |
| DMA por frame | [N] words | [N] |
| Sprites SAT | [N] | [N] |
| Paletas | [N] | [N] |
