---
name: art-translation-to-vdp
description: Use quando houver uma imagem-fonte forte em PNG, concept art, mockup, crop high-res ou arte de IA que precise ser reinterpretada como sprite, sprite sheet, tilemap ou cena para o Mega Drive. Esta skill preserva a alma visual da imagem e a traduz para paleta, grid 8x8, contraste de planos, modularidade e limites reais do VDP. Nao use para apenas diagnosticar o cenario de arte, converter assets ja SGDK-validos sem reinterpretacao, ou buscar arte externa.
---

# Art Translation to VDP

Esta skill existe para o caso em que a imagem e boa, mas nao e hardware.

Ela nao trata o `.png` como asset final.
Ela trata a imagem-fonte como materia-prima.

## Missao

Transformar imagem-fonte em recurso visual de Mega Drive preservando:

- silhueta
- hierarquia visual
- material dominante
- foco da composicao
- impacto de leitura

sem tentar preservar, de forma ingenua, tudo o que o hardware nao suporta.

## Quando usar

Use esta skill quando:

- a IA gerou uma boa imagem-fonte em `.png`
- existe concept art que precisa virar sprite ou tilemap
- o asset parece forte no PC e fraco demais quando reduzido para o Mega Drive
- e preciso preservar a "alma" da imagem em vez de apenas quantizar

## Nao use

- para decidir se o projeto tem ou nao arte
- para buscar assets na web
- para converter automaticamente assets que ja foram desenhados para SGDK
- para validacao puramente pixel-rigida sem problema de traducao visual

## Entradas obrigatorias

- `source_image`
- `translation_target`
  - `sprite_single`
  - `sprite_sheet`
  - `tilemap`
  - `scene_slice`
- `reference_profile`
- `hardware_spec`
- `hardware_expectations`
- `intent_notes`

## Contrato Operacional

### Entrada minima

- `source_image`
- `translation_target`
- `reference_profile`
- `hardware_spec`
- `hardware_expectations`
- `intent_notes`

### Saida minima

- `semantic_parse_report`
- `translation_report`
- pacote `basic`
- pacote `elite`
- review estrutural de tileset e paleta

### Saida opcional quando houver multiplas rotas viaveis

- `route_exploration_board`
- `route_comparison_matrix`
- `route_decision_record`
- `locked_visual_direction`

### Passa quando

- o parsing semantico foi emitido antes de qualquer promocao final
- `elite` se sustenta melhor que `basic`
- quando houver duas ou mais leituras fortes, a exploracao de rotas foi registrada antes da promocao final
- o caso ja aponta sua classe dominante: `erro_de_asset`, `erro_de_recurso_sgdk`, `erro_de_budget` ou `erro_de_pipeline`

### Handoff para proxima etapa

- entregar assets e reports para `visual-excellence-standards`
- entregar `route_exploration_board` e `route_decision_record` quando houver alternativas vivas
- entregar review estrutural e `hardware_budget_review` para `megadrive-vdp-budget-analyst`

## Curadoria e acuracia da skill

Esta skill deve ser treinada com casos canonicos, nao com impressao subjetiva de uma unica imagem.

Pacote minimo de curadoria:

- protocolo: `doc/03_art/04_art_translation_curation_protocol.md`
- sprint: `doc/03_art/03_ai_source_to_vdp_sprint.md`
- manifesto de caso: `tools/image-tools/specs/art_translation_case.template.json`
- avaliador: `tools/image-tools/analyze_translation_case.py`

Regra pratica:

- todo `source` complexo precisa passar por `source semantic parsing` antes da traducao
- toda traducao importante deve nascer com `basic` e `elite`
- toda curadoria deve medir delta entre as duas
- toda falha recorrente deve virar heuristica no feedback bank
- toda validacao humana de arte deve apresentar `original + basic + elite` lado a lado
- quando a cena for heroica, altamente atmosferica ou o usuario pedir opcoes, a validacao humana deve poder apresentar tambem uma `route_exploration_board` com alternativas controladas
- quando houver `source_semantic_map`, a validacao humana deve incluir tambem `ORIGINAL -> A/B/C extraidos -> ELITE remontado`
- toda traducao de `tilemap` ou `scene_slice` deve gerar artefatos de review de tileset e paleta por layer
- todo `translation_report` de `tilemap` ou `scene_slice` deve incluir `hardware_budget_review`

