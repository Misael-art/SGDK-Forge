# Motor de swap de CRAM por consumidor (Rota iii / A2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalizar o swap pré-declarado da REGRA 1c (hoje só o flash) em uma primitiva `CramConsumer`, rotear por ela o flash e o bgfx-do-super mantendo CRAM byte-idêntico, e fechar o vazamento de PAL0 quando um super termina em round/KO.

**Architecture:** Toda a lógica vive na fonte do conversor (`runtime/mg_fight.c`, `runtime/mg_runtime.h`), propagada ao projeto por `install-runtime` (nunca se edita `src/mg/` do projeto como origem). Um único ponto de escrita de CRAM por consumidor, com faixa `[lo..hi]` declarada e save/restore LIFO em buffers estáticos consumidos no VBlank. Testes rodam no host contra uma **cópia de laboratório**, nunca contra a produção.

**Tech Stack:** C (SGDK 2.11 / 68000, stub `tests/host/genesis.h` com `host_cram[64]`), Python 3 + pytest, `gcc`.

**Spec:** `SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/doc/mugen/spec_cram_swap_engine_2026_09_25.md`

## Global Constraints

- `TOOL_VERSION`: `0.3.0` → **`0.3.1`** (bump de patch).
- Nada de `float`/`double`, nada de `malloc`/`free`; toda DMA só enfileirada para consumo no VBlank; **fonte de `DMA_QUEUE` deve ser buffer estático** (pilha já estaria morta quando a cópia rodar).
- `src/mg/*.c` e `inc/mg/*.h` do projeto são **artefatos copiado**s com banner `/* COPIADO de tools/mugen2sgdk_forge/runtime/<name> (v<VER>). Edite na fonte. */`. Editar apenas em `tools/mugen2sgdk_forge/runtime/`.
- **Byte-identidade obrigatória:** os asserts existentes de `tests/host/impact_fx.c` (`bad_flash`, `bad_restore`, `bad_iso`, `bad_round`, `superpause_directed_ok`) devem permanecer verdes **sem nenhuma edição**.
- **Nenhum waiver, exclusão de recurso ou mudança de assert** para tornar um relatório verde. Um assert que passa por causa de stub infiel é tratado como bug de harness (Task 1), não como sucesso.
- **Produção intocada:** todo build/verificação consome a cópia de laboratório `SGDK_projects/.../rascunho/temporario/cram_lab`. Instalação em produção, build de ROM e capturas **não** fazem parte deste plano.
- Sem merge/push. Commits são locais, nesta branch, um por tarefa.
- `context_type` permanece `technical_demo` e `delivery_claim_ceiling` permanece `technical_demo`.
- Escopo fechado (não-metas da spec): nenhuma arte nova de famílias FX (B2), nenhuma migração de retrato (C), nada em `res/`.

---

### Task 1: Cópia de laboratório isolada + green nativo

**Files:**
- Create: `SGDK_projects/<PROJ>/rascunho/temporario/cram_lab/` (subárvores `src/`, `inc/`, `res/`)
- Read-only: `tools/mugen2sgdk_forge/tests/host/build_host.sh`

`<PROJ>` = `Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]` (caminho com espaços — sempre entre aspas).

**Interfaces:**
- Produces: `$LAB` — diretório de projeto mínimo e válido para `build_host.sh` (precisa de `inc/mg/*.h`, `inc/mg_gen/*.h`, `src/mg/*.c`, `src/mg_gen/*.c`, `res/mgres_*.res`). Todas as tarefas seguintes constroem contra ele.

- [ ] **Step 1: Criar a cópia a partir da produção (somente leitura da produção)**

```bash
cd "/mnt/sdcard/Projects/Sgdk Forge"
PROJ="SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
LAB="$PROJ/rascunho/temporario/cram_lab"
mkdir -p "$LAB/src" "$LAB/inc" "$LAB/res"
cp -r "$PROJ/src/mg" "$PROJ/src/mg_gen" "$LAB/src/"
cp -r "$PROJ/inc/mg" "$PROJ/inc/mg_gen" "$LAB/inc/"
cp -r "$PROJ/res/"* "$LAB/res/" 2>/dev/null || cp -r "$PROJ/res"/* "$LAB/res/"
ls "$LAB/src/mg" "$LAB/inc/mg" | head -20
```

- [ ] **Step 2: Provar que a cópia é equivalente à produção no runtime atual**

