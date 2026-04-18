# AGENTS.md – Pequeno Principe: Cronicas das Estrelas

> **Ponto de entrada obrigatorio para qualquer agente de IA que atue neste projeto.**

Este repositorio e editado por multiplas IAs e por humanos.
O objetivo destas diretrizes e impedir alucinacao, escopo falso, regressao silenciosa, poluicao estrutural e informativo mentiroso de entrega.

---

## HIERARQUIA DE VERDADE

Se dois documentos entrarem em conflito, siga esta ordem:

| Ordem | Fonte | Autoridade |
|-------|-------|------------|
| 1 | `doc/10-memory-bank.md` | Estado operacional real, prioridade atual e restricoes de sessao |
| 2 | `doc/11-gdd.md` | Design do jogo: mecanicas, progressao, regras |
| 3 | `doc/13-spec-cenas.md` | Especificacao tecnica por cena: budget, efeitos, limites de hardware |
| 4 | `doc/00-diretrizes-agente.md` | Regras de processo, gates e anti-poluicao |
| 5 | `doc/12-roteiro.md` | Roteiro narrativo: dialogos, encontros, sequencias |
| 6 | `doc/03-arquitetura.md` | Estrutura de codigo e modulos |
| 7 | `doc/07-budget-vram-dma.md` | Budget global de VRAM e DMA |
| 8 | `doc/09-checklist-anti-alucinacao.md` | Gates praticos e regras anti-poluicao detalhadas |
| 9 | `doc/08-bible-artistica.md` | Direcao visual e identidade |
| 10 | `doc/15-diretrizes-producao-assets.md` | Regras tecnicas e checklist para assets visuais |
| 11 | `README.md` / este arquivo | Onboarding resumido |

Se um documento de menor prioridade contradizer um superior, o superior vence.
Se a divergencia for detectada, corrija na mesma sessao.

---

## LEITURA OBRIGATORIA ANTES DE QUALQUER ACAO

1. `doc/10-memory-bank.md`
2. `doc/11-gdd.md`
3. `doc/13-spec-cenas.md`
4. `doc/00-diretrizes-agente.md`

Responda com `[Contexto Carregado]` antes de propor qualquer acao relevante.

---

## REGRAS CRITICAS (RESUMO)

- Nao antecipe cenas ou planetas que nao estejam no GDD aprovado.
- Nao use `float`, `double`, `malloc` ou biblioteca externa ao SGDK.
- Nao altere `tools/sgdk_wrapper` sem necessidade comprovada e documentada.
- Nao declare feature pronta sem build verde e teste em emulador.
- Nao crie arquivos fora da arvore definida em `doc/03-arquitetura.md`.
- Nao modifique dialogos ou encontros sem consultar `doc/12-roteiro.md`.
- Nao exceda os budgets definidos em `doc/13-spec-cenas.md` e `doc/14-spec-travel.md`.
- Mantenha `doc/10-memory-bank.md` atualizado ao encerrar sessao.

---

## BUILD E VALIDACAO

```bat
build.bat
run.bat
```

O projeto delega ao wrapper canonico em `tools/sgdk_wrapper`. Nenhuma logica de build deve existir fora do wrapper.

---

## REFERENCIA RAPIDA

| O que voce precisa | Arquivo |
|--------------------|---------|
| Estado real do projeto | `doc/10-memory-bank.md` |
| Design do jogo | `doc/11-gdd.md` |
| Roteiro e dialogos | `doc/12-roteiro.md` |
| Spec tecnica por cena | `doc/13-spec-cenas.md` |
| Regras para agente | `doc/00-diretrizes-agente.md` |
| Arquitetura de codigo | `doc/03-arquitetura.md` |
| Budget VRAM/DMA | `doc/07-budget-vram-dma.md` |
| Gates e anti-alucinacao | `doc/09-checklist-anti-alucinacao.md` |
| Bible artistica | `doc/08-bible-artistica.md` |
| Pipeline de assets | `doc/04-recursos-e-pipeline.md` |
| Spec tecnica viagens | `doc/14-spec-travel.md` |
| Producao de assets visuais | `doc/15-diretrizes-producao-assets.md` |
