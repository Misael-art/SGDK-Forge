# Direcao de cena antes de asset — ordem de trabalho canonica

Origem: curadoria de 2026-08-17, 24 fases documentadas em
`doc/curation/ASSET_PROVENANCE_BASELINE_2026-08-17.md`.

Este workflow existe porque a abertura `branding_sequence_v2` foi produzida **na ordem errada**
e pagou por isso em retrabalho medido. A ordem errada nao foi preguica: foi plausivel a cada
passo. Por isso ela precisa estar escrita.

---

## A ordem que falhou

```
tecnicas -> lista de assets -> despacho de arte -> coreografia -> runtime -> medicao
```

Parece razoavel: escolher as tecnicas, derivar os assets, mandar produzir. O defeito e que
**coreografia e medicao entram depois da arte existir**, e as duas mudam a arte.

Custo real, tudo registrado:

| Descoberta tardia | O que quebrou |
|---|---|
| a coreografia exigia o martelo se movendo | o martelo estava dentro de uma **imagem estatica de fundo**; virou sprite, 8 assets viraram 9 |
| a brasa pousa na bigorna | faltavam quadros de esmagamento e assentamento: 4 -> 6 quadros |
| a faixa inferior sofre cisalhamento | restricao de composicao descoberta com o fundo ja pronto |
| a cicatriz e escrita em tiles | exigia 32x16 px de superficie limpa que ninguem tinha reservado |
| revisao de vitrine | martelo 6 -> 7 quadros **depois do despacho ja enviado** |
| dedup nunca medido no asset | `bg_b` com 2% de dedup, 1093 tiles, re-autoria completa do fundo |
| coreografia nunca medida | 36 sprites numa scanline, `status: error`, contra um limite de 20 |
| contrato nunca reconciliado | contrato declarando 56 estilhacos enquanto a ROM rodava 32 |

Nenhum desses e erro de arte. Todos sao **consequencia de perguntar tarde**.

---

## A ordem canonica

```
1. ROTEIRO          o que a cena diz, em prosa, do primeiro ao ultimo quadro
2. STORYBOARD       o que se ve, quadro-chave a quadro-chave, com posicao na tela
3. COREOGRAFIA      o que se move, para onde, em quantos quadros, com que peso
4. MEDICAO          scanline, pixel por linha, VRAM, DMA, CPU — antes de qualquer arte
                    Tetos: `doc/03_art/live_scene_bar_parameters.json` (nao inventar numeros)
5. ORCAMENTO        decisoes de streaming, residencia, teto por ato
6. CONTRATO DE ASSET  derivado dos passos 2-5, com ancoras de posicao e restricoes
7. MODEL SHEET      direcao provada, aprovada por humano
8. ASSETS           producao
9. RUNTIME          implementacao
10. EVIDENCIA       emulador, dump, reconciliacao do contrato com o que roda
```

**Os passos 3, 4 e 5 nao custam arte.** Sao Python e planilha. Erram barato e cedo, e e por
isso que vem antes.

---

## O que cada passo precisa conter

### 1. Roteiro

Prosa, do primeiro ao ultimo quadro. Sem tecnica, sem asset. O que o espectador entende e
sente, e em que ordem. Se o roteiro nao existe, a cena vira lista de efeitos.

### 2. Storyboard — o passo mais pulado

Quadros-chave com **posicao na tela**. Nao e concept art: e planta baixa.

- **onde cada objeto fica**, em coordenada de pixel, nao em "no centro";
- **o que entra, o que sai, e por qual borda**;
- **sucessao de nomes, fontes e direcoes**: em que ordem os wordmarks aparecem, qual
  tipografia cada um usa, de onde cada um vem;
- **enquadramento**: o que ocupa o terco superior, o inferior, o que fica em silhueta;
- **o que permanece na tela** entre um quadro-chave e o seguinte;
- **como cada elemento SAI**, elemento por elemento. Proibir corte a preto sem declarar a
  alternativa vira "nunca remova nada" e a tela acumula. Continuidade e ter saida desenhada —
  scroll, fade ou substituicao — nao ausencia de remocao;