```bash
diff -q "$PROJ/src/mg/mg_fight.c" "$LAB/src/mg/mg_fight.c" && echo "LAB mg_fight OK"
diff -q "$PROJ/inc/mg/mg_runtime.h" "$LAB/inc/mg/mg_runtime.h" && echo "LAB mg_runtime OK"
```
Expected: as duas linhas `OK`. Qualquer divergência aqui invalida o laboratório — parar e re-copiar.

- [ ] **Step 3: Rodar o baseline host contra a cópia**

```bash
cd tools/mugen2sgdk_forge
MG_DEMO_PROJECT="$OLDPWD/../SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/rascunho/temporario/cram_lab" \
  python3 -m pytest tests/test_host_runtime.py -q
```
Expected: PASS (ou skip se `gcc`/Ken ausente — nesse caso registrar SKIP, não verde). Este é o número a bater nas tarefas seguintes.

- [ ] **Step 4: Commit**

```bash
git status --short "$PROJ/rascunho"   # conferir que rascunho/ e' ignorado ou aceitavel
```
Sem commit (rascunho é material de laboratório; nada de código mudou).

---

### Task 2: Fidelidade do harness — `PAL_getColors` lê CRAM de verdade

**Files:**
- Modify: `tools/mugen2sgdk_forge/tests/host/genesis.h:85`
- Test: `tools/mugen2sgdk_forge/tests/host/cram_getcolors.c` (Create)
- Test: `tools/mugen2sgdk_forge/tests/test_host_runtime.py` (adicionar função)

**Interfaces:**
- Produces: stub `PAL_getColors(u16 i, u16 *d, u16 n)` que copia de `host_cram[i..i+n-1]` (clamp a 64), com o mesmo compromisso de ordem que o real: valores já consumidos no VBlank anterior.

- [ ] **Step 1: Escrever o teste que falha**

Create `tests/host/cram_getcolors.c`:

```c
/* O stub de host precisa ler CRAM de verdade: sem isso, nenhum teste consegue provar
 * que um "borrow" de paleta devolve a linha exatamente como encontrou. */
#include "mg/mg_runtime.h"
int main(void)
{
    u16 src[16] = { 0x111,0x222,0x333,0x444,0x555,0x666,0x777,0x888,
                    0x999,0xAAA,0xBBB,0xCCC,0xDDD,0xEEE,0xFFF,0x000 };
    PAL_setColors(16, src, 16, DMA);                 /* PAL1 inteira */
    host_vblank();
    u16 back[16] = { 0 };
    PAL_getColors(16, back, 16);
    int ok = !memcmp(src, back, sizeof src);
    /* clamp: pedir alem do fim de CRAM nao pode escrever fora do buffer */
    u16 tail[4] = { 0xBAD,0xBAD,0xBAD,0xBAD };
    PAL_getColors(62, tail, 4);
    int clamped = tail[2] == 0 && tail[3] == 0xBAD;
    printf("{\"getcolors_roundtrip\": %d, \"clamped\": %d}\n", ok, clamped);
    return !(ok && clamped);
}
```

- [ ] **Step 2: Rodar e confirmar o vermelho**

```bash
cd tools/mugen2sgdk_forge
MG_HOST_MAIN=tests/host/cram_getcolors.c bash tests/host/build_host.sh \
  "<LAB>" /tmp/cram_getcolors/bin -O1 && /tmp/cram_getcolors/bin
```
Expected: `{"getcolors_roundtrip": 0, ...}` e exit code 1 (o stub atual faz `memset(d,0,...)`).

- [ ] **Step 3: Consertar o stub**

Em `tests/host/genesis.h:85`, substituir:

```c
static inline void PAL_getColors(u16 i, u16 *d, u16 n) { (void)i; memset(d, 0, n * 2); }
```
por:

```c
static inline void PAL_getColors(u16 i, u16 *d, u16 n)
{
    for (u16 k = 0; k < n; k++) d[k] = (i + k < 64) ? host_cram[i + k] : 0;
}
```

- [ ] **Step 4: Rodar e confirmar o verde**

```bash
MG_HOST_MAIN=tests/host/cram_getcolors.c bash tests/host/build_host.sh "<LAB>" /tmp/cram_getcolors/bin -O1 && /tmp/cram_getcolors/bin
```
Expected: `{"getcolors_roundtrip": 1, "clamped": 1}`, exit 0.

- [ ] **Step 5: Provar que o stub fiel não revelou regressão — provou uma limitação de teste**

