# KOF94 HAMOOPIG MINIMALIST [VER.001] [SGDK 211] [GEN] [ENGINE] [LUTA]

Este projeto usa um layout canonico **nested** no MegaDrive_DEV.
A pasta atual e o ponto de entrada para leitura, build e execucao, mas o
**SGDK root real** fica em `KOF94`.

---

## Estrutura do Projeto

```text
projeto/
  .mddev/
    project.json          # Manifesto que aponta para o SGDK root real
  .vscode/                # Configuracao do editor apontando para o projeto real
  doc/                    # Documentacao tecnica e onboarding
    assets/               # Material visual de referencia
    reference/            # Documentos historicos e readmes legados
  KOF94/          # SGDK root real
    src/                  # Codigo C do projeto
    res/                  # Recursos do ResComp
    inc/                  # Headers do projeto
    out/                  # ROM e artefatos gerados
    .sgdk_migration_state.json
  build.bat               # Compila via wrapper central
  clean.bat               # Limpa artefatos
  run.bat                 # Recompila se preciso e abre o emulador
  rebuild.bat             # Clean + build
  .gitignore              # Ignora artefatos gerados dentro de KOF94/
  README.md               # Este arquivo
```

## Regra pratica

- Rode `build.bat`, `clean.bat`, `run.bat` e `rebuild.bat` pela raiz do projeto.
- Edite codigo e recursos dentro de `KOF94/`.
- Consulte `doc/README.md` para a ordem de leitura recomendada.
- Use a configuracao de editor em `.vscode/` na raiz, nao dentro de `KOF94/`.
- Melhorias genericas de build ficam em `tools/sgdk_wrapper/`.
- Material ambiguo, legado ou solto deve ir para `archives/manual_review/`.

## Fluxo rapido

1. Leia `doc/README.md`.
2. Abra `KOF94/src/main.c`.
3. Rode `build.bat`.
4. Rode `run.bat`.

Se a ROM nao existir ou estiver desatualizada, `run.bat` tenta recompilar antes
de abrir o emulador. Se o build falhar, o wrapper para com diagnostico em vez de
rodar uma ROM antiga e enganosa.
