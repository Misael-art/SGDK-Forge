# Producao dos 9 assets — `branding_sequence_v2` fase 2

Liberado pelo curador em 2026-08-17. Model sheet v02 aprovado como direcao provada; concepcao
de cena aprovada.

Autoridades, em ordem:
`doc/branding_v2_art_direction.md` (como desenhar) ·
`doc/branding_v2_scene_conception.md` (o que se move) ·
`doc/branding_v2_cinematic_storyboard.json` (coreografia medida) ·
`doc/branding_v2_dma_queue_contract.json` (orcamento do martelo)

---

## O que a v02 provou e voce herda

Nao redecida nada disto. Ja passou pela revisao:

- **luz de baixo** — plano superior em sombra, face inferior iluminada, sombra subindo;
- **sombra fria em metal quente** — violeta-azul, nunca cinza neutro;
- **arquitetura de paleta** — papel de indice travado, PAL0 ambiente, PAL1 metal, PAL2
  wordmarks, PAL3 FX;
- **`silhouette_hooks`** — bico da bigorna, cunha do martelo, diagonal da coifa;
- **marca de ferramenta assimetrica** — a mossa no J e o padrao a repetir;
- **rota de proveniencia** — median 3x3 + snap 9-bit antes do remap, fontes limpas em
  `raw_png/`, sha256 por asset no lineage. Reaproveite o assemblador.

---

## REQUISITO NAO NEGOCIAVEL, herdado da revisao

**`img_logo_engine_v2` precisa de um degrau de luz.**

O model sheet v02 nao tem passo de luz nenhum: `PAL1[13..14]` a 0,0% de uso, e o pixel mais
claro e um glint de 1% ja no teto. A rampa vai de contorno para azul, para ouro, e para.

A varredura especular do ato 2 corre **sobre este asset**. O operador de Shadow/Highlight
clareia a cor de saida do pixel: sem um degrau com folga, a varredura nao tem onde pousar e o
beat central do ato 2 nao acontece.

- degrau em `PAL1[13..14]`, **canal maximo `<= 0xCC`**;
- posicao: aresta **inferior** de cada haste, onde o fogo bate;
- espessura: 1px a 2px, fino;
- nao e brilho pintado andando — e o degrau que permite ao hardware clarear.

O gate mede isso: `model_sheet_specular_headroom_unusable` reprova acima de 15% dos pixels no
teto e marca abaixo disso.

---

## Registro de posicao — o que faz os assets se encaixarem

A coreografia fixou coordenadas. Assets desenhados fora delas nao compoem cena, flutuam.

| Ancora | Coordenada | Consequencia |
|---|---|---|
| face da bigorna | **(128, 104)** | a brasa pousa aqui em F96 e o martelo bate aqui em F120 |
| caixa do logo | **x 48-272, y 80-144** | 224x64; os 32 estilhacos pousam em grade 8x4 dentro dela |
| faixa de ar quente | **48 scanlines inferiores** | sofrem cisalhamento por linha em F180-F300 |
| entrada do martelo | alto a direita, ~x150 | sobe em F96-120, bate em F120, recua em 10 quadros |

`img_forge_bg_a_props` precisa ter a face da bigorna exatamente em (128,104). Se ela estiver
20px acima, a brasa pousa no ar e o martelo bate no vazio.

---

## OS 9 ASSETS

Todos: PNG indexado, index 0 transparente, 15 cores visiveis por paleta, grid de 8px, sem
alpha. Larguras/alturas de SPRITE em tiles, por quadro.

### 1. `img_forge_bg_b` — 320x224 (40x28) · PAL0 · ato 1
Interior da forja, escuro, piso lavado por brasa. Rampa fria de pedra em 1-5, ciclo de brasa
em 9-12.
**Restricao da coreografia:** as **48 scanlines inferiores** sofrem deslocamento horizontal por
linha no ato 2. Nessa faixa use material continuo — brasa, piso, fumaca. Nenhum detalhe fino
nem aresta que dependa de alinhamento horizontal exato: cisalha e quebra.
**Da v02:** a parede ainda le como fiada. Aqui e onde isso se resolve — quebre a modularidade
com fiadas irregulares, blocos de tamanhos diferentes, pedra faltando ou trincada.

### 2. `img_forge_bg_a_props` — 320x224 (40x28) · PAL0 · ato 1
Bigorna e ferramentas em foreground, com priority split sobre BG_B.
**O MARTELO NAO ESTA AQUI.** Ele virou sprite porque se move.
**Registro obrigatorio:** face da bigorna em **(128, 104)**.
**Area reservada para a cicatriz:** o runtime escreve uma marca incandescente em tiles nesse
ponto no F120 e ela permanece ate o fim. Deixe cerca de **32x16 px de superficie limpa**
centrada em (128,104) — detalhe fino ou textura carregada ali competem com a marca e ela nao
le.
O bico conico da bigorna e `silhouette_hook` numero 1: preserve o perfil da v02.

### 3. `spr_forge_ember` — 16x16 (2x2) · **6 quadros** · PAL3 · ato 1
Brasa que cai e pousa.
- quadros 0-3: rotacao do nucleo em queda — **o mesmo objeto girando**, nao 4 desenhos
  parecidos. A v02 acertou isso com nucleo em lagrima a 0/35/100/195 graus;
- quadro 4: **esmagamento** no contato com a bigorna em F96;
- quadro 5: **assentamento**, a brasa acomodada e pulsando.
Emissivo: sem contorno, sem lado de sombra. Rampa em PAL3[5..9].
Os fantasmas do rastro sao o mesmo sprite remapeado para PAL3[10..13] pelo runtime — voce nao
desenha quadros de rastro.

