# 09 - Checklist Anti-Alucinacao e Gates — BENCHMARK_VISUAL_LAB

**Status:** Template

> Este documento e a ultima linha de defesa antes de codigo entrar no projeto.
> Toda proposta — de agente de IA ou humano — deve passar por estas verificacoes.

---

## 1. GATE ZERO: ANTES DE QUALQUER CODIGO

| # | Pergunta | Se a resposta for NAO |
|---|----------|-----------------------|
| 1 | Li `doc/10-memory-bank.md` e sei onde o projeto parou? | Pare e leia |
| 2 | A tarefa esta prevista no GDD (`doc/11-gdd.md`)? | Pare e consulte o usuario |
| 3 | Sei o budget da cena afetada (`doc/13-spec-cenas.md`)? | Pare e leia |
| 4 | O roteiro permite essa mudanca (`doc/12-roteiro.md`)? | Pare e consulte |
| 5 | Consigo compilar o projeto AGORA, antes de comecar? | Pare e conserte primeiro |

---

## 2. GATE TECNICO: COMPATIBILIDADE COM HARDWARE

| # | Verificacao | Teste |
|---|-------------|-------|
| 1 | Nenhum `float` ou `double` no codigo | `grep -rn "float\|double" src/ inc/` deve retornar vazio |
| 2 | Nenhum `malloc` ou `free` no loop | `grep -rn "malloc\|free\|calloc\|realloc" src/` deve retornar vazio |
| 3 | Nenhuma biblioteca externa ao SGDK | Todos os `#include` apontam para `genesis.h`, `project.h` ou `resources.h` |
| 4 | Tipos corretos: `u8`, `u16`, `s16`, `u32`, `fix16`, `fix32` | Sem `int`, `long` para numeros (exceto strings literais) |
| 5 | DMA total da cena dentro do budget | Calcular e comparar com `doc/13-spec-cenas.md` |
| 6 | Sprites de hardware dentro do limite | Contar todos os meta-sprites |
| 7 | Nenhuma API deprecada do SGDK 1.60 | Sem `VDP_setPalette`, `VDP_setPaletteColors`, `SPR_addSpriteEx` com 6 args |

---

## 3. GATE DE BUILD: COMPILACAO E EXECUCAO

| # | Verificacao | Comando |
|---|-------------|---------|
| 1 | Compila sem erro | `build.bat` retorna sem erro |
| 2 | ROM gerada | `out/rom.bin` existe e tem tamanho > 0 |
| 3 | ROM roda em emulador com evidencia rastreavel | Abrir em BlastEm; usar BizHawk apenas para telemetria complementar |
| 4 | Cena afetada acessivel | Navegar ate a cena alterada e observar |
| 5 | Sem tearing visivel | Observar por 10 segundos sem glitch |
| 6 | Sem sprite overflow visivel | Sprites nao desaparecem em nenhuma scanline |

---

## 4. GATE DE DOCUMENTACAO: COERENCIA

| # | Verificacao |
|---|-------------|
| 1 | `doc/10-memory-bank.md` foi atualizado com o que mudou? |
| 2 | Se budget mudou, `doc/13-spec-cenas.md` foi atualizado? |
| 3 | Nenhum documento canonico ficou em conflito com o estado real? |

---

## 5. GATE DE MAESTRIA 16-BIT

| # | Verificacao | Se a resposta for NAO |
|---|-------------|-----------------------|
| 1 | A tecnica alterada existe em `doc/05_technical/93_16bit_hardware_mastery_registry.json`? | Registrar antes de promover |
| 2 | A cena alterada tem `scene_id` e `budget line` em `doc/13-spec-cenas.md`? | Pare e completar o contrato |
| 3 | A cena alterada declarou `intencao_da_cena`, `signature_moment` e `causa_de_gameplay`? | Nao tratar benchmark como prova dramatica valida |
| 4 | Se houver H-Int, existe `hint_owner` e `hint_callback_contract` explicitos? | Bloquear a promocao ate haver owner unico |
| 5 | A `operational_policy` da tecnica esta declarada? | Pare e classifique como `default_safe`, `advanced_tradeoff`, `special_scene_only` ou `hazardous_experimental` |
| 6 | O `evidence bundle` da tecnica foi capturado? | Nao promover acima de `candidate_with_evidence` |
| 7 | O grupo de regressao da tecnica foi reexecutado? | Tratar como prova incompleta |
| 8 | O novo estado da tecnica foi refletido no registry? | Corrigir tracking antes de encerrar |

## 5.1 GATE ESPECIAL: H-INT, WINDOW E DISPLAY

| # | Verificacao | Se a resposta for NAO |
|---|-------------|-----------------------|
| 1 | So existe um owner ativo para `H-Int` na scene? | Tratar como conflito estrutural |
| 2 | `WINDOW` esta sendo usada como HUD fixo ou esta explicitamente livre para tecnica avancada? | Bloquear a integracao |
| 3 | `window alias` foi separado do uso normal de `WINDOW`? | Reprovar a classificacao da tecnica |
| 4 | `interlaced_448` esta marcado como `special_scene_only` e comparado contra 224p? | Nao promover |
| 5 | `sprite_midframe_sat_reuse` foi tratado como tecnica distinta de multiplex temporal? | Reprovar o laudo tecnico |

## 5.2 GATE ESPECIAL: MUTACAO LOCAL E MICROBUFFER

| # | Verificacao | Se a resposta for NAO |
|---|-------------|-----------------------|
| 1 | `mutable_tile_decal_mutation` declarou `RAM shadow copy` em vez de assumir readback livre de `VRAM`? | Reprovar o desenho tecnico |
| 2 | Existe `mutable tile pool` limitado por sala, setor ou contrato de cena? | Nao promover a tecnica |
| 3 | O budget de `dirty uploads` por quadro foi medido no pior caso? | Bloquear o benchmark |
| 4 | `cellular_microbuffer_sim` esta restrito a ilha pequena com solver local e cadencia explicita? | Tratar como promessa irreal |
| 5 | A tecnica foi descrita como ilusao robusta de hardware, e nao como equivalente literal a pipeline moderno? | Reescrever o laudo antes de promover |

---

## 6. LISTA DE ALUCINACOES COMUNS DE IAs

| Alucinacao | Realidade |
|------------|-----------|
| "Vou usar alpha blending" | Mega Drive nao tem alpha. Hilight/Shadow e o maximo |
| "malloc para alocar sprites" | Usar arrays estaticos ou pools pre-alocados |
| "float para fisica" | Usar fix16/fix32 |
| "Vou adicionar SDL" | SGDK e o unico stack aprovado |

