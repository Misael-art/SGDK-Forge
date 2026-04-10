# Material de Referencia e Curadoria

Este projeto passou por uma organizacao manual para separar claramente:

- o que e **operacional** para build e execucao
- o que e **referencia historica**
- o que e **legado ambiguo** que deve ficar em arquivo para validacao manual

## O que foi mantido no SGDK root real

Em `KOF94/` ficam apenas os itens tecnicos do projeto:

- `src/`
- `res/`
- `inc/` quando existir
- `out/`
- `.sgdk_migration_state.json`

## O que foi promovido para a documentacao

- PDF tecnico original
- readmes historicos em portugues e ingles
- imagens de branding e lineart

Esses materiais agora vivem em `doc/reference/` e `doc/assets/`.

## O que foi mandado para arquivo manual

- atalhos `.lnk` de fluxo antigo
- wrappers redundantes dentro de `KOF94/`
- arquivos de emulador indevidamente misturados ao `out/`

Tudo isso foi preservado em `archives/manual_review/` para rastreabilidade.