- **zonas de tela com papel fixo**, e a regra de quantos elementos cada zona aceita ao mesmo
  tempo. Um palco que aceita um wordmark por vez impede empilhamento por construcao.

Sem storyboard, `img_forge_bg_a_props` nao teria a bigorna em (128,104) e a brasa pousaria no
ar. Essa ancora so apareceu na fase 10, depois da arte despachada.

### 3. Coreografia

Para cada objeto que se move: trajetoria, duracao em quadros, curva de aceleracao, o que
acontece no contato, e quantos sprites vivem em cada janela.

E aqui que se descobre que **um objeto que se move nao pode viver dentro de uma imagem
estatica de fundo**.

### 4. Medicao — antes da arte, sempre

- pressao de scanline pelos **dois** limites (`vdp_scanline_simulator.py`);
- residencia de tiles com dedup H/V (`audit_tile_residency.py`), que so precisa dos assets
  candidatos, nao dos finais;
- custo de DMA por quadro e por evento;
- CPU: divisoes, loops por quadro, tabelas recomputadas.

Varredura de **todos** os quadros da janela, nunca de um quadro escolhido.

### 5. Orcamento

Decisoes que mudam o que o artista desenha: streaming ou residente, quantos quadros de
animacao cabem, quanto de VRAM sobra por ato. **Nao sao decisoes de arte** e precisam estar
fechadas antes do despacho.

### 6. Contrato de asset

So agora. Derivado dos passos 2 a 5, carregando:

- dimensao, paleta e papel de indice;
- **ancoras de posicao** com coordenada;
- **restricoes de composicao** (area reservada, faixa que sofre cisalhamento, folga de rampa);
- contagem de quadros ja fechada pela coreografia.

### 7 a 10

Model sheet aprovado antes do pacote; assets; runtime; evidencia. E ao final, **reconciliar o
contrato com o que roda** — contrato que descreve coreografia nao implementada e falso verde.

Antes do model sheet, a aprovacao precisa comparar o papel visual contra a
`quality_reference_board` do projeto conforme
`tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`. A comparacao preserva
anatomia, materiais, landmarks e funcao das camadas; ela nunca e uma aprovacao
relativa ao placeholder anterior.

---

## Regras que caem fora da ordem

**Mudanca depois do despacho e evento, nao detalhe.** Se a spec de um asset muda com o
artista trabalhando, isso vai no topo do brief, marcado, com o que preservar do trabalho
existente. Foi assim que o martelo 6 -> 7 quadros nao virou refacao total.

**Direcao pode estar errada.** Quando o artista entrega diferente e o resultado le melhor,
corrija a direcao. Aconteceu duas vezes: a exigencia de silhueta "sobre transparente" era
aperto sem ganho, e "leve, sem chanfro" para o PRESENTS produziu contraste de −8 porque pedia
discricao sem piso.

**Nenhum gate ve composicao.** Todos os validadores deste workspace medem hardware:
residencia, scanline, proveniencia, compreensao de marca. Uma cena com quatro elementos
empilhados na mesma faixa passa em todos eles com folga. Composicao se pega com planta baixa e
revisao humana, nunca com validador — e por isso o passo 2 nao tem substituto automatico.

**Nao invente numero de asset.** `img_forge_bg_a_props` foi hardcoded como 304 tiles a partir
de uma contagem propria; o ResComp gerou 309, e os cinco de diferenca encheram a tela de lixo.
Derive de `tileset->numTile`.

---

## Como usar

Projeto novo com cena nao trivial: siga os 10 passos.

Projeto com arte ja produzida fora de ordem: nao refaca por refazer. Rode os passos 3, 4 e 5
sobre o que existe e **veja o que eles invalidam**. Foi assim que a coreografia revelou que a
lista de assets estava errada, e ainda deu tempo de corrigir antes do runtime.
