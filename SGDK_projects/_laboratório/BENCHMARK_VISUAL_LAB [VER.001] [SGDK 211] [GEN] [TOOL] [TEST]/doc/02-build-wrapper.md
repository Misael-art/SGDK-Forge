# 02 - Build Wrapper

Este projeto nao tem scripts de build proprios. Tudo delega ao wrapper central.

## Entrada canonica

- `build.bat`
- `run.bat`
- `clean.bat`
- `rebuild.bat`

## O que o wrapper faz

- resolve path seguro no Windows (incluindo nomes com colchetes)
- aplica validacoes de recurso
- roda o fluxo SGDK 2.11
- reaproveita correcoes genericas do workspace

## Estado atual

- `build.bat` delega a `tools/sgdk_wrapper/build.bat`
- qualquer correcao de build generica deve ir para `tools/sgdk_wrapper`, nao para este projeto