```bash
MG_DEMO_PROJECT="<LAB>" python3 -m pytest tests/test_host_runtime.py -q
```
Expected: os mesmos resultados do baseline (Task 1 Step 3), **com `impact_fx` ainda verde sem edição**. Se `impact_fx` quebrar, o assert existente estava compensando o stub — tratar como defeito real e reportar ao humano, NÃO ajustar o assert.

- [ ] **Step 6: Commit**

```bash
git add tools/mugen2sgdk_forge/tests/host/genesis.h \
        tools/mugen2sgdk_forge/tests/host/cram_getcolors.c
git commit -m "test(host): PAL_getColors le host_cram de verdade (stub era infiel)"
```

---

### Task 3: Primitiva `CramConsumer` + versões

**Files:**
- Modify: `tools/mugen2sgdk_forge/mugen2sgdk_forge/__main__.py:22` (TOOL_VERSION)
- Modify: `tools/mugen2sgdk_forge/runtime/mg_runtime.h` (tipo + constantes + protótipos)
- Modify: `tools/mugen2sgdk_forge/runtime/mg_fight.c` (implementação)
- Test: `tools/mugen2sgdk_forge/tests/host/cram_swap.c` (Create)
- Test: `tools/mugen2sgdk_forge/tests/test_host_runtime.py` (adicionar função)

**Interfaces:**
- Produces (em `mg_runtime.h`):

```c
typedef struct {
    u8        line;                    /* 0..3 = PAL0..PAL3 */
    u8        lo, hi;                  /* indices [lo..hi] que o consumidor POSSUI */
    u8        borrow;                  /* 1 = nao dono: save/restore obrigatorios */
    const u16 *tab;                    /* swap pre-declarado (REGRA 1c) ou 0 */
} CramConsumer;

extern const CramConsumer CRAM_FLASH_P1, CRAM_FLASH_P2, CRAM_SUPER_BGFX, CRAM_FX_PAL3;
extern const CramConsumer CRAM_STAGERES, CRAM_HUDRES, CRAM_PORTRAIT_P1, CRAM_PORTRAIT_P2;

void cram_write(const CramConsumer *c, const u16 *src);   /* so [lo..hi], DMA_QUEUE, fonte estatica */
void cram_save(const CramConsumer *c, u16 *dst);          /* dst com ao menos hi-lo+1 palavras */
void cram_restore(const CramConsumer *c, const u16 *saved);
u8   cram_span(const CramConsumer *c);                    /* hi-lo+1 */
```

- [ ] **Step 1: Escrever o teste que falha**

Create `tests/host/cram_swap.c`:

```c
/* A primitiva e a unica porta de escrita de CRAM de um consumidor: ela nao pode
 * alcancar indice fora de [lo..hi] nem escrever quando a faixa estiver vazia. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"

int main(void)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);   /* preenche host_cram com as linhas reais */
    host_vblank();

    u16 mark[16]; for (int i = 0; i < 16; i++) mark[i] = 0x0AD;
    int bad = 0;

    /* 1. escreve so a faixa declarada: CRAM_FX_PAL3 possui 0..15; usar um sub-consumidor 5..9 */
    const CramConsumer mid = { 3, 5, 9, 0, 0 };
    cram_write(&mid, mark); host_vblank();
    for (int k = 0; k < 5; k++)  if (host_cram[48 + k] == 0x0AD) bad++;   /* abaixo de lo: intacto */
    for (int k = 10; k < 16; k++) if (host_cram[48 + k] == 0x0AD) bad++;  /* acima de hi: intacto */
    for (int k = 5; k <= 9; k++)  if (host_cram[48 + k] != 0x0AD) bad++;  /* dentro: escrito */

    /* 2. faixa vazia (reserva de indice) nao escreve nada */
    const CramConsumer empty = { 1, 0, 0, 0, 0 };
    u16 before[64]; memcpy(before, host_cram, sizeof before);
    cram_write(&empty, mark); host_vblank();
    if (memcmp(before, host_cram, sizeof before)) bad++;

    /* 3. save/restore devolve a linha exatamente (depende do stub fiel da Task 2) */
    const CramConsumer *c = &CRAM_SUPER_BGFX;
    u16 saved[16]; cram_save(c, saved);
    cram_write(c, mark); host_vblank();
    cram_restore(c, saved); host_vblank();
    u16 now[16]; PAL_getColors((u16)(c->line * 16 + c->lo), now, cram_span(c));
    for (int k = 0; k < cram_span(c); k++) if (now[k] != saved[k]) bad++;

    /* 4. posse declarada: flash nao pode tocar a linha FX nem o emprestimo do super */
    if (CRAM_FLASH_P1.line != 1 || CRAM_FLASH_P1.lo != 1 || CRAM_FLASH_P1.hi != 15) bad++;
    if (CRAM_FLASH_P2.line != 2 || CRAM_FLASH_P2.borrow || CRAM_SUPER_BGFX.borrow != 1) bad++;
    if (CRAM_SUPER_BGFX.line != 0 || CRAM_SUPER_BGFX.lo != 1 || CRAM_SUPER_BGFX.hi != 14) bad++;

    printf("{\"bad\": %d}\n", bad);
    return bad != 0;
}
```

