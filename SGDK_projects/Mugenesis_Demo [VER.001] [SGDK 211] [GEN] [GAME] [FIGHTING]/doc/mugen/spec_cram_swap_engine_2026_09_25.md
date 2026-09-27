# Spec — Motor de swap de CRAM por consumidor (Rota iii / A2)

Data: 2026-09-25 · Branch `feat/mugenesis-impact-fx-v2` · Escopo: Etapa B (base para C/D)
Autor: executor · Status: aguardando revisão humana antes do plano de implementação.

## Contexto e decisão que originou este documento

O mapa de CRAM (`doc/mugen/cram_map_2026_09_25.md`) e a simulação das três rotas
(`doc/mugen/routes_cost_simulation_2026_09_25.md`) mediram o seguinte:

- Pressão de scanline é **invariante** à rota de posse de paleta; o estouro de FX
  (super 28/20 sprites, 832/320 px, 156/80 links) é trabalho de decomposição de sheets
  (B2, com aprovação humana por família), não deste incremento.
- `palette-check` exato: corpo+FX = **23/15 (`over_by 8`)**, `lossless_merges` vazio →
  a rota (ii) (FX nas linhas do corpo) é inviável por número.
- A rota (i) deixa PAL0 em 15/15 e o bgfx-do-super invade stage+HUD → bloqueia Etapa D.
- A rota (iii) mantém FX em PAL3 dedicada, resolve as colisões por **swap pré-declarado
  com save/restore garantido**, sem linha CRAM nova e sem remape lossy.

O usuário escolheu **rota iii**, formato **A2 mínimo**, escopo **"só o motor + retrofit"**.

## Objetivo

Generalizar o mecanismo REGRA 1c que hoje só cobre o flash (`s_flash_tab`) em uma única
primitiva de runtime de swap de CRAM por consumidor, e rotear por ela os dois
consumidores que **já colidem hoje** — flash e bgfx-do-super — **mantendo o resultado
CRAM byte-idêntico** ao comportamento atual. Declarar os ganchos de posse que a Etapa C
(retrato) e a Etapa D (stage/HUD-sob-super) consumirão, **sem** migrar arte nova aqui.

## Não-objetivos (gates explícitos)

- Sem arte nova de famílias FX (B2). Sem decomposição de sheets.
- Sem migrar a arte do retrato para uma linha/subconjunto próprio (é Etapa C, exige
  aprovação por hash). Aqui só se declara o gancho `CRAM_PORTRAIT_*`.
- Sem tocar `res/`, ROM, ou capturas.
- Nenhum commit/merge/promoção sem autorização humana.
- Nenhum waiver, exclusão de recurso ou mudança de assert para tornar o relatório verde.
- Pressão de scanline não é tratada aqui (é invariante à rota).

## Descoberta que limita o retrofit (registrada honestamente)

Corpo usa 14 índices da linha PAL1/PAL2; o retrato usa {1,2,3,4,5,8,11} que **se
sobrepõem** na mesma linha. O flash branqueia PAL1/2[1..15]. Proteger os índices do retrato
dentro do flash deixaria 7 cores do corpo sem flash (flash mais fraco = regressão visual).
Portanto **isolar retrato-vs-flash sem arte nova não é totalmente alcançável**. Este
incremento entrega o *gancho de posse* (`CRAM_PORTRAIT_P1/P2`) e o *motor* que a usará;
a decisão de arte de re-home do retrato fica na Etapa C. Consequência: o retrofit real,
sem arte, é **flash + bgfx-do-super**.

## Arquitetura

### Origem persistente (requisito do diretivo)

Toda a lógica de runtime vive na **fonte do conversor**:
- `tools/mugen2sgdk_forge/runtime/mg_fight.c` (a primitiva + retrofit dos consumidores)
- `tools/mugen2sgdk_forge/runtime/mg_runtime.h` (o tipo `CramConsumer` + constantes de posse)

O projeto recebe a cópia apenas via `install-runtime` (que grava o banner
`/* COPIADO de tools/mugen2sgdk_forge/runtime/<name> (v<TOOL_VERSION>). Edite na fonte. */`).
`TOOL_VERSION` sobe de `0.3.0` → `0.3.1`. Nunca se edita o `src/mg/mg_fight.c` do projeto
como origem; ele é artefato copiado.

