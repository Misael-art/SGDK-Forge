# Direcao de arte — abertura de assinatura `branding_sequence_v2`

Companheiro artistico de `doc/branding_sequence_contract.json`. Onde os dois divergirem, o
contrato ganha nos numeros e este documento ganha na direcao.

**Este documento existe para que o agente de arte nao invente a direcao.** A direcao ja foi
tomada. Sua tarefa e executa-la em pixel e provar que executou, comecando pelo model sheet.

---

## 1. O que a abertura tem que provar

Uma abertura de marca nao tem gameplay para carregar espetaculo. Ela tem 8,7 segundos para
dizer uma coisa: **quem fez isso sabe o que este hardware faz.**

O v1 falhou nisso com hardware medido ocioso: 0 sprites de 80, 2 paletas de 4, nenhum H-Int,
Shadow/Highlight nunca ligado. A arte tem que dar suporte material aos efeitos, senao eles
nao aparecem. Uma rampa de metal sem folga no topo mata a varredura especular. Uma brasa sem
nucleo emissivo mata a luz mascarada. **Aqui a arte e pre-requisito do efeito, nao decoracao
dele.**

---

## 2. A LOGICA DE LUZ — leia isto duas vezes

**A forja ilumina de baixo.** A fonte de calor esta no piso, no nivel da fornalha.

Isso inverte tudo que o reflexo pede. Nao existe luz de ceu nesta cena. Portanto:

- **o plano superior de cada volume esta em SOMBRA** — o topo da bigorna, o dorso do martelo,
  a face de cima de cada ferramenta;
- **a face inferior e a barriga de cada volume estao ILUMINADAS** — o beico da bigorna, a
  parte de baixo do cabo, a aresta inferior das letras;
- **a sombra sobe pela parede**, nao desce pelo chao;
- **o contato com o piso e o ponto mais quente da imagem**, nao o mais escuro.

Se o seu asset puder ser lido como iluminado de cima, ele esta errado e sera reprovado, ainda
que a rampa tenha 15 cores e o dither seja impecavel.

Segunda lei: **sombra em metal quente e FRIA, nao preta.** O aco que perde calor vai para
azul-violeta, nunca para cinza neutro. Rampas de sombra neutra sao o principal sintoma de
pixel art generica.

Terceiro evento de luz: a varredura especular do ato 2 vem na **horizontal**, cruzando o
logo da esquerda para a direita. Ela e um segundo evento de luz sobre a luz de baixo. E o
que faz o metal parecer metal em vez de plastico laranja. Ela e feita pelo operador de
Shadow/Highlight do VDP, **nunca assada no asset** — voce nao desenha o brilho andando, voce
desenha a rampa que permite ao hardware clarear.

---

## 3. Os nove eixos visuais

- **dimensionality:** volume solido em 2 planos + foreground em silhueta. Sem falsa
  perspectiva, sem fuga. Profundidade vem de valor atmosferico, nao de linhas de fuga.
- **fidelity_detail:** densidade media. Detalhe concentrado em 3 lugares (aresta da bigorna,
  cabeca do martelo, chanfro das letras) e o resto simplificado. Detalhe uniforme le como
  ruido no CRT.
- **color_theory:** temperatura como estrutura. Frio no que esta longe e frio no que esfriou;
  quente no que esta perto do fogo e no que esta sendo forjado. Nenhuma cor neutra pura.
- **lighting_shadow:** iluminacao inferior emissiva, com sombra fria subindo. Ver secao 2.
- **shape_language:** peso e assimetria. Massa pesada embaixo, silhueta assimetrica de
  proposito. Nada centrado, nada espelhado.
- **surface_material:** quatro materiais e apenas quatro. Ver secao 4.
- **ui_integration:** nenhuma. Nao existe HUD nesta cena. Wordmark nao e UI, e objeto.
- **motion_style:** a arte e estatica; o movimento vem do runtime. Mas os quadros de brasa e
  estilhaco precisam ler como o MESMO objeto em rotacao, nao 4 desenhos parecidos.
- **vfx_language:** emissivo sem contorno. Brasa e faisca nao tem outline: elas sao luz.
  Todo o resto tem contorno escuro.

## 4. Gramatica de material — `material_marks`

