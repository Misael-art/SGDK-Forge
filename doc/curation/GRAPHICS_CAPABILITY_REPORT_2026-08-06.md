# Relatório transversal de capacidade gráfica — SGDKForge

Data da varredura: 2026-08-06
Escopo: SGDK_projects/ e SGDK_Engines/, incluindo subpastas de treino,
laboratório, evidência, rascunho, builders, data/, res/ e documentação.
Uso: handoff para agentes. Este relatório não promove automaticamente tentativa,
asset, ferramenta ou projeto a referência canônica.

## 1. Resultado executivo

A varredura encontrou 10 iniciativas com atividade gráfica, 700 arquivos
visuais (666 PNG, 28 GIF e 6 SVG) e 166 lições registradas nos learning ledgers.
SGDK_Engines/ está vazio; toda experiência gráfica material está em
SGDK_projects/.

A capacidade mais madura do acervo não é um gerador automático de sprites. É um
sistema de produção e veto que já aprendeu a:

1. separar fonte, candidato, processado, recurso ativo e evidência;
2. distinguir technical_pass de visual_pass;
3. preservar tentativas reprovadas como negative_evidence;
4. exigir model sheet, escala, anatomia, material, pivot e movimento;
5. montar cenários por planos, kits e contratos;
6. medir paleta, tiles, transparência, VRAM, DMA, scanline e runtime;
7. limitar a conclusão ao menor escopo realmente visto no BlastEm.

O maior gargalo continua artístico: traduzir uma fonte forte para pixel art
nativa sem perder anatomia, carisma, materiais e acting. Nearest-neighbor,
quantização global, downscale direto, primitivas Pillow e SVG tecnicamente limpo
não resolveram esse problema.

## 2. Método da auditoria

- inventário recursivo por extensão e ownership;
- art_diagnostic.py executado em cada raiz relevante;
- leitura de memory banks, manifests, reports, changelogs e learning ledgers;
- inspeção de comparativos, contact sheets e capturas representativas;
- separação entre recurso ativo em res, fonte em data, arte de laboratório,
  output gerado e evidência;
- nenhum status visual inferido apenas porque o PNG compila.

Este é um inventário completo das iniciativas e métodos encontrados, não uma
aprovação pixel a pixel dos 700 arquivos.

## 3. Censo por iniciativa

| Iniciativa | Cenário diagnosticado | Arte descoberta | Grafo ativo | Lições | Teto honesto |
|---|---|---:|---:|---:|---|
| BLUE_CIRCUIT | 2_res_inadequate_check | 42 | 9/9 tecnicamente OK | 15 | player v002 aprovado no escopo medido; projeto visual bloqueado |
| Celestial Chase Revive | 2_res_inadequate_check | 77 | 11/11 tecnicamente OK | 18 | runtime técnico com placeholders; criativo bloqueado |
| Celestial Chase visual benchmark | 2_res_inadequate_check | 131 | 21/21 tecnicamente OK | 18 | laboratório em BlastEm; movimento perceptual pendente |
| FORGE_REFERENCE | 1_data_and_res_check | 11 | sem grafo gráfico próprio | 1 | fixture neutra, não referência de arte |
| KIRBY_FAN GAME CLOUDE | 2_res_inadequate_check | 162 | 22/22 tecnicamente OK | 64 | P1–P4 arquivadas; sem master gráfico aprovado |
| MARE_BRAVA | 2_res_inadequate_check | 131 | 15/15 tecnicamente OK | 19 | direção forte; produção visual ainda parcial |
| SMOKE_TEST | 2_res_inadequate_check | 44 | 16/16 tecnicamente OK | 0 | branding procedural em needs_review |
| SCENE_TILEMAP_CURATION_FIXTURE | 2_res_inadequate_check | 15 | 6/6 tecnicamente OK | 0 | fixture técnica; closeout visual bloqueado |
| HYBRIDO_MUAY_THAI | 2_res_inadequate_check | 132 | 11/11 tecnicamente OK | 18 | estudo de personagem; visual não liberado |
| MUGEN SFF Showdown | 4_lab_nested_art_review | 90 | viewer aninhado, 5 ativos | 13 | multi-plano visto; dump/budget pendente |

