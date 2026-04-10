# Trigonometry Projetil [VER.250221] [SGDK 211] [GEN] [ESTUDO] [TRIGONOMETRIA]

Este projeto usa um layout canonico **nested** no MegaDrive_DEV.
A pasta atual e o ponto de entrada para leitura, build e execucao, mas o
**SGDK root real** fica em `trigonometry_v250221`.

---

## Estrutura do Projeto

```text
projeto/
  .mddev/
    project.json          # Manifesto que aponta para o SGDK root real
  doc/                    # Documentacao tecnica e onboarding
  trigonometry_v250221/          # SGDK root real
    src/                  # Codigo C do projeto
    res/                  # Recursos do ResComp
    inc/                  # Headers do projeto
    out/                  # ROM e artefatos gerados
  build.bat               # Compila via wrapper central
  clean.bat               # Limpa artefatos
  run.bat                 # Recompila se preciso e abre o emulador
  rebuild.bat             # Clean + build
  README.md               # Este arquivo
```

## Regra pratica

- Rode `build.bat`, `clean.bat`, `run.bat` e `rebuild.bat` pela raiz do projeto.
- Edite codigo e recursos dentro de `trigonometry_v250221/`.
- Consulte `doc/README.md` para a ordem de leitura recomendada.
- Melhorias genericas de build ficam em `tools/sgdk_wrapper/`.
- Material ambiguo, legado ou solto deve ir para `archives/manual_review/`.

## Fluxo rapido

1. Leia `doc/README.md`.
2. Abra `trigonometry_v250221/src/main.c`.
3. Rode `build.bat`.
4. Rode `run.bat`.

Se a ROM nao existir ou estiver desatualizada, `run.bat` tenta recompilar antes
de abrir o emulador. Se o build falhar, o wrapper para com diagnostico em vez de
rodar uma ROM antiga e enganosa.
