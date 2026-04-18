# 02 - Build Wrapper

Este projeto nasce acoplado ao `sgdk_wrapper`.

## Proposito

- centralizar bootstrap de ambiente;
- validar recursos;
- preparar assets brutos automaticamente;
- manter o fluxo replicavel entre projetos.

## Como atua

1. `build.bat` localiza o wrapper.
2. `sgdk_wrapper_env.bat` ativa os modos canonicamente recomendados.
3. `tools/sgdk_wrapper/build.bat` resolve o contexto do projeto.
4. `prepare_assets.py` atua sobre `res/` e `res/data/`.
5. `validate_resources.ps1` confirma compatibilidade SGDK.
6. O `makefile.gen` do SGDK compila a ROM.

## Flags padrao deste modelo

- `SGDK_AUTO_PREPARE_ASSETS=1`
- `SGDK_AUTO_FIX_RESOURCES=1`