| Material | Onde | Como e desenhado |
|---|---|---|
| **Pedra** | paredes, piso, fornalha | hachura por cluster, nunca dither uniforme. Rampa fria de 5 passos. Junta de bloco irregular: sem grid cookie-cutter. |
| **Ferro** | bigorna, martelo, estilhaco, logo | 3 valores minimos + 1 especular duro. Aresta viva com 1px de luz na face inferior. Sombra fria, nunca cinza. |
| **Brasa / calor** | fornalha, nucleo do metal, faisca | emissivo: sem lado de sombra, sem contorno. O gradiente e dither de 2-3 cores, nunca rampa longa. |
| **Fuligem** | transicao piso-parede, base do wordmark | dither com papel: escurece o que esta longe do fogo. Dither sem funcao de material reprova. |

---

## 5. Arquitetura de paleta

**O papel de cada indice e CONTRATO — o runtime depende dele.** Os valores hex sao SEED: o
artista pode e deve refinar a cor, nunca mover o papel.

Formato MD: `0x0BGR`, nibbles pares de `0` a `E`. Nibble impar nao existe no CRAM de 9 bits:
`0x0630` e `0x0CDD` sao invalidos, `0x0620` e `0x0CCC` sao validos.

**Layout da paleta no PNG do model sheet.** A folha e um unico PNG indexado com ate 64
entradas, organizadas em 4 grupos de 16 na ordem das paletas:

```
entradas  0-15  -> PAL0   entradas 16-31 -> PAL1
entradas 32-47  -> PAL2   entradas 48-63 -> PAL3
```

O indice 0 de **cada grupo** (0, 16, 32, 48) e o slot transparente daquela paleta. Essa
ordem nao e sugestao: o gate de contrato le a paleta do PNG nessas posicoes para conferir a
folga de highlight de PAL1 e o fechamento do ciclo de PAL0. Paleta fora de ordem reprova por
nao poder ser verificada.

### PAL0 — ambiente da forja

| Idx | Papel | Seed | Trava |
|---|---|---|---|
| 1-2 | pedra em sombra profunda (fria) | `0x0000` `0x0200` | |
| 3-5 | pedra em rampa (fria -> neutra) | `0x0420` `0x0642` `0x0864` | |
| 6-8 | ferro/fuligem quente escuro | `0x0024` `0x0046` `0x0068` | |
| **9-12** | **CICLO DE BRASA** | `0x008A` `0x00AC` `0x02CE` `0x0068` | **precisa fechar em loop: o runtime rotaciona estes 4 em CRAM. Se o passo 12 nao emendar no 9, aparece um salto visivel** |
| 13-14 | nucleo emissivo quente | `0x02CE` `0x08EE` | |
| 15 | fuligem / linha de silhueta | `0x0222` | |

### PAL1 — metal e logo da engine

| Idx | Papel | Seed | Trava |
|---|---|---|---|
| 1-3 | sombra de ferro (FRIA, violeta-azul) | `0x0200` `0x0420` `0x0620` | sombra neutra reprova |
| 4-8 | corpo do ferro | `0x0642` `0x0864` `0x0A86` `0x0CA8` `0x0ECA` | |
| 9-12 | metal aquecido | `0x0068` `0x008A` `0x00AC` `0x02CE` | |
| **13-14** | **FOLGA DE HIGHLIGHT** | `0x0AAC` `0x0CCC` | **nenhum canal pode chegar a `E`. Se a rampa chegar em `0x0EEE`, o operador de highlight do VDP nao tem para onde clarear e a varredura especular do ato 2 desaparece. Regra mecanica: canal maximo `<= C` nos dois indices.** |
| 15 | contorno / chanfro escuro | `0x0000` | |

### PAL2 — wordmarks (autor, projeto, presents)

| Idx | Papel | Seed |
|---|---|---|
| 1-2 | contorno e sombra projetada | `0x0000` `0x0200` |
| 3-7 | corpo da letra | `0x0422` `0x0644` `0x0866` `0x0A88` `0x0CAA` |
| 8-11 | luz de chanfro (aresta inferior) | `0x0068` `0x008A` `0x00AC` `0x04CE` |
| 12-14 | acento de assinatura | `0x00CE` `0x06EE` `0x0CEE` |
| 15 | passo de dither na base | `0x0422` |

