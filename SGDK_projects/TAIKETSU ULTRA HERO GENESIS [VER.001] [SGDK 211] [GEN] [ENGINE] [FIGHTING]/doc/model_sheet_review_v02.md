# Revisao do model sheet `model_sheet_forge_v02.png` — fase 1, passada 2

Data: 2026-08-17
Revisor: curadoria (funcao art-director)
Anterior: `doc/model_sheet_review_v01.md` (`rework`) · Brief: `doc/model_sheet_rework_v02_brief.md`

**Recomendacao: aprovar como direcao provada, com um item obrigatorio de arrasto.**
Aprovacao final e do curador humano.

---

## Os dois blockers duros da v01 estao resolvidos

### Wordmark — a lei da luz virou

Cada letra agora carrega azul-ardosia frio no **topo** e ouro quente na aresta **inferior**,
com transicao dura. Le sem ambiguidade como iluminado de baixo pelo fogo. Achatado em 2D,
sem falso 3D. A mossa assimetrica esta no **J** e so nele: `costume_asymmetry` entregue.
Altura util de 64px. Contorno escuro consistente com o `line_signature`.

Medicao: 100% dos pixels do wordmark caem em PAL1, entao a familia de paleta foi corrigida
de vez. O ruido de JPEG sumiu — a decisao de median 3x3 + snap 9-bit antes do remap funcionou
e as arestas estao limpas.

### Martelo — resolvido e bem

Grande, dominante, angulado para a bigorna. Cunha legivel: cabeca afilada com dorso plano.
E a luz esta invertida corretamente — a face **inferior** da cabeca e o contato com a bigorna
sao o ponto mais quente do quadro. Serve agora como `silhouette_hook` numero 2.

### Preservado como pedido

Composicao e lei da luz do painel A, bico da bigorna, convencao do painel B, rota do
assemblador. Nada de valor foi perdido na passada.

---

## Furo NO MEU GATE, encontrado ao revisar esta entrega

A autocritica do agente dizia que o remap empurrou a letra para os slots de metal aquecido.
Medi para confirmar e o numero e este:

| Faixa de PAL1 | Papel | Share do wordmark |
|---|---|---|
| 1-3 | sombra fria | 2,7% |
| 4-8 | corpo de ferro | 28,0% |
| 9-12 | metal aquecido | 44,7% |
| **13-14** | **folga de highlight** | **0,0%** |
| 15 | contorno | 24,6% |

Os slots de folga **nao sao pintados**. Meu gate conferia a folga exatamente neles, ou seja,
media a declaracao e nao a realidade: o asset podia encostar no teto por outro indice e passar.
E era o caso — `PAL1[12] = (238,204,34)`, canal de pico `0xEE`, no teto, e em uso.

O operador de Shadow/Highlight do VDP clareia a **cor de saida do pixel**, nao o slot que o
contrato reservou. Corrigido: novo check `model_sheet_specular_headroom_unusable` mede as
cores realmente pintadas.

Calibrado por proporcao, porque um glint no teto e escolha legitima e reprovar 1% seria gate
gritando em asset saudavel: acima de 15% dos pixels no teto reprova (o corpo do metal morre
sob o highlight), abaixo disso fica marcado como aviso. A v02 mede 1% e sai como **warning**.

---

## Duas vezes em que a medicao me corrigiu

**Achei que a parede tinha regredido para salpico branco.** Medi pixels claros isolados no
painel A: v01 tem 17, v02 tem **4**. O que eu li como salt noise e cluster — que e justamente
a hachura por cluster que a direcao pede. Impressao minha errada, ampliacao de 3x enganando.

**Achei que a parede competia com o foco.** Medi o pico de luminancia: fundo 80, foco 226,
separacao de +146, com mediana da parede em 3. A hierarquia de valor esta forte, melhor do
que o agente marcou como `partial` na v01.

---

## O item obrigatorio de arrasto

**O wordmark nao tem passo de luz nenhum.** A rampa vai de contorno para azul, para ouro, e
para. Os slots 13-14 estao a 0% e o unico pixel acima do teto e um glint de 1%.

Isso nao e refinamento, e a existencia do efeito: `img_logo_engine_v2` e o asset sobre o qual
a varredura especular do ato 2 corre. Sem um degrau de luz deliberado, a varredura nao tem
onde pousar e o beat central do ato 2 nao acontece.

Na producao do asset final, o wordmark precisa de um degrau de luz na faixa `PAL1[13..14]`,
com canal maximo `<= 0xCC`, colocado na aresta **inferior** de cada haste — onde o fogo bate.
Fino, 1px a 2px. Nao e brilho pintado andando: e o degrau que permite ao hardware clarear.

---

## Arrasto menor, entra na producao dos assets

- **Parede** ainda le como fiada. Trincas e o vao ajudaram, mas a modularidade persiste. Vale
  resolver quando `img_forge_bg_b` for autorado, nao numa terceira folha.
- **Rotulos do painel C** existem e estao apertados. Cumprem a funcao de revisao humana.
- **Entalhe do estilhaco a 16x16** ainda pede a ampliacao 4x para virar gancho. Aceitavel:
  o painel E prova a rotacao, e o entalhe pode ser reforcado em `spr_forge_shard`.

---

## Por que aprovar em vez de pedir v03

O model sheet existe para provar decisoes que os 8 assets herdam. Estao provadas: a lei da luz
de baixo, a arquitetura de paleta, os `silhouette_hooks`, a gramatica de marca de ferramenta,
a rotacao de FX e a rota de proveniencia. Os itens restantes sao de autoria dos assets, e
resolve-los numa terceira folha custaria uma passada sem provar nada novo.

O `visual_quality_bar_1994` continua `no_not_yet` por avaliacao do proprio agente, e isso e
verdade — mas a folha e prova de direcao, nao peca final, e o teto de 1994 e cobrado nos
assets.

## Limites

Nao promove asset. Nao substitui `art_quality_gate.py`, a aprovacao humana da trava 3, nem
evidencia de emulador. `art_diagnostic.py` marca `TOO_MANY_COLORS` porque a folha carrega 4
paletas de prova em `source_art/`; e esperado e nao se aplica a asset de `res/`.
