# Arquitetura

## Estrutura principal

- `../../upstream/lou/experimental/src/`: codigo C do jogo
- `../../upstream/lou/experimental/inc/`: headers do projeto
- `../../upstream/lou/experimental/res/`: recursos usados pelo ResComp
- `../../upstream/lou/experimental/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/lou/experimental/src/` e `../../upstream/lou/experimental/inc/`
- Recurso novo entra em `../../upstream/lou/experimental/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/lou/experimental/out/`
