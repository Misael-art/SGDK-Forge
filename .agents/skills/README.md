# Skills Metadata Policy

Esta arvore contem a fonte canonica das skills do framework MegaDrive_DEV.

## Politica de `openai.yaml`

- `allow_implicit_invocation: true`
  - use apenas em skills com escopo operacional claro e baixo risco de disparo indevido
  - exemplos: diagnostico de arte, conversao de assets, budget de VDP, arquitetura de estados

- `allow_implicit_invocation: false`
  - use em skills de governanca, auditoria, roteamento, status ou sourcing externo
  - use tambem em skills de planejamento, seed de GDD ou definicao de escopo
  - use tambem quando o disparo implicito puder levar o agente para um workflow mais caro ou mais invasivo do que o pedido do usuario

### Regras praticas

- `agents/openai.yaml` e o metadata consumido para descoberta repo-native e politica de invocacao.
- `SKILL.md` continua sendo o contrato humano e a fonte de verdade do comportamento operacional.
- Default seguro:
  - se uma skill nao tiver `agents/openai.yaml`, trate como `allow_implicit_invocation: false` ate ser explicitamente curada.
- Nunca use a ausencia de `openai.yaml` como justificativa para "skill legada" ou para limpeza estrutural.

## Fonte de verdade

- skills canonicas: `tools/sgdk_wrapper/.agent/skills`
- ponte repo-native para descoberta pelo Codex: `.agents/skills`

Nao duplique nem edite skills em dois lugares.

### Saude da ponte `.agents/skills`

- A ponte deve apontar para `tools/sgdk_wrapper/.agent/skills` (junction/symlink).
- Se a ponte existir mas estiver quebrada, ela pode falhar silenciosamente e degradar a descoberta de skills.
- O wrapper central valida isso e reporta em `validation_report.json` quando o contexto da `.agent` estiver degradado.

## Crescimento da arvore

- especializacoes de planejamento, GDD seed e scope slicing entram primeiro em `planning/`
- especializacoes de runtime entram primeiro em `code/`
- especializacoes de budget entram em `hardware/`
- especializacoes de leitura e direcao visual entram em `art/`

Regra:

- skill nova so nasce quando o gap for puro ou quando o modulo deixar de caber com clareza na skill dona atual

## Politica de descricao em `SKILL.md`

A descricao frontmatter decide o matching implicito. Portanto cada skill deve declarar:

- quando deve disparar
- quando nao deve disparar
- qual trabalho ela faz melhor do que as skills vizinhas

Descricoes vagas como "ajuda com arte" ou "cuida do projeto" sao proibidas.
