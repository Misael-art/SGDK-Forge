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
