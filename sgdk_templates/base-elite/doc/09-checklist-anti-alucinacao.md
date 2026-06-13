# 09 - Checklist Anti-Alucinacao e Gates — __PROJECT_NAME__

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

## 5. LISTA DE ALUCINACOES COMUNS DE IAs

| Alucinacao | Realidade |
|------------|-----------|
| "Vou usar alpha blending" | Mega Drive nao tem alpha. Hilight/Shadow e o maximo |
| "malloc para alocar sprites" | Usar arrays estaticos ou pools pre-alocados |
| "float para fisica" | Usar fix16/fix32 |
| "Vou adicionar SDL" | SGDK e o unico stack aprovado |
