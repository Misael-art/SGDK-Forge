# Arquitetura

## Estrutura principal

- `../../upstream/spacer/SpacerHarry/src/`: codigo C do jogo
- `../../upstream/spacer/SpacerHarry/inc/`: headers do projeto
- `../../upstream/spacer/SpacerHarry/res/`: recursos usados pelo ResComp
- `../../upstream/spacer/SpacerHarry/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/spacer/SpacerHarry/src/` e `../../upstream/spacer/SpacerHarry/inc/`
- Recurso novo entra em `../../upstream/spacer/SpacerHarry/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/spacer/SpacerHarry/out/`
