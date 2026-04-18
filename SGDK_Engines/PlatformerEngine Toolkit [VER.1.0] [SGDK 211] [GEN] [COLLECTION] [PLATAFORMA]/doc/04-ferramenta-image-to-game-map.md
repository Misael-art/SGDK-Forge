# Ferramenta ImageToGameMap

`ImageToGameMap` nao e um projeto SGDK. Ele e um componente de host feito em
Unity para apoiar a preparacao de mapas.

## Papel no ecossistema

- acelerar a conversao de dados de mapa
- servir como referencia de pipeline para plataformas 2D
- mostrar a separacao entre runtime do console e ferramentas de apoio

## Onde ficou

- entrada canonica: `companions/ImageToGameMap [VER.1.0] [HOST] [TOOL] [PIPELINE]`
- conteudo original: `upstream/ImageToGameMap`

## Regra operacional

O wrapper SGDK nao tenta buildar essa ferramenta. Ela fica marcada como
material de pipeline e deve ser aberta em um ambiente Unity apropriado.
