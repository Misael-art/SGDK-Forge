# Arquitetura

## Estrutura principal

- `src/`: codigo C do jogo
- `inc/`: headers do projeto
- `res/`: recursos usados pelo ResComp
- `out/`: artefatos gerados pelo build
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

- Codigo novo entra em `src/` e `inc/`
- Recurso novo entra em `res/` com subpastas coerentes
- Relatorios, notas e guias entram em `doc/`
- Nada gerado manualmente deve viver fora de `out/`
