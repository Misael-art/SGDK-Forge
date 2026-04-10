# PlatformerEngine Core [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]

Esta e a entrada canonica buildavel da colecao `PlatformerEngine Toolkit`.
Ela usa layout `nested`: a pasta atual serve para leitura, build e execucao,
mas o SGDK root real fica em `../../upstream/PlatformerEngine`.

## Estrutura desta variante

```text
PlatformerEngine Core/
  .mddev/project.json
  doc/
  ../../upstream/PlatformerEngine/
    src/
    inc/
    res/
    out/
  build.bat
  clean.bat
  run.bat
  rebuild.bat
```

## Regra pratica

- Rode os wrappers por esta pasta.
- Edite o codigo e os recursos em `../../upstream/PlatformerEngine/`.
- Use `../../upstream/Level/` como referencia de dados de fase.
- Consulte `doc/README.md` antes de mexer na arquitetura.
