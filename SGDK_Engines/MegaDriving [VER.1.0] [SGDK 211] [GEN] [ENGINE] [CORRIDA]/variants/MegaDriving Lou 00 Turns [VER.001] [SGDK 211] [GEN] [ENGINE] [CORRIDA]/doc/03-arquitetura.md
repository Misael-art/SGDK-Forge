# Arquitetura

## Estrutura principal

- `../../upstream/lou/00_turns/src/`: codigo C do jogo
- `../../upstream/lou/00_turns/inc/`: headers do projeto
- `../../upstream/lou/00_turns/res/`: recursos usados pelo ResComp
- `../../upstream/lou/00_turns/out/`: artefatos gerados pelo build
- `.mddev/project.json`: manifesto de estrutura
- `doc/`: conhecimento tecnico e operacional

## Intencao da arquitetura

Esta divisao deixa explicito o que e:

- codigo editavel
- recurso bruto
- artefato gerado
- documentacao
- configuracao estrutural

## Como evoluir sem baguncar

- Codigo novo entra em `../../upstream/lou/00_turns/src/` e `../../upstream/lou/00_turns/inc/`
- Recurso novo entra em `../../upstream/lou/00_turns/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/lou/00_turns/out/`
