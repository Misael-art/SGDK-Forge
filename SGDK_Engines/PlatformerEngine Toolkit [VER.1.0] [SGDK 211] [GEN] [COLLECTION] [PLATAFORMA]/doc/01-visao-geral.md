# Visao Geral

`PlatformerEngine Toolkit` existe para resolver um problema de organizacao:
o repositorio original mistura pelo menos tres camadas diferentes em uma unica
raiz.

## Camadas presentes no upstream

- `PlatformerEngine`: a engine SGDK compilavel
- `ImageToGameMap`: a ferramenta Unity usada no pipeline de mapas
- `Level`: assets de nivel e dados de exemplo

## Decisao aplicada no MegaDrive_DEV

Em vez de fingir que tudo isso e um unico projeto SGDK, a raiz passou a ser
uma colecao canonica com:

- uma entrada buildavel em `variants/`
- uma entrada de ferramenta em `companions/`
- o material original preservado em `upstream/`

Essa separacao deixa o uso pedagogico muito mais claro para quem esta
aprendendo e evita que o wrapper tente tratar uma ferramenta Unity como se ela
fosse uma ROM de Mega Drive.
