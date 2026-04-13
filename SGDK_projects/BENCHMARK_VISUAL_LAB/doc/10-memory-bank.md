# 10 - Memory Bank

## Estado operacional

- projeto: `BENCHMARK_VISUAL_LAB`
- objetivo atual: Sprint 1 runtime proof (S1.1 Sprite Animation, S1.2 Character Design, S1.3 Multi-Plane Composition)
- status: `buildado` — ROM compilada com 3 cenas Gaira, aguardando captura BlastEm

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
- a arte canônica de curadoria continua sendo a variante full-size armazenada em `assets/reference/translation_curation/verdant_forest_depth_scene/`

## Aprendizado assimilado: `sunny_land`

- sintoma observado: a promocao da cena para o lab gerava leitura errada em ROM, incluindo area preta/corrompida e divergencia entre a prova offline e a prova integrada
- falso diagnostico inicial: tratar o problema como se fosse apenas transparencia quebrada
- reconciliacao da evidencia atual:
  - a prova atual em BlastEm sustenta com seguranca que a promocao com `IMAGE ... BEST ALL 0` foi parte material do fechamento visual da cena em ROM
  - transparencia indexada continua sendo triagem obrigatoria quando a layer depende de alpha estrutural, mas a evidência final hoje nao sustenta tratá-la sozinha como causa raiz consolidada do fechamento de `sunny_land`
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

## Sprint 1 Runtime Proof — Gaira (2026-04-12)

### Decisoes tomadas

- personagem de referencia: Gaira (Samurai Shodown, Neo Geo) — 607 frames raw, 100 strips semanticos
- 5 animacoes selecionadas: idle (6f), walk (8f), attack_light (5f), hurt (2f), jump (3f)
- cell size: 56x72px (7x9 tiles) — escalado de Neo Geo (~120-190px) via nearest-neighbor
- 3 cenas separadas (decisao do usuario, nao unificada)
- paleta: 15 cores + transparente, snapped para grid 9-bit do VDP
- utilitarios SRAM extraidos para modulo compartilhado (`system/sram_evidence`)

### Cenas implementadas

| Cena | Scene ID | Proposito | Controles |
|------|----------|-----------|-----------|
| `scene_sprite_anim` | 5 | S1.1 — 5 anims, state machine, auto-cycle, debug overlay | D-PAD/A/UP/DOWN/START/B |
| `scene_character_design` | 6 | S1.2 — 3 modos (normal/silhueta/paleta), analise visual | A:modo, L/R:anim, START:auto |
| `scene_multiplane` | 7 | S1.3 — parallax BG_B(25%) + BG_A(100%) + Gaira sprite + physics | Full controls + jump physics |

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
- build wrapper `validate_resources.ps1` tem bug com paths que contem `C:\` (PS interpreta `C` como cmdlet); workaround: build direto via make
- SRAM evidence compartilhado entre cenas evita 4x duplicacao de helpers

### Proximo gate

- rodar ROM no BlastEm
- captura dedicada (screenshot, SRAM dump) para cada cena
- aprovacao humana explicita para promover `POC_PENDENTE_ROM` → `VALIDADA_EM_ROM`
