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
