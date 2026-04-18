# 10 - Memory Bank & Context Tracker

**Ultima atualizacao:** 2026-03-16
**Fase atual:** Fase 2 (Loop Autonomo) — arquitetura expandida para 12 planetas + 11 viagens
**Proxima fase:** Implementar Viagem D (Arco-Iris) conforme doc/14-spec-travel.md

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona
- Vertical slice jogavel (baseline) com 4 micro-planetas: B-612, Rei, Lampiao, Deserto.
- State machine com 8 estados: boot, title, story, planet, travel, pause, codex, credits.
- Player com fisica em fix16/fix32, pulo, planar, cachecol segmentado.
- Dialogos em window plane com speaker e linhas de texto.
- Efeitos visuais por planeta: line scroll, column scroll, H-Int split, hilight/shadow, palette cycling.
- Assets reais via rescomp: 4 tilesets de marcos, paleta de sprites, 8 WAVs (4 vozes + 4 SFX).
- HUD com nome do planeta, objetivo e indicador de efeito.
- Codex tecnico desbloquavel por planeta.
- Build funcional via wrapper canonico.

### O que e placeholder
- Tiles do cenario sao gerados por codigo (procedurais), nao vem de assets.
- Player e desenhado com tiles procedurais (6 tiles), nao e sprite de rescomp.
- Cachecol usa tiles procedurais.
- Halo usa tile procedural.
- Telas de titulo, story, credits usam texto e tiles procedurais.
- Travel usa rendering procedural de circulos e estrelas.

### O que falta para o slice ser completo
- Integracao e verificacao de budgets apos entrada de assets finais (seguir `doc/21-plano-verificacao-budgets.md`).
- BGM (atualmente sem musica de fundo) e SFX de ambiente.
- Assets finais de arte (sprites, tilemaps, backgrounds).
- Teste sistematico em emulador real ou hardware.

### Metricas de codigo
- ~2770 linhas C total (10 arquivos .c + 1 .h).
- 27 tiles procedurais + 16 tiles de rescomp.
- 4 paletas x 2 (pal0/pal1) por planeta = 8 paletas definidas.
- 8 sprites de hardware reservados (PP_HW_SPRITES).

---

## 2. O QUE ACABOU DE ACONTECER

**2026-03-15 — Sessao de fundamentacao documental**
- Criada infraestrutura de governanca: `AGENTS.md`, `doc/00-diretrizes-agente.md`, `doc/10-memory-bank.md`.
- Criados documentos de design: `doc/11-gdd.md`, `doc/12-roteiro.md`, `doc/13-spec-cenas.md`.
- Reescrito `doc/09-checklist-anti-alucinacao.md` com gates reais.
- Atualizado `doc/README.md` com hierarquia de leitura.
- Nenhum codigo C foi alterado nesta sessao.

**2026-03-15 — Expansao do jogo completo (viagens jogaveis)**
- GDD expandido para v2.0: 12 planetas/locais + 11 viagens jogaveis com gameplay unico.
- Criado `doc/14-spec-travel.md` com especificacao tecnica detalhada de cada viagem:
  - Budget de VRAM, DMA, sprites, CPU por viagem.
  - Arquitetura de engine por tipo de gameplay (pseudo-3D, shmup, plataforma, etc.).
  - Mapeamento de virtudes por mecanica.
  - Ordem de implementacao sugerida por risco.
- Roteiro expandido para v2.0: dialogos para 12 planetas + textos de abertura/chegada para 11 viagens.
- Codex expandido: 23 entradas (12 planetas + 11 viagens).
- Novos planetas: Vaidoso, Bebado, Homem de Negocios, Geografo, Serpente, Jardim das Rosas, Poco no Deserto, B-612 retorno.
- Viagens mapeadas a tecnicas: Panorama Cotton, Thunder Force IV, M.U.S.H.A., Space Megaforce, Mickey Mania (2 cenas), Vectorman, Batman & Robin, Gunstar Heroes, Castlevania Bloodlines, Red Zone.
- Nenhum codigo C foi alterado nesta sessao.

**2026-03-16 — Fase 1: Auditoria e Revisao de Placeholders**
- Criada auditoria completa em `doc/16-auditoria-placeholders-assets.md`: mapeamento de todos os tiles procedurais e assets reais por cena.
- Criada matriz de assets em `doc/16-matriz-assets-graficos.md`: referencia rapida de sprites e TILESETs por cena.
- Definidas especificacoes do sprite do player em `doc/17-spec-sprite-player.md`: tamanhos, animacoes, paleta, orcamento DMA (planetas e viagens).
- Definidas especificacoes de TILESETs dos 4 planetas em `doc/18-spec-tilesets-planetas.md`: B-612, Rei, Lampiao, Deserto, alinhadas aos budgets.
- Definidas especificacoes de TILESETs para Travel e UI em `doc/19-spec-tilesets-ui-travel.md`.
- Desenhada estrategia de integracao em `doc/20-estrategia-integracao-assets.md`: Render_init, Planet_draw, Player_render, resources.res, project.h.
- Criado plano de verificacao de budgets em `doc/21-plano-verificacao-budgets.md`: criterios de sucesso e recuo para VRAM, DMA e sprites.
- Nenhum codigo C foi alterado; arte ainda nao produzida. Proximo passo: produzir assets conforme specs e integrar.

