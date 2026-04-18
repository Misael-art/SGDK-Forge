# Arquitetura

## Estrutura principal

- `../../upstream/lou/02_hills/src/`: codigo C do jogo
- `../../upstream/lou/02_hills/inc/`: headers do projeto
- `../../upstream/lou/02_hills/res/`: recursos usados pelo ResComp
- `../../upstream/lou/02_hills/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/lou/02_hills/src/` e `../../upstream/lou/02_hills/inc/`
- Recurso novo entra em `../../upstream/lou/02_hills/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/lou/02_hills/out/`
