# Workflow: Project Opening

Use este fluxo sempre que um agente receber um pedido de iniciar trabalho em um projeto SGDK e ainda nao estiver claro se o contexto e:

- continuidade de projeto existente
- reseed parcial de projeto existente
- fundacao de projeto novo

Nenhum agente deve abrir arte, runtime, assets ou claims de estrutura antes de classificar corretamente uma dessas 3 situacoes.

Depois da classificacao, o agente deve abrir `workflows/route-decision-gate.md` sempre que a primeira entrega ainda nao tiver rota tecnica, skill dona e ferramenta inicial declaradas.

---

## Objetivo

Evitar dois erros caros:

1. tratar projeto existente como se estivesse nascendo do zero
2. tratar projeto novo como se ja tivesse briefing, GDD e spec suficientes

O protocolo existe para forcar um gate curto de entendimento antes da execucao.

---

## Passo 0. Classificar o tipo de abertura

### A. Projeto existente

Trate como `projeto_existente` quando houver evidencias suficientes de contexto operacional, por exemplo:

- pasta de projeto SGDK materializada
- `doc/10-memory-bank.md` com historico real
- `doc/11-gdd.md` e/ou `doc/13-spec-cenas.md` coerentes
- `out/logs/validation_report.json`, `emulator_session.json` ou changelog rastreavel
- codigo, resources e cenas ja existentes

Acao:

- ler a hierarquia de verdade
- resumir o estado atual
- detectar drift entre docs, codigo e evidencias
- perguntar apenas o necessario para continuar a iteracao atual
- se a iteracao apontar para cena `aaa_layered`, abrir cedo `workflows/scene-architecture-triage.md` antes de arte/runtime

Nao reabrir briefing do zero sem sinal concreto de que o usuario quer reseed.

### B. Reseed de projeto existente

Trate como `reseed` quando o projeto existe, mas o escopo atual nao cabe mais nos docs vigentes ou quando o usuario quer redefinir a base conceitual.

Sinais comuns:

- o usuario pede "refazer do zero" mantendo o nome ou parte do historico
- GDD/spec nao explicam mais o objetivo atual
- o projeto anterior serviu como aprendizado, mas a nova versao sera outro baseline

Acao:

- preservar o historico como referencia
- separar claramente `aprendizado herdado` de `escopo vigente`
- usar `planning/game-design-planning` para emitir novos seeds
- nao reciclar automaticamente estruturas, cenas ou claims da versao anterior

### C. Projeto novo

Trate como `projeto_novo` quando nao houver base documental suficiente ou quando o diretor pedir explicitamente a fundacao do zero.

Acao:

- parar antes de runtime
- abrir questionario de fundacao
- emitir seeds documentais minimos
- emitir `route_decision_record` para o primeiro slice antes de qualquer arte/runtime
- so depois abrir estrutura de projeto

---

## Passo 1. Questionario minimo de fundacao

Quando a classificacao for `projeto_novo` ou `reseed`, o agente deve obter no minimo:

1. natureza essencial do projeto
2. primeiro slice obrigatorio
3. eixos obrigatorios ja na fundacao
4. tom do front-end inicial
5. regra de progresso e validacao por etapa
6. regra de canonizacao de curadoria

Se esses 6 pontos ainda nao estiverem claros, o agente nao deve improvisar GDD completo.

---

## Passo 2. Artefatos minimos antes de codigo

Para `projeto_novo` ou `reseed`, a abertura so passa quando existir fundacao documental minima contendo:

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `front_end_profile`
- `route_decision_record` do primeiro slice

Mapeamento recomendado:

- `doc/11-gdd.md`
  - `project_brief`
  - `core_loop_statement`
  - `feature_scope_map`
  - `front_end_profile`
- `doc/13-spec-cenas.md`
  - `scene_roadmap`
  - `first_playable_slice`
  - `route_decision_record`

Regra:

- projeto novo nao deve comecar por conversao de imagem, runtime ou depuracao visual
- primeiro deve existir decisao de rota: `planning`, `art_diagnostic`, `curated_builder`, `source_translation`, `conversion_batch`, `scene_architecture`, `budget`, `runtime` ou `validation`
- quando a cena tiver pack grande, parallax, foreground/oclusao, stage largo ou relacao forte sprite/cenario, `scene_architecture_triage` nasce junto do `route_decision_record`

Se o projeto ja for operacional, esses blocos podem ser revalidados em vez de recriados.

---

## Passo 3. Regra de continuidade

Quando a classificacao for `projeto_existente`, o agente deve preferir:

- continuar a iteracao vigente
- pedir confirmacoes curtas
- preservar nomenclatura, contratos e memoria operacional ja aceitos

Perguntas de abertura para projeto existente devem focar em:

- o que mudou desde o ultimo estado valido
- qual entrega atual deve ser perseguida
- quais blockers ou aprendizados recentes precisam guiar a iteracao

Se a entrega atual envolver cena com base + foreground/oclusao + relacao forte entre sprite e cenario, a abertura tambem deve produzir:

- `scene_profile`
- `baseline_technique_applicability`
- `baseline_decision`
- `reference_implementation` quando houver referencia interna forte

O template recomendado para isso e:

- `workflows/scene-architecture-triage.md`

---

## Passo 4. Regra de curadoria

Aprendizado observado durante a execucao nao vira canon automaticamente.

Fluxo correto:

1. registrar como aprendizado operacional local
2. validar em build/evidencia quando aplicavel
3. obter aprovacao humana quando a curadoria alterar comportamento canonico
4. so entao promover para workflow, skill, regra, `lib_case` ou memoria canônica de framework

---

## Passa quando

- o agente classificou corretamente `projeto_existente`, `reseed` ou `projeto_novo`
- o nivel de perguntas foi proporcional ao caso
- projetos novos nao pularam a fundacao documental
- projetos existentes nao foram resetados sem necessidade

---

## Handoff

- `planning/game-design-planning`
  - quando for `projeto_novo` ou `reseed`
- `workflows/plan.md`
  - quando a abertura estiver classificada e a iteracao puder ser planejada
- `workflows/production-loop.md`
  - quando houver base suficiente para entrar no pipeline de producao
