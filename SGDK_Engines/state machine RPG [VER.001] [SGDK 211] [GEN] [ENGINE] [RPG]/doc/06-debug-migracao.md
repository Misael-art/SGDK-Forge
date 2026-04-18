# Debug e Migracao

## Onde olhar quando algo falha

- terminal do build
- `build_output.log`
- `build_debug.log`
- `validation_report.json`

## Erros comuns

- `GDK not defined`
- erro de transparencia em PNG
- API deprecada entre versoes do SGDK
- referencia faltando no linker
- dimensao incorreta em recursos de sprite

## Como pensar a investigacao

1. Descobrir se o erro e de ambiente, recurso ou codigo
2. Ver se o wrapper ja sabe corrigir esse problema
3. Se for algo generico, corrigir no wrapper central
4. Se for algo especifico do projeto, documentar nesta pasta

## Migracoes SGDK

Se este projeto nasceu em SGDK antigo, mantenha um registro claro:

- API antiga
- API nova
- arquivo afetado
- impacto funcional

Isso evita retrabalho e ajuda quem for revisar ou portar o projeto depois.
