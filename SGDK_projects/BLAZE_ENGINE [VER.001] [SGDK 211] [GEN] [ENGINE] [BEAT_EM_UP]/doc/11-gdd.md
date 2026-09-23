# GDD técnico — BLAZE_ENGINE Beat 'em Up SGDK 2.11

## Objetivo

Preservar o vertical slice jogável do BLAZE_ENGINE como um technical demo de beat 'em up para Mega Drive/Genesis, compilado com SGDK 2.11 e validado por ROM, recursos e evidência de emulador.

## Identidade de gênero

O projeto é um beat 'em up (brawler) de progressão lateral: o jogador avança por trechos de fase, controla posição no eixo de profundidade, enfrenta grupos de inimigos, encadeia golpes e atravessa transições de cena. Não é um fighting game de arena/duelo 1 contra 1.

## Escopo desta conversão

- manter as cenas legadas de créditos, tela principal, seleção e gameplay;
- manter sprites, fundos e áudio fornecidos pelo engine original;
- corrigir incompatibilidades de API e contratos de memória detectadas no build SGDK 2.11;
- medir e registrar os limites de VDP antes de qualquer promoção para AAA.

## Fora de escopo

- reautoria de sprites ou paletas sem uma especificação visual aprovada;
- transformar referências de Discord em requisitos por inferência;
- declarar release, jogo completo ou `ready_for_aaa` sem closeout BlastEm completo.

## Critério de aceite do protótipo

Build SGDK 2.11 reproduzível, ROM presente, recursos sem erros estruturais, boot observado no BlastEm e limitações de VDP/evidência explicitamente registradas.