### 4. `spr_forge_hammer` — 48x48 (6x6 tiles) · **7 quadros** ⚠ MUDOU · PAL1 · ato 1-2 · **STREAMED**
O golpe. Momento de assinatura da abertura.
- quadro 0: repouso;
- quadro 1: recuo, carregando;
- quadros 2-3: descida, dois intermediarios;
- quadro 4: **contato em SMEAR** — o quadro de F120. Cabeca alongada no eixo do golpe, nao
  pose limpa. A 60fps uma pose parada no contato le como teletransporte e o impacto perde a
  aceleracao;
- quadro 5: retorno do recuo (sai em 10 quadros);
- quadro 6: assentamento.

> **MUDANCA APOS O DESPACHO INICIAL:** este asset foi de 6 para 7 quadros na revisao de
> vitrine. O quadro de smear e novo e nao estava no despacho original.
**Cunha assimetrica obrigatoria:** um lado plano, um lado em cunha, legivel em preto chapado.
E `silhouette_hook` numero 2 e a v02 provou o desenho.
**Luz de baixo tambem aqui:** a face inferior da cabeca e o contato com a bigorna sao o ponto
mais quente do quadro no F120.
**Registro:** o ponto de contato do quadro 4 precisa cair em (128,104) quando o sprite estiver
na posicao de F120.
Streaming em janela dupla: 72 tiles residentes, 1152 B por troca. Voce nao precisa fazer nada
por causa disso — so saiba que os 7 quadros cabem porque foi decidido assim: 252 tiles residentes viram 72.

### 5. `spr_forge_shard` — 16x16 (2x2) · 4 quadros · PAL3 · ato 2
Estilhaco de metal do enxame de 32.
- **4 angulos genuinamente distintos**, pensados para que o flip H/V do runtime **acrescente**
  orientacao em vez de repetir. A v02 acertou com 0/28/81/157 graus;
- entalhe assimetrico para o flip nao virar espelho obvio;
- ferro quente: corpo em PAL3[1..4], aresta viva, sombra fria.
**Da v02:** o entalhe so vira gancho na ampliacao 4x. Reforce para ler a 16x16 nativo.

### 6. `img_logo_engine_v2` — 224x64 (28x8) · PAL1 · ato 2
O wordmark da engine, em metal forjado.
- rampa de ferro completa: sombra fria 1-3, corpo 4-8, metal aquecido 9-12;
- **degrau de luz em 13-14, canal `<= 0xCC`, na aresta inferior** — ver o requisito nao
  negociavel acima;
- marca de ferramenta assimetrica em exatamente uma letra;
- chanfro na aresta inferior, achatado em 2D, contorno escuro.
**Registro:** ocupa x 48-272, y 80-144. Os 32 estilhacos pousam em grade 8x4 dentro desta
caixa, entao a forma das letras precisa cobrir a grade de forma plausivel.

### 7. `img_logo_author_v2` — 192x32 (24x4) · PAL2 · ato 3
Wordmark do autor. Revelado pela cortina por coluna em F300-360.
Mesma gramatica tipografica do wordmark da engine, em PAL2. Nunca `VDP_drawText`.

### 8. `img_logo_project_v2` — 224x48 (28x6) · PAL2 · ato 3
Wordmark do projeto. Assume o centro em F430.

### 9. `img_presents_text_v2` — 96x16 (12x2) · PAL2 · ato 3
O oposto dos outros: leve, pequeno, **sem chanfro**, apenas corpo e contorno. Nao compete com
o wordmark do projeto — entra, respira, para.

---

## Revisao de vitrine — o que mudou depois do despacho

Tres tecnicas novas entraram para a abertura virar vitrine do que o jogador vai encontrar.
**Custo em sprites: zero.** Custo em arte: um quadro a mais no martelo.

- **cicatriz na bigorna** (`mutable_tile_decal_mutation`) — o golpe grava uma marca
  incandescente permanente na face da bigorna. Nao e asset novo: o runtime escreve os tiles.
  Mas `img_forge_bg_a_props` precisa deixar a face da bigorna **limpa o bastante** para a
  cicatriz aparecer: nada de detalhe fino exatamente em (128,104);
- **smear no contato** (`smear_frame_animation`) — o quadro 4 do martelo. Voce desenha;
- **presents no plano WINDOW** (`window_plane_static_hud`) — o wordmark fica imovel enquanto a
  cortina move os planos por baixo. Nao muda o asset, muda onde ele vive.

## Ordem de producao sugerida

1. `img_forge_bg_a_props` — porque fixa o registro de (128,104) que os outros dependem;
2. `img_forge_bg_b` — o par dele, mesma paleta;
3. `img_logo_engine_v2` — o de maior consequencia, com o degrau de luz;
4. `spr_forge_hammer` — o golpe;
5. `spr_forge_ember`, `spr_forge_shard` — os FX;
6. os tres wordmarks de PAL2.

## Entrega e gates

Para cada asset: descomentar a linha em `res/resources.res`, adicionar a entrada em
`doc/asset_provenance_manifest.json`, atualizar o lineage com sha256.

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root "<este projeto>" --shared-builder-root tools/image-tools
python3 tools/sgdk_wrapper/art_diagnostic.py
python3 tools/sgdk_wrapper/art_quality_gate.py
```

Continua valendo: nenhum pixel nasce de primitiva; codigo monta, recorta e paletiza arte
autoral, nunca a desenha. E voce pode encerrar dizendo que um asset nao atingiu o nivel — isso
e entrega honesta.

O teto de 1994 e cobrado **aqui**. O model sheet era prova de direcao; estes sao os assets.
