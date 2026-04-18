# 02 - Build Wrapper

SGDK-Forge nao tem scripts de build proprios. Tudo delega ao wrapper central.

## Entrada canonica

- `build.bat`
- `run.bat`
- `clean.bat`
- `rebuild.bat`

## O que o wrapper faz

- resolve caminhos seguros no Windows;
- aplica validacoes de recurso antes do `rescomp`;
- promove assets de `data/` para `res/` de forma auditavel;
- reaproveita correcos genericas do workspace;
- executa o fluxo SGDK 2.11 de forma consistente.

## Estado atual

- `build.bat` delega ao `tools/sgdk_wrapper/build.bat`;
- qualquer correcao generica deve ir para `tools/sgdk_wrapper`, nao para o projeto;
- o comportamento padrao do build e controlado por `sgdk_wrapper_env.bat`.
