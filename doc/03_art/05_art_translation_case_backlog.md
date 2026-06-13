# 05 - Art Translation Case Backlog

## Objetivo

Este backlog define a ordem canonica dos primeiros casos de curadoria da skill `art-translation-to-vdp` a partir do lote fornecido em `SGDK_projects/data`.

A prioridade nao segue apenas "qual imagem e mais bonita".
Ela segue o quanto cada caso ajuda a ensinar:

- preservacao da alma visual
- traducao de profundidade
- leitura de material
- modularidade de tiles
- salto real entre `basic` e `elite`

## Ordem recomendada

## Sprint de alfabetizacao semantica de source

Antes de promover novos casos `basic vs elite`, a skill precisa dominar leitura semantica de pranchas-fonte complexas.

Corpus canonico:

- `assets/reference/translation_curation/composição_de_cenas/`
- `tools/image-tools/specs/source_semantic_cases/`

Casos iniciais obrigatorios:

1. `metal_slug_urban_sunset_source_semantics`
2. `china_arena_stage_board_source_semantics`
3. `ryu_sprite_sheet_source_semantics`
4. `double_dragon_stage1_tileset_objects_source_semantics`

Objetivo da sprint:

- distinguir cena util de ruido editorial
- identificar `BG-B`, `BG-A` e foreground composicional quando existirem
- separar actor sheet, palette strip e metadata em sprite sheets
- distinguir tile cluster de object cluster em tile/object sheets
- emitir `semantic_parse_report` antes de qualquer traducao visual

## Triagem inicial do lote

Baseline rodado com `analyze_aesthetic.py` nas imagens-fonte brutas:

| Caso | Score inicial | Status inicial | Leitura |
|---|---:|---|---|
| `verdant_forest_depth_scene` | `0.7672` | `needs_review` | melhor ponto de entrada; profundidade forte, risco controlado |
| `metal_slug_urban_sunset_scene` | `0.4886` | `rework` | caso forte, mas pesado demais para primeira passada |
| `crystal_cavern_tilemap` | `0.6617` | `needs_review` | bom segundo caso para modularidade |
| `armand_compact_sprite_sheet` | `0.6664` | `needs_review` | bom caso de sprite, mas menos valioso que cenarios para abrir a skill |

Leitura pratica:

- `verdant_forest_depth_scene` abre melhor a skill porque ensina profundidade, separacao de planos e preservacao de atmosfera sem colapsar o caso em ruido
- `metal_slug_urban_sunset_scene` deve entrar depois que a skill ja provar que sabe simplificar sem matar a cena

### 1. `verdant_forest_depth_scene`

- tipo: `scene_slice`
- fonte: `Free Verdant Tileset and parallax Bacground/Bacground reference.png`
- prioridade: `P0`
- estado atual: `pass_03 elite_delta_confirmed`

Por que entra primeiro:

- cena forte e legivel
- profundidade clara entre primeiro plano, plano medio e fundo
- boa para treinar `O Segredo da Profundidade`
- boa para medir separacao BG_A / BG_B
- complexidade alta o bastante para exigir traducao, mas baixa o bastante para curadoria rapida

Risco principal:

- o verde vibrante engolir a hierarquia de planos

Resultado canônico atual:

- `basic_score = 0.6577`
- `elite_score = 0.8419`
- `elite_minus_basic = 0.1842`
- laudo salvo em `assets/reference/translation_curation/verdant_forest_depth_scene/reports/translation_case_report.json`

Aprendizado de curadoria:

- uma passada `tile-first` mais agressiva melhorou artefatos de review, mas derrubou a elite para `0.7672`
- uma passada reequilibrada subiu para `0.8233`, mas ainda abaixo da melhor elite historica
- a versao atual preserva o ganho de processo do video como `palette_strip + tileset_sheet + auditoria de H-Flip` e restaura como canon a elite comprovada de `0.8419`

### 2. `metal_slug_urban_sunset_scene`

- tipo: `scene_slice`
- fonte: `MetalSlug_Backgrounds.png`
- prioridade: `P1`
- estado atual: `pass_03 semantic_layers_refined elite_delta_confirmed`

Por que entra cedo:

- excelente caso para atmosfera, skyline, arquitetura e sunset gradient
- força o agente a decidir o que preservar e o que simplificar
- bom para testar se a skill evita o look de "quantizacao cega"

Risco principal:

- colapso de detalhe arquitetonico e perda de leitura do ceu dramatizado

