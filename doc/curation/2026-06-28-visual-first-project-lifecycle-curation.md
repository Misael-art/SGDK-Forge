# Curadoria 2026-06-28 - Visual-first project lifecycle

Status: `curated_framework_no_rom`.

## Escopo auditado

- `SGDK_projects/_agent_laboratory`
- `SGDK_projects/_agent_training`
- `SGDK_projects/BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]`
- `SGDK_projects/Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`
- `SGDK_projects/Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`
- `SGDK_projects/SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]`

## Parecer por estagio

| Projeto | Estagio honesto | Sinal positivo | Bloqueio principal |
|---|---|---|---|
| `_agent_laboratory` | area de laboratorio agregada, nao projeto de entrega | possui arte e fixtures locais | falta contexto/metodologia/higiene de projeto raiz |
| `_agent_training` | area controlada de treino, nao projeto de entrega | contem licoes e casos visuais uteis | raiz agregadora nao deve declarar AAA; licoes precisam promocao humana |
| `BLUE_CIRCUIT` | `aaa_game` em pre-runtime visual-first | contexto, metodologia e higiene passam; fonte premium e gates humanos orientam a rota | runtime ainda bloqueado por conversao VDP, budget, BlastEm/freshness e closeout |
| `Celestial Chase Revive` | `aaa_game` com runtime tecnico, mas criatividade bloqueada | rotas BlastEm e first playable tecnico existem | `visual_gate_blocked`; assets atuais ainda nao correspondem a entrega visual AAA |
| `Celestial Chase visual benchmark` | `technical_demo`/laboratorio visual avancado | provou movimento, budget e captura BlastEm em varias iteracoes | `perceptual_motion_unvalidated` e higiene de input externo ainda bloqueiam promocao |
| `SMOKE_TEST` | smoke/lab estrutural | higiene passa e assets de branding existem | contexto ausente, metodologia invalida e muitos blockers de closeout |

## Comparacao BLUE_CIRCUIT x Celestial Chase Revive

`BLUE_CIRCUIT` avancou melhor porque entrou em uma rota visual-first: GDD/spec
declararam identidade, fonte premium, plano de aprovacao humana, visual route,
blocked runtime e atalhos proibidos antes de tentar transformar o jogo em
runtime final. Isso reduziu diagnostico repetido e impediu que placeholder
procedural virasse entrega por inercia.

`Celestial Chase Revive` acumulou evidencia tecnica real, mas gastou muitas
iteracoes em seed, placeholders, build, rota, input e correcao de erro antes de
fechar uma direcao visual autoral. O resultado correto e reconhecer o valor do
runtime tecnico, mas manter `creative_quality=blocked` ate fonte premium,
conversao VDP, aprovacao perceptual e visual delivery gate fecharem.

## Licoes canonicas

1. Projeto `aaa_game` deve nascer com front-end, cena assinatura e asset critico
   tratados como risco visual primario, nao como acabamento posterior.
2. Runtime antes da rota visual so pode ser smoke tecnico com teto explicito;
   se o projeto continuar nele por inercia, o agente entra em loop caro.
3. Fonte premium aprovada, mesmo ainda sem conversao, economiza tokens porque
   reduz exploracao solta e estabiliza o vocabulario visual do projeto.
4. Arte tecnicamente valida pode continuar reprovada se nao tiver leitura,
   identidade, material, profundidade e funcao de gameplay.
5. Movimento critico precisa evidencia temporal e aprovacao perceptual; uma
   screenshot nao prova animacao, acting, impacto ou fluidez.
6. Laboratorio e treino sao fontes de heuristica, nao prova de entrega; a
   promocao canonica exige revisao humana, patch controlado e regressao.

## Curadoria aplicada

- novo workflow canonico `visual-first-project-lifecycle.md`;
- reforco no `production-loop` para usar esse workflow antes de runtime em
  projeto novo, reseed, amadurecimento, revisao e closeout AAA;
- reforco em `visual-excellence-standards` para transformar o contraste
  BLUE_CIRCUIT/Celestial em regra operacional;
- reforco em `sgdk-build-wrapper-operator` para impedir novo build quando o
  blocker dominante for visual e a mudanca nao atacar fonte, conversao ou gate.

## Limite factual

Nenhum projeto, asset ou ROM foi promovido. Nenhuma nova sessao BlastEm foi
executada por esta curadoria. Os reports gerados em `out/curation/` servem como
evidencia de auditoria local e nao substituem closeout de projeto.