### A primitiva

```c
typedef struct {
    u8        line;    /* 0..3 = PAL0..PAL3 */
    u8        lo;      /* primeiro indice [lo..hi] que o consumidor possui */
    u8        hi;      /* ultimo indice (inclusivo) */
    u8        borrow;  /* 1 = nao dono: o motor DEVE salvar em enter e restaurar em exit */
    const u16 *tab;    /* swap pre-declarado (REGRA 1c) ou 0 quando o fonte vem por argumento */
} CramConsumer;

/* Unica porta para escrever CRAM na area de um consumidor. Deriva a base = line*16+lo.
 * So usa PAL_setColors/PAL_getColors com DMA_QUEUE apontando para buffer ESTATICO. */
static void apply_cram_swap(const CramConsumer *c, const u16 *src, u8 n);
static void cram_swap_save(const CramConsumer *c, u16 *dst);   /* PAL_getColors(line*16+lo, dst, hi-lo+1) */
static void cram_swap_restore(const CramConsumer *c, const u16 *saved); /* PAL_setColors(...DMA_QUEUE) */
```

Invariantes garantidas pelo motor:
1. Todo write de CRAM passa por `apply_cram_swap`/`cram_swap_restore` com `base=line*16+lo`
   e `count <= hi-lo+1` → **um consumidor nunca escreve fora da sua faixa declarada**.
