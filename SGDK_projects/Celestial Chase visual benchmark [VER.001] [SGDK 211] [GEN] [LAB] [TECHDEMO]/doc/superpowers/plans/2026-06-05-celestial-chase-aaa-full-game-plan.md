# Celestial Chase (1 fase AAA + Endless) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar “jogo completo” como **1 fase AAA** (vertical slice) + **modo endless** com score/highscore, com ROM validada, evidência BlastEm rastreável e documentação sincronizada.

**Architecture:** Reusar a arquitetura de cenas já existente (`BRANDING -> BOOT -> MENU -> CHASE -> RESULT`) e expandir `CHASE` para suportar dois modos (Run 75s e Endless) via estado global simples + regras determinísticas. Manter gates canônicos (build/validation/BlastEm/regressão/VLAB/VRAM/DMA).

**Tech Stack:** SGDK 2.11, C (68000), XGM2, SRam handshake (`MDRT/READY/VLAB`), wrapper `tools/sgdk_wrapper/*`.

---

## Escopo Formal (fechado)

- **Conteúdo do “jogo completo”**: 1 fase AAA + modo endless (sem múltiplas fases).
- **Arte**: baseline v011 + rework seletivo; sem “gráfico baixo nível” aceito como final.
- **Áudio**: recomposição do zero em WAV → XGM2.
  - **Bloqueio não-negociável**: WAVs AAA autorais exigem criação humana (compositor/sound designer) ou fornecimento externo. Este plano implementa a **arquitetura + integração + budgets + gates**; a entrega `creative_ready` só sobe quando os WAVs finais existirem e forem aprovados.

---

## Task 1: Formalizar “modo de jogo” (Run vs Endless) e fluxo de menu

**Files:**
- Modify: inc/game_vars.h
- Modify: src/scenes/scene_menu.c
- Modify: src/scenes/scene_chase.c
- Test: data/builders/tests/test_chase_v011_runtime_contract.py

- [ ] **Step 1: Adicionar enum de modo em `game_vars.h`**

```c
typedef enum ChaseMode {
    CHASE_MODE_RUN = 0,
    CHASE_MODE_ENDLESS = 1
} ChaseMode;
```

- [ ] **Step 2: Adicionar `gApp.chaseMode` em `AppState`**

```c
typedef struct AppState {
    AppScene currentScene;
    AppScene previousScene;
    AppScene transitionTarget;
    u32 totalFrames;
    u16 sceneFrames;
    u8 transitionFrames;
    u16 targetFps;
    AppRegion region;
    bool sceneNeedsEnter;
    bool showDebugHud;
    bool paused;
    ChaseMode chaseMode;
} AppState;
```

- [ ] **Step 3: Set default em `APP_boot()`**

Em `src/core/app.c` (`APP_boot`), adicionar:

```c
gApp.chaseMode = CHASE_MODE_RUN;
```

- [ ] **Step 4: Transformar MENU em seletor de modo (Run/Endless)**

Implementar cursor simples de 2 itens em `src/scenes/scene_menu.c` (sem HUD de debug), onde:
- `UP/DOWN` alterna `gApp.chaseMode`
- `A/START` inicia CHASE com o modo escolhido
- `B` volta para BOOT

- [ ] **Step 5: CHASE respeita o modo escolhido**

Em `src/scenes/scene_chase.c`, trocar:

```c
CHASE_RULES_reset(&sRules, gApp.targetFps);
```

por:

```c
CHASE_RULES_reset(&sRules, gApp.targetFps, gApp.chaseMode);
```

- [ ] **Step 6: Rodar testes do projeto**

Run:

```powershell
py .\SGDK_projects\Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]\data\builders\tests\test_chase_v011_runtime_contract.py
```

Expected: PASS

---

## Task 2: Regras do modo Endless (score + dificuldade + condição de fim)

**Files:**
- Modify: inc/gameplay/chase_rules.h
- Modify: src/gameplay/chase_rules.c

- [ ] **Step 1: Estender API do reset**

```c
void CHASE_RULES_reset(ChaseRulesState* state, u16 targetFps, ChaseMode mode);
```

- [ ] **Step 2: Estender estado com score/dificuldade**

Em `ChaseRulesState`, adicionar:

```c
ChaseMode mode;
u32 score;
u16 difficulty;
```

- [ ] **Step 3: Semântica do Endless**

Implementar as regras:
- `mode == CHASE_MODE_RUN`: mantém `roundLength=targetFps*75`
- `mode == CHASE_MODE_ENDLESS`: `roundLength=0` e **não** usa vitória por tempo; vitória fica desativada
- Score:
  - +1 por frame vivo
  - +`energy`/pickup: +25 score (alinha com energia)
  - +Pulse usado: +50 score
- Difficulty:
  - cresce a cada 10s: `difficulty++`
  - impacta `pressurePeriod` reduzindo intervalo mínimo até `targetFps/2`