### PAL3 — sprites de FX

| Idx | Papel | Seed |
|---|---|---|
| 1-4 | corpo do estilhaco de ferro | `0x0200` `0x0642` `0x0A86` `0x0ECA` |
| 5-9 | brasa emissiva | `0x0046` `0x0068` `0x008A` `0x00AC` `0x02CE` |
| 10-13 | rastro de afterimage (copias mais fracas) | `0x0024` `0x0046` `0x0068` `0x008A` |
| 14-15 | ponta de faisca branco-quente | `0x08EE` `0x0EEE` |

---

## 6. Voz tipografica dos wordmarks

Nao e fonte. E **objeto de metal forjado** com letras.

- peso: massa pesada, haste grossa, contra-forma pequena. Uma letra que sobrevive a 8px de
  altura de traco;
- construcao: chanfro em 45 graus na aresta **inferior** (a luz vem de baixo), com 1px de
  luz de chanfro e 2px de corpo;
- serifa: nenhuma serifa decorativa. Se houver terminacao, ela e um corte de ferramenta,
  chanfrado, nao uma serifa tipografica;
- assimetria obrigatoria: uma letra do conjunto carrega uma marca de ferramenta que as
  outras nao tem. Isso e `costume_asymmetry` aplicado a tipografia — e o que impede o
  wordmark de parecer template;
- o `presents` e o oposto: leve, pequeno, sem chanfro, apenas corpo e contorno. Ele nao
  compete com o wordmark do projeto.

**Proibido:** `VDP_drawText`, fonte do SGDK, texto renderizado por engine. Os tres wordmarks
sao assets de pixel art. O cursor de maquina de escrever do v1 esta revogado.

## 7. `silhouette_hooks` — 3 marcas que sobrevivem em preto puro

1. **o bico da bigorna** — o perfil conico apontando para fora, assimetrico, que identifica a
   bigorna mesmo em silhueta total;
2. **a cabeca assimetrica do martelo** — um lado plano, um lado em cunha;
3. **a diagonal da coifa da fornalha** — a linha inclinada no alto da cena que ancora a
   composicao e da o unico angulo agudo do enquadramento.

Teste: preencha tudo de preto. Se voce nao reconhece a cena por essas 3 formas, a silhueta
falhou.

## 8. `generic_blockers` — o que faria isso parecer outro jogo

- rampa de sombra em cinza neutro;
- iluminacao superior, ainda que discreta;
- dither uniforme cobrindo tudo, sem funcao de material;
- grid de tijolo/pedra regular e visivel (cookie-cutter);
- brasa desenhada como circulo laranja com contorno;
- wordmark centrado e simetrico, com chanfro nas 4 arestas;
- paleta de uma nota (tudo laranja) sem a ancora fria;
- estilhaco de metal como triangulo generico sem aresta viva.

---

## 9. O MODEL SHEET — o que entregar na fase 1

Arquivo: `data/source_art/branding_v2/model_sheet_forge_v01.png`
Canvas: **512 x 384**, PNG indexado, index 0 transparente.

Nao e concept art bonita. E uma folha de PROVA: cada painel prova uma decisao que o resto da
producao vai herdar.

| Painel | Regiao | O que precisa provar |
|---|---|---|
| **A — luz** | topo-esquerda, 256x160 | bigorna + martelo em tamanho aproximado de cena, com a luz vindo de baixo. 3 valores minimos por material. Prova a secao 2. |
| **B — silhueta** | topo-direita, 256x160 | os hooks do painel A em preto chapado. Fundo transparente ou branco liso, tanto faz: a convencao de estudio preto-sobre-branco le igual ou melhor. Prova os 3 `silhouette_hooks`. |
| **C — rampas** | meio, 512x64 | as 4 paletas como tiras de degraus rotulados por indice, na ordem da secao 5. A tira de PAL1 deve mostrar visivelmente que 13-14 estao abaixo do branco. A tira de PAL0 deve mostrar os 4 passos do ciclo de brasa em sequencia fechada. |
| **D — tipografia** | baixo-esquerda, 256x96 | uma palavra de teste (nao o nome final) no corpo do wordmark da engine, em tamanho real de 64px de altura, com o chanfro inferior e a marca de ferramenta assimetrica. |
| **E — FX em tamanho real** | baixo-direita, 256x96 | brasa e estilhaco a **16x16, tamanho real, nao ampliados**, com os 4 quadros de cada um lado a lado. Ao lado, uma versao ampliada 4x apenas para leitura humana, claramente marcada como ampliacao. |

