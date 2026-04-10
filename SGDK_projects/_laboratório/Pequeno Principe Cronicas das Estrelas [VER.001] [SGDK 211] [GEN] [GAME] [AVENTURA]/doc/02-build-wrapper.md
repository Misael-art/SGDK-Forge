# 02 - Build Wrapper

Este projeto nao tem scripts de build proprios. Tudo delega ao wrapper central.

## Entrada canonica

- `build.bat`
- `run.bat`
- `clean.bat`
- `rebuild.bat`

## O que o wrapper faz

- resolve path seguro no Windows
- aplica validacoes de recurso
- roda o fluxo SGDK 211
- reaproveita correcoes genericas do workspace

## Estado atual

- `build.bat` validado com sucesso neste slice
- `resources.res` mantido enxuto porque os placeholders atuais sao gerados por codigo
- qualquer correcao de build generica deve ir para `tools/sgdk_wrapper`, nao para este projeto