- [ ] **Step 4: Condição de fim no Endless**

No endless, fim ocorre apenas por falha (integrity==0 ou pressure==100).

- [ ] **Step 5: Rodar build**

Run:

```powershell
.\SGDK_projects\Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]\build.bat
```

Expected: sucesso e `out/rom.bin` gerado

---

## Task 3: HUD e tela de resultado suportam Endless (score + highscore)

**Files:**
- Modify: src/gameplay/chase_hud.c
- Create: `inc/system/save_data.h`
- Create: `src/system/save_data.c`
- Modify: src/scenes/scene_chase.c

- [ ] **Step 1: Implementar save data em SRAM sem colidir com MDRT/READY/VLAB**

Reservar offset **0x600**:
- `MDRT`: 0x000
- `READY`: 0x100
- `SBIS`: 0x120
- `VLAB`: 0x200
- `SAVE`: 0x600 (novo)

Formato (big-endian):
- magic `"CCSV"`
- version u16 = 1
- length u16
- highscore_endless u32

- [ ] **Step 2: Atualizar result screen**

Em `CHASE_HUD_showResult`:
- Se `CHASE_MODE_ENDLESS`, mostrar `SCORE` e `HIGHSCORE`
- Se `CHASE_MODE_RUN`, manter a mensagem atual e incluir `SCORE` como extra

- [ ] **Step 3: Atualizar HUD durante gameplay**

Em `CHASE_HUD_update`:
- Se `CHASE_MODE_ENDLESS`: trocar `secondsLeft` por `timeSurvived` e mostrar `SCORE:%06lu`
- Se `CHASE_MODE_RUN`: manter contador regressivo

- [ ] **Step 4: Persistir highscore no fim de uma run endless**

Em `chaseHandleResult()` em `src/scenes/scene_chase.c`:
- ler highscore atual
- se `rules->score > highscore`, gravar novo

---

## Task 4: “AAA feel” sem trapacear: impacto, peso e leituras

**Files:**
- Modify: src/scenes/scene_chase.c
- Modify: `src/gameplay/chase_pursuer.c`
- Modify: `src/gameplay/chase_player.c`

- [ ] **Step 1: Padronizar hitstop (máximo 6 frames) e shake (máximo 5 frames)**
- [ ] **Step 2: Garantir que todo FX tenha consequência mecânica**
  - dano: hitstop + shake + afterimage + cue
  - pulse: limpeza + highlight/shadow + cue
- [ ] **Step 3: Aumentar fluidez do Perseguidor via suporte a mais frames**
  - Implementar suporte no runtime para strips maiores (sem assumir que os frames existem ainda)
  - A promoção de novos frames só entra quando houver arte source-baked aprovada

---

## Task 5: Áudio (arquitetura + integração) — pronto para WAVs AAA

**Files:**
- Modify: src/system/audio.c
- Modify: inc/system/audio.h
- Modify: res/resources.res

- [ ] **Step 1: Definir estados musicais**
  - `intro`, `pressure`, `climax`, `result_victory`, `result_failure`, `menu`
- [ ] **Step 2: Alocar canais PCM com ownership fixo**
  - CH1: música base/loop
  - CH2: cues críticos (hit/pulse/victory/failure)
  - CH3: UI/movimento/pickups
- [ ] **Step 3: Integrar WAVs quando existirem**
  - adicionar recursos no `.res`
  - rodar validação de áudio do wrapper (budget + ownership)

---

## Task 6: Gates finais (ROM + BlastEm + relatórios + docs)

**Files:**
- Modify: doc/10-memory-bank.md
- Modify: doc/11-gdd.md
- Modify: doc/13-spec-cenas.md
- Modify: doc/changelog/changelog.md

- [ ] **Step 1: Rodar suíte de gates**

Run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/scene_closeout_gate.ps1 -ProjectRoot "." -SceneId "front_end_main_menu"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/scene_closeout_gate.ps1 -ProjectRoot "." -SceneId "first_playable_slice"
```

Expected: `passed` (ou blockers criativos explicitamente listados, nunca mascarados)

- [ ] **Step 2: Build final e validação**

Run:

```powershell
.\SGDK_projects\Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]\build.bat
```

Expected: `out/rom.bin` existe

- [ ] **Step 3: BlastEm evidência canônica**
  - screenshot dedicado
  - `save.sram`
  - `visual_vdp_dump.bin`

- [ ] **Step 4: Atualizar docs de fechamento**
  - `doc/10-memory-bank.md` com hashes e blockers reais remanescentes
  - `doc/changelog/changelog.md` com build_v### e mudanças

- [ ] **Step 5: Capturar aprendizado local**

Run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/audit_project_learning.ps1 -Mode Capture -ProjectRoot "."
```

---

## Execução

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** — despacho um subagente por task, reviso entre tasks
2. **Inline Execution** — executo task-a-task aqui usando executing-plans, com checkpoints

Escolha 1 ou 2.
