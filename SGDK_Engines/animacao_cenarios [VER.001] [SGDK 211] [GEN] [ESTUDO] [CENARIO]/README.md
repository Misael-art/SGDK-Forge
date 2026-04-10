# animacao_cenarios [VER.001] [SGDK 211] [GEN] [ESTUDO] [CENARIO]

Este diretorio agora e um **pacote canonico de referencia** para estudo da
rotina de animacao de cenarios. O snapshot preservado aqui nao compila sozinho
porque depende de recursos e headers gerados (`cenarios_res.h`) que nao vieram
junto com a extracao.

## O que existe aqui

- `snapshot/source/cenarios.c`: implementacao original
- `snapshot/source/include/`: headers originais do modulo
- `doc/`: explicacao de uso, limites e caminho de integracao

## Como usar no ecossistema

- `build.bat`, `run.bat` e `rebuild.bat` respondem de forma segura e explicativa
- o wrapper central identifica este pacote como referencia pedagogica
- a documentacao orienta em que tipo de projeto este modulo deve ser acoplado

## Quando este pacote e util

- para entender como um fundo animado e trocado via tilemap
- para estudar a assinatura das funcoes `CEN_init`, `CEN_Anima` e `CEN_AnimaEx`
- para extrair a logica e adaptar em engines maiores como HAMOOPIG/KOF94