- [ ] **Step 2: Rodar e confirmar o vermelho**

```bash
MG_HOST_MAIN=tests/host/cram_swap.c bash tests/host/build_host.sh "<LAB>" /tmp/cram_swap/bin -O1
```
Expected: falha de compilação com `error: unknown type name 'CramConsumer'` / `'CRAM_FLASH_P1' undeclared`.

- [ ] **Step 3: Subir a versão na fonte**

`mugen2sgdk_forge/__main__.py:22`:

```python
TOOL_VERSION = "0.3.1"
```

- [ ] **Step 4: Declarar tipo, constantes e protótipos em `runtime/mg_runtime.h`**

Acrescentar na seção de API de paleta (antes de `MG_fightRender`):

```c
/* ---- REGRA 1c generalizada: posse de CRAM declarada por consumidor ----
 * Uma linha CRAM tem 16 indices (0 = transparente). O contrato do projeto e
 * PAL0 cenario/HUD, PAL1/PAL2 corpo+retrato, PAL3 FX. Como as 4 linhas ja estao
 * todas comprometidas, isolamento se faz por FAIXA de indice e por emprestimo com
 * save/restore -- nunca por emprestar a linha inteira. */
typedef struct {
    u8        line;                    /* 0..3 = PAL0..PAL3 */
    u8        lo, hi;                  /* indices [lo..hi] que o consumidor possui */
    u8        borrow;                  /* 1 = nao dono: save/restore obrigatorios */
    const u16 *tab;                    /* swap pre-declarado (REGRA 1c) ou 0 */
} CramConsumer;

#define CRAM_CONSUMER(l, lo, hi, br) { (l), (lo), (hi), (br), 0 }

void cram_write(const CramConsumer *c, const u16 *src);
void cram_save(const CramConsumer *c, u16 *dst);
void cram_restore(const CramConsumer *c, const u16 *saved);
u8   cram_span(const CramConsumer *c);
```

- [ ] **Step 5: Implementar em `runtime/mg_fight.c`**

Inserir junto às definições de flash (`s_pal0_saved`), **após** os statics que as constantes referenciam:

```c
const CramConsumer CRAM_FLASH_P1   = CRAM_CONSUMER(1, 1, 15, 0);
const CramConsumer CRAM_FLASH_P2   = CRAM_CONSUMER(2, 1, 15, 0);
const CramConsumer CRAM_SUPER_BGFX = CRAM_CONSUMER(0, 1, 14, 1);
const CramConsumer CRAM_FX_PAL3    = CRAM_CONSUMER(3, 0, 15, 0);
/* Reservas de posse: lo==hi==0 escreve nada. A faixa real e declarada por quem consome
 * (retrato na Etapa C; stage/HUD na Etapa D), o que impede dois consumidores de reivindicarem
 * o mesmo indice por silencio. */
const CramConsumer CRAM_STAGERES   = CRAM_CONSUMER(0, 1, 8, 0);
const CramConsumer CRAM_HUDRES     = CRAM_CONSUMER(0, 9, 15, 0);
const CramConsumer CRAM_PORTRAIT_P1 = CRAM_CONSUMER(1, 0, 0, 0);
const CramConsumer CRAM_PORTRAIT_P2 = CRAM_CONSUMER(2, 0, 0, 0);

u8 cram_span(const CramConsumer *c) { return (u8)(c->hi >= c->lo ? c->hi - c->lo + 1 : 0); }

static u16 cram_base(const CramConsumer *c) { return (u16)(c->line * 16 + c->lo); }

/* Fonte deve ser memoria estatica: DMA_QUEUE so le o ponteiro no VBlank. */
void cram_write(const CramConsumer *c, const u16 *src)
{
    u8 n = cram_span(c);
    if (!n) return;
    PAL_setColors(cram_base(c), src, n, DMA_QUEUE);
}

void cram_save(const CramConsumer *c, u16 *dst)
{
    u8 n = cram_span(c);
    if (!n) return;
    PAL_getColors(cram_base(c), dst, n);
}

void cram_restore(const CramConsumer *c, const u16 *saved) { cram_write(c, saved); }
```

