# Arquitetura

## Estrutura principal

- `../../upstream/lou/03_hilly_road/src/`: codigo C do jogo
- `../../upstream/lou/03_hilly_road/inc/`: headers do projeto
- `../../upstream/lou/03_hilly_road/res/`: recursos usados pelo ResComp
- `../../upstream/lou/03_hilly_road/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/lou/03_hilly_road/src/` e `../../upstream/lou/03_hilly_road/inc/`
- Recurso novo entra em `../../upstream/lou/03_hilly_road/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/lou/03_hilly_road/out/`