O nome histórico 2_res_inadequate_check identifica o cenário de revisão de res.
Nos casos acima, os recursos ativos contabilizados estavam tecnicamente
adequados. Isso não equivale a aprovação estética.

## 4. Catálogo das iniciativas

### 4.1 BLUE_CIRCUIT — gates humanos e revalidação de sprite

Explorado:

- storyboard, model sheet e spritesheet HD aprovados para tradução;
- conversão de title, BG/FG, player, inimigo, mini-boss e projétil;
- reconstrução do player em grid nativo 24x32;
- contact sheet e GIFs de corrida, tiro, salto e idle;
- integração estática observada em BlastEm.

Método:

brief autoral -> gates humanos -> model sheet -> tradução VDP ->
sprite_artifact_report.v2 -> contact sheet/motion -> res -> BlastEm.

Correção decisiva: strips antigos foram retraídos como
technical_pass_visual_fail. O report v2 passou a medir clipping, ilhas,
anatomia, pivot, contato dos pés e delta entre frames. Os strips anteriores
viraram evidência histórica e foram proibidos como fonte.

Ferramentas/evidências:

- data/builders/build_blue_player_v002.py;
- doc/contracts/sprite_strip_rejection_report_20260723.json;
- out/logs/sprite_artifact_report.json;
- out/evidence/sprite_rework_20260723/blue_player_contact_sheet_v002.png;
- doc/contracts/sprite_revalidation_report_20260724.json.

Lição: auditoria de dimensões, paleta e grid pode produzir falso positivo
visual. O redraw nativo funciona melhor quando parte do model sheet aprovado e
é avaliado por ação.

### 4.2 Celestial Chase Revive — placeholder procedural

Explorado:

- assets de corrida e HUD por primitivas Pillow;
- first playable técnico, road plane, sprites e HUD;
- mockups SVG de planejamento com hash;
- contratos de identidade, cutscene, boss, UI, paleta e animação.

Método observado:

builder procedural -> res -> runtime técnico -> diagnóstico da dívida criativa.

O memory bank reclassifica tools/generate_assets.py como placeholder. A
iniciativa provou fluxo e expôs bugs, mas não definiu arte final.

Lições:

- assets Pillow não são camada visual de alto padrão;
- branding em VDP_drawText não cria identidade;
- mockup local orienta planejamento, não substitui arte final;
- módulos não viram first playable sem a ROM vigente;
- restauração de paletas e ownership de cena precisam ser explícitos.

### 4.3 Celestial Chase visual benchmark — perspectiva e gate de cor

Explorado:

- perseguição pseudo-3D com estrada, BG_A/B, herói, ghost, perseguidor, HUD e FX;
- builders tile-aware, dedup, perspectiva, dithering e redução de micro-ruído;
- gate de screenshot para detectar matte/cápsula opaca;
- baseline, WebP multi-frame, SRAM e VDP dump;
- paleta, VRAM, scanline, CPU e composição de câmera.

Método:

fonte premium -> compare_flat -> builder semântico/tile-aware -> testes -> res
-> runtime -> screenshot gate -> baseline seletivo -> VDP/telemetria.

Ferramentas:

- data/builders/build_chase_first_playable_assets.py;
- data/builders/validate_chase_visual_screenshot.py;
- data/builders/tests/test_chase_v009_assets.py;
- scene_tilemap_conversion_report.json;
- per_tile_palette_conflict_report.json.

Lições:

- PNG indexado ainda pode ter cápsula opaca se o builder pintar o canvas;
- estabilidade técnica mascarou falha visual;
- estrada e movimento exigem evidência temporal;
- multiplicação por scanline pode destruir o budget;
- trick de raster não entra automaticamente em cena saturada;
- total de sprites por frame não mede pressão por scanline.