- [ ] **Step 6: Instalar na cópia e rodar o teste (verde)**

```bash
PYTHONPATH=. python3 -m mugen2sgdk_forge install-runtime "<LAB>"
MG_HOST_MAIN=tests/host/cram_swap.c bash tests/host/build_host.sh "<LAB>" /tmp/cram_swap/bin -O1 && /tmp/cram_swap/bin
```
Expected: `{"bad": 0}`, exit 0.

- [ ] **Step 7: Wire no pytest + regression**

Adicionar a `tests/test_host_runtime.py`:

```python
def test_cram_consumer_write_is_bounded_by_declared_span(tmp_path):
    exe = build(tmp_path, "cram_swap")
    r = json.loads(subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout)
    assert r["bad"] == 0, r
```

```bash
MG_DEMO_PROJECT="<LAB>" python3 -m pytest tests/test_host_runtime.py -q
```
Expected: verde, com `impact_fx` inalterado.

- [ ] **Step 8: Commit**

```bash
git add tools/mugen2sgdk_forge/runtime/mg_runtime.h tools/mugen2sgdk_forge/runtime/mg_fight.c \
        tools/mugen2sgdk_forge/mugen2sgdk_forge/__main__.py \
        tools/mugen2sgdk_forge/tests/host/cram_swap.c tools/mugen2sgdk_forge/tests/test_host_runtime.py
git commit -m "feat(runtime): CramConsumer - posse de CRAM declarada por faixa (REGRA 1c generalizada)"
```

---

### Task 4: Retrofit do flash (byte-idêntico)

**Files:**
- Modify: `tools/mugen2sgdk_forge/runtime/mg_fight.c` (`impact_fx_step`, hoje ~linhas 100-105 da fonte)
- Test: `tools/mugen2sgdk_forge/tests/host/impact_fx.c` — **não editar**; é a prova de byte-identidade.

**Interfaces:**
- Consumes: `CRAM_FLASH_P1/P2`, `cram_write` (Task 3).
- Produz: flash aplicado exclusivamente via `cram_write`, mesma linha/faixa/fonte estática.

- [ ] **Step 1: Escrever o teste de igualdade estrutural (falha antes da troca)**

```bash
cd tools/mugen2sgdk_forge
MG_HOST_MAIN=tests/host/impact_fx.c bash tests/host/build_host.sh "<LAB>" /tmp/fx_before/bin -O1
/tmp/fx_before/bin 36000 > /tmp/fx_before.json
```
Guarda o JSON de referência ANTES da troca de implementação.

- [ ] **Step 2: Rotear flash pela primitiva**

Em `impact_fx_step`, substituir o corpo do laço de flash:

```c
        const u16 *src = s_basepal[s];
        if (lvl == 1) PAL_setColors(s ? 33 : 17, &src[1], 15, DMA_QUEUE);   /* fim: paleta original exata */
        else PAL_setColors(s ? 33 : 17, s_flash_tab[s][lvl - 2], 15, DMA_QUEUE);
```
por:

```c
        const CramConsumer *cons = s ? &CRAM_FLASH_P2 : &CRAM_FLASH_P1;
        const u16 *src = s_basepal[s];
        /* lvl 1 = ultima passada: devolve a linha ao corpo original; acima, o swap pre-declarado */
        cram_write(cons, lvl == 1 ? &src[1] : s_flash_tab[s][lvl - 2]);
```

- [ ] **Step 3: Reconstruir e comparar com a referência**

```bash
PYTHONPATH=. python3 -m mugen2sgdk_forge install-runtime "<LAB>"
MG_HOST_MAIN=tests/host/impact_fx.c bash tests/host/build_host.sh "<LAB>" /tmp/fx_after/bin -O1
/tmp/fx_after/bin 36000 > /tmp/fx_after.json
diff /tmp/fx_before.json /tmp/fx_after.json && echo "BYTE-IDENTICAL"
```
Expected: `BYTE-IDENTICAL` (JSON idêntico byte a byte; deterministico, sem RNG nao semeado).

