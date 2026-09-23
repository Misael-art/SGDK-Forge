# vibe_playable_loop_v1

Este workflow transforma pedidos naturais de jogo, fase, personagem, UI, FX ou animacao em uma rota visual verificavel antes de qualquer runtime de producao.

## Entrada canonica

Use `tools/sgdk_wrapper/route_vibe_playable_request.ps1` para gerar:

- `vibe_playable_route_report`;
- contexto compacto com `detected_targets`;
- owners visuais em ordem deterministica;
- bloqueio de runtime quando a entrega altera o que o jogador vera.

## Regra de runtime

Quando `visual_route_required=true`, `runtime_open_allowed=false` ate existir:

1. direcao visual selecionada por `art-direction-selector` via dispatch explicito do roteador;
2. diagnostico de assets;
3. fonte premium rastreavel;
4. aprovacao humana do asset vinculada aos hashes da fonte e do convertido;
5. traducao VDP e budget;
6. build com ROM hash;
7. evidencia BlastEm vinculada ao hash da ROM.

`art-direction-selector` continua com `allow_implicit_invocation=false`. O roteador nao muda o lifecycle da skill: ele registra uma chamada explicita quando regras deterministicas detectam alvo visual.

## Ambiguidade

Se o texto nao encaixar em regra visual conhecida, mas ainda puder ser player-facing, a rota usa fallback de seguranca: registra `ambiguity_fallback.used=true` e bloqueia runtime de producao ate classificacao humana ou regra canonica.

## Graphify

Graphify e consultivo. A rota deve continuar pelos arquivos canonicos quando o cache estiver ausente, lento ou degradado.