### 4.4 FORGE_REFERENCE — fixture neutra

Explorado:

- runtime sem IP/case source, baseado em primitives/texto;
- contratos ROM-side de telemetria, SRAM, hash, gate e aprendizado;
- branding de template somente como fixture.

Papel: validar que evidência, gate e aprendizado compartilham a mesma identidade
de ROM. Não deve ser usado como benchmark estético ou fonte de arte.

### 4.5 KIRBY_FAN GAME CLOUDE — quatro rotas arquivadas

Explorado:

- R1: concepts/fontes com prompts, RGB333 declarado e manifests;
- P1: redraw procedural em Python, regular tecnicamente e fraco visualmente;
- P2: masters HD arcade, reprovados;
- P3: conceito HD + recorte + nearest-neighbor + quantização; melhor intenção,
  mas arte esmagada por algoritmo;
- P4: master SVG flat; limpeza vetorial não corrigiu anatomia.

Estado: P1, P2, P3 e P4 estão archived_visual_rejected. Nenhuma pode servir de
fonte, baseline, entrada de quantização ou promoção para res.

Ferramentas/métodos:

- build_placeholder_art.py;
- build_p1_kirby.py e build_p1_remaining_assets.py;
- Pillow/numpy para RGB333, cores, luminância, transparência e downscale;
- quantizador P3 arquivado;
- SVG + rsvg-convert na P4;
- contact sheets, notes de autocrítica e comparação conceito/aplicação.

Lições:

- checks técnicos passaram arte inaceitável;
- nearest-neighbor não é pixel art;
- quantização pode deslocar o magenta e criar franja;
- vetor limpo não substitui topologia, proporção ou acting;
- métrica ruim induz micro-dither destrutivo;
- validação começa por anatomia/silhueta e termina na técnica.

Último arquivo: data/archive/p4_2026-08-06_vector_master_anatomy_rejected/.

### 4.6 MARE_BRAVA — visual-first e cena modular

É a iniciativa mais completa em direção de arte e organização de pipeline.

Explorado:

- art bible, style manifest, moodboard, brand, palette master e drift policy;
- prompt pack assíncrono com lineage e descartes;
- prova VDP em 320x224, 15 cores e snap 9-bit;
- TAINA: concepts, model sheets, lineart 1 px, fidelity reports, visual DNA,
  scale/pivot, turnaround, frame delta, foot contact, strips e contact sheets;
- CAIS_01: semantic parse, layer plan, scene kit, world layout, parallax,
  ecology, tilemap, paleta por tile, budget, basic/elite/runtime;
- builders de locomotion, jab e passes de cenário.

Método consolidado:

direção + gameplay -> premium source -> prova 320x224 -> model sheet pixel ->
lineart nativo -> key poses -> strip -> movimento/fidelidade -> res -> cena
composta -> BlastEm.

Lições:

- fonte premium e asset VDP são categorias diferentes;
- downscale serve melhor a massas de cenário do que anatomia;
- modelos ignoram proporção estilizada com frequência;
- gerar todos os frames por IA produz morphing;
- pose-mestre + edição de clusters preservam autoria;
- panorama deve virar kit modular montado pelo level design;
- efeito técnico não substitui composição;
- contact sheet VDP é uma prova barata;
- montagem modular nativa preserva leitura e reduz tiles.

Ferramentas:

- tools/art/build_taina_*;
- tools/art/build_cais01_*;
- reports em doc/art/characters/taina/ e doc/art/environments/cais01/;
- scene_tilemap_conversion_report.json;
- per_tile_palette_conflict_report.json.

### 4.7 SMOKE_TEST — branding determinístico

Explorado:

- três gerações de fundos, logos, fontes e FX;
- builder determinístico 4-bit e lineage;
- shimmer, palette cycling, line scroll, shake, debris e XGM2;
- evidência de runtime e custos de cena.

Método:

builder procedural -> asset SGDK-safe -> FSM branding -> res -> BlastEm.

