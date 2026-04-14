# Route Decision Record - METAL_SLUG_URBAN_SUNSET

## Estado

- `locked_visual_direction`: `default_multi_plane_method`
- `incumbent_visual_method`: composicao padrao do projeto usando `sky_bg_b` + `city_bg_a`
- `challenger_routes_presented`: `high_key_haze`, `cool_evening`, `anime_style`
- `diagnostic_board`: `grid_alignment`
- `challenger_ready_for_user_choice`: `anime_style`

## Decisao atual

As rotas alternativas continuam validas como referencia de curadoria e podem ser apresentadas ao usuario.

O default do projeto permanece sendo o metodo padrao ja criado ate haver congelamento explicito do usuario.

## Motivo

No comparativo mais justo do case:

- `high_key_haze` e `cool_evening` ganharam em atmosfera, mas perderam estruturalmente
- o incumbente multi-plano mostrou vantagem clara como solucao de projeto contra essas duas rotas
- o incumbente composto ficou com `1260` tiles unicos no teste flat equivalente
- `high_key_haze` e `cool_evening` ficaram em `1512` e `1518`
- `anime_style` foi a primeira rota alternativa a fechar `perceptual win` e `system win`, com `1191` tiles unicos e score `0.8267`

Conclusao:

- `high_key_haze` e `cool_evening` sao bons estudos
- `anime_style` e uma candidata real a troca de default
- o incumbente continua travado por enquanto porque a mudanca de filosofia visual precisa de aprovacao humana explicita

## Regra para futuras iteracoes

Uma rota alternativa so substitui o default se provar:

1. `perceptual win`
2. `system win`

Se a dupla vitoria acontecer, mas a troca alterar a filosofia-base de pintura da cena, a substituicao ainda depende de congelamento humano.

Na ausencia dessa validacao final, o projeto continua com `default_multi_plane_method`.
