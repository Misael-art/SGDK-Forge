# Revisao do model sheet `model_sheet_forge_v01.png` — fase 1

Data: 2026-08-17
Revisor: curadoria (funcao art-director)
Contrato: `branding_sequence_v2` · Direcao: `doc/branding_v2_art_direction.md`

**Recomendacao: `rework`.** Aprovacao final e do curador humano; esta revisao nao a substitui.

---

## O que passou, e passou de verdade

**Proveniencia limpa.** `assemble_model_sheet.py` tem **zero** chamadas de primitiva: so
`crop`, `resize` nearest, `paste`, chroma key e remap de paleta. As fontes autorais estao
persistidas em `raw/` com sha256 por painel em `model_sheet_lineage.json`, canal declarado
`native_chat_image_generation_callable`, `procedural_generation_used_as_asset_source: false`.
Essa e exatamente a rota `procedural_composed_from_authored`: codigo montou, nao desenhou.

**Gate mecanico limpo.** `validate_model_sheet_contract.py` exit 0. Canvas 512x384, 5 paineis
com conteudo, painel B silhueta, `PAL1[13..14]` com folga, `PAL0[9..12]` fechando como anel,
painel E em escala real.

**Autocritica honesta.** O agente declarou `visual_quality_bar_1994: no_not_yet` por conta
propria e nomeou a parede modular, o martelo e a perda dos rotulos do painel C. Nao vendeu a
folha como pronta. Isso e o comportamento correto e conta a favor.

**A lei da luz funciona no painel A.** A fornalha esta no piso, a barriga da bigorna e a
parede atras dela lavam em laranja quente, o plano superior da bigorna fica escuro e a pedra
longe do fogo vai para azul-violeta. Temperatura fazendo trabalho estrutural. O bico conico
da bigorna le como hook mesmo em silhueta. Isso e o nucleo da direcao e ele esta de pe.

---

## O que reprova

### 1. Painel D: o wordmark esta iluminado por cima — BLOCKER

Cada letra de `FORJA` carrega uma calota clara e espessa na aresta **superior**, e apenas um
fio dourado fino embaixo. A massa de luz esta em cima. A direcao exige o inverso: chanfro de
45 graus na aresta **inferior**, com a luz de baixo. Nao existe fonte de luz superior nesta
cena, entao a calota clara nao tem de onde vir.

O criterio da direcao e literal: *asset que possa ser lido como iluminado de cima e
reprovado, ainda que a rampa e o dither sejam impecaveis*. Este pode.

Esse painel e o que vira `img_logo_engine_v2`. Errar a lei da luz aqui contamina o ato 2
inteiro.

### 2. Painel D: familia de paleta errada — BLOCKER

O wordmark e azul-ardosia com calota branca. Deveria viver na rampa de ferro de PAL1, com o
metal aquecido em 9-12 e a folga de highlight em 13-14. Do jeito que esta le como pedra fria
ou plastico, nao como ferro forjado. O ato 2 precisa que a varredura especular corra sobre
metal; sobre isto ela nao vai significar nada.

### 3. Painel D: sem a marca de ferramenta assimetrica — BLOCKER

As 5 letras sao uniformes. A direcao pede que uma letra carregue uma marca que as outras nao
tem — e `costume_asymmetry` transposto para tipografia, e e o que separa wordmark autoral de
template. Sem ela, cai direto no `generic_blocker` "wordmark centrado e simetrico".

### 4. Painel A: o martelo contradiz a propria lei do painel — BLOCKER

Tudo no painel A obedece a luz de baixo, menos o martelo: a face superior da cabeca esta mais
clara que a inferior. Ele esta iluminado por cima, dentro do painel cuja funcao e provar a
iluminacao inferior. Alem disso ele esta pequeno demais e sem cunha, entao falha tambem como
`silhouette_hook` numero 2.

### 5. Painel E: os 4 quadros de brasa nao sao uma rotacao — BLOCKER

Sao 4 manchas amarelas parecidas com nucleo claro, nao o mesmo objeto girando. A regra do
painel E e explicita: *quatro desenhos parecidos nao formam rotacao*.

### 6. Painel E: os 4 estilhacos ja sao espelhos entre si — REWORK

Os quadros 1 e 4, e 2 e 3, ja parecem espelhamentos um do outro. Como o runtime gera as
orientacoes por flip H/V, isso colapsa as 16 orientacoes esperadas para cerca de metade. Os
4 quadros precisam ser angulos genuinamente distintos, pensados para que o flip **acrescente**
variedade em vez de repetir.

### 7. Parede em grade quase regular — REWORK

Ja nomeado pelo agente. Le como textura tileada, nao como alvenaria autoral. Cai no
`generic_blocker` "grid de pedra regular e visivel (cookie-cutter)".

### 8. Ruido de quantizacao no lugar de material — REWORK

O salpico dentro da pedra e das letras e artefato de JPEG sobrevivendo a quantizacao, nao
hachura por cluster com funcao de material. A direcao pede hachura por cluster na pedra e
proibe dither uniforme sem papel.

---

## Correcao na direcao, nao no trabalho

**O painel B esta certo e minha especificacao estava errada.** Eu pedi silhueta "em preto
puro sobre transparente"; o agente entregou preto sobre branco, que e convencao de estudio
padrao e le melhor. A intencao era provar os hooks em preto chapado, e isso foi cumprido.
Especificacao ajustada; o gate ja tolerava dois indices e continua como esta.

**O painel C perdeu os rotulos de indice.** O agente flagou. Vale registrar que os checks de
folga de highlight e de ciclo de brasa passaram porque o gate le a **tabela de paleta do
PNG**, nao o painel. O painel C existe para revisao humana, entao sem rotulo ele nao cumpre a
funcao dele — mas nada de mecanico foi perdido.

---

## Ordem de refacao sugerida

1. Wordmark do painel D refeito na rampa de ferro de PAL1, com chanfro na aresta inferior e
   uma marca de ferramenta em uma letra. Esse e o item de maior consequencia.
2. Martelo maior, com cunha assimetrica legivel, e reiluminado de baixo.
3. Brasa: 4 quadros como rotacao real de um mesmo nucleo emissivo.
4. Estilhaco: 4 angulos distintos, planejados para o flip H/V somar orientacao.
5. Parede: quebrar a modularidade da alvenaria e trocar salpico por hachura por cluster.
6. Painel C: devolver os rotulos de indice.

Os itens 1 a 4 sao blockers de aprovacao. Os itens 5 e 6 podem entrar na mesma passada.

## Limite desta revisao

Julga aderencia a direcao e leitura visual. Nao substitui `art_quality_gate.py`, nem a
aprovacao humana da trava 3, nem qualquer evidencia de emulador. Nenhum asset foi promovido.