Resultado: laboratório técnico reutilizável, porém needs_review como arte final.
O diagnóstico histórico registra que builder-generated e tiling foram
confundidos com composição.

Ferramentas:

- tools/image-tools/build_branding_intro_assets.py;
- tools/image-tools/build_branding_v3_assets.py;
- versões em doc/changelog/assets/.

### 4.8 SCENE_TILEMAP_CURATION_FIXTURE — conversão de cena

Explorado:

- imagem indexada 320x224 em rascunho e res/bgs;
- conversão, dedup, flags e conflitos;
- branding integrado para exercitar o grafo;
- build e captura de laboratório.

Estado: recursos tecnicamente OK; direção visual, VDP dump, performance e
closeout bloqueados. É fixture, não benchmark estético.

### 4.9 HYBRIDO_MUAY_THAI — laboratório de personagem

Explorado:

- v001 procedural; v002 downscale; v003–v008 model sheets;
- v009 sheet nativa tecnicamente válida, visualmente reprovada;
- v010 recovery com gates, visual DNA, lineart, key poses, strips, pivot,
  contact sheet e runtime;
- v011/v012 hi-bit/IA ainda sem fechamento;
- material lock por membro assimétrico;
- anatomia, acting, eye tracking e endpoint do braço especial;
- visual_source_of_truth proibindo sheet ruim como fonte.

Método aprendido:

gate arte+gameplay -> model sheet com scale/turnaround/material lock ->
aprovação -> lineart 1 px por estado -> clusters nativos -> key poses -> strips
-> fidelity/artifact/motion -> runtime.

Falhas decisivas:

- terceiro braço por sobreposição;
- mão especial ilegível;
- face estática em combate;
- spray virando tile-noise;
- sprite 48x64 tecnicamente correto, porém blocado e genérico;
- BlastEm e estabilidade mascarando reprovação visual.

Ferramentas:

- build_hibrido_fighter_assets_v002.py;
- build_hibrido_fighter_sprite_sheet_v009.py;
- build_hibrido_fighter_visual_package_v010.py;
- build_hibrido_fighter_arcade_hi_bit_v011.py;
- build_hibrido_ai_visual_package_v012.py;
- validators, fidelity reports, comparison boards e GIFs.

### 4.10 MUGEN SFF Showdown — reconstrução e streaming

Explorado:

- parser SFF v1.01 e execução de regras DEF;
- quatro frames/camadas em mundo 768x480;
- tiles 8x8, dedup, H/V/HV flip e sub-paletas;
- bins, viewer SGDK, câmera de palco e streaming;
- route A com BG_B distante, BG_A mid/floor, culling e line scroll;
- comparação source viewport -> export preview -> BlastEm.

Método:

SFF/DEF local com hash -> parse semântico -> mundo -> tiles/paleta -> budget de
janela -> bins -> viewer -> câmera/streaming -> BlastEm -> comparação.

Ferramentas:

- tools/mugen_sff/sff_v1.py, def_stage.py e visual_gate.py;
- tools/vdp_tiles/tile_codec.py, tile_dedup.py e palette_plan.py;
- tools/pipeline/run_showdown_pipeline.py;
- tools/sgdk_export/export_showdown_bins.py;
- câmera, auditors e 22 testes Python no snapshot de recovery.

Lições:

- composição MUGEN é execução, não metadado;
- crop de viewport não é conversão de stage;
- world-size deve ser preservado e navegado;
- tiles globais da ROM não são budget residente;
- streaming full-frame pode rasgar evidência;
- HUD/viewer não pode sobrescrever paleta do stage;
- stage visível ainda pode falhar em composição e cor;
- gate matte/magenta não mede vitalidade cromática.

## 5. Genealogia dos métodos

