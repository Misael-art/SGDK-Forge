# 06 - AI Memory Bank (MegaDrive_DEV)

**Última atualização:** 2026-04-21
**Escopo:** Repositório MegaDrive_DEV (workspace global)  
**Projeto em foco:** Shadow Dancer Hamoopig, Pequeno Príncipe, engines SGDK 211, reorganização workspace, assimilação do engine scan pass 2

> **DIRETRIZ:** Este é o bloco de memória primário para o workspace global.
> Leia integralmente antes de decisões que afetem múltiplos projetos.
> Atualize ao encerrar sessões relevantes.

---

## 1. ESTADO ATUAL DO REPOSITÓRIO

### Build e validação
- **Wrapper centralizado:** `tools/sgdk_wrapper/` — única fonte de verdade para build, clean, run.
- **Validação:** `validate_resources.ps1` gera `validation_report.json` em `out/logs/`.
- **Scripts de projeto:** build.bat, clean.bat, run.bat delegam ao wrapper (2–3 níveis `..` conforme profundidade).
- **13/13 projetos compiláveis** geram ROM com sucesso (AGENTS.md).

### Projetos principais
| Projeto | Tipo | Memory Bank próprio |
|---------|------|---------------------|
| Pequeno Príncipe Cronicas das Estrelas | GAME [AVENTURA] | `doc/10-memory-bank.md` |
| Shadow Dancer Hamoopig | ENGINE [PLATAFORMA] | — |
| BLAZE_ENGINE | ENGINE [BRIGA DE RUA] | — |

---

## 2. O QUE ACABOU DE ACONTECER (2026-04-02)

### Reconciliacao do diagnostico AAA externo (2026-04-10)
- O diagnostico externo de gaps AAA foi aceito parcialmente como disciplina de canonizacao, mas NAO como roadmap literal.
- Foi criado o protocolo-meta `doc/03_art/AAA_SKILL_CANONIZATION_PROTOCOL.md` para reger canonizacao de skills artisticas e tecnicas sem substituir protocolos especializados.
- `doc/03_art/04_art_translation_curation_protocol.md` permanece como protocolo especializado de `art-translation-to-vdp`.
- `doc/03_art/AAA_SKILL_CURATION_STATUS.md` passou a operar com dois eixos obrigatorios:
  - `doctrine_status`
  - `runtime_proof_status`
- Sprint 1 foi preservada como `INCORPORADO` em doutrina, sem ser promovida artificialmente para prova em ROM.
- `S5.1` Forward Kinematics e `S5.2` XGM2 Audio Architecture foram aceitas como backlog oficial futuro, ambas ainda bloqueadas antes de Fase 1.
- Regra consolidada para drafts de Sprint 2+: citar `92_frontdoor`, depois `92_registry`, e usar `99_appendix` apenas como evidencia bruta.
- Decisao consolidada: nao duplicar skills ja existentes (`sprite-animation`, `character-design`, `multi-plane-composition`) nem recriar docs que ja existem e devem ser revisados in place.

### Matriz de maestria hardware-level 16-bit (2026-04-10)
- Criada a nova camada de dominio em `doc/05_technical/93_16bit_hardware_mastery_matrix.md`, `doc/05_technical/93_16bit_hardware_mastery_registry.json` e `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`.
- A nova camada NAO substitui `92_frontdoor` nem `92_registry`; ela organiza a maestria por tecnica e por owner skill.
- Estado consolidado do agente:
  - `incorporated`: tile flipping, DMA safety basico, sprite timing/pivot, multi-plano basico, budget VDP basico
  - `candidate_with_evidence`: line scroll, H-Int palette split, pseudo-3D road stack, priority split foreground, tile cache streaming
  - `partial`: column scroll, Shadow/Highlight como trilha dedicada, palette cycling formal, CRT-aware dithering, sprite multiplexing, BG_B bypassing, slot rule de S/H
  - `gap_pure`: forward kinematics, XGM2 audio
