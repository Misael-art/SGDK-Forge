# Arquitetura

## Estrutura principal

- `../../upstream/lou/05_sprites/src/`: codigo C do jogo
- `../../upstream/lou/05_sprites/inc/`: headers do projeto
- `../../upstream/lou/05_sprites/res/`: recursos usados pelo ResComp
- `../../upstream/lou/05_sprites/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/lou/05_sprites/src/` e `../../upstream/lou/05_sprites/inc/`
- Recurso novo entra em `../../upstream/lou/05_sprites/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/lou/05_sprites/out/`
