# Arquitetura

## Estrutura principal

- `../../upstream/streeter/02_curvy/src/`: codigo C do jogo
- `../../upstream/streeter/02_curvy/inc/`: headers do projeto
- `../../upstream/streeter/02_curvy/res/`: recursos usados pelo ResComp
- `../../upstream/streeter/02_curvy/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/streeter/02_curvy/src/` e `../../upstream/streeter/02_curvy/inc/`
- Recurso novo entra em `../../upstream/streeter/02_curvy/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/streeter/02_curvy/out/`
