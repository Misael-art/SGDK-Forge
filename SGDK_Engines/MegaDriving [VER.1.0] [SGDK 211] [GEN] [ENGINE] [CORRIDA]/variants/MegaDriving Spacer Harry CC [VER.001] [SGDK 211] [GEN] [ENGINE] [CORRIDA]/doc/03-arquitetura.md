# Arquitetura

## Estrutura principal

- `../../upstream/spacer/SpacerHarryCC/src/`: codigo C do jogo
- `../../upstream/spacer/SpacerHarryCC/inc/`: headers do projeto
- `../../upstream/spacer/SpacerHarryCC/res/`: recursos usados pelo ResComp
- `../../upstream/spacer/SpacerHarryCC/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/spacer/SpacerHarryCC/src/` e `../../upstream/spacer/SpacerHarryCC/inc/`
- Recurso novo entra em `../../upstream/spacer/SpacerHarryCC/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/spacer/SpacerHarryCC/out/`