## Few-shot canonico de falhas caras

Ao diagnosticar regressao, consultar explicitamente estes tres padroes antes de improvisar:

- `PALETTE_INFLATED`: PNG aparentemente correto, mas com PLTE inflada e deduplicacao quebrada
- overflow real de VRAM: `rescomp` cabe no build, mas a soma de tiles invade a faixa do VDP
- escolha errada entre `IMAGE`, `MAP` e streaming: arquitetura muda por numerologia real, nao por preferencia

## Checklist obrigatorio

1. Ler `doc/03_art/00_visual_quality_bar.md`
2. Ler `doc/03_art/01_visual_cohesion_system.md`
3. Ler `doc/03_art/02_visual_feedback_bank.md`
4. Aplicar `visual-excellence-standards`
5. Validar contra `megadrive-pixel-strict-rules`
6. Quando houver cena real, consultar `megadrive-vdp-budget-analyst`

Competencias complementares obrigatorias por contexto:

- se o alvo for `sprite_single` ou `sprite_sheet`, consultar `tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md`
- se a tarefa mexer na identidade do personagem, consultar `tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md`
- se o alvo for `scene_slice`, `paired_bg` ou composicao em profundidade, consultar `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md`

## Processo

### 1. Fazer alfabetizacao semantica do `source`

Antes de pensar em paleta, dithering ou tile reuse, o agente precisa provar que entendeu o que esta vendo.

Etapas obrigatorias:

- `source inventory`
- `layout classification`
- `semantic region parsing`
- `composition role assignment`
- `drop/ignore classification`
- `recomposition hypothesis`

Tipos minimos que a skill deve reconhecer:

- `scene_plane_bg_b`
- `scene_plane_bg_a`
- `scene_plane_foreground_composition`
- `scene_plane_sky`
- `scene_plane_architecture`
- `scene_plane_ground`
- `actor_sprite_sheet`
- `palette_strip`
- `labels_and_names`
- `author_credits`
- `metadata_block`
- `avatar_or_icon`
- `mockup_preview`
- `unrelated_reference`
- `tile_cluster`
- `object_cluster`
- `object_animation_sequence`
- `overlay_cluster`
- `corrupted_region`

Regra:

- o agente so pode quantizar ou reinterpretar depois de emitir um `semantic_parse_report`
- a inferencia operacional deve materializar `observed_ir.json` e `derived_structure_ir.json`; a primeira descreve evidencia, a segunda descreve estrutura derivada minima
- `derived_structure_ir` so pode promover papeis que o sinal visual sustenta; quando nao sustentar, marque `unknown` ou degrade para `provisional`
- quando o `source` vier como prancha editorial, spritesheet com residuos ou tile/object sheet misto, a primeira tarefa e entender a organizacao da prancha
- a skill precisa chegar so a partir do `source` na mesma logica de decomposicao que um humano experiente chegaria
- **POLIVALÊNCIA E DIAGNÓSTICO (DIAGNOSE FIRST):** O agente nunca assume um método de recorte cego. A primeira obrigação é investigar a taxonomia do `source`:
  1. Se for `editorial_board`: A separação exige delimitação espacial (recorte por caixas delimitadoras lógicas).
  2. Se for `palette_separated_panorama` (cena flat achatada): A separação exige decomposição algorítmica por agrupamentos de paleta restritos em profundidade (cores que só existem no BG vs FG).
  3. Se for `spritesheet`: A extração exige Auto-Assembler. Faça limpeza por Chroma Key. Identifique via Isolação Condicional de Bounding Boxes de Oclusão (BFS) os sprites válidos (matando lixo literário por massa mínima). Agrupe as sequências nativas originais calculando as Medianas de Eixo Y. Re-encaixe (Snap) as animações juntas no grid VDP, garantindo Canvas Width/Height padronizados pela fita resultante e alinhando os "pés" no Eixo Bottom-Center.
  4. Se for `cutscene_board`: São storyboards ripados com quadros de cena completos misturados com close-ups, sprites isolados e lixo editorial. A extração exige: Chroma Key do fundo da prancha, Islands BFS com massa alta (>=2000) para matar créditos do ripper, e classificação automática por dimensão (fullscreen >= 200x150, closeup >= 80x80, element = resto). Fullscreen frames devem ser oferecidos em DUAS versões: fixa (320x224) e scroll/panning (320xN). A quantização deve ser ARTÍSTICA (interpretação estética, não conversão direta) com 60 cores máximo para fullscreen e 15 para close-ups/elements. Todas as cores devem ser snapped para a grade MD (/34).
  5. Se for `level_tilemap`: São mapas de geometria completa desenhados em gerações pós 16-bits (PS1, Saturn) usando Luma, Alpha Blending e vertex lighting dinâmico, contendo centenas de cores exclusivas. A conversão plana afunda a iluminação e destrói a atmosfera. A extração exige Decomposição Heurística de Luma: separe a Arte Crua (30 paletas clusterizadas usando KMeans e resnapped no MD) em um 'Base Tilemap', isole os picos de iluminação (> Luma Threshold) em uma 'Máscara 1-bit de Highlight (+Luma)' e os fossos opacos (< Luma Threshold) em 'Máscara 1-bit Shadow (-Luma)'. Gere a Prova Virtual replicando virtualmente o funcionamento H/S do VDP para garantir ressonância de luz sem custo extra de paletas de cor. **DOGMA CRÍTICO (Anti-Pixel Crust):** Em elementos orgânicos com forte anti-aliasing (ex: cachoeiras e pedras do SOTN), NUNCA tente isolar os elementos em camadas espaciais rígidas usando "hard thresholding de cor" (e.g., separar a água para um overlay/BG_A transparente por corte raso de RGB). Isso destrói o blending e cria crostas pixelizadas. Preserve o tilemap coeso (Água + Pedra fundidos nativamente) em um único `Base Tilemap`. O volume dinâmico virá puramente da inserção cirúrgica da Máscara Highlight sob a água conectada, permitindo fluidificar o visual com Palette Cycling nas cores que compõem o elemento, sem quebrar a malha espacial.
  É estritamente proibido agir no automático manipulando pixels globalmente sem ANTES tipificar a estrutura base da fonte lógica.
  > **IMPORTANTE (FEW-SHOT LEARNING):** Caso sinta dificuldade em traduzir essas teorias algorítmicas, leia os modelos-base acadêmicos arquivados em `tools/sgdk_wrapper/.agent/lib_case/art-translation/`. Comece por `tools/sgdk_wrapper/.agent/lib_case/art-translation/index.json` para localizar a taxonomia correta e depois mimetize a solução destes *scripts didáticos* para as imagens contemporâneas.
- **RÉGUA DO JUIZ ESTÉTICO (IoU > 85%):** Toda vez que o agente processar uma imagem fonte complexa, o aprendizado (ou validação contra o material humano) deve apontar um alinhamento estrutural de `IoU` (Intersection over Union) de no mínimo 85% antes da decomposição ser considerada final.
- `palette_strip` e dado auxiliar, nao frame jogavel
- stage board pede leitura estrutural de ceu, arquitetura e chao antes de qualquer recorte por profundidade
- sprite sheet pede leitura por linhas de animacao antes de recorte por frame
- tile/object sheet pede separacao entre `tile_cluster`, `overlay_cluster`, `object_animation_sequence` e `corrupted_region`

Corpus canonico de treino:

- `assets/reference/translation_curation/composição_de_cenas/`
- `tools/image-tools/specs/source_semantic_cases/`
- `tools/image-tools/analyze_source_semantics.py`

Corpus canonico de casos reais:

- `assets/reference/translation_curation/case_registry.json`

Regra de consulta:

- a skill define o fluxo
- `lib_case` define o few-shot pedagogico
- `case_registry.json` define qual caso real e a referencia canonica de cada taxonomia

### 2. Extrair a alma da imagem

Identifique:

- se a fonte e um frame jogavel, um crop valido ou uma sheet editorial que precisa ser decomposta antes
- se a fonte e `single_frame`, `scene_sheet`, `sprite_sheet`, `tilemap_sheet` ou `editorial_board`
- quais regioes sao cena util
- quais regioes sao preview, nota, texto, credito ou apoio editorial
- quando houver animacao, onde comecam e terminam os blocos de frames
- quais elementos exoticos podem ser isolados em vez de contaminar a composicao principal
- forma dominante
- leitura em miniatura
- material dominante
- detalhe essencial
- detalhe descartavel
- ponto focal

