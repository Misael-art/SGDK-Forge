# MegaDriving [VER.1.0] [SGDK 211] [GEN] [ENGINE] [CORRIDA]

Esta pasta agora e a **colecao canonica** do conjunto MegaDriving dentro do
MegaDrive_DEV. Ela nao representa uma ROM unica: aqui reunimos varias
experiencias de pseudo-3D, road rendering e tecnicas de corrida para Mega
Drive, cada uma com entrada propria em `variants/`.

## Como usar esta colecao

1. Leia `doc/README.md` para entender o mapa das variantes.
2. Escolha uma pasta em `variants/`.
3. Rode `build.bat` ou `run.bat` dentro da variante desejada.
4. Edite o codigo no caminho `upstream/...` apontado pelo `README.md` da variante.

## O que existe aqui

- `variants/`: pontos de entrada canonicos, um por demo/versao
- `upstream/`: codigo e assets preservados da colecao original
- `doc/`: guias pedagogicos, mapa de familias e orientacoes de uso

## O que nao fazer

- Nao tente compilar a raiz desta colecao como se fosse um projeto unico.
- Nao edite scripts de build locais; toda logica fica em `tools/sgdk_wrapper/`.
- Nao mova ou apague conteudo de `upstream/` sem registrar a decisao em `doc/`.

## Material preservado

O README original, a nota original do workspace e a licenca do upstream foram
preservados em `doc/reference/upstream/`.
