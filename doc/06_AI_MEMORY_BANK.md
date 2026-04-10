# 06 - AI Memory Bank (MegaDrive_DEV)

**Última atualização:** 2026-04-10  
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