Saida:

- `semantic_parse_report`
- `source_inventory`
- `layout_classification`
- `drop_policy`
- `composition_schema`
- `soul_summary`
- `must_keep`
- `can_simplify`
- `must_drop`
- `source_region_strategy`
- `source_semantic_map`

### 3. Traduzir para decisoes de hardware

Defina:

- plano de paleta
- plano de dithering
- plano de separacao de camadas
- plano de reuso de tile
- plano de sprite ou tilemap
- plano de extrapolacao segura do VDP quando a cena estiver perto do limite

Saida:

- `palette_plan`
- `dithering_plan`
- `layer_plan`
- `tile_reuse_plan`
- `vdp_extrapolation_plan`

Regra de paleta:

- `basic` pode nascer de uma quantizacao cega para servir de controle
- `elite` deve preferir curadoria manual semantica de paleta quando a alma visual depender de materiais, roster compartilhado ou hierarquia cromatica
- "caber em 16 cores" nao basta; e preciso decidir quais rampas sobrevivem, quais tons compartilham funcao e quais cores saem de cena

Regra de leitura da fonte:

- o agente nao deve tratar uma spritesheet, tilemap sheet ou board editorial como se fosse um frame unico
- primeiro decompor semanticamente, depois traduzir
- textos, creditos, numeros de frame, setas, anotacoes e crops auxiliares devem ser classificados antes de qualquer quantizacao
- quando a decomposicao gerar camadas isoladas em canvas transparente, classifique-as como `midground_layer` ou `foreground_layer` no manifesto em vez de forcar `bg_a` ou `sprite`
- segmentacao por cor, threshold duro ou edge detection sozinho nao conta como decomposicao semantica valida

Regra de pipeline de camada:

- primeiro extrair sentido, depois extrair camada, depois compor, e so entao quantizar
- nao reduzir a paleta cedo demais se isso matar gradiente, iluminacao, volume ou recorte de alpha
- cada layer precisa manter a mesma base espacial da cena final
- toda layer semantica precisa declarar sua estrategia de alpha/matte e sua estrategia de composicao
- o gate estrutural precisa validar coerencia local, conflito entre regioes e afinidade real com o papel de engine/VDP antes de exportar assets finais
- quando a estrutura ainda for util para diagnostico mas nao segura para uso direto, exportar como `provisional` e nunca como `final`
- antes da entrega o agente precisa emitir `delivery_findings` com oportunidades de ajuste fino, e nao esperar feedback manual para descobrir:
  - `frame spill` entre bandas vizinhas de sprite sheet
  - possiveis `internal key holes` uteis em sprites
  - `drop regions` grandes que merecem revisao humana
  - o fato de que `scene layers` em `shared_canvas` RGBA de review podem parecer "vazias" fora da area util

Regra de composicao:

- `ELITE` nao e soma cega de PNGs
- recompor sempre por `alpha compositing`, nunca por sobreposicao bruta sem matte controlado
- `A` define a base atmosferica
- `B` deve entrar por alpha sobre `A`, preservando recortes e sem tapar o ceu por bloco opaco
- `C` deve entrar por alpha sobre o resultado, preservando massa, sombra e pertencimento espacial

Regra de quantizacao:

- `basic` pode usar quantizacao cega como controle
- `elite` deve adiar a quantizacao ate depois que a separacao semantica, os mattes e a recomposicao estiverem corretos
- em layers transparentes, o slot transparente nunca pode participar do remapeamento de pixels visiveis

### 4. Gerar duas leituras

Produza sempre:

- `basic_translation`
- `elite_translation`

`basic` serve de controle.
`elite` serve para provar que houve traducao inteligente.

### 4.1 Explorar alternativas sem perder coerencia

Quando a imagem-fonte permitir mais de uma direcao forte, ou quando o usuario explicitamente quiser escolher a melhor rota visual, a skill pode abrir um laboratorio controlado de alternativas.

Objetivo:

- contornar limitacoes do Mega Drive sem cair em aleatoriedade
- mostrar ao usuario rotas legitimas de direcao de arte
- congelar uma escolha antes de budget final e runtime

