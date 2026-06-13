# AGENTS.md — MegaDrive_DEV

> **Ponto de entrada obrigatorio para qualquer agente de IA neste workspace.**
> Diga `[Contexto MD Carregado]` antes de propor qualquer acao.

---

## REGRA FINAL DE FERRO

**"Se nao foi visto rodando no emulador, nao existe."**
Intencao nao e validacao. ROM rodando em 60fps constantes sim.

---

## FRAMEWORK CANONICO DE AGENTES

O workspace usa o framework `.agent` centralizado em `tools/sgdk_wrapper/.agent/`.
Cada projeto recebe uma materializacao local via bootstrap automatico.

```
tools/sgdk_wrapper/.agent/
  ARCHITECTURE.md          ← leia para entender o framework
  rules/SGDK_GLOBAL.md     ← regras sempre ativas
  agents/                  ← personas especializadas
  skills/                  ← conhecimento por dominio
  workflows/               ← runbooks operacionais
  scripts/                 ← automacoes de auditoria
```

**Politica de sobrescrita: `.agent` local existente nao e sobrescrita.**

### Compatibilidade Codex Skills

Para descoberta nativa de skills pelo Codex em nivel de repositorio, o workspace expõe `.agents/skills` como ponte de compatibilidade.

- `.agents/skills` aponta para `tools/sgdk_wrapper/.agent/skills`
- a fonte canonica continua sendo `tools/sgdk_wrapper/.agent/skills`
- nao duplique nem edite skills em uma segunda arvore paralela

---

## HIERARQUIA DE VERDADE

| # | Fonte | Autoridade |
|---|-------|------------|
| 1 | `doc/10-memory-bank.md` | Estado operacional real |
| 2 | `doc/11-gdd.md` | Design e escopo do jogo |
| 3 | `doc/13-spec-cenas.md` | Budget real por cena |
| 4 | `doc/00-diretrizes-agente.md` | Regras de processo |
| 5 | `doc/12-roteiro.md` | Roteiro e dialogos |
| 6 | `doc/03-arquitetura.md` | Estrutura de codigo |
| 7 | `.mddev/project.json` | Manifesto estrutural |
| 8 | Headers SGDK `sdk/sgdk-2.11/inc/` | API definitiva |
| 9 | Suposicao / memoria | Ultima prioridade — nunca especular |

---

## RESTRICOES NAO NEGOCIAVEIS

```
❌ float / double        — use fix16/fix32
❌ malloc / free         — use buffers estaticos no loop
❌ APIs SGDK 1.60        — ver tabela de migracao
❌ DMA fora do VBlank    — apenas seguro no VBlank callback
❌ Logica de build em projeto — apenas em tools/sgdk_wrapper/
❌ Inventar API do SGDK  — verificar header antes de usar
❌ Declarar "pronto" sem ROM rodando no emulador
```

---

## VOCABULARIO DE STATUS

| Termo | Significado |
|-------|-------------|
| `documentado` | Existe apenas em docs |
| `implementado` | Codigo existe, nao buildado |
| `buildado` | Compila, nao testado |
| `testado_em_emulador` | Rodou com evidencia rastreavel; BlastEm fecha gate e BizHawk apenas complementa |
| `validado_budget` | VRAM/DMA/sprites confirmados |
| `placeholder` | Asset ou logica provisoria |
| `parcial` | Incompleto mas funcional |
| `futuro_arquitetural` | Fora do escopo atual |

---

## PIPELINE DE PRODUCAO

```
Director → Pixel Engineer → Programador → QA → Iteracao
```

Nenhum passo pode ser pulado. Ver `tools/sgdk_wrapper/.agent/workflows/production-loop.md`.

**Regras do loop:**
- Feature creep bloqueado na etapa 1 (se nao esta no GDD, nao entra)
- Assets nao validados nao entram no build
- ROM nao testada nao e entregue
- Evidencia obrigatoria em cada transicao

