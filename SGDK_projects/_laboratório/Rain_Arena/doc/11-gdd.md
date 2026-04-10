# 11 - Game Design Document — Rain_Arena

## Visao

Rain_Arena e um microjogo de timing ambientado em uma tempestade. O jogador observa a cena de chuva e deve disparar o impacto no instante em que a janela de flash aparece, convertendo o antigo slice visual em um loop jogavel curto e legivel.

O projeto ainda nao e um jogo completo com fases, personagem dedicado ou audio ativo. O escopo atual e provar que a cena validada em emulador consegue sustentar leitura de estado, objetivo, erro, sucesso e reinicio sem depender de assets novos.

## Mecanicas core

- ler a cadencia da tempestade e esperar a janela de flash
- apertar `A`, `B` ou `C` no momento certo para marcar ponto
- evitar disparos fora da janela para nao consumir tentativas

## Progressao

- o round dura 30 segundos
- o jogador vence ao atingir 6 acertos antes de acumular 3 erros
- apos vitoria ou derrota, `START` reinicia o loop imediatamente

## Regras e limites

- nao introduzir assets novos enquanto o loop base ainda estiver sendo provado
- preservar o budget tecnico ja consolidado da cena
- nao e escopo atual adicionar narrativa, mapa, audio real ou personagem dedicado

## Escopo atual

- slice jogavel minimo com HUD textual em window plane e reaproveitamento integral da cena de chuva
- fora do escopo desta fase: hardware real, audio ativo, progressao multi-cena e combate completo