Gatilhos legitimos:

- cena heroica ou identitaria do projeto
- conflito entre fidelidade ao `source` e leitura em hardware
- tensao entre atmosfera dramatica e legibilidade de gameplay
- estudos externos anexados pelo usuario com mais de uma rota promissora

Regras duras:

- manter o mesmo `shared_canvas_contract`
- manter o mesmo `translation_target`
- manter geometria, perspectiva e foco composicional
- variar no maximo um eixo visual maior por rota
- permitir no maximo 3 rotas de producao e 1 board diagnostica
- nunca deixar que cada rota invente uma fase diferente

Eixos de variacao aceitaveis:

- temperatura e historia cromatica do ceu
- agressividade de contraste e gamma
- carater do dithering
- hierarquia entre planos e peso atmosferico do `BG_B`
- densidade de detalhe e limpeza de materiais

Artefatos obrigatorios da exploracao:

- `route_exploration_board`
  - miniaturas lado a lado
  - nome da rota
  - o que ganha
  - o que sacrifica
  - risco de budget
- `route_comparison_matrix`
  - leitura
  - atmosfera
  - separacao de planos
  - aderencia ao `source`
  - risco de VRAM
- `route_decision_record`
  - rota preferida pela skill
  - rota escolhida pelo usuario
  - restricoes que passam a valer para o resto do projeto

Regra de congelamento:

- se mais de uma rota continuar forte apos a review, `visual-excellence-standards` deve ranquear as sobreviventes
- se o usuario escolher uma rota, essa escolha vira `locked_visual_direction`
- depois do congelamento, as proximas iteracoes devem preservar essa linguagem visual em vez de reabrir a direcao do zero
- se ja existir `locked_visual_direction` no projeto, novas rotas entram como `challenger routes` e o default continua incumbente ate que uma rota prove vitoria perceptual e estrutural

### 5. Validar

O resultado deve passar por:

- `analyze_aesthetic.py`
- `hardware_budget_review` do `analyze_translation_case.py` quando o alvo for `tilemap` ou `scene_slice`
- validacao pixel-rigida
- budget de VDP quando aplicavel
- prova em ROM com evidencia

### 5.1 Triagem de promocao para ROM

Antes de declarar que uma traducao esta pronta para benchmark ou integracao SGDK, classifique o problema dominante:

- `erro_de_asset`
  - o PNG ainda nao respeita indexacao, slot transparente, matte ou alinhamento espacial
- `erro_de_recurso_sgdk`
  - o asset esta bom, mas a linha `IMAGE` ou `MAP` foi promovida com politica errada de compressao, otimizacao ou papel de runtime
- `erro_de_budget`
  - a curadoria venceu offline, mas a topologia de tiles, mapas ou sprite reserve nao fecha em VRAM real
- `erro_de_pipeline`
  - build, geracao de dependencia, captura ou promocao automatica ainda nao sao estaveis o bastante para sustentar a prova

Ordem obrigatoria:

1. confirmar se a camada ainda esta correta em review humano
2. confirmar se o PNG final continua indexado e se o slot transparente ficou isolado dos pixels visiveis
3. revisar a linha de recurso SGDK e desconfiar de configuracao conservadora em cenas grandes promovidas por `IMAGE`
4. medir tiles uteis, `reuse`, mapa e pressao de VRAM antes de culpar o alpha
5. validar a mesma composicao em BlastEm e so entao fechar o caso

Regra:

- restaurar transparencia indexada e apenas o inicio do diagnostico quando a cena continua divergindo em ROM
- `scene_slice` promovido por `IMAGE` precisa ser revisado tambem como recurso de tile, nao apenas como imagem bonita
- se a prova offline vencer mas a integracao cair, registrar a classe do erro antes de tentar nova rodada de arte
- nunca atribuir a falha inteira ao asset sem auditar `resources.res`, custo estrutural e estabilidade do build

### 5.2 Interpretar o `hardware_budget_review`

Os seguintes sinais do laudo sao canonicos:

- `WHOLE_IMAGE_CONVERSION_RISK`
  - a cena parece compressao direta de ilustracao inteira
  - resposta esperada: modularizar, redistribuir detalhe por plano e evitar aprovar a imagem inteira como tilemap final
