# Arquitetura

## Estrutura principal

- `../../upstream/spacer/SpacerHarry2/src/`: codigo C do jogo
- `../../upstream/spacer/SpacerHarry2/inc/`: headers do projeto
- `../../upstream/spacer/SpacerHarry2/res/`: recursos usados pelo ResComp
- `../../upstream/spacer/SpacerHarry2/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/spacer/SpacerHarry2/src/` e `../../upstream/spacer/SpacerHarry2/inc/`
- Recurso novo entra em `../../upstream/spacer/SpacerHarry2/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/spacer/SpacerHarry2/out/`