Regra do painel E: se os 4 quadros nao lerem como o mesmo objeto girando, refaca. Quatro
desenhos parecidos nao formam rotacao.

## 10. Criterio de aceitacao

### Cinco gates do template

- `scope_style_constraints` — 4 paletas, 15 cores visiveis, grid de 8px, sem alpha
- `silhouette_shape_language` — painel B prova os 3 hooks
- `value_hierarchy` — foreground / mid / background distinguiveis por valor atmosferico
- `palette_role_map` — papel de indice da secao 5 respeitado, com a folga de PAL1 visivel
- `polish_vfx_gameplay_signal` — brasa e estilhaco emissivos, sem contorno

### Teste final da Visual Quality Bar

> "Isso poderia estar em um jogo comercial AAA de 1994?"

Se nao for um SIM categorico, refazer. Nao ajustar: refazer.

### Eixo de consequencia — `brand_comprehension_consequence`

Cena de marca nao tem gameplay, entao o eixo canonico de consequencia jogavel foi substituido
por `brand_comprehension_consequence`, aprovado pela curadoria em 2026-08-17:

> **cada decisao de arte precisa mudar o que o espectador entende sobre quem fez este jogo.**

Isso vale para a sua arte tambem, nao so para as tecnicas do runtime. Para cada decisao
visual que voce tomar no model sheet, saiba responder: *se eu achatasse isso, o que o
espectador deixaria de entender?* Se a resposta for "nada, mas fica mais bonito", a decisao e
decoracao — corte ou declare como tal.

Exemplos ja declarados no contrato, para voce calibrar o nivel de exigencia:

| Decisao | O que o espectador entende | Teste negativo |
|---|---|---|
| luz vinda de baixo | existe uma fonte de calor fisica no piso | luz de cima: a cena vira um cenario qualquer com paleta laranja |
| sombra fria no metal | o aco esta perdendo calor, tem temperatura | sombra cinza: o metal vira plastico pintado |
| folga de highlight em PAL1 | isto e metal, nao plastico laranja | rampa no branco: a varredura especular desaparece |
| marca de ferramenta assimetrica | isto foi feito por alguem, nao gerado | wordmark simetrico: le como template |

O gate estrutural roda por `tools/sgdk_wrapper/validate_brand_comprehension_gate.py` e prova
que nenhuma tecnica passou sem justificativa. Ele **nao** julga se o claim e verdadeiro — isso
e decisao humana contra a sua folha e, depois, contra screenshot real do BlastEm.

### Calibracao de teto

Compare somente com a mesma geracao de hardware. Os benchmarks canonicos do workspace
(`doc/03_art/00_visual_quality_bar.md`) sao ancoras **tecnicas**: extraia deles disciplina de
rampa, densidade de detalhe e comportamento de luz. Nunca nome de jogo, estudio ou IP como
prompt de copia — isso exige `authoriality_gate_report` e `clone_risk_score` medido por
`environment_and_costume_distance`.

O criterio nao e contagem de tons. Um asset com 8 cores e direcao de luz coerente passa; um
com 15 cores e luz ambigua reprova.

---

## 11. Entrega da fase 1 e o portao

Entregue junto do PNG:

1. `doc/art_direction_decision_record.json` — o esqueleto ja esta preenchido com as decisoes
   de direcao deste documento. Complete os campos de execucao e nao altere as decisoes.
2. `doc/authoriality_gate_report.json` — `clone_risk_score` medido, metodo declarado,
   nenhum IP usado como prompt.
3. Um paragrafo honesto dizendo onde a folha ficou fraca. Folha sem autocritica volta.

**PARE aqui.** O model sheet exige aprovacao humana explicita antes de qualquer um dos 8
assets finais. Pacote de assets entregue sem model sheet aprovado ja falhou 4 vezes neste
workspace e sera reprovado sem leitura.

Depois da aprovacao, siga a fase 2 de `doc/15-prompt-telas-assinatura.md`.
