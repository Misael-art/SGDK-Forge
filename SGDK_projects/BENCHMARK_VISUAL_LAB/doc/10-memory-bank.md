<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-04-18T00:27:35.6763816-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 6
- Ultimo build versionado: build_v012
- ROM vigente: `18d7b10600af66ff69cb0e3839e6abb211b15da1097eb953a8d2f9dfc248202c` (`262144` bytes)
- Validation summary: errors=0 warnings=2
- Blockers vigentes: emulator_evidence_stale
- Evidencia de emulador: runtime_metrics_stale
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=stale performance=estavel audio=ok hardware_real=ok
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank

## Estado operacional

- projeto: `BENCHMARK_VISUAL_LAB`
- objetivo atual: showroom tecnico (S1 + labs canonicos: line scroll, FK, pseudo3D, H-Int/paleta, XGM2)
- status: `buildado` Ã¢â‚¬â€ ROM compilada e lancada via BlastEm (eixos ainda `nao_testado` no artefato de sessao)

## Verdade visual atual

- `basic_score = 0.6577`
- `elite_score = 0.8419`
- `elite_minus_basic = 0.1842`

## Escopo desta passada

- materializar o lab ausente neste checkout
- promover `verdant` para comparativo em ROM
- substituir a tentativa `BG_B + BG_A` por um `compare_flat` single-plane validado para o VDP
- preservar labels e toggles minimos para leitura humana em emulador

## Evidencia esperada

- `out/rom.bin`
- `out/logs/validation_report.json`
- sessao em BlastEm

## Observacoes

- a tentativa original com `BG_B + BG_A` corrompia a cena porque os dois planos somavam `1853` tiles uteis, acima do teto pratico antes da regiao de mapas do VDP em `0xC000`
- a prova em ROM agora usa `compare_flat` em um unico plano, preservando o comparativo humano `basic-left / elite-right` dentro do budget real de VRAM
- a arte canÃƒÂ´nica de curadoria continua sendo a variante full-size armazenada em `assets/reference/translation_curation/verdant_forest_depth_scene/`

## Aprendizado assimilado: `sunny_land`

- sintoma observado: a promocao da cena para o lab gerava leitura errada em ROM, incluindo area preta/corrompida e divergencia entre a prova offline e a prova integrada
- falso diagnostico inicial: tratar o problema como se fosse apenas transparencia quebrada
- reconciliacao da evidencia atual:
  - a prova atual em BlastEm sustenta com seguranca que a promocao com `IMAGE ... BEST ALL 0` foi parte material do fechamento visual da cena em ROM
  - transparencia indexada continua sendo triagem obrigatoria quando a layer depende de alpha estrutural, mas a evidÃƒÂªncia final hoje nao sustenta tratÃƒÂ¡-la sozinha como causa raiz consolidada do fechamento de `sunny_land`
  - a trilha de robustez de build envolvendo `resources.d` deve permanecer separada como aprendizado operacional de pipeline ate ficar apontada por artefato auditavel proprio
- correcao documentada:
  - manter export SGDK-safe e auditoria de representacao indexada como pre-flight de promocao
  - promover os recursos com `IMAGE ... BEST ALL 0` em vez de configuracao conservadora que inflava o custo estrutural
  - registrar incidentes de `resources.d` como risco de pipeline em trilha propria, sem colapsar essa investigacao dentro da causa raiz visual
- implicacao operacional:
  - prova offline bonita nao basta; toda cena promovida para ROM precisa ser triada por transparencia, flags do recurso, custo de tiles e evidencia de emulador
  - ao investigar erro visual, separar sempre `erro de asset`, `erro de recurso SGDK`, `erro de budget` e `erro de pipeline`
- evidencia associada:
  - `out/rom.bin`
  - `out/logs/validation_report.json`
  - captura canonica do BlastEm com screenshot, `save.sram` e `visual_vdp_dump.bin`

## Sprint 1 Runtime Proof Ã¢â‚¬â€ Gaira (2026-04-12)

### Decisoes tomadas

- personagem de referencia: Gaira (Samurai Shodown, Neo Geo) Ã¢â‚¬â€ 607 frames raw, 100 strips semanticos
- 5 animacoes selecionadas: idle (6f), walk (8f), attack_light (5f), hurt (2f), jump (3f)
- cell size: 56x72px (7x9 tiles) Ã¢â‚¬â€ escalado de Neo Geo (~120-190px) via nearest-neighbor
- 3 cenas separadas (decisao do usuario, nao unificada)
- paleta: 15 cores + transparente, snapped para grid 9-bit do VDP
- utilitarios SRAM extraidos para modulo compartilhado (`system/sram_evidence`)

### Cenas implementadas

| Cena | Scene ID | Proposito | Controles |
|------|----------|-----------|-----------|
| `scene_sprite_anim` | 5 | S1.1 Ã¢â‚¬â€ 5 anims, state machine, auto-cycle, debug overlay | D-PAD/A/UP/DOWN/START/B |
| `scene_character_design` | 6 | S1.2 Ã¢â‚¬â€ 3 modos (normal/silhueta/paleta), analise visual | A:modo, L/R:anim, START:auto |
| `scene_multiplane` | 7 | S1.3 Ã¢â‚¬â€ parallax BG_B(25%) + BG_A(100%) + Gaira sprite + physics | Full controls + jump physics |
| `scene_fx_line_scroll_water_lab` | 8 | line scroll (HSCROLL_LINE) aplicado em BG_B, camera em BG_A | LEFT/RIGHT, A overlay, B menu |
| `scene_boss_kinematics_lab` | 9 | forward kinematics (cadeia 2D) em fix16 + sprites | D-PAD, A overlay, B menu |
| `scene_pseudo3d_tower_lab` | 10 | column scroll (VSCROLL_COLUMN) para profundidade pseudo-3D | LEFT/RIGHT, A overlay, B menu |
| `scene_masked_light_lab` | 11 | H-Int para troca de paleta (split) + hilight/shadow | UP/DOWN, LEFT/RIGHT, A overlay, B menu |
| `scene_audio_xgm2_lab` | 12 | driver ownership XGM2 + controle pause/stop/reload | A/START/C, B menu |

### Asset pipeline

- script: `tools/image-tools/build_gaira_sgdk_sheet.py`
- entrada: 5 strips de `gaira_assembled_strips/`
- saida: `res/sprites/spr_gaira.png` (448x360px, 8-bit indexed, 15+1 cores)
- SPRITE declaration: `SPRITE spr_gaira "sprites/spr_gaira.png" 7 9 FAST 5`

### Aprendizado assimilado

- escalar de Neo Geo para MD via nearest-neighbor preserva pixel art melhor que Lanczos
- cell 56x72 (7x9 tiles) e bom compromisso entre detalhe e VRAM (~63 tiles/frame)
- 5 anims x 8 frames padded = 40 cells, compressao LZ4W media ~70-85% do original
- ROM total: 256KB incluindo todas cenas e assets
- build wrapper `validate_resources.ps1` exige PNG indexado com PLTE compacta (<=16 entradas); assets com PLTE inflada (256) quebram deduplicacao e foram normalizados
- SRAM evidence compartilhado entre cenas evita 4x duplicacao de helpers

### Proximo gate

- rodar ROM no BlastEm
- captura dedicada (screenshot, SRAM dump) para cada cena
- aprovacao humana explicita para promover `POC_PENDENTE_ROM` Ã¢â€ â€™ `VALIDADA_EM_ROM`
























































