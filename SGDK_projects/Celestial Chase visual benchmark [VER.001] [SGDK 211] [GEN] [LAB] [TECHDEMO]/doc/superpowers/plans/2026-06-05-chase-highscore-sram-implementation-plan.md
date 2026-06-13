# Highscore Endless em SRAM (CCSV v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persistir e exibir highscore do modo Endless usando SRAM offset `0x600` com schema `CCSV v1`.

**Architecture:** Um módulo `system/save_data` cacheia o highscore em RAM e expõe uma API mínima para leitura/submissão no Result. A cena Chase inicializa o módulo no Enter e, no Result, submete o score do Endless e repassa `score/highscore/new_record` para o HUD. O HUD mostra `SCORE/HI` durante gameplay Endless (linhas 2/3 quando não-cinematic) e `SCORE/HIGH` no Result.

**Tech Stack:** SGDK 2.11 (`sram.h`, `genesis.h`), C, HUD via `WINDOW` (`VDP_drawTextFill`/`VDP_drawText`).

---

### Task 1: Criar módulo de persistência em SRAM (`system/save_data`)

**Files:**
- Create: `inc/system/save_data.h`
- Create: `src/system/save_data.c`

- [ ] **Step 1: Definir o contrato público em `save_data.h`**

```c
#ifndef SYSTEM_SAVE_DATA_H
#define SYSTEM_SAVE_DATA_H

#include <genesis.h>

#define SAVE_DATA_SRAM_OFFSET 0x600

void SAVE_DATA_init(void);
u32 SAVE_DATA_highscore(void);
bool SAVE_DATA_trySubmitEndlessScore(u32 score);

#endif
```

- [ ] **Step 2: Implementar leitura/gravação `CCSV v1` em `save_data.c`**

Regras:
- Ler magic `CCSV` + `u16be version==1` + `u32be highscore` em `SAVE_DATA_init`.
- Se inválido, cache = `0`.
- `SAVE_DATA_trySubmitEndlessScore`: grava apenas se `score > cached`.

```c
#include <genesis.h>

#include "system/save_data.h"

#define SAVE_DATA_SCHEMA_VERSION 1

static u32 sHighscore;
static bool sInitialized;

static u16 read_u16be(u32 offset);
static u32 read_u32be(u32 offset);
static void write_u16be(u32 offset, u16 value);
static void write_u32be(u32 offset, u32 value);

void SAVE_DATA_init(void);
u32 SAVE_DATA_highscore(void);
bool SAVE_DATA_trySubmitEndlessScore(u32 score);
```

- [ ] **Step 3: Build para validar includes e link**

Rodar build do projeto pelo wrapper (ver `build.bat` do projeto).
Esperado: `out/rom.bin` gerado sem erros.

---

### Task 2: Integrar no fluxo de Result e expor ao HUD

**Files:**
- Modify: `src/scenes/scene_chase.c`
- Modify: `inc/gameplay/chase_hud.h`
- Modify: `src/gameplay/chase_hud.c`

- [ ] **Step 1: Incluir `save_data.h` e inicializar em `SCENE_chaseEnter`**

Em `SCENE_chaseEnter`:
- chamar `SAVE_DATA_init()` antes de `CHASE_HUD_enter()`/`CHASE_HUD_update()` para HUD ter `HI`.

- [ ] **Step 2: Atualizar a assinatura do Result HUD para receber score/highscore/new_record**

Alterar `CHASE_HUD_showResult` para:

```c
void CHASE_HUD_showResult(const ChaseRulesState* rules, u32 score, u32 highscore, bool newRecord);
```

- [ ] **Step 3: No Result, submeter score Endless e calcular `newRecord`**

Em `chaseHandleResult`:
- `u32 score = (rules->mode == CHASE_MODE_ENDLESS) ? rules->score : 0;`
- `u32 oldHigh = SAVE_DATA_highscore();`
- se Endless: `bool newRecord = SAVE_DATA_trySubmitEndlessScore(score);`
- `u32 high = SAVE_DATA_highscore();`
- chamar `CHASE_HUD_showResult(&sRules, score, high, newRecord);`

- [ ] **Step 4: Gameplay HUD Endless**

Em `CHASE_HUD_update`:
- Quando `rules->mode == CHASE_MODE_ENDLESS` e `!sCinematic`:
  - linha 2: `SCORE:%lu`
  - linha 3: `HI:%lu`
- Quando não for Endless e `!sCinematic`: limpar linhas 2/3.

---

### Task 3: Evidência e validação (build + testes + BlastEm canônico)

**Files:**
- Output: `out/rom.bin`
- Output: pasta `out/evidence/...` do BlastEm (screenshot, save.sram, visual_vdp_dump.bin)

- [ ] **Step 1: Rodar suite de testes do projeto**

Rodar o comando de testes existente (ver `data/builders/tests/`).
Esperado: PASS.

- [ ] **Step 2: Rodar BlastEm canônico via wrapper e capturar evidência**

Usar o runner canônico do wrapper (ex.: `tools/sgdk_wrapper/run_visual_capture.ps1` ou equivalente do projeto) para capturar:
- `screenshot.png`
- `save.sram`
- `visual_vdp_dump.bin`

Critério:
- `save.sram` contém `CCSV` em `0x600` e highscore esperado persistido após fechar uma run Endless e reiniciar.

- [ ] **Step 3: Registrar paths e hashes da evidência**

Listar no fechamento:
- paths de arquivos alterados
- paths da evidência gerada
- SHA256 de `out/rom.bin` e, se aplicável, de `save.sram`/`visual_vdp_dump.bin`
