# Arquitetura

## Estrutura principal

- `../../upstream/streeter/UTIL/test_proj/src/`: codigo C do jogo
- `../../upstream/streeter/UTIL/test_proj/inc/`: headers do projeto
- `../../upstream/streeter/UTIL/test_proj/res/`: recursos usados pelo ResComp
- `../../upstream/streeter/UTIL/test_proj/out/`: artefatos gerados pelo build
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

- Codigo novo entra em `../../upstream/streeter/UTIL/test_proj/src/` e `../../upstream/streeter/UTIL/test_proj/inc/`
- Recurso novo entra em `../../upstream/streeter/UTIL/test_proj/res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `../../upstream/streeter/UTIL/test_proj/out/`