| Método | Onde | Ganho | Limite | Decisão |
|---|---|---|---|---|
| Primitivas procedurais | Smoke, Revive, Kirby P1 | determinismo e teste rápido | visual genérico/anatomia pobre | somente fixture/placeholder |
| IA/concept + quantização | Híbrido v002, Kirby P3, Mare prova VDP | exploração rápida | destrói rosto/material | prova de sobrevivência, não final |
| Vetor + raster posterior | Kirby P4 | editável e flat | anatomia continuou ruim | não validado como incumbente |
| Model sheet + redraw nativo | Blue v002, Híbrido v010, TAINA | controle de identidade | exige revisão artística | incumbente para personagem |
| Scene kit + multi-plane | Mare, MUGEN A, Celestial | autoria de cena e budget | mais contratos/streaming | incumbente para cenário complexo |
| Builder semântico/tile-aware | Celestial, Mare, MUGEN | dedup e repetibilidade | não substitui direção | usar após direção congelada |
| Runtime-first provisório | Revive, Smoke, labs | prova arquitetura | falsa sensação de maturidade | rotular creative_blocked |

## 6. Padrões adotados

### 6.1 Linhagem

- source_candidate, mood_reference_only, processed, active_res_art,
  evidence_art, negative_evidence e obsolete_for_generation_source são papéis
  diferentes;
- fonte precisa de hash, origem e uso permitido;
- tentativa reprovada é arquivada;
- runtime candidate não vira source automaticamente.

### 6.2 Personagem

1. art_gameplay_direction_gate;
2. anatomia/topologia antes de cor;
3. scale contract;
4. turnaround, material e assimetria travados;
5. lineart_blocking_1px;
6. key poses por ação;
7. model_sheet_to_sprite_fidelity_report;
8. sprite_artifact_report.v2;
9. pivot, pés e delta medidos;
10. contact sheet e captura animada;
11. BlastEm vinculado ao hash da ROM.

### 6.3 Imagem técnica

- PNG modo P e PLTE até 16;
- index 0 consistente;
- máximo 15 cores visíveis;
- RGB333 na etapa VDP;
- dimensões múltiplas de 8;
- auditoria por célula/frame;
- sem clipping, matte, ilhas, debris ou FX assado.

### 6.4 Cenário

- semantic parse;
- layer plan e papel de BG_A/B/foreground;
- kit modular e object role map;
- tilemap/flip/sub-paleta;
- palette vitality e separação de planos;
- VRAM/DMA/streaming/scanline;
- comparação original/basic/elite/runtime;
- câmera/parallax ligados ao gameplay.

### 6.5 Evidência

- technical_pass e visual_pass separados;
- screenshot única não prova movimento;
- GIF/WebP não substitui spritesheet ou runtime;
- captura confirma cena, ROM e sessão;
- screenshot BlastEm, SRAM e VDP dump quando aplicável;
- sem evidência, status fica documentado/buildado/lab.

## 7. Ferramentas

| Função | Encontradas/empregadas | Limite |
|---|---|---|
| Descoberta | art_diagnostic.py, manifests, rg, inventories | discovery não aprova arte |
| Geração raster | canal nativo, prompt packs, Pillow | saída fica candidata até gates |
| Geração local planejada | imagegen_circuit, Bonsai/ComfyUI preflight | frequentemente ausente/offline/bloqueado |
| Vetor | SVG + rsvg-convert | P4 reprovada por anatomia |
| Quantização | Pillow, numpy, RGB333 snap, palette maps | pós-processo, não direção |
| Auditoria PNG | art_diagnostic, validators, ImageMagick/Pillow | técnica separada de estética |
| Personagem | fidelity/artifact/pivot/foot/delta/contact/GIF | principal barreira contra falso positivo |
| Cenário | Tiled/JSON quando presente, scene kit, tilemap reports | montagem semântica vence panorama |
| MUGEN | SFF/DEF parser, tile codec, dedup, palette, exporter | ferramenta local de estudo |
| Runtime | wrapper SGDK 2.11, ResComp, BlastEm, SRAM/VLAB | necessário para claim runtime |
| Autoria manual planejada | Aseprite/GraphicsGale citados em Mare | planejado; uso consolidado não provado |

## 8. Lições documentadas

