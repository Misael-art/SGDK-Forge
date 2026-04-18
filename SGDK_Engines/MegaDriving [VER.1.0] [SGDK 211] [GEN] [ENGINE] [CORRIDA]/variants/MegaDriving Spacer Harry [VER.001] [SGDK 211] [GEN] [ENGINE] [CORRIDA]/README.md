# MegaDriving Spacer Harry [VER.001] [SGDK 211] [GEN] [ENGINE] [CORRIDA]

Este projeto usa um layout canonico **nested** no MegaDrive_DEV.
A pasta atual e o ponto de entrada para leitura, build e execucao, mas o
**SGDK root real** fica em `../../upstream/spacer/SpacerHarry`.

---

## Estrutura do Projeto

```text
projeto/
  .mddev/
    project.json          # Manifesto que aponta para o SGDK root real
  doc/                    # Documentacao tecnica e onboarding
  ../../upstream/spacer/SpacerHarry/          # SGDK root real
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
- Edite codigo e recursos dentro de `../../upstream/spacer/SpacerHarry/`.
- Consulte `doc/README.md` para a ordem de leitura recomendada.
- Melhorias genericas de build ficam em `tools/sgdk_wrapper/`.
- Material ambiguo, legado ou solto deve ir para `archives/manual_review/`.

## Fluxo rapido

1. Leia `doc/README.md`.
2. Abra `../../upstream/spacer/SpacerHarry/src/main.c`.
3. Rode `build.bat`.
4. Rode `run.bat`.

Se a ROM nao existir ou estiver desatualizada, `run.bat` tenta recompilar antes
de abrir o emulador. Se o build falhar, o wrapper para com diagnostico em vez de
rodar uma ROM antiga e enganosa.

## Contexto da Variante

- Familia: `Spacer`
- SGDK root preservado: `upstream/spacer/SpacerHarry`
- Foco pedagogico: Variante inspirada em Space Harrier, com foco em perspectiva e objetos vindo ao jogador.