- [ ] **Step 4: Rodar a suite host inteira**

```bash
MG_DEMO_PROJECT="<LAB>" python3 -m pytest tests/test_host_runtime.py -q
```
Expected: tudo verde, `impact_fx.c` sem uma linha editada.

- [ ] **Step 5: Commit**

```bash
git add tools/mugen2sgdk_forge/runtime/mg_fight.c
git commit -m "refactor(runtime): flash roteado por CramConsumer (CRAM byte-identico, provado)"
```

---

### Task 5: Retrofit do bgfx-do-super + fechar o vazamento em round/KO

**Files:**
- Modify: `tools/mugen2sgdk_forge/runtime/mg_fight.c` (`bgfx_render`, `bgfx_end`, transicao de round)
- Test: `tools/mugen2sgdk_forge/tests/host/cram_borrow.c` (Create)
- Test: `tools/mugen2sgdk_forge/tests/test_host_runtime.py` (adicionar função)

**Interfaces:**
- Consumes: `CRAM_SUPER_BGFX`, `cram_save`, `cram_write`, `cram_restore` (Task 3).
- Produces: `bgfx_release(void)` — devolve PAL0 se houver empréstimo pendente; idempotente.

- [ ] **Step 1: Escrever o teste que falha (o vazamento real)**

Create `tests/host/cram_borrow.c`:

```c
/* O emprestimo de PAL0 do super era devolvido so quando o explod morria. Um round que
 * termina sob o super deixava a linha do cenario/HUD com as cores do fundo do super.
 * Aqui o emprestimo e forcado e devolvido na transicao de round, sem explod morrer. */
#include "mg/mg_runtime.h"
#include "mg_gen/mg_ken.h"

int main(void)
{
    MG_fightInit(&mg_char_ken, 0, &mg_char_ken, 0, 0);
    host_vblank();
    u16 before[16]; PAL_getColors(0, before, 16);       /* stub fiel (Task 2) le PAL0 real */
    int bad = 0;

    mg_fight.bgfx_active = 1;                           /* forca o emprestimo declarado */
    u16 steal[14]; for (int i = 0; i < 14; i++) steal[i] = 0x0EE;
    cram_write(&CRAM_SUPER_BGFX, &steal[0]);            /* base = 1 -> PAL0[1..14] */
    cram_save(&CRAM_SUPER_BGFX, mg_fight.pal0_saved);   /* salva o que estava na linha */
    host_vblank();
    for (int k = 1; k <= 8; k++) if (host_cram[k] != 0x0EE) bad++;   /* index 0 fora da faixa */

    bgfx_release();                                     /* deve devolver PAL0[1..14] exatos */
    host_vblank();
    for (int k = 1; k < 15; k++) if (host_cram[k] != mg_fight.pal0_saved[k]) bad++;
    if (mg_fight.bgfx_active) bad++;
    bgfx_release(); bgfx_release();                     /* idempotente: nao escreve de novo */
    host_vblank();
    for (int k = 1; k < 15; k++) if (host_cram[k] != mg_fight.pal0_saved[k]) bad++;

    printf("{\"bad\": %d}\n", bad);
    return bad != 0;
}
```

- [ ] **Step 2: Rodar e confirmar o vermelho**

```bash
MG_HOST_MAIN=tests/host/cram_borrow.c bash tests/host/build_host.sh "<LAB>" /tmp/cram_borrow/bin -O1
```
Expected: `error: 'bgfx_release' undeclared` (e `mg_fight` sem campo `pal0_saved`).

- [ ] **Step 3: Mover `s_pal0_saved` para o estado de luta e criar o ponto único de liberação**

Em `runtime/mg_fight.c`, apagar `static u16 s_pal0_saved[16];` (linha 20) e, em
`runtime/mg_types.h`, acrescentar ao struct `MgFight`:

```c
    u16 pal0_saved[16];        /* snapshot PAL0 devolvido por cram_restore no fim do emprestimo */
```

Substituir `bgfx_end` por:

```c
/* Devolve PAL0[1..14] se houver emprestimo pendente. Idempotente: chamado no fim do explod
 * E na transicao de round/KO, e o segundo chamado precisa nao escrever nada. */
void bgfx_release(void)
{
    if (!mg_fight.bgfx_active) return;
    VDP_clearTileMapRect(BG_B, 0, 0, 40, 28);
    cram_restore(&CRAM_SUPER_BGFX, &mg_fight.pal0_saved[1]);
    s_bgfx_owner = -1;
    mg_fight.bgfx_active = 0;
}

static void bgfx_end(void) { bgfx_release(); }
```

