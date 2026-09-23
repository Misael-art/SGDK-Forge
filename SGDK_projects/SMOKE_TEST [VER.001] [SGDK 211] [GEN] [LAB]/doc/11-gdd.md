# 11 - Game Design Document — SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

## Project Brief

- Promessa central: provar uma abertura de branding reutilizavel com tres identidades visuais distintas no Mega Drive.
- Interacao: o usuario observa a sequencia ou usa `A`/`START` para pular ao boot.
- Valor para o Mega Drive: combina FSM, fontes bitmap, sprites animados, line scroll, cycling de paleta e PCM XGM2 com budget rastreavel.
- O projeto nao e um jogo completo, vertical slice de gameplay nem entrega AAA; e um laboratorio estrutural.

## Visao

`SMOKE_TEST` valida o caminho completo do wrapper SGDK 2.11: assets, runtime, audio, build, BlastEm e documentacao. O slice atual e a cena `APP_SCENE_BRANDING`, composta pelas assinaturas engine, autor e projeto.

O laboratorio prioriza prova tecnica e rastreabilidade. Aprovacao estetica final, gameplay, boss, fisica de pista e campanha ficam explicitamente fora do escopo.

## Core Loop

- Boot da ROM -> sequencia de branding -> boot/menu.
- `A`/`START` -> skip imediato -> confirmacao de que o teardown da cena nao deixa sprites ou scroll residuais.

## Feature Scope Map

### Entra no slice

- FSM de branding em tres fases.
- Tres fontes bitmap identitarias.
- Cinco sprites procedurais de FX.
- Cinco cues PCM via XGM2 com reforco PSG.
- Evidencia BlastEm, SRAM MDRT, audio validation e budget VRAM.

### Entra depois

- Revisao estetica humana e eventual remaster dos logos/fundo.
- Visual delivery gate dedicado.

### Fora de escopo

- Gameplay, progressao, inimigos, boss, fisica de pista e cutscene narrativa.
- Promocao para AAA sem aprovacao visual humana.

## Identidade de Front-End

- Engine: forja industrial, impacto, calor e particulas.
- Autor: terminal digital com monograma rotativo e escrita progressiva.
- Projeto: selo arcade industrial com queda do escudo e brilho de paleta.
- Movimento vivo: line scroll, contramovimento de BG, cycling de paleta e sprites por frame.
- Fora de tom: tela estatica sem ligacao com a identidade ou efeito sem impacto temporal.

## Mecanicas core

- Avanco automatico por timeline.
- Skip seguro com `A`/`START`.
- Teardown completo antes de entrar em `BOOT`.

## Progressao

- A sequencia avanca por frames: engine `0..149`, autor `150..314`, projeto `315..519`.
- Apos o frame 520, a ROM entra em `APP_SCENE_BOOT`.

## Regras e limites

- Sem `float`, alocacao dinamica ou API SGDK inventada.
- Line scroll usa `DMA_QUEUE` com buffer estatico.
- Nao declarar aprovacao visual/AAA sem gate humano.

## First Playable Slice

- Entrega atual: sequencia de branding funcional seguida de boot/menu.
- Sistemas provados: ResComp, VDP, sprites, XGM2, input, FSM, runtime probe e teardown.
- Criterio minimo: tres fases visiveis, skip funcional, transicao ao boot e ROM viva no BlastEm.

## Route Decision Record

- `context_type`: projeto_existente
- `dominant_route`: runtime
- `first_skill`: sgdk-runtime-coder
- `first_tool`: `tools/sgdk_wrapper/rebuild.bat`
- `resource_loading_model`: scene_local_preload
- `asset_strategy`: mixed
- `evidence_required`: build, validation, res_graph, audio validation, runtime metrics, BlastEm e freshness
- `forbidden_shortcuts_until_evidence`: promover visual, AAA ou ROM final sem BlastEm

## Escopo atual

- Em producao: fechamento tecnico da cena `APP_SCENE_BRANDING` como LAB showcase.
- Fora do escopo: gameplay, inimigos, boss, progressao, promocao para AAA.
- Ceiling de status: `technical_lab_validated`. `ready_for_aaa=false` por design.

## Cenas de Front-End

- `APP_SCENE_BRANDING`: engine, autor e projeto.
- `APP_SCENE_BOOT`: confirmacao de transicao limpa.
- `APP_SCENE_MENU`: destino funcional apos o boot.

## Fantasia do Laboratorio

