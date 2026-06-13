# Skills Metadata Policy

Esta arvore contem a fonte canonica das skills do framework MegaDrive_DEV.

## Politica de `openai.yaml`

- `allow_implicit_invocation: true`
  - use apenas em skills com escopo operacional claro e baixo risco de disparo indevido
  - exemplos: diagnostico de arte, conversao de assets, budget de VDP, arquitetura de estados

- `allow_implicit_invocation: false`
  - use em skills de governanca, auditoria, roteamento, status ou sourcing externo
  - use tambem quando o disparo implicito puder levar o agente para um workflow mais caro ou mais invasivo do que o pedido do usuario

## Fonte de verdade

- skills canonicas: `tools/sgdk_wrapper/.agent/skills`
- ponte repo-native para descoberta pelo Codex: `.agents/skills`

Nao duplique nem edite skills em dois lugares.

## Politica de descricao em `SKILL.md`

A descricao frontmatter decide o matching implicito. Portanto cada skill deve declarar:

- quando deve disparar
- quando nao deve disparar
- qual trabalho ela faz melhor do que as skills vizinhas

Descricoes vagas como "ajuda com arte" ou "cuida do projeto" sao proibidas.
