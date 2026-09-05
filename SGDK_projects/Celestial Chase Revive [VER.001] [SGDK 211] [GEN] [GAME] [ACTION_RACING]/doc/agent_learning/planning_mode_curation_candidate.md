# Planning Mode Curation Candidate

Status: `needs_human_review`.

Data: 2026-06-16

Este arquivo registra um candidato local para o agente canonico avaliar. Nada aqui foi promovido para `tools/sgdk_wrapper/.agent/`.

## Problema observado

A primeira fundacao documental parecia completa para pre-producao, mas ainda nao guiava producao ponta-a-ponta. A revisao humana apontou lacunas criticas: track data, colisao, HUD, animacao, tuning, asset spec, build, boss, game over/pause/continue e mockups visuais.

## Padrao proposto

Para projetos `aaa_game` ou vertical slices com gameplay real, o modo de planejamento deveria exigir um fechamento pre-runtime antes de iniciar codigo:

- formato de dados jogaveis;
- contrato de colisao;
- HUD wireframe pixel;
- contrato de animacao;
- tabela numerica de tuning;
- asset production spec;
- contrato de build via wrapper central;
- padroes de boss, se houver boss;
- pause/game over/continue;
- referencia visual local com hash quando nao houver concept art final.

## Evidencia local

- `doc/canonical_planning_curation_handoff.json`
- `doc/critical_gap_audit.json`
- `doc/22-production-spec-gap-closure.md`
- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`

## Limites

- Este padrao nao deve ser imposto em `exercise` ou `technical_demo` sem proporcionalidade.
- Estes contratos nao substituem build, `.res`, medicao de budget ou BlastEm.
- O caso ainda nao foi provado em runtime; portanto a decisao maxima e candidato de planejamento, nao regra operacional validada.

## Proxima revisao humana

Avaliar se este fechamento deve virar:

- checklist em `project-methodology-adoption`;
- etapa no `aaa-scene-pipeline`;
- template de docs para novo `aaa_game`;
- ou apenas recomendacao local sem promocao.