---

## FILOSOFIA MAXIMALISTA

Nao basta FX isolado. E obrigatorio:
- Combinar FX com efeito colateral fisico real
- Timeline de cena com variacao temporal (nao estatico)
- Todo efeito deve ter ligacao direta com o gameplay

---

## ANTI-ALUCINACAO

| Alucinacao | Realidade |
|-----------|-----------|
| Alpha blending | Nao existe — apenas Highlight/Shadow |
| Terceiro plano BG | Apenas BG_A + BG_B + WINDOW |
| `int` e 16 bits | GCC 68000: `int` = 32 bits — use `u16`/`s16` |
| DMA fora de VBlank | Apenas seguro no VBlank |
| Gradiente suave | Max 61 cores — fade = troca de paleta |
| `PAL_getColors(4 args)` | SGDK 2.11: 3 args `(index, dest, count)` |
| Sombra assada no sprite | Use shadow bit do VDP |

---

## MIGRACAO SGDK 1.60 → 2.11

| 1.60 | 2.11 |
|------|------|
| `VDP_setPalette(pal, data)` | `PAL_setPalette(pal, data, DMA)` |
| `VDP_setPaletteColors(idx, data, n)` | `PAL_setColors(idx, data, n, DMA)` |
| `PAL_setPaletteDMA(pal, data)` | `PAL_setPalette(pal, data, DMA)` |
| `SPR_addSpriteEx(def,x,y,attr,idx,flags)` | `SPR_addSprite(def,x,y,attr)` |
| `SPR_FLAG_AUTO_SPRITE_ALLOC` | `SPR_FLAG_AUTO_VRAM_ALLOC` |

Ferramentas: `fix_migration_issues.ps1`, `autofix_sprite_res.ps1`, `validate_resources.ps1`

---

## GATE DE ENTREGA

So declare "pronto" com todos os 7 eixos de QA reportados:

```
✅ build: sucesso → out/rom.bin existe
✅ validation_report: limpo
✅ boot_emulador: ok (BlastEm obrigatorio no gate; BizHawk so complementa telemetria)
✅ gameplay_basico: funcional
✅ performance: estavel (60fps)
✅ audio: ok
✅ memoria operacional canonica atualizada (`doc/10-memory-bank.md` no projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace)
```

### Evidencia Canonica de Emulador

- BlastEm continua sendo o gate obrigatório de entrega.
- Quando o projeto gerar um bloco visual canônico em SRAM, a evidência mínima aceita passa a ser:
  - screenshot dedicado da janela do BlastEm
  - `save.sram`
  - `visual_vdp_dump.bin`
- Nessa modalidade, o quicksave nativo do BlastEm é opcional e não bloqueia sozinho o status `testado_em_emulador`.

---

## ARQUITETURA DO WORKSPACE

```
sdk/sgdk-2.11/           ← toolchain (gitignored)
tools/sgdk_wrapper/      ← fonte unica de logica de build + framework .agent
tools/emuladores/        ← BlastEm, BizHawk, Exodus, GensKMod
SGDK_templates/base-elite/  ← template canonico
SGDK_projects/           ← jogos
SGDK_Engines/            ← engines
doc/                     ← documentacao do workspace
```

Naming convention: `NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]`

---

## REFERENCIA RAPIDA

| Necessidade | Arquivo |
|-------------|---------|
| Framework .agent | `tools/sgdk_wrapper/.agent/ARCHITECTURE.md` |
| Regras globais | `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` |
| Pipeline | `tools/sgdk_wrapper/.agent/workflows/production-loop.md` |
| Pixel strict rules | `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/` |
| Budget VDP | `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/` |
| Migracao batch | `doc/migrations/MIGRATION_BATCH_211.md` |
| Nomenclatura | `doc/PADRAO_NOMENCLATURA.md` |
| Emuladores | `tools/emuladores/` |
