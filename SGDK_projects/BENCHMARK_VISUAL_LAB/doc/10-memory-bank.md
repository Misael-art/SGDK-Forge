# 10 - Memory Bank

## Estado operacional

- projeto: `BENCHMARK_VISUAL_LAB`
- objetivo atual: prova em ROM do caso `verdant_forest_depth_scene`
- status: `implementado`

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
