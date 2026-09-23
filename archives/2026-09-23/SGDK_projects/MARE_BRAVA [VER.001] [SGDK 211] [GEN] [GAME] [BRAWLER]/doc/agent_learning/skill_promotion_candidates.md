# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Itens permanecem pendentes salvo quando uma decisao humana explicita e sua
evidencia forem registradas em `canonical_promotion_review.md`.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| [DATA] | `promotion_candidate` | [nome curto] | [problema] | [build/log/screenshot/hash] | [baixo/medio/alto] | [criterio] |

## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.


## 2026-07-03 — Candidatos desta producao (aguardando revisao humana)

| Lesson | Skill/ferramenta alvo | Proposta |
|---|---|---|
| L01 | art/art-creation-sourcing | formalizar `prompt_pack` como saida padrao quando canal IA = blocked |
| L02 | art/concept-art-direction + prompt pack | prompts de personagem pedem anatomia realista e declaram compressao pixel como etapa |
| L03 | art gates | classificar texto emergente como aceito_diegetico/rejeitado |
| L04 | art/art-translation-to-vdp | script canonico de contact sheet VDP (320x224+15c+9bit) como gate |
| L06 | tools/sgdk_wrapper validators | varredura pwsh/Linux (chips task_0721942b, task_7b255b45, task_1e7be1cf) |
| L07 | audit_game_design_contracts | status design_contracts_ready em planejamento (chip task_1e7be1cf) |

Nenhuma promocao automatica: `canonical_auto_mutation=false`; revisao humana obrigatoria.

## 2026-07-29 — Promocao humana aplicada

| Lesson | Skill/ferramenta alvo | Decisao | Evidencia |
|---|---|---|---|
| L11/L12 | `sgdk-build-wrapper-operator`, `production-diagnostic-triage`, `preflight_host.ps1`, `select_sgdk_build_route.py` | `promoted_with_explicit_human_authorization` | `out/logs/sgdk_build_route_report.json`, `out/logs/linux_wine_build_report.json`, ROM SHA-256 `8ed8f28b...434d`, regressao 5/5 |

A promocao e limitada ao roteamento/diagnostico de build. Nao promove a ROM a
`testado_em_emulador`, nao valida gameplay/arte/audio/performance e nao torna
outros candidatos automaticamente aprovados.
