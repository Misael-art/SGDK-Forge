# Build e Wrapper

Os scripts desta pasta nao tem logica propria. Eles apenas delegam ao wrapper
central em `tools/sgdk_wrapper/`.

## Fluxo rapido

1. `build.bat` compila a ROM.
2. `run.bat` recompila se preciso e abre o emulador.
3. `clean.bat` limpa artefatos no SGDK root real.
4. `rebuild.bat` faz limpeza seguida de build.

## Onde a ROM aparece

- `../../upstream/PlatformerEngine/out/rom.bin`
