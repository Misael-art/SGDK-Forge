# Documentacao — __PROJECT_NAME__

## Leitura obrigatoria (nesta ordem)

| Ordem | Documento | Conteudo |
|-------|-----------|----------|
| 1 | `10-memory-bank.md` | Estado real do projeto — onde paramos, o que funciona, o que falta |
| 2 | `11-gdd.md` | Game Design Document — mecanicas, progressao, regras, escopo |
| 3 | `13-spec-cenas.md` | Especificacao tecnica por cena — budgets de VRAM, DMA, sprites, efeitos |
| 4 | `00-diretrizes-agente.md` | Regras para agentes de IA — proibicoes, gates, protocolo |
| 5 | `12-roteiro.md` | Roteiro narrativo — dialogos, encontros, tom, sequencias |

## Referencia tecnica

| Documento | Conteudo |
|-----------|----------|
| `01-visao-geral.md` | Intencao, escopo e pilares do projeto |
| `02-build-wrapper.md` | Como o build funciona (delegacao ao wrapper) |
| `03-arquitetura.md` | Estrutura de codigo, modulos, interfaces |
| `04-recursos-e-pipeline.md` | Pipeline de assets (rescomp, placeholders, promocao) |
| `05-guia-de-desenvolvimento.md` | Como adicionar conteudo, features, assets |
| `06-debug-migracao.md` | Problemas ja resolvidos de migracao SGDK |
| `07-budget-vram-dma.md` | Budget global de VRAM e DMA |
| `08-bible-artistica.md` | Direcao visual, identidade, referencia de concept art |
| `09-checklist-anti-alucinacao.md` | Gates praticos e lista de erros comuns |

## Hierarquia de verdade

Se dois documentos entrarem em conflito, a ordem de prioridade e:

1. `10-memory-bank.md` (estado real)
2. `11-gdd.md` (design do jogo)
3. `13-spec-cenas.md` (limites tecnicos)
4. `00-diretrizes-agente.md` (regras de processo)
5. `12-roteiro.md` (narrativa)
6. Demais documentos

O documento de maior prioridade vence. Se a divergencia for detectada, corrija na mesma sessao.
