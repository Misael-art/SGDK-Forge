# Estrutura Padrao de doc/ por Projeto

Este documento define a estrutura canonica de `doc/` para projetos SGDK (GAME, ENGINE, TEMPLATE) no workspace MegaDrive_DEV.

---

## 1. Estrutura Padrao Organizada

```
doc/
├── README.md                    # Indice, hierarquia de verdade, ordem de leitura
├── 00-diretrizes-agente.md      # OBRIGATORIO — Regras para agentes de IA
├── 01-visao-geral.md            # OBRIGATORIO — Visao, escopo, pilares
├── 02-build-wrapper.md          # OBRIGATORIO — Delegacao ao wrapper
├── 03-arquitetura.md            # OBRIGATORIO — Estrutura de codigo
├── 04-recursos-e-pipeline.md    # OBRIGATORIO — Pipeline de assets
├── 05-guia-de-desenvolvimento.md# OBRIGATORIO — Como desenvolver
├── 06-debug-migracao.md         # OBRIGATORIO — Debug e migracao SGDK
├── 07-budget-vram-dma.md        # OBRIGATORIO — Budget de hardware
├── 08-bible-artistica.md        # OBRIGATORIO — Direcao visual
├── 09-checklist-anti-alucinacao.md # OBRIGATORIO — Gates praticos
├── 10-memory-bank.md            # OBRIGATORIO (GAME) — Estado operacional
├── 11-gdd.md                    # OBRIGATORIO (GAME) — Game Design Document
├── 12-roteiro.md                # OBRIGATORIO (GAME com narrativa)
├── 13-spec-cenas.md             # OBRIGATORIO (GAME) — Spec tecnica por cena
├── 14-spec-travel.md            # Quando aplicavel — Cenas de transicao
├── 15-diretrizes-producao-assets.md # Quando aplicavel — Producao de assets
└── [16-22] specs e planos       # Conforme fase do projeto
```

---

## 2. Documentos Obrigatorios por Categoria

### 2.1 Nucleo minimo (todo projeto GAME/ENGINE)

| # | Documento | Conteudo |
|---|-----------|----------|
| 1 | README.md | Indice e hierarquia de verdade |
| 2 | 00-diretrizes-agente.md | Regras para agentes de IA — proibicoes, gates, protocolo |
| 3 | 01-visao-geral.md | Intencao, escopo e pilares do projeto |
| 4 | 02-build-wrapper.md | Como o build funciona (delegacao ao wrapper) |
| 5 | 03-arquitetura.md | Estrutura de codigo, modulos, interfaces |
| 6 | 04-recursos-e-pipeline.md | Pipeline de assets (rescomp, placeholders, promocao) |
| 7 | 05-guia-de-desenvolvimento.md | Como adicionar conteudo, features, assets |
| 8 | 06-debug-migracao.md | Problemas ja resolvidos de migracao SGDK |
| 9 | 07-budget-vram-dma.md | Budget global de VRAM e DMA |
| 10 | 08-bible-artistica.md | Direcao visual, identidade, referencia de concept art |
| 11 | 09-checklist-anti-alucinacao.md | Gates praticos e lista de erros comuns |

### 2.2 Design de jogo (obrigatorio para GAME)

| # | Documento | Conteudo |
|---|-----------|----------|
| 12 | 10-memory-bank.md | Estado real do projeto — onde paramos, o que funciona, o que falta |
| 13 | 11-gdd.md | Game Design Document — mecanicas, progressao, regras, escopo |
| 14 | 12-roteiro.md | Roteiro narrativo — dialogos, encontros, tom, sequencias (se houver historia) |
| 15 | 13-spec-cenas.md | Especificacao tecnica por cena — budgets VRAM, DMA, sprites, efeitos |

### 2.3 Assets (obrigatorio quando houver producao visual)

| # | Documento | Conteudo |
|---|-----------|----------|
| 16 | 14-spec-travel.md | Especificacao de cenas de viagem/transicao (se aplicavel) |
| 17 | 15-diretrizes-producao-assets.md | Regras tecnicas e checklist para assets visuais |

---

## 3. Leitura Obrigatoria (ordem para agentes)

Antes de qualquer codigo ou decisao, ler nesta ordem:

1. `10-memory-bank.md` — Estado operacional real
2. `11-gdd.md` — Design do jogo
3. `13-spec-cenas.md` — Limites tecnicos por cena
4. `00-diretrizes-agente.md` — Regras de processo
5. `12-roteiro.md` — Narrativa (se a tarefa tocar dialogos)

Responder com `[Contexto Carregado]` antes de propor acoes.

---

## 4. Hierarquia de Verdade

Quando documentos entrarem em conflito, a ordem de prioridade e:

1. `10-memory-bank.md` (estado real)
2. `11-gdd.md` (design do jogo)
3. `13-spec-cenas.md` (limites tecnicos)
4. `00-diretrizes-agente.md` (regras de processo)
5. `12-roteiro.md` (narrativa)
6. Demais documentos

O documento de maior prioridade vence. Se a divergencia for detectada, corrija na mesma sessao.

---

## 5. Referencias

- [CANONICAL_WORKTREE.md](CANONICAL_WORKTREE.md) — Estrutura canonica de projeto
- [AGENTS.md](AGENTS.md) — Diretrizes para agentes
- Projeto de referencia: `SGDK_projects/Pequeno Principe Cronicas das Estrelas [VER.001].../doc/`
