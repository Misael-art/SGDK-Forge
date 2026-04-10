# 09 - Checklist Anti-Alucinacao e Gates

**Status:** Definitivo

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
| 4 | Tipos corretos: `u8`, `u16`, `s16`, `u32`, `fix16`, `fix32` | Sem `int`, `long`, `char` (exceto strings literais) |
| 5 | DMA total da cena dentro do budget | Calcular e comparar com `doc/13-spec-cenas.md` |
| 6 | Sprites de hardware dentro do limite | Contar todos os `VDP_setSprite*` e meta-sprites |
| 7 | H-Int so em `hint_manager.c` | `grep -rn "SYS_setHIntCallback" src/` deve apontar SOMENTE para hint_manager.c |
| 8 | Nenhuma API deprecada do SGDK 1.60 | Sem `VDP_setPalette`, `VDP_setPaletteColors`, `SPR_addSpriteEx` com 6 args |

---

## 3. GATE DE DESIGN: COERENCIA COM O JOGO

| # | Verificacao |
|---|-------------|
| 1 | A mudanca respeita os pilares de design (sem morte, sem timer, sem inimigos, sem coleta)? |
| 2 | Os dialogos alterados estao em `doc/12-roteiro.md` ANTES de ir para o codigo? |
| 3 | O tom do speaker esta correto (Rosa=intima, Rei=cerimonioso, Acendedor=ritmico, Vento=impessoal)? |
| 4 | Nenhum dialogo tem mais de 4 linhas? |
| 5 | Nenhum dialogo contem termos tecnicos (exceto codex)? |
| 6 | A progressao continua linear e sem backtracking? |
| 7 | Nenhuma mecanica nova foi adicionada sem estar no GDD? |

---

## 4. GATE DE BUILD: COMPILACAO E EXECUCAO

| # | Verificacao | Comando |
|---|-------------|---------|
| 1 | Compila sem erro | `build.bat` retorna sem erro |
| 2 | ROM gerada | `out/rom.bin` existe e tem tamanho > 0 |
| 3 | ROM roda em emulador | Abrir em Blastem/Gens/Kega, chegar ao title screen |
| 4 | Cena afetada acessivel | Navegar ate a cena alterada e observar |
| 5 | Sem tearing visivel | Observar por 10 segundos sem glitch |
| 6 | Sem sprite overflow visivel | Sprites nao desaparecem em nenhuma scanline |
| 7 | 60fps mantidos | Sem slowdown perceptivel |

---

## 5. GATE DE DOCUMENTACAO: COERENCIA

| # | Verificacao |
|---|-------------|
| 1 | `doc/10-memory-bank.md` foi atualizado com o que mudou? |
| 2 | Se budget mudou, `doc/13-spec-cenas.md` foi atualizado? |
| 3 | Se dialogo mudou, `doc/12-roteiro.md` esta sincronizado com o codigo? |
| 4 | Nenhum documento canonico ficou em conflito com o estado real? |

---

## 6. LISTA DE ALUCINACOES COMUNS DE IAs NESTE PROJETO

| Alucinacao | Realidade |
|------------|-----------|
| "Vou usar alpha blending" | Mega Drive nao tem alpha. Hilight/Shadow e o maximo |
| "Vou criar um terceiro plano de background" | Sao 2 planes (BG_A + BG_B) + window. Ponto. |
| "Vou usar sprites para texto" | Use tilemap ou window plane. Sprites sao escassos |
| "Vou alocar um buffer por frame" | Sem malloc no loop. Buffers sao estaticos |
| "Vou adicionar fade com gradiente suave" | 61 cores simultaneas. Fade e por paleta inteira |
| "Vou usar DMA durante active display" | DMA so e seguro no VBlank (ou H-blank com cuidado extremo) |
| "Vou criar uma funcao de 200 linhas no main" | Main tem 10 linhas. Logica vai nos modulos |
| "O SGDK tem funcao X" (inventada) | Verificar documentacao oficial. Se nao existe, nao usar |
| "Vou mudar a resolucao para 256x224" | O slice e 320x224. Nao mudar. |
| "Vou adicionar scroll vertical" | O slice e horizontal. Scroll vertical so para column scroll parcial |
| "Vou usar `int` em vez de `u16`" | `int` pode ser 32 bits no GCC do SGDK. Usar tipos explicitos |

---

## 7. REGRA FINAL

Se voce nao consegue explicar em uma frase:
- **O que** esta mudando
- **Por que** o hardware suporta
- **Onde** isso esta documentado

...entao a mudanca nao esta pronta para ser implementada.