2. Consumidor com `borrow=1` **não pode** ser aplicado sem um `save` correspondente em
   escopo aninhado LIFO; a restauração ocorre no mesmo tick de saída **e** é reforçada na
   transição de round/KO (fecha a colisão #6 de forma provável, não incidental).
3. Fontes de `DMA_QUEUE` são sempre buffers estáticos (`s_flash_tab`, `s_pal0_saved`),
   preservando a restrição "DMA lê a fonte no VBlank".

### Constantes de posse (declaradas, parte só ativa neste incremento)

| Constante | line | lo..hi | borrow | Usado agora? |
|---|---|---|---|---|
| `CRAM_STAGE` | 0 | 1..8 | 0 | reservado (D) |
| `CRAM_HUD` | 0 | 9..15 | 0 | reservado (C/D) |
| `CRAM_SUPER_BGFX` | 0 | 1..14 | 1 | **sim** (retrofit) |
| `CRAM_FLASH_P1` | 1 | 1..15 | 0 | **sim** (retrofit) |
| `CRAM_FLASH_P2` | 2 | 1..15 | 0 | **sim** (retrofit) |
| `CRAM_PORTRAIT_P1` | 1 | (definir em C) | 0 | reservado (C) |
| `CRAM_PORTRAIT_P2` | 2 | (definir em C) | 0 | reservado (C) |
| `CRAM_FX` | 3 | 0..15 | 0 | intocado |

Nota: `CRAM_PORTRAIT_*` fica com faixa a definir na C porque hoje compartilha índices com
o corpo; o tipo já expressa "possui um subconjunto da linha" para C preencher.

## Retrofit (comportamento byte-idêntico)

### Flash (`impact_fx_step`)
Hoje: `PAL_setColors(s?33:17, s_flash_tab[s][lvl-2], 15, DMA_QUEUE)`. Passa a ser
`apply_cram_swap(&CRAM_FLASH_Pn, s_flash_tab[s][lvl-2], 15)` (lvl==1 usa `s_basepal[s]+1`).
Mesma linha, mesma faixa, mesma fonte → `host_cram` idêntico quadro a quadro. O
`build_flash_table` permanece inalterado.

### bgfx-do-super (`bgfx_render` / `bgfx_end`)
Hoje: no primeiro frame, `PAL_getColors(0, s_pal0_saved, 16)` e por elemento
`PAL_setColors(1, &fx->pals[k][1], 14, DMA_QUEUE)`; em `bgfx_end`, `PAL_setColors(1, &s_pal0_saved[1], 14, DMA_QUEUE)`.
Passa a: `cram_swap_save(&CRAM_SUPER_BGFX, s_pal0_saved)` na entrada;
`apply_cram_swap(&CRAM_SUPER_BGFX, &fx->pals[k][1], 14)` por elemento;
`cram_swap_restore(&CRAM_SUPER_BGFX, s_pal0_saved)` na saída. **Adição de robustez:** o
motor também restaura `CRAM_SUPER_BGFX` na transição de round/KO se `bgfx_active` estiver
pendente, cobrindo o caso em que hoje a restauração só é segura "porque ainda não há
stage". Nenhum novo write fora de PAL0[1..14].

Nada muda no caminho PAL0 de boot/fundo, no `VDP_setTileMapEx` do super, nem no pool de
explods.

## Fluxo de dados / disciplina de VBlank

Ordem por tick (inalterada): `MG_fightUpdate` → `MG_fightRender` → `host_vblank` (que
consome as filas DMA). Os swaps são enfileirados via `DMA_QUEUE` durante update/render e
materializam só no VBlank. O motor introduz zero alocação dinâmica e zero buffer de pilha
usado como fonte DMA.

## Testes (TDD — vermelho antes do verde)

1. **Host harness `tools/mugen2sgdk_forge/tests/host/impact_fx.c`** (estende, não substitui):
   - Assert novo: `CRAM_SUPER_BGFX` devolve PAL0[1..14] **exato** após KO/troca de round
     mesmo com super pendente (caso que hoje não ocorre naturalmente em CPU x CPU): dirigir
     `bgfx_active=1` + `round_state` mudando, conferir `host_cram[1..14] == iso0`.
   - Assert novo: linhas de `CRAM_PORTRAIT_*` (a faixa reservada documentada) permanecem
     intocadas pelo flash; sem arte de retrato ativa isto é trivialmente verde, mas fixa o
     contrato para C.
   - Os asserts existentes (`bad_flash`, `bad_restore`, `bad_iso`, `bad_round`) devem
     permanecer **zero sem edição** → prova de byte-identidade.
2. **`test_host_runtime.py`**: novo caso que roda o binário do host e exige zero violações +
   os dois asserts novos acima.
3. **`test_palette_contract.py`**: inalterado (gate de orçamento 23/15); a rota iii não o
   muda — só demonstra que ninguém escreve fora da faixa declarada.
4. **Idempotência de reconversão em cópia**: `install-runtime` numa **cópia**, duas vezes;
   comparar por `sha256` o `src/mg/mg_fight.c`/`mg_runtime.h` resultantes (devem ser
   idênticos entre si e ao esperado v0.3.1) e o `doc/asset_provenance_manifest.json`
   (inalterado). Evidência persistida em `rascunho/temporario/`.
5. **Suite completa** do branch ao final: esperado apenas **somar** testes, zero regressão.

## Critério de aceite (Etapa B1→B2 desta rota)

- Motor `CramConsumer` + `apply_cram_swap`/save/restore presentes na **fonte** do conversor,
  `TOOL_VERSION` em `0.3.1`.
- Flash e bgfx-do-super roteados pelo motor com `host_cram` byte-idêntico (asserts
  existentes verdes sem edição) + asserts novos de restauração em KO/round verdes.
- Ganchos `CRAM_STAGE/HUD/PORTRAIT_*` declarados e documentados como consumo futuro C/D.
- Reconversão em cópia ×2 idempotente (hashes iguais) e proveniência inalterada.
- Zero mudança em `res/`/ROM/arte; zero commit/merge sem autorização.

## Riscos e mitigação

- **Regressão do flash**: mitigada por byte-identidade verificada pelo oráculo existente.
- **Restauração LIFO incorreta no borrow do super**: mitigada por assert dirigido de
  KO/round pendente (não depende do acaso do CPU x CPU).
- **Falsa sensação de que retrato já está isolado**: mitigada pela seção "Descoberta" — o
  gancho é declarado mas o isolamento real é Etapa C com arte.

## Ordem de trabalho derivada

Este incremento **não** cria storyboard/núcleo de arte; é infraestrutura de runtime. A
ordem roteiro→storyboard→coreografia→medição→budget→contrato continua válida para B2/C/D,
que **consomem** os ganchos aqui declarados.