| Iniciativa | Lições | Temas |
|---|---:|---|
| BLUE_CIRCUIT | 15 | captura, sessão, escopo e revalidação |
| Celestial Revive | 18 | placeholder, front-end, corrupção, cena |
| Celestial benchmark | 18 | perspectiva, raster, transparência, budget |
| FORGE_REFERENCE | 1 | identidade de ROM e gate |
| Kirby | 64 | cor, CRAM, S/H, parallax, arte, performance |
| Mare Brava | 19 | prompts, proporção, model sheet, modularidade |
| Smoke | 0 | lições ainda no memory/changelog |
| Scene fixture | 0 | fixture sem captura no ledger |
| Híbrido | 18 | anatomia, assimetria, acting, fidelidade |
| MUGEN | 13 | composição, câmera, paleta, streaming |

Os ledgers são derivados de success/failure patterns e não devem ser editados
manualmente. O inventário JSON aponta para cada arquivo.

## 9. Anti-padrões comprovados

- promover arte porque compila;
- nearest-neighbor como desenho;
- todos os frames por IA;
- quantizar antes de anatomia;
- procedural como fonte final crítica;
- medir somente dimensões/cores/grid;
- screenshot estática como movimento;
- usar candidate reprovado como nova fonte;
- panorama sem câmera/gameplay/streaming;
- confundir transparência com qualidade;
- micro-dither para bater métrica;
- FX sem função/ownership;
- atualizar baseline para esconder diferença;
- chamar lab de entrega.

## 10. Fluxo recomendado ao próximo agente

### Personagem crítico

1. diagnosticar data/res e ler memory bank;
2. declarar função, câmera, escala e hitbox;
3. congelar direção e must_preserve;
4. aprovar model sheet com frente/costas/anatomia/material;
5. lineart 1 px em grid nativo;
6. key poses antes de frames;
7. clusters e mapa de material; FX separado;
8. fidelity + artifact report v2;
9. contact/pivot/foot/delta/motion;
10. promover para res somente após aprovação;
11. build, BlastEm, multi-frame e revisão humana;
12. arquivar falha como negative_evidence.

### Cenário

1. preservar fonte e fazer semantic parse;
2. separar atmosfera, plano jogável, oclusão e anchors;
3. kit modular e layout/câmera;
4. BG_A/B, foreground, parallax e ecologia;
5. paletas por papel/material;
6. conversão tile-aware e conflitos;
7. VRAM/DMA/streaming;
8. source/basic/elite/runtime em 320x224;
9. BlastEm sem extrapolar claim.

## 11. Sugestão de canonização

Pode agregar após revisão humana:

- technical_pass_visual_fail;
- sprite_artifact_report.v2;
- visual_source_of_truth;
- model sheet com scale/turnaround/material lock;
- lineart nativo por estado e key poses;
- scene kit + multi-plane + semantic parse;
- contact sheet VDP e comparação source/runtime;
- BlastEm vinculado ao hash da ROM.

Não canonizar como método vencedor:

- P1/P2/P3/P4 do Kirby;
- downscale Híbrido v002/v009;
- procedural como arte crítica final;
- quantização automática como passe estético;
- SVG limpo como substituto de anatomia;
- MUGEN como ferramenta canônica antes de aprovação e dump/budget.

## 12. Fontes de retomada

- painel: doc/curation/evidence/graphics_initiatives_board_2026-08-06.png;
- inventário: doc/curation/graphics_capability_inventory_2026-08-06.json;
- memory banks de cada projeto;
- Mare: doc/21-relatorio-direcao-de-arte-ver-001.md;
- Híbrido e MUGEN: memory banks nas áreas de treinamento;
- learning ledgers de cada iniciativa.

## 13. Limites

- não houve aprovação humana dos 700 arquivos;
- SGDK_Engines/ não contém material;
- “arte descoberta” inclui cópias em source/processado/res/evidence;
- o relatório não altera skills, schemas ou política canônica;
- o status de cada projeto continua subordinado ao memory bank e evidência.
