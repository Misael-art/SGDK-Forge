# Arquitetura

## Estrutura principal

- `../../upstream/streeter/03_luts/src/`: codigo C do jogo
- `../../upstream/streeter/03_luts/inc/`: headers do projeto
- `../../upstream/streeter/03_luts/res/`: recursos usados pelo ResComp
- `../../upstream/streeter/03_luts/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/streeter/03_luts/src/` e `../../upstream/streeter/03_luts/inc/`
- Recurso novo entra em `../../upstream/streeter/03_luts/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/streeter/03_luts/out/`