- `COMPARE_FLAT_CANDIDATE`
  - a curadoria multi-plano venceu offline, mas a soma de tiles unicos do fundo excede o teto pratico para prova em ROM
  - resposta esperada: manter a curadoria `original + basic + elite` offline e promover um `compare_flat` single-plane honesto para o benchmark, registrando o motivo
- `MANUAL_VRAM_PARTITION_CANDIDATE`
  - a cena mistura fundo pesado com elementos de frente e a reserva padrao do sprite engine pode estar desperdicando VRAM
  - resposta esperada: consultar `megadrive-vdp-budget-analyst` e medir se `SPR_initEx(u16 vramSize)` devolve VRAM suficiente sem quebrar sprites

Regra de pareamento:

- `paired_bg` e credito de composicao, nao premio automatico.
- Se o `basic` ainda for controle ingenuo, crop errado ou sheet editorial desmontada pela metade, deixe a variante sem `paired_bg` e reserve o pareamento para a leitura `elite`.

### 5.3 Escolher a classe certa de tecnica de VDP

Quando a traducao pedir mais do que quantizacao e reuso normal, classifique a tecnica:

- `canonica_segura`
  - `plane size tuning`
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `3+1 palette split`
  - `compare_flat` para prova honesta em ROM
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite graft`
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - exploits e quirks do VDP

Regra:

- a skill pode propor tecnicas `canonica_segura` por padrao
- tecnicas `avancada_com_tradeoff` exigem decisao registrada no caso
- tecnicas `opt_in_de_cena_especial` so entram com intencao declarada, benchmark dedicado e evidencia em BlastEm

### 5. Revisar como tileset, nao apenas como imagem

Toda traducao de `scene_slice` ou `tilemap` deve gerar um pacote de review estrutural:

- `palette_strip` por layer
- `tileset_sheet` por layer
- contagem de tiles totais
- estimativa de reuso por duplicata exata
- estimativa de reuso por `H-Flip`

Objetivo:

- inspecionar se a arte traduzida sobrevive como recurso de tilemap
- revelar desperdicio de VRAM e oportunidades de espelhamento
- separar julgamento estrutural de julgamento estetico

Regra importante:

- `tileset review` e tecnica de inspecao e estruturacao
- nao e permissao para achatar a cena, borrar o fundo ou sacrificar a alma visual so para melhorar a sheet
- se a passada `tile-first` reduzir leitura, material ou profundidade, preserve os artefatos de review e reverta a transformacao visual agressiva

## Tecnicas avancadas permitidas

### `3+1 palette split`

- Se houver foreground heroico, logo importante ou sprite ornamental grande, tente fundo com 3 paletas e reserve 1 para o elemento de frente.
- Isso e preferivel a esmagar tudo em 4 paletas de fundo e depois culpar o sprite por parecer fraco.

### Curadoria manual semantica de paleta

- Quando a imagem-fonte vier rica demais para o budget do Mega Drive, o caminho elite nao e pedir que o quantizador resolva a direcao de arte.
- O agente deve escolher conscientemente:
  - qual rampa representa ceu, pele, metal, pedra ou rua
  - quais tons podem ser fundidos
  - quais highlights precisam sobreviver
  - quais cores saem porque nao sustentam leitura
- Em casos de elenco, ports de arcade ou cena com muitos elementos compartilhando paleta, isso e `canonica_segura`.

### `borrowed_fx_ramp`

- FX pequenos ou embutidos no personagem podem usar uma rampa emprestada da paleta do proprio personagem.
- Isso troca independencia cromatica por economia de paleta.
- Tratar como tecnica `avancada_com_tradeoff`, nunca como default.

### `sprite-grafted parallax`

- Quando BG_A e BG_B nao bastarem para a profundidade desejada, detalhes intermediarios podem virar sprites auxiliares.
- Antes de aprovar, consultar `megadrive-vdp-budget-analyst` para scanline pressure e custo de VRAM.

### `compare_flat` para prova em ROM

- Em benchmark ou validacao humana, uma composicao multi-plano pode ser excelente offline e inviavel em VRAM.
- Nesses casos, a prova em ROM pode usar `compare_flat` single-plane, desde que:
  - a curadoria offline preserve `original + basic + elite`
  - a memoria operacional registre o motivo
  - o benchmark deixe claro que a fusao foi escolha de budget

### `whole-image conversion` e suspeita por padrao

- Imagem inteira convertida direto para tilemap costuma gerar explosao de tiles unicos.
- O agente deve preferir modularizar, redistribuir detalhe por funcao de plano ou fundir apenas a prova de benchmark.
- Se a fonte for uma sheet com estudos, creditos, miniaturas ou quadros auxiliares, tratar o material como referencia editorial e isolar primeiro a regiao jogavel; a sheet inteira nao pode virar `basic` ou `elite` final sem justificativa explicita.

### `plane size tuning`

- Antes de aceitar fundo enorme ou alias de tabela, verificar se a cena realmente precisa de mapa grande.
- `VDP_setPlaneSize(..)` e a forma mais limpa de recuperar espaco de tabelas quando a fase pede menos area de scroll.
- Isso e tecnica de layout, nao hack visual.

### `window alias`

- Se a Window estiver realmente fora do design da cena, a tabela dela pode ser candidata a alias ou reaproveitamento.
- Isso nunca deve ser assumido por padrao.
- Bloqueios tipicos:
  - HUD ou texto em `WINDOW`
  - console/debug ativo
  - pipeline da fase ainda reaproveita a Window em outro estado

### `hscroll slack reuse`

- O bloco da tabela de H-Scroll nao deve ser tratado como livre sem provar que a cena esta travada em `HSCROLL_PLANE`.
- Se houver qualquer chance de scroll por tile ou por linha, o espaco volta a ser area viva do VDP.

### `SAT reuse`

- Reservado para title screens, menus, cutscenes ou benchmarks especiais.
- Nao use como resposta padrao para fazer gameplay "caber".

## Outputs obrigatorios

- `semantic_parse_report`
- `source_inventory`
- `layout_classification`
- `drop_policy`
- `composition_schema`
- asset traduzido
- variante `basic`
- variante `elite`
- `translation_report`
- score do `Juiz Estetico`
- evidencia de emulador
- painel humano `original + basic + elite`
- pacote de review estrutural com `tileset_sheet`, `palette_strip` e resumo de reuso

## Outputs opcionais para curadoria AAA

- `route_exploration_board`
- `route_comparison_matrix`
- `route_decision_record`
- `locked_visual_direction`

## Comando de avaliacao

```bash
python tools/image-tools/analyze_translation_case.py --manifest <caso.json> --output <laudo.json>
```

O laudo deve sair acompanhado de um painel visual lado a lado para validacao humana:

- `ORIGINAL`
- `BASIC`
- `ELITE`

## Gates

- `input_ok`
  - imagem-fonte e spec existem
- `pixel_ok`
  - regras duras do VDP respeitadas
- `visual_ok`
  - leitura, contraste e material sobrevivem
- `delta_ok`
  - `elite > basic`
- `hardware_ok`
  - cabe no budget
- `emulator_ok`
  - foi visto rodando com evidencia

## Regra de Ouro

Se o feedback humano corrigir a traducao, o ajuste nao vai direto para o PNG.

Primeiro:

1. registrar em `doc/03_art/02_visual_feedback_bank.md`
2. transformar em heuristica preventiva
3. atualizar a skill geral se a regra for reaproveitavel
4. so entao corrigir o asset

## Anti-padroes

- quantizacao cega
- downscale sem redesenho
- excesso de detalhe fino
- dithering decorativo
- fidelidade servil a imagem-fonte
- chamar de "traduzido" o que so foi comprimido
- usar `tileset review` como desculpa para degradar contraste, material ou profundidade da cena
- orcar a cena contra `2048` tiles brutos
- assumir que `SPR_init()` automatico serve para qualquer background pesado
- assumir que o layout padrao do VDP e fixo e intocavel
- pular `VDP_setPlaneSize(..)` e ir direto para alias de tabela ou reciclagem agressiva
- tratar `window alias`, `hscroll slack reuse` ou `SAT reuse` como tecnicas seguras por padrao
- usar bug de sprite em `X = -128` como tecnica padrao
- insistir em comparativo dual-plane em ROM quando o hardware pede `compare_flat`
