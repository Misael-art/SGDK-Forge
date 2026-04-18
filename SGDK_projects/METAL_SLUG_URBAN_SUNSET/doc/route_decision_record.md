# Route Decision Record - METAL_SLUG_URBAN_SUNSET

## Estado

- `locked_visual_direction`: `default_multi_plane_method`
- `incumbent_visual_method`: composicao padrao do projeto usando `sky_bg_b` + `city_bg_a`
- `challenger_routes_presented`: `high_key_haze`, `cool_evening`, `anime_style`, `anime_linefirst_balanced`, `anime_linefirst_cohesive`
- `diagnostic_board`: `grid_alignment`
- `anime_style_previous_attempt`: `rejected_by_human_review`
- `anime_reference_target`: `Gemini_Generated_Image_riu4i2riu4i2riu4.png`

## Decisao atual

As rotas alternativas continuam validas como referencia de curadoria e podem ser apresentadas ao usuario.

O default do projeto permanece sendo o metodo padrao ja criado ate haver congelamento explicito do usuario.

## Motivo

No comparativo mais justo do case:

- `high_key_haze` e `cool_evening` ganharam em atmosfera, mas perderam estruturalmente
- o incumbente multi-plano mostrou vantagem clara como solucao de projeto contra essas duas rotas
- o incumbente composto ficou com `1260` tiles unicos no teste flat equivalente
- `high_key_haze` e `cool_evening` ficaram em `1512` e `1518`
- `anime_style` parecia forte nos numeros, mas foi rejeitada pelo usuario por leitura errada de traco e cor
- a referencia humana aprovada para a familia anime agora e `Gemini_Generated_Image_riu4i2riu4i2riu4.png`
- os testes diretos dessa referencia ficaram visualmente muito mais corretos, mas ainda nao fecharam budget:
  - flat direta: `1363` tiles
  - split `BG_A + BG_B`: `1347` tiles
- a familia `anime_linefirst` passou a fechar budget com o processo correto definido pelo usuario:
  - `anime_linefirst_balanced`: score `0.7184`, `1261` tiles totais
  - `anime_linefirst_cohesive`: score `0.6988`, `1248` tiles totais

Conclusao:

- `high_key_haze` e `cool_evening` sao bons estudos
- `anime_style` nao deve mais ser usada como interpretacao valida de anime para esta cena
- `anime_background_reference` e a direcao estetica correta para futuras iteracoes desta familia
- `anime_linefirst` e o processo correto para promover essa familia ao Mega Drive sem perder controle de traco e massa
- o incumbente continua travado por enquanto porque a mudanca de filosofia visual precisa de aprovacao humana explicita

## Regra para futuras iteracoes

Uma rota alternativa so substitui o default se provar:

1. `perceptual win`
2. `system win`

Se a dupla vitoria acontecer, mas a troca alterar a filosofia-base de pintura da cena, a substituicao ainda depende de congelamento humano.

Na ausencia dessa validacao final, o projeto continua com `default_multi_plane_method`.