---

## 3. PROXIMO PASSO IMEDIATO

1. Rodar `build.bat` e validar compilacao e execucao no emulador.
2. Implementar Viagem D (Arco-Iris) conforme doc/14-spec-travel.md — vertical contemplativo, palette cycling, particulas com flickering.
3. Seguir ordem de risco: E, C, B, A, I, G, J, F, H, K.
4. Produzir assets conforme specs (doc/17, 18, 19) para os 4 planetas originais e viagens.

---

## 3.1. O QUE FOI IMPLEMENTADO (2026-03-16 — Fase 2)

### Arquitetura expandida
- **inc/project.h:** `PlanetId` expandido para 12 (B612, Rei, Vaidoso, Bebado, Homem Neg, Acendedor, Geografo, Serpente, Deserto, Jardim, Poco, B612 retorno). `TravelId` para 11 (A–K). `GameContext.currentTravel` adicionado. Prototipos `Travel_update`, `Travel_draw`, `Travel_getFromPlanets`.
- **src/game/travel.c:** Novo modulo com `Travel_getFromPlanets(from, to)` mapeando pares de planetas para viagens, e `Travel_update` com logica de transicao (frame, radius, completion) delegada do flow.
- **src/states/flow.c:** `States_getNextPlanet` atualizado para fluxo completo de 12 planetas. `States_enter(TRAVEL)` define `currentTravel`. `States_updateTravel` delega a `Travel_update`.
- **src/game/planets.c:** Renomeados `PLANET_LAMPLIGHTER` → `PLANET_ACENDEDOR`, `PLANET_DESERT` → `PLANET_DESERTO`. Adicionados 8 novos planetas com cenas placeholder (Vaidoso, Bebado, Homem Neg, Geografo, Serpente, Jardim, Poco, B-612 retorno). Dialogos e codex conforme doc/12-roteiro.md. Proximos destinos corrigidos (King→Vaidoso, Acendedor→Geografo, Deserto→Jardim).
- **src/game/player.c:** `Player_getGround`, `Player_getLandmarkSprite`, `Player_reset` atualizados para os 12 planetas.
- **src/audio/audio.c:** Referencias atualizadas para `PLANET_ACENDEDOR` e `PLANET_DESERTO`.
- **src/render/render.c:** `gPlanetShortLabels` expandido para 12. `Render_drawOrbitMap` com 12 posicoes e labels abreviados. Codex com loop seguro por `codexLineCount`.

### Decisao conservadora
- Novos planetas usam visual placeholder (Desert-style: sky + dunes) para garantir estabilidade. Arte especifica sera integrada em ciclo posterior.

---

## 4. DECISOES CONSOLIDADAS (NAO ALTERAR SEM ORDEM EXPRESSA)

| Decisao | Razao |
|---------|-------|
| Placeholders sao gerados por codigo, nao por assets dummy | Destravar engenharia sem depender de arte |
| Window plane para dialogos | Nao sofre scroll, garante legibilidade |
| H-Int centralizado em `hint_manager.c` | Um unico ponto de controle para raster |
| Cachecol com 5 segmentos em sinFix16 | Compromisso entre visual e CPU |
| 8 sprites de hardware reservados | Budget conservador para o slice |
| Efeitos visuais diferentes por planeta | Cada planeta e aula de uma tecnica |
| State machine em `flow.c` com enum | Simples, debugavel, sem overhead |
| Fix16/fix32 para toda fisica | Sem FPU no 68000 |

---

## 5. RISCOS CONHECIDOS

| Risco | Mitigacao |
|-------|-----------|
| DMA budget apertado no B-612 (palette cycling + line scroll + hilight) | Budget formal em `doc/13-spec-cenas.md`; medir com Blastem debugger |
| H-Int no Lampiao pode conflitar com sprite DMA | Split line posicionada abaixo da area de sprites ativos |
| Tiles procedurais dificultam teste visual de budget real | Priorizar troca para assets reais no proximo ciclo |
| Dialogos longos podem ultrapassar window plane | Roteiro limita a 4 linhas por encontro |
| Sem BGM, teste de timing de audio esta incompleto | Adicionar BGM placeholder antes de integrar SFX finais |