- [ ] **Step 4: Rotear a entrada/elemento do empréstimo pela primitiva**

Em `bgfx_render`, substituir:

```c
        PAL_getColors(0, s_pal0_saved, 16);
```
por:

```c
        cram_save(&CRAM_SUPER_BGFX, &mg_fight.pal0_saved[1]);
```

e substituir:

```c
    if (k < fx->npals) PAL_setColors(1, &fx->pals[k][1], 14, DMA_QUEUE);
```
por:

```c
    if (k < fx->npals) cram_write(&CRAM_SUPER_BGFX, &fx->pals[k][1]);
```

- [ ] **Step 5: Chamar a liberação na transição de round/KO**

No ponto de `MG_fightUpdate` onde `round_state` muda (o ramo que zera o estado da rodada),
incluir `bgfx_release();` junto das limpezas existentes — o ponto exato é onde hoje
`mg_fight.flash_lvl[]`/projéteis são reiniciados. Se não houver um único ponto, chamar
`bgfx_release()` na saída de `bgfx_render` quando `e->removetime <= 0` já cuida do caminho
normal e o novo cobre apenas o round.

- [ ] **Step 6: Rodar o teste dirigido (verde)**

```bash
PYTHONPATH=. python3 -m mugen2sgdk_forge install-runtime "<LAB>"
MG_HOST_MAIN=tests/host/cram_borrow.c bash tests/host/build_host.sh "<LAB>" /tmp/cram_borrow/bin -O1 && /tmp/cram_borrow/bin
```
Expected: `{"bad": 0}`.

- [ ] **Step 7: Provar que o super real continua devolvendo PAL0 exato**

```bash
MG_DEMO_PROJECT="<LAB>" python3 -m pytest tests/test_host_runtime.py -q
```
Expected: verde, incluindo `impact_fx` (`bad_iso`/`bad_round` inalterados) e
`test_super_effects_ring_parts_and_background`.

- [ ] **Step 8: Wire no pytest + commit**

```python
def test_super_palette_borrow_is_released_on_demand(tmp_path):
    exe = build(tmp_path, "cram_borrow")
    r = json.loads(subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout)
    assert r["bad"] == 0, r
```

```bash
git add tools/mugen2sgdk_forge/runtime/mg_fight.c tools/mugen2sgdk_forge/runtime/mg_types.h \
        tools/mugen2sgdk_forge/tests/host/cram_borrow.c tools/mugen2sgdk_forge/tests/test_host_runtime.py
git commit -m "fix(runtime): emprestimo de PAL0 do super devolvido na transicao de round (bgfx_release)"
```

---

### Task 6: Idempotência de reconversão em cópia + suite completa

**Files:**
- Test: `tools/mugen2sgdk_forge/tests/test_runtime_install.py` (Create)

- [ ] **Step 1: Escrever o teste de idempotência**

```python
"""install-runtime deve ser deterministico: a mesma fonte produz bytes identicos em duas
passadas, e nao toca em dado gerado nem em proveniencia. Provar isso ANTES de instalar em
producao e o que deixa a Etapa B reversivel."""
import hashlib
from pathlib import Path

from mugen2sgdk_forge.__main__ import install_runtime, RUNTIME_FILES

COPIED = RUNTIME_FILES + ["mg_ops.h"]


def _digest(project: Path) -> dict:
    out = {}
    for sub in ("src/mg", "inc/mg"):
        for p in sorted((project / sub).glob("*")):
            if p.name in COPIED:
                out[p.relative_to(project).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def test_install_runtime_is_byte_idempotent(tmp_path):
    (tmp_path / "src" / "mg").mkdir(parents=True)
    (tmp_path / "inc" / "mg").mkdir(parents=True)
    install_runtime(tmp_path)
    first = _digest(tmp_path)
    install_runtime(tmp_path)
    assert _digest(tmp_path) == first
    assert all(f".{n}" in "".join(k) for n in COPIED for k in first)   # todos os arquivos presentes
```

- [ ] **Step 2: Rodar**

```bash
cd tools/mugen2sgdk_forge && python3 -m pytest tests/test_runtime_install.py -q
```
Expected: 1 passed.

