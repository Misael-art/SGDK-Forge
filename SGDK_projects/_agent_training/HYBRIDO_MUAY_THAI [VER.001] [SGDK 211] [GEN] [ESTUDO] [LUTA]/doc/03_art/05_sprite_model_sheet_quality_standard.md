# Sprite And Model Sheet Quality Standard

## 1. Anatomia e contagem de membros

Antes de aceitar qualquer model sheet ou frame:

- Contar exatamente 2 bracos, 2 pernas, 1 cabeca e 1 tronco.
- Confirmar que cada braco nasce de um ombro plausivel e cada perna nasce de um quadril plausivel.
- Rejeitar membro duplicado no mesmo ombro, membro fantasma, sobreposicao ambigua ou articulacao sem dono.
- Rejeitar maos/pes amorfos, dedos fundidos sem intencao clara, falta de polegar quando a mao esta legivel.

## 2. Acting facial

Cada estado precisa de expressao coerente:

- `idle`: concentrado, boca fechada, olhar no oponente.
- `walk_step`: concentrado com leve tensao.
- `teep`, `knee`, `punch`: esforco visivel, mandibula tensionada, dentes ou boca aberta de kiai, olhos estreitos.
- `hurt`: dor, choque ou contracao, cabeca reagindo ao vetor do golpe.

## 3. Input gatekeeper

Se a fonte tiver anomalia anatomica, expressao congelada ou perda de
identidade visual:

1. Bloquear conversao para PNG indexado final.
2. Gerar relatorio de defeitos com pose, regiao e motivo.
3. Solicitar inpaint/correcao ou redraw antes de qualquer strip runtime.

## 4. Traducao 48x64

Proibido reduzir concept high-res diretamente para 48x64 usando downscale
suave. O sprite deve ser reconstruido em clusters pixel art:

- Outline escuro e silhueta clara.
- Pele bronzeada, pedra escura, lava laranja/vermelha, calcao preto/dourado e faixas brancas discerniveis.
- Sem ruido de dithering automatico.
- Sem blur, anti-aliasing ou halo.
- Sem promocao visual apenas por validacao tecnica.

## 5. Gate model sheet -> sprite sheet

Antes de promover uma folha derivada do model sheet:

- Gerar `model_sheet_to_sprite_fidelity_report`.
- Comparar model sheet, sprite sheet e contact sheet lado a lado.
- Listar traços `must_preserve`: anatomia, rosto/olhos, braco de lava, shorts, bandagens, faixa vermelha, paleta/material e acting por estado.
- Marcar como blocker qualquer traço assinatura que vire bloco generico.
- Separar `technical_pass` de `visual_pass`.
- Se o sheet falhar, voltar para lineart/blocking por acao; nao remendar o PNG final.

Critério: folha tecnicamente indexada, 48x64 e alinhada ainda reprova se nao herdar o DNA visual do model sheet aprovado.

## 6. Gate de direcao arte + game design

Antes de gerar model sheet, key pose, strip ou sprite sheet final:

- Gerar `art_gameplay_direction_gate`.
- Confirmar supervisao do art director e contexto de GDD/spec.
- Declarar camera, perspectiva, oponente/interacao, contato de solo, alcance de golpe e papel do estado no jogo.
- Listar marcadores `must_preserve`: cabelo, olhos, rosto, roupa, emblemas, cicatrizes, braco de lava, bandagens, faixa vermelha, ornamentos dourados, materiais e assimetria.
- Se o proprio model sheet aceito tiver drift interno, como cabelo diferente entre poses, bloquear a derivacao ate decidir se e variacao intencional, erro de pose ou necessidade de redraw.
- Declarar movimento secundario e carisma: cabelo, faixas, shorts, expressao facial, maos, anticipation, active, hitstop visual, recovery e follow-through.

Critério: sprite sheet feito sem saber camera, interacao, leitura de golpe e identidade preservada nao e asset dirigido; e `director_gate_unapproved`.