O usuario observa uma cerimonia de forja digital: tres identidades se apresentam em sequencia como selos industriais que tomam forma, brilham e se consolidam. A linguagem e metalurgica no primeiro slot, eletronica no segundo e heraldica no terceiro. A sensacao deve ser de peso e oficio, nao de marketing generico.

## Criterios Visuais por Slot

### Engine (frames 0-149)

- Tom: forja industrial, calor residual, metal pesado.
- Paleta dominante: laranjas quentes transitando para cinzas frios (cooldown de forja).
- FX obrigatorio: sparks com gravidade real, line scroll wave decaying, shimmer metalico.
- Signature moment: frame 2, impacto do logo com burst de sparks e screen shake.
- Subtexto: `FORGED AT 60HZ` em fonte forja.

### Author (frames 150-299)

- Tom: terminal digital, fosforo CRT, selo criptografico.
- Paleta dominante: verdes fosforo com highlights ambar e dourado no monograma.
- FX obrigatorio: typewriter reveal com cursor piscante, glow flutuante, monograma rotativo.
- Signature moment: frame 110, reveal da assinatura completa com sino.
- Identidade: monograma `MO` facetado, nome progressivo, selo autoral.

### Project (frames 300-479)

- Tom: prensa heraldica, selo de aprovacao, impacto vertical.
- Paleta dominante: vermelhos e laranjas industriais com flash dourado no impacto.
- FX obrigatorio: queda do escudo com debris, wave scroll na zona de impacto, fade progressivo.
- Signature moment: frame 326, queda do escudo com debris burst e acorde PSG.
- Identidade: escudo `MMG`, nome em fonte crest, `PRESENTS` + nome do projeto.

## Ambicao Tecnica

- FSM explicita com enter/update/exit por slot e teardown simetrico.
- Line scroll via `DMA_QUEUE` com buffer estatico de 224 words.
- Palette cycling, shimmer, flash e cooldown per-material.
- Cinco cues PCM XGM2 com reforco PSG nos impactos.
- Camera shake controlada via `VDP_setVerticalScroll` no `BG_A`.
- Skip seguro com `A`/`START` e cleanup completo em qualquer frame.
- Runtime probe MDRT com heartbeat SRAM.
- Zero float, zero malloc, zero DMA fora de VBlank.

## Regras Sistemicas

- Cada slot usa fonte bitmap scene-local carregada em `BRAND_TILE_FONT`.
- Paletas: PAL0 (BG), PAL1 (logo), PAL2 (sprites FX), PAL3 (fonte), com separacao funcional.
- Sprites SAT: max 13 no Engine, 3 no Author, 9 no Project.
- Nenhum efeito existe sem ligacao com a identidade do slot.
- Todo FX tem decaimento temporal; nada permanece estatico indefinidamente.

## Criterios de Qualidade Visual

- Assets atuais sao builder-generated via `build_branding_v3_assets.py`.
- Status visual: `needs_review` para entrega; classificados como `local_author_pixel_rasterization`.
- Para elevar a entrega visual, os backgrounds precisam virar composicoes autorais com staging e focal point.
- Logotipos precisam virar IMAGE compostas, nao glifos bitmap glyph-by-glyph.
- Monogramas e sprites FX precisam de versoes com mais presenca.
- Ate que arte autoral substitua os assets gerados, o teto visual e `technical_lab_validated`.

## Tecnicas Escolhidas

- `LINE_SCROLL_WAVE`: wave scroll decaying via `HSCROLL_LINE` + `DMA_QUEUE`; owner: `sgdk-runtime-coder`; budget: 224 words/frame; fallback: `HSCROLL_PLANE`.
- `PALETTE_CYCLING`: shimmer, cooldown e glow por manipulacao direta de `PAL_setColor`; owner: `sgdk-runtime-coder`; budget: 2-4 cores/frame; fallback: cor estatica.
- `PSG_PROCEDURAL_REINFORCEMENT`: tons PSG sincronizados com cues PCM; owner: `sgdk-runtime-coder`; budget: 3 canais; fallback: PCM only.
- `CAMERA_SHAKE`: screen shake via `VDP_setVerticalScroll` no impacto; owner: `sgdk-runtime-coder`; budget: 1-3 frames; fallback: sem shake.
- `SPRITE_PARTICLE_PHYSICS`: sparks e debris com gravidade, velocidade variada e release; owner: `sgdk-runtime-coder`; budget: 12 sparks + 8 debris max; fallback: menos particulas.