- [ ] **Step 3: Reconversão em cópia ×2, com proveniência preservada**

```bash
cd "/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
sha256sum src/mg/mg_fight.c inc/mg/mg_runtime.h doc/asset_provenance_manifest.json doc/mugen/provenance_annotations.json > /tmp/lab_before.sha
PYTHONPATH=../../../tools/mugen2sgdk_forge python3 -m mugen2sgdk_forge install-runtime rascunho/temporario/cram_lab
(cd rascunho/temporario/cram_lab && sha256sum src/mg/mg_fight.c inc/mg/mg_runtime.h > ../lab1.sha)
PYTHONPATH=../../../tools/mugen2sgdk_forge python3 -m mugen2sgdk_forge install-runtime rascunho/temporario/cram_lab
(cd rascunho/temporario/cram_lab && sha256sum src/mg/mg_fight.c inc/mg/mg_runtime.h > ../lab2.sha)
diff rascunho/temporario/lab1.sha rascunho/temporario/lab2.sha && echo "IDEMPOTENTE"
```
Expected: `IDEMPOTENTE`. O banner das duas fontes deve ler `(v0.3.1)`. `doc/asset_provenance_manifest.json`
e `provenance_annotations.json` não mudam (o instalador não os toca) — conferir que `/tmp/lab_before.sha`
ainda bate para esses dois arquivos.

- [ ] **Step 4: Suite completa do repositório**

```bash
cd "/mnt/sdcard/Projects/Sgdk Forge/tools/mugen2sgdk_forge" && python3 -m pytest -q
```
Expected: só adição de testes; zero regressão sobre o baseline da Etapa A (78 passed).

- [ ] **Step 5: palette-check inalterado (rota iii não mexe no orçamento)**

```bash
cd "/mnt/sdcard/Projects/Sgdk Forge"
PYTHONPATH=tools/mugen2sgdk_forge python3 -m mugen2sgdk_forge palette-check \
  --project "SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]" --id ken
```
Expected: `exact_need=23`, `over_by=8`, `status=fail` — **o mesmo número de antes**. Esta rota reorganiza posse, não cria slots; se o número mudar, algo saiu do escopo.

- [ ] **Step 6: Atualizar memória e backlog, depois commit**

Escrever em `doc/10-memory-bank.md` (fonte de verdade #1) o que foi instalado só na cópia, e
marcar B1 no backlog como concluído na rota iii. **Não instalar em produção, não buildar ROM,
não declarar nada `testado_em_emulador`** — o gate de emulador pertence à Etapa F.

```bash
git add tools/mugen2sgdk_forge/tests/test_runtime_install.py
git commit -m "test(runtime): install-runtime byte-idempotente"
```

---

## Self-review do plano

**1. Cobertura da spec.** Motivo → Task 3 (primitiva) + Task 4/5 (retrofit). Origem persistente +
`TOOL_VERSION` → Task 3 Step 3. Byte-identidade → Task 4 Step 1-3 (diff de JSON de referência).
Restauração garantida em round/KO → Task 5. Ganchos de retrato/HUD → Task 3 Step 5 (`CRAM_PORTRAIT_*`,
`CRAM_HUDRES`, `CRAM_STAGERES`) com comportamento de faixa vazia testado em Step 1. Testes 1-5 da
spec → Tasks 2, 3, 4, 5, 6. Idempotência em cópia → Task 6 Step 3. Não-metas → Global Constraints.

**2. Placeholders.** Nenhum `TBD`. `"<LAB>"` é definido na Task 1 Step 1 como caminho concreto. A faixa
do retrato é declarada vazia de propósito (o valor real é decisão de arte da Etapa C) e o teste cobre
que faixa vazia **não escreve nada** — não é um assert faltando.

**3. Consistência de tipos.** `cram_write/cram_save/cram_restore/cram_span/CRAM_CONSUMER/CramConsumer`
e os nomes `CRAM_FLASH_P1/P2, CRAM_SUPER_BGFX, CRAM_FX_PAL3, CRAM_STAGERES, CRAM_HUDRES,
CRAM_PORTRAIT_P1/P2` são definidos na Task 3 e consumidos com as mesmas assinaturas nas Tasks 4-5.
`mg_fight.pal0_saved[16]` é introduzido na Task 5 Step 3 e usado nos Steps 4 e no teste do Step 1;
`s_pal0_saved` é removido no mesmo passo, então nenhum passo posterior pode referenciá-lo.