Resultado canônico atual:

- `basic_score = 0.6545`
- `elite_score = 0.8242`
- `elite_minus_basic = 0.1697`
- laudo salvo em `assets/reference/translation_curation/metal_slug_urban_sunset_scene/reports/translation_case_report.json`

Aprendizado de curadoria ate aqui:

- a fonte e uma sheet editorial, nao um frame unico; isso provou a heuristica `Sheet de Referencia Nao e Frame Jogavel`
- a skill precisou aprender a decompor a fonte por funcao visual:
  - `A`: por do sol e nuvens como camada mais ao fundo
  - `B`: edificacoes e rua base como camada estrutural do background
  - `C`: destrocos como massa frontal isolada, nao background automatico
- creditos, avatar, preview montado da direita e sprite de referencia interno precisaram ser classificados como material editorial e descartados da traducao principal
- o salto final so fechou quando o `basic` deixou de receber credito de `paired_bg`; isso virou a heuristica `Controle Ingenuo Nao Ganha Credito de Pareamento`
- a camada `B` precisou virar `midground_layer` e a camada `C` precisou virar `foreground_layer`; o juiz so estabilizou quando parou de tratar massa estrutural e destrocos isolados como `bg_a` cheio ou `sprite` compacto
- a montagem final so ficou conceitualmente correta quando `B` passou a ser posicionada como layer estrutural com transparencia real acima dela, em vez de ser esticada como bloco opaco da metade da tela
- a camada `C` so parou de parecer ruido quando a extracao passou a preencher a massa frontal antes do detalhe, preservando volume e sombra dos destrocos
- o pipeline precisou aprender que quantizacao nao pode destruir alpha nem remapear pixel visivel para o slot transparente
- a versao `elite` usa curadoria manual semantica de paleta para preservar o drama do por do sol e a leitura da arquitetura sem depender de quantizacao cega
- o caso agora tambem serve como trilha-supervisao de parsing semantico; o agente deve chegar a partir de `source.png` na mesma leitura ensinada em `SEPARAÇÃO RACIONAL.png` sem usar os PNGs manuais como entrada operacional

### 3. `crystal_cavern_tilemap`

- tipo: `tilemap`
- fonte: `crystal_tileset.png`
- prioridade: `P1`
- estado atual: `pass_01 elite_delta_confirmed`

Por que entra cedo:

- caso perfeito para modularidade, repeticao inteligente e economia de tiles
- bom para diferenciar "tile bonito" de "tile usavel"
- ajuda a treinar a skill fora do eixo apenas ilustrativo

Risco principal:

- excesso de detalhe colorido sem estrutura forte de tile reutilizavel

Resultado canônico atual:

- `basic_score = 0.6685`
- `elite_score = 0.8118`
- `elite_minus_basic = 0.1433`
- laudo salvo em `assets/reference/translation_curation/crystal_cavern_tilemap/reports/translation_case_report.json`

Aprendizado de curadoria:

- o salto principal veio de consolidacao agressiva de paleta e reforco estrutural de facetas, nao de dithering adicional
- a elite canônica venceu com `8` cores bem distribuidas e contraste melhor entre rocha e brilho
- o caso provou que `tilemap` pode ganhar muito em leitura e identidade mesmo sem disparar `COMPARE_FLAT_CANDIDATE` ou outros alertas de budget
- a revisao estrutural ficou salva com `palette_strip` e `tileset_sheet`, o que ajuda a skill a diferenciar "tile bonito" de "tilemap promovivel"

### 4. `armand_compact_sprite_sheet`

- tipo: `sprite_sheet`
- fonte: `Sprite Pack 8/3 - Armand/Idle (32 x 32).png`
- prioridade: `P2`

Por que entra depois:

- e util para consistencia de sprite pequeno e compactacao de sheet
- serve como caso de controle para animacao e leitura em 32x32
- mas e menos valioso como treino de "traducao high-res para VDP" do que os tres primeiros

Risco principal:

- virar apenas limpeza estrutural em vez de traducao interpretativa

## Criterio de promocao

Cada caso so entra na fila ativa quando tiver:

- source copiado para `assets/reference/translation_curation/<case_id>/source/source.png`
- manifesto em `tools/image-tools/specs/translation_cases/`
- contrato da alma visual definido
- alvo de traducao declarado

## Proximo passo recomendado

Fechar a sprint de alfabetizacao semantica de `source` com os 4 casos supervisionados e so depois promover novos casos para `basic vs elite`.
