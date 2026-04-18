# Build e Wrapper

Este projeto nao carrega logica de build propria.
Os scripts `build.bat`, `clean.bat`, `run.bat` e `rebuild.bat` apenas delegam
ao wrapper central em `tools/sgdk_wrapper/`.

## Por que isso e importante

- Evita que cada projeto reinvente a mesma logica
- Permite corrigir bugs uma vez so
- Mantem consistencia entre engines, jogos e templates
- Facilita migracoes de SGDK e padronizacoes de ambiente

## Fluxo resumido

1. O script local chama o wrapper central
2. O wrapper resolve o projeto via `.mddev/project.json` ou heuristica
3. O ambiente SGDK e carregado
4. Recursos e codigo sao validados
5. O `makefile.gen` do SGDK compila o projeto

## Regra de ouro

Nunca adicione logica de build nos scripts locais do projeto.
Se algo precisar mudar para todos os projetos, a alteracao deve ser feita em
`F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper`.

