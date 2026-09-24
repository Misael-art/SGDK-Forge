# GDD - Shadow Dancer Revisitado

## Fantasia e escopo

Este projeto e um slice tecnico de acao/plataforma com scroll lateral. O objetivo desta versao e provar que um mapa maior que o plano pode ser percorrido com cache de tiles, movimento e colisao. Nao ha ainda combate ou inimigos.

## Loop jogavel atual

1. Ler direcao e botoes do controle 1P.
2. Aplicar gravidade, pulo e deslocamento livre quando a gravidade e alternada.
3. Consultar a imagem de colisao do mapa.
4. Mover a camera pela dead zone e atualizar o mapa virtual.
5. Atualizar sprite e fechar o frame no VBlank.

## Controles

- Direcional: move o player.
- B/C: pulo quando grounded.
- A: alterna gravidade para teste do mapa e da colisao.

## Nao-objetivos desta conversao

Beat 'em up, combate, inimigos, boss, HUD, audio, save, multiplayer e release ficam fora ate existir novo contrato aprovado.
