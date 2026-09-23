# Menu Visual Language

## Objetivo

Definir um padrao de menu e title screen para MegaDrive_DEV que seja:
- impactante
- legivel
- coerente com o tema do projeto
- versatil o suficiente para diferentes generos

## Principios

- menu e uma cena de showcase
- idle precisa ter vida
- legibilidade vence ornamento
- a fantasia do jogo manda na linguagem visual
- nostalgia de Mega Drive e meio, nao fantasia unica

## Estrutura recomendada

- fundo com profundidade viva
- geometria forte de conducao do olhar
- tipografia com separacao dura
- selecao com feedback ativo
- paleta de contraste alto

## Logo e identidade de marca

Title screen e menu principal precisam de `brand_identity_manifest` quando o
projeto tiver logo, press-start, front-end autoral ou identidade de produto.
O logo nao e decoracao: ele comunica genero, tom e qualidade percebida em
poucos segundos.

Regras:

- o nome principal deve dominar a leitura; subtitulo e ornamento ficam
  subordinados
- a metafora visual precisa nascer da mecanica, mundo ou fantasia do jogo,
  sem prejudicar a leitura da palavra
- o logo precisa passar em silhueta, monocromatico, miniatura e fundo dinamico
- fonte-display, fonte-body, fonte-HUD e fonte narrativa devem ser decididas
  como sistema, com `glyph_manifest` e fallback
- SVG/EPS ou fonte high-res sao fonte mestre em `data/source_art/`; runtime
  Mega Drive exige tiles/sprites indexados, paleta auditada e budget real
- camadas do logo podem ser exportadas separadas para pulso, palette cycling,
  brilho ou reveal, desde que exista fallback estatico legivel

## Equivalentes tematicos

- sci-fi: grade, horizonte tecnico, distorcao digital, glow duro
- fantasia: linhas de energia, ruinas, ceu dramatizado, runas, neblina controlada
- urbano: skyline, placas, concreto, janela iluminada, trafego de luz
- industrial: grelhas, andaimes, cabos, warning lights, massa mecanica
- natural: camadas atmosfericas, relevo, agua, vento, silhuetas organicas

## Anti-padroes

- fundo morto
- menu que parece debug screen
- fonte generica ou SGDK default usada como identidade final
- logo ornamental que so funciona ampliado
- metafora de gameplay que torna o nome dificil de ler
- excesso de detalhe atras do texto
- tema visual importado de outro genero sem justificativa
- selecao passiva demais

## Checklist de aprovacao

- comunica o tema do jogo no primeiro frame
- logo e familia tipografica batem com o GDD e o `master_style_manifest`
- logo passa silhueta, monocromatico, miniatura e fundo dinamico
- segue legivel em 320x224
- tem movimento ou respiracao visual em idle
- item selecionado e obvio sem depender de leitura demorada
- entra e sai sem vazamento de estado