- Decisao consolidada: nao criar skills novas para tecnicas que ainda podem amadurecer dentro de `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst`, `multi-plane-composition`, `visual-excellence-standards`, `sprite-animation` e `character-design`.
- Skills novas justificadas imediatamente:
  - `forward-kinematics-rigging`
  - `xgm2-audio-director`
- O `BENCHMARK_VISUAL_LAB` continua sendo o unico laboratorio oficial de prova. Nenhuma tecnica nova sobe acima de `blastem_proven` sem scene dedicada, budget line e evidence bundle rastreavel.

### Reconciliacao dos efeitos lendarios na malha de maestria (2026-04-10)
- `H-Int` deixou de existir apenas como restricao de budget e passou a ser tratado como substrato formal via `h_int_control_plane`.
- `mid-frame palette swap` foi explicitamente absorvido como alias visual de `hint_palette_blending`; nao virou trilha separada.
- `pseudo-3D` foi dividido em duas trilhas distintas:
  - `pseudo3d_road_stack`
  - `software_affine_pseudo3d`
- `Window Plane` entrou na matriz como competencia formal de HUD e arquitetura de display:
  - `window_plane_static_hud`
- `window alias` permanece tecnica avancada e nao-default; nunca deve ser confundida com uso normal da `WINDOW`.
- `interlaced_448_display_mode` entrou no core roadmap de maestria, mas com politica operacional `special_scene_only`.
- `sprite multiplexing` deixou de ser categoria unica e passou a ser dividido em:
  - `sprite_temporal_multiplexing`
  - `sprite_midframe_sat_reuse`
- `sprite_midframe_sat_reuse` depende formalmente de `h_int_control_plane` e ficou classificado como trilha futura perigosa.
- O contrato do `BENCHMARK_VISUAL_LAB` foi endurecido para exigir:
  - `intencao_da_cena`
  - `signature_moment`
  - `causa_de_gameplay`
  - `secondary_fx_pairings`
  - `hint_owner`
  - `operational_policy`
  - `budget_line`
- Decisao consolidada:
  - nao criar skill nova para H-Int, Window Plane, interlaced, palette split ou pseudo-3D road-stack
  - novas skills continuam restritas aos gaps puros ja aceitos (`forward-kinematics-rigging` e `xgm2-audio-director`)

### Avaliacao honesta de efeitos especulativos modernos (2026-04-10)
- Quatro propostas especulativas de "efeitos modernos no Mega" foram reconciliadas com nomes honestos e limites claros de hardware.
- Ranking consolidado de viabilidade:
  1. `procedural_raster_glitch_suite`
  2. `masked_shadow_highlight_lighting`
  3. `mutable_tile_decal_mutation`
  4. `cellular_microbuffer_sim`
- Decisoes consolidadas:
  - `procedural_raster_glitch_suite` e altamente viavel como combinacao dirigida de `line scroll`, `palette shock`, `WINDOW` e leitura dramatica sob controle
  - `masked_shadow_highlight_lighting` e viavel como ilusao forte de spotlight/lanterna, mas NAO equivale a iluminacao dinamica moderna nem a alpha blending
  - `mutable_tile_decal_mutation` so e honesto como dano persistente local por `RAM shadow copy` + `mutable tile pool`; VRAM nao deve ser tratada como framebuffer livre
  - `cellular_microbuffer_sim` so e honesto como microframebuffer local em ilha pequena; NAO equivale a sandbox global estilo Noita
- Alocacao no framework:
  - `procedural_raster_glitch_suite` entra em `S2.1`
  - `masked_shadow_highlight_lighting` entra em `S2.2`
  - `mutable_tile_decal_mutation` vira trilha futura `T3`
  - `cellular_microbuffer_sim` vira trilha futura tardia `T4`
- Benchmarks oficiais reservados:
  - `fx_procedural_glitch_lab`
  - `fx_masked_light_lab`
  - `fx_decal_mutation_lab`
  - `fx_cellular_microbuffer_lab`
