# Sprite AnimationFrame Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminar o `AnimationFrame` invalido no Sector 01 com uma regressao especifica, uma correcao minima em `race_scene.c` e evidencia BlastEm vinculada a uma unica ROM.

**Architecture:** Manter o runtime e os assets atuais. A correcao deve remover a contagem duplicada de frames no caminho de hazards/pickups e usar `SpriteDefinition.animations[0].numFrame`, que e a verdade gerada pelo ResComp. Nenhuma outra mecanica, asset, audio ou cena sera ampliada nesta iteracao.

**Tech Stack:** C SGDK 2.11, ResComp, Python `unittest`, PowerShell, wrapper central SGDK e BlastEm.

---

### Task 1: Congelar baseline e provar a causa

**Files:**
- Inspect: `src/scenes/race_scene.c`
- Inspect: `res/resources.res`
- Inspect: `out/rom.out`
- Inspect: `out/symbol.txt`
- Inspect: `sdk/sgdk-2.11/inc/sprite_eng.h`
- Inspect: `sdk/sgdk-2.11/src/sprite_eng.c`

- [ ] **Step 1: Registrar os valores reais**

Registrar:

```text
spr_lio_all: numAnimation=5, numFrame=[6,6,3,4,2]
spr_lumen_orb: numAnimation=1, numFrame=[3]
spr_low_stone: numAnimation=1, numFrame=[2]
spr_astral_mark: numAnimation=1, numFrame=[3]
spr_beacon_key: numAnimation=1, numFrame=[3]
spr_pursuer_shadow: numAnimation=1, numFrame=[1]
```

- [ ] **Step 2: Confirmar o acesso invalido**

Confirmar que `draw_entities()` seleciona para `spr_lumen_orb`:

```c
u8 num_frames = (e->kind == EV_BEACON_KEY) ? 3 : 4;
u8 frame = (frame_counter / 8) % num_frames;
SPR_setFrame(sp, frame);
```

O indice `3` excede `spr_lumen_orb.animation[0].numFrame == 3`.

### Task 2: Criar regressao vermelha

**Files:**
- Modify: `tools/tests/test_sector01_recovery.py`

- [ ] **Step 1: Adicionar teste de contrato ResComp/runtime**

Adicionar um teste que leia `out/symbol.txt`, confirme tres frames gerados para `spr_lumen_orb_animation0` e exija que `race_scene.c` derive a contagem de `def->animations[0]->numFrame`, sem modulo literal `4` para Lumen.

- [ ] **Step 2: Executar o teste**

Run:

```powershell
py -m unittest tools.tests.test_sector01_recovery.Sector01RecoveryTests.test_lumen_orb_frame_selection_matches_rescomp_definition -v
```

Expected: `FAIL`, porque o runtime atual usa quatro frames.

### Task 3: Aplicar a correcao minima

**Files:**
- Modify: `src/scenes/race_scene.c`

- [ ] **Step 1: Remover a tabela duplicada**

Remover `get_hazard_frames()` e, apos uma definicao de sprite aceita, obter:

```c
const Animation* animation = def->animations[0];
u8 num_frames = animation->numFrame;
u8 frame = (frame_counter / 8) % num_frames;
SPR_setAnimAndFrame(sp, 0, frame);
```

Aplicar o mesmo caminho aos pools de hazard e pickup. Nao alterar assets, timing, colisao, gameplay ou outras cenas.

- [ ] **Step 2: Executar regressao especifica**

Run:

```powershell
py -m unittest tools.tests.test_sector01_recovery.Sector01RecoveryTests.test_lumen_orb_frame_selection_matches_rescomp_definition -v
```

Expected: `PASS`.

- [ ] **Step 3: Executar toda a suite local**

Run:

```powershell
py -m unittest discover -s tools/tests -p "test_*.py" -v
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_sector01_recovery_contracts.ps1 -ProjectRoot .
```

Expected: todos os testes passam; qualquer falha preexistente do contrato PowerShell deve ser reconciliada sem alterar runtime fora da causa confirmada.

### Task 4: Rebuild e validacao

**Files:**
- Verify: `out/rom.bin`
- Verify: `out/rom.out`
- Verify: `out/symbol.txt`
- Verify: `out/logs/validation_report.json`

- [ ] **Step 1: Build pelo wrapper central**

Definir:

```powershell
$env:SGDK_TARGET_BLOCKER = "runtime_address_error_before_closeout"
$env:SGDK_CHANGE_CATEGORY = "runtime"
$env:SGDK_CHANGE_SUMMARY = "Corrigir frame 3 invalido de spr_lumen_orb usando numFrame real do ResComp."
```

Executar o wrapper canonico do projeto.

- [ ] **Step 2: Confirmar ROM e simbolos**

Confirmar build com exit code zero, novo SHA-256 e `spr_lumen_orb_animation0.numFrame == 3`.

- [ ] **Step 3: Rodar validadores e regressao de cena**

Executar validator, freshness, scene regression, code review e closeout aplicaveis sem promover claims visuais ou de audio nao provados.

### Task 5: Captura BlastEm e selo

**Files:**
- Create/refresh: `out/blastem_env_*`
- Refresh: `out/logs/emulator_session.json`
- Refresh: `out/logs/evidence_closeout_report.json`

- [ ] **Step 1: Capturar a rota**

Capturar na mesma ROM:

```text
Title
abertura
inicio da corrida
meio da corrida
Beacon
resultado
retorno ao Title
```

- [ ] **Step 2: Validar claims observados**

Validar VRAM, sprites, HUD/WINDOW, Pulse, Pressure Gate, perseguidor, salto e sucesso/falha. Performance e audio so podem subir de status com evidencia correspondente.

- [ ] **Step 3: Selar evidencia**

Executar `finalize_emulator_evidence.ps1` e confirmar que screenshot(s), `save.sram`, dump aplicavel e ROM possuem hashes coerentes.

### Task 6: Sincronizar documentacao e bloquear expansao

**Files:**
- Modify: `doc/10-memory-bank.md`
- Modify: `doc/changelog/changelog.md`
- Modify: `doc/code_review_report.json`
- Modify: budget/closeout reports aplicaveis

- [ ] **Step 1: Atualizar fatos**

Registrar causa, teste vermelho/verde, SHA-256 da ROM, capturas, SRAM e resultados dos gates.

- [ ] **Step 2: Atualizar budget VDP**

Separar VRAM residente, DMA por frame, sprites totais e pressao por scanline; nao confundir uso total de sprites com scanline.

- [ ] **Step 3: Manter fases posteriores bloqueadas**

Arte definitiva, audio, Upgrade Intermission e Sector 02 permanecem bloqueados ate o closeout do Sector 01 estar selado e sem blocker de runtime.
