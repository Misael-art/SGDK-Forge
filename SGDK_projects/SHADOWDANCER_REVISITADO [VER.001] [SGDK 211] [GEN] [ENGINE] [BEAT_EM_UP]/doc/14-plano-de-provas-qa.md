# Plano de provas QA

## Gate tecnico

- [ ] `validate_project_name.ps1` passa.
- [ ] contexto, metodologia e higiene passam.
- [ ] art diagnostic sem blocker ativo.
- [ ] rescomp e compilacao usam `sdk/sgdk-2.11` pelo wrapper.
- [ ] nenhum `malloc`, `free`, `float` ou `double` em `src`.
- [ ] nenhum `DMA_transfer(DMA, ...)` em callback de gameplay; uploads usam fila.
- [ ] `validate_resources.ps1` passa.

## Gate de runtime

- [ ] ROM inicia no BlastEm.
- [ ] player responde a direcional, A, B e C.
- [ ] camera chega ao limite sem mostrar area fora do mapa.
- [ ] colisao nao acessa tile fora dos limites.
- [ ] scroll agressivo nao perde tiles visiveis.
- [ ] 60 fps e audio permanecem nao provados ate existir evidencia especifica; audio nao faz parte deste slice.

## Status atual

O projeto pode ser promovido a `buildado_emulator_pending` somente apos build real. Sem captura BlastEm, nao usar `testado_em_emulador` ou `pronto`.