- Regra consolidada: nenhum desses quatro efeitos existe no framework sem ROM, BlastEm, budget aprovado e aprovacao humana.

### Assimilação do engine scan pass 2 (2026-04-10)
- Criado o front door canônico em `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md` para resolver a ambiguidade de "pass 2 sem pass 1".
- Criado o registry machine-readable em `doc/05_technical/92_sgdk_engine_pattern_registry.json` com classificação explícita: `verified_example`, `interpreted_pattern`, `candidate_for_canon`, `blocked_pending_repro`.
- `doc/05_technical/99_sgdk_engines_scan_appendix.md` foi rebaixado semanticamente para `appendix / raw extraction log`; continua preservado, mas não funciona como registro canônico.
- A skill `sgdk-runtime-coder` e `references/pattern_catalog.json` passaram a apontar para o registry como fonte de padrões candidatos, sem promover scan para canon por inércia.
- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json` recebeu `registry_path` e a wave 1 de casos executáveis:
  - `case_variable_width_font_tidytext`
  - `case_tile_text_stream_renderer`
  - `case_pseudo3d_road_zmap`
  - `case_tile_cache_streaming`
  - `case_hint_wobble_spotlight`
- Fila de canonização inicial registrada:
  1. TidyText
  2. pseudo-3D road stack
  3. tile refcount cache
  4. H-Int FX family
  5. platformer feel
  6. multi-rate deceleration
  7. entity manager
  8. HUD patterns
  9. slope collision
  10. trig library
- Regra consolidada: pesquisa validada de engine é insumo forte, mas não canon pronta; promoção depende de referência exata, descrição limpa, `lib_case` reprodutível e gate humano explícito.

### Sistema de decisao HUD/UI FX canonizado (2026-04-20)
- Criado `doc/03_art/13_hud_ui_fx_decision_system.md` como doutrina principal de `S3.2 HUD Design`.
- `ui_decision_card` passa a ser o artefato canonico para HUD, interface, overlay, subscreen, menu, title e FX de interface.
- `front_end_profile` deixa de existir como artefato separado e passa a sobreviver apenas como `profile_kind=front_end_profile` dentro do mesmo `ui_decision_card`.
- `AAA_SKILL_CURATION_STATUS.md` promoveu `S3.2` para `INCORPORADO`, mas `runtime_proof_status` continua `NAO_INICIADA`.
- Pipeline e workflows da `.agent` agora exigem que ownership, fallback e budget de UI sejam declarados antes de budget/runtime quando houver surface formal de interface.
- `scene-state-architect`, `visual-excellence-standards`, `megadrive-vdp-budget-analyst`, `sgdk-runtime-coder`, `sgdk-build-wrapper-operator` e `game-director-sgdk` foram alinhados ao novo contrato.
- Decisao consolidada:
  - `window_plane_static_hud` continua sendo o default seguro para leitura constante
  - `window_plane_lifebar` e `sonic_hud_physics_family` seguem como referencias de pattern, nao defaults universais
  - `procedural_raster_glitch_suite` continua tecnica de alto risco e so entra com owner explicito, reset simetrico e fallback honesto
- Politica tipografica consolidada:
  - `fixed_custom_hud_font` e a rota default para HUD, labels fixos e leitura rapida
  - `variable_width_tidytext` fica para dialogo, credito, lore e texto premium em PT-BR
  - `glyph_manifest` passa a ser obrigatorio sempre que a UI subir fonte dedicada, acentos ou compositor proporcional

### Sistema de transicoes contextualizadas canonizado (2026-04-21)
- Criado `doc/03_art/14_contextual_scene_transition_system.md` como doutrina principal de `S3.4 Scene Transition Design`.
- `scene_transition_card` passa a ser o artefato canonico para troca de cena, zona, ato, menu, cutscene ou estado visual com peso dramatico/tecnico.
- `scene_transition_card` permanece separado de `ui_decision_card`, mas deve referenciar UI quando a transicao tocar HUD, menu, title, overlay ou texto critico.
- Classes canonicas registradas: `palette_fade_bridge`, `spatial_scroll_bridge`, `scripted_avatar_bridge`, `tile_mask_mosaic_transition`, `raster_distortion_bridge`, `lighting_state_transition`, `pseudo3d_perspective_bridge` e `meta_cut_bridge`.
- Pipeline, workflows, frontdoor tecnico, registry de engine patterns, registry de maestria 16-bit e contracts das skills foram alinhados ao novo contrato.
- Decisao consolidada:
  - fade preto generico deixa de ser reflexo default; fallback seguro e `palette_fade_bridge` contextualizado
  - H-Int, palette split, wobble, pseudo-3D, tile mutation e audio fade so entram com owner unico, budget, reset simetrico e fallback
  - status inicial e `INCORPORADO` em doutrina e `NAO_INICIADA` em runtime proof ate existir benchmark em BlastEm

### Roadmap de proficiencia AAA do agente canonizado (2026-04-21)
- O roadmap oficial de proficiencia AAA do agente passa a viver em quatro fontes sincronizadas:
  - `doc/03_art/AAA_SKILL_CURATION_STATUS.md` como placar executivo
  - `doc/05_technical/93_16bit_hardware_mastery_matrix.md` como mapa humano
  - `doc/05_technical/93_16bit_hardware_mastery_registry.json` como registry machine-readable
  - `doc/05_technical/94_16bit_hardware_mastery_roadmap.md` como ordem de execucao
- Menu, fontes, HUD/UI e transicoes ja tem doutrina canonizada, mas continuam sem equivaler a runtime proof completo.
- Raster/luz/feedback FX, boss/setpieces, tilemap avancado e audio senior tambem passam a ter doutrina canonizada por `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`.
- Proxima lacuna prioritaria:
  - prova runtime de `P0 Raster + Lighting + Feedback FX` no `BENCHMARK_VISUAL_LAB`
- Ordem consolidada de proficiencia:
  1. `aaa_agent_proficiency_roadmap`
  2. `feedback_fx_decision_system`
  3. `boss_setpiece_design`
  4. `advanced_tilemap_design`
  5. `xgm2_audio_architecture`
  6. kinematics e experimentos especiais
- Regra consolidada:
  - `INCORPORADO` em doutrina nao significa `VALIDADA_EM_ROM`
  - nenhuma tecnica vira default AAA sem benchmark em BlastEm, budget aprovado e evidencia rastreavel

### Reorganização do Workspace
- **Backup completo:** Criado `archives/backup_pre_reorg_2026/` com cópia de doc/, SGDK_projects/, SGDK_Engines/, assets/, tmp/.
- **Renomeações:** `Assets and Sprites/` → `assets/`; `tmp/` → `.tmp/`.
- **Consolidação de scripts:** Scripts raiz (new-project.bat, setup-env.bat, etc.) movidos para `scripts/`.
- **Organização de logs:** Logs temporários em `doc/` movidos para `doc/logs/` e arquivados em `archives/logs_build_2026/`.
- **Limpeza de arquivos soltos:** Scripts avulsos em `SGDK_Engines/` movidos para `tools/maintenance/`.
- **Estrutura atualizada:** README.md raiz atualizado para refletir nova organização.
- **Validação:** Builds testados; resource validation OK (0 erros).

### Bateria grep/read_file — confirmação de implementações

**Símbolos pesquisados:**

| Símbolo | Resultado | Localização |
|---------|-----------|-------------|
| **SceneLayer** | Não encontrado | 0 ocorrências no repositório |
| **CollisionMap** | Encontrado (várias variantes) | Ver tabela abaixo |
| **sgdk_emitter** | Não encontrado em código SGDK | Apenas em Godot/Freetype/Aseprite (externos) |

**Implementações de colisão:**

| Projeto | Implementação | Trecho relevante |
|---------|---------------|------------------|
| **Shadow Dancer Hamoopig** | `collisionMatrix[TOTAL_MAP_BOXES][5]`, `collisionMatrixB` | Caixas [x1,y1,x2,y2,plano]; `CHECK_COLLISION` + `COLLISION_HANDLING`; `playerLayer` para planos |
| **PlatformerEngine Toolkit** | `generateCollisionMap()`, `freeCollisionMap()` | `levelgenerator.c/h` — mapa u8[][] 48 colunas |
| **Example Platformer** | `collision_map1[1182]` | Tile-based; `collision.h` |
| **Platformer 2** | `collision_mapa2[3584]` | Tile-based; `mapa2.h` |
| **Mega Metroid** | `curr_collision_map` | `types.h` — conversão para array 2D |
| **PlatformerStudio** | `collisionMap1..126` (símbolos exportados) | Godot → SGDK export |

**Trecho importante — Shadow Dancer (main.c ~1856–1867):**
```c
// MAP PLANE A — colisão com caixas do cenário
if(( CHECK_COLLISION(P[1].x-8, P[1].y-32, P[1].x+8, P[1].y,
    collisionMatrix[i][0], collisionMatrix[i][1], collisionMatrix[i][2], collisionMatrix[i][3])==1 && collisionTest==1)
   && enableTestCollision==TRUE)
{
    if(P[1].playerLayer==collisionMatrix[i][4])
    {
        COLLISION_HANDLING(1, collisionMatrix[i][0], collisionMatrix[i][1], collisionMatrix[i][2], collisionMatrix[i][3]);
        collisionTest=0;
    }
}
```

### Documentos criados nesta sessão
- `doc/06_AI_MEMORY_BANK.md` — este arquivo (memory bank global).
- `doc/QA_CHECKLIST_ROTEIRO.md` — roteiro QA passo-a-passo e checklist de evidências para RC.

---

## 3. PRÓXIMO PASSO IMEDIATO

1. Rodar `build.bat` em um projeto alvo (ex.: Shadow Dancer ou Pequeno Príncipe) e validar ROM no emulador.
2. Executar `validate_resources.ps1` em projetos com recursos (res/) para checagem pré-build.
3. Seguir roteiro em `doc/QA_CHECKLIST_ROTEIRO.md` para testes manuais e coleta de evidências RC.

---

## 4. DECISÕES CONSOLIDADAS (NÃO ALTERAR SEM ORDEM EXPRESSA)

| Decisão | Razão |
|---------|-------|
| Wrapper em `tools/sgdk_wrapper/` é única fonte de build | Evitar duplicação e inconsistência |
| Projetos delegam via `call "..\..\tools\sgdk_wrapper\build.bat" "%~dp0"` | Padronização e automação |
| Documentação em `doc/` (não `docs/`) | Convenção do repositório |
| Shadow Dancer usa collisionMatrix (caixas AABB), não tile-based | Arquitetura original do engine |

---

## 5. RISCOS CONHECIDOS

| Risco | Mitigação |
|-------|-----------|
| Grep em repositório grande pode dar timeout | Restringir path (ex.: SGDK_Engines, projeto específico) |
| Scripts de validação exigem Java, ImageMagick, SGDK | Documentar dependências em README do wrapper |
| `SceneLayer` e `sgdk_emitter` não existem no codebase | Não são APIs do SGDK; usar nomenclatura existente |

---

## 6. REFERÊNCIAS RÁPIDAS

| O que você precisa | Arquivo |
|--------------------|---------|
| Diretrizes para agentes | `doc/AGENTS.md` |
| Índice da documentação | `doc/README.md` |
| Wrapper e build | `tools/sgdk_wrapper/README.md` |
| Roteiro QA e evidências RC | `doc/QA_CHECKLIST_ROTEIRO.md` |
| Memory Bank Pequeno Príncipe | `SGDK_projects/.../doc/10-memory-bank.md` |
