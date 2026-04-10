# Arquitetura

## Estrutura principal

- `../../upstream/streeter/04_drive/src/`: codigo C do jogo
- `../../upstream/streeter/04_drive/inc/`: headers do projeto
- `../../upstream/streeter/04_drive/res/`: recursos usados pelo ResComp
- `../../upstream/streeter/04_drive/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/streeter/04_drive/src/` e `../../upstream/streeter/04_drive/inc/`
- Recurso novo entra em `../../upstream/streeter/04_drive/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/streeter/04_drive/out/`
