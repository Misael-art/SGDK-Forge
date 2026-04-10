# PlatformerEngine Toolkit [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]

Esta pasta agora e a colecao canonica do pacote `PlatformerEngine` dentro do
MegaDrive_DEV. Ela nao representa uma ROM unica: aqui reunimos a engine SGDK
buildavel, a ferramenta auxiliar de pipeline e os assets de nivel preservados
do repositorio original de Gerard Gascon.

## Como usar esta colecao

1. Leia `doc/README.md`.
2. Para compilar a engine, entre em `variants/PlatformerEngine Core ...`.
3. Para estudar o pipeline de conversao de mapas, abra
   `companions/ImageToGameMap ...`.
4. Para consultar o upstream sem alterar a apresentacao canonica, use
   `upstream/`.

## O que existe aqui

- `variants/`: pontos de entrada canonicos para itens buildaveis
- `companions/`: ferramentas auxiliares e componentes de host
- `upstream/`: codigo e assets preservados do repositorio original
- `doc/`: guias pedagogicos, organizacao e contexto tecnico

## Regra de nomenclatura para este tipo de pacote

- A raiz agregadora usa um nome semantico como `Toolkit` e o marcador
  `[COLLECTION]`.
- A parte SGDK compilavel ganha uma entrada propria com `[ENGINE]`.
- Ferramentas auxiliares de host ganham uma entrada propria com `[HOST] [TOOL]`.

## O que nao fazer

- Nao tente compilar a raiz desta colecao como se fosse um projeto SGDK unico.
- Nao edite os wrappers locais para colocar logica; toda a automacao continua em
  `tools/sgdk_wrapper/`.
- Nao reorganize `upstream/` sem registrar a decisao em `doc/`.

## Material preservado

O README original, a licenca original e a documentacao gerada na primeira
canonicalizacao foram preservados em `doc/reference/`.
