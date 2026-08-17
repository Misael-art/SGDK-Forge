# Rework brief — `model_sheet_forge_v02.png`

Origem: `doc/model_sheet_review_v01.md` (recomendacao `rework`)
Direcao inalterada: `doc/branding_v2_art_direction.md`
Contrato inalterado: `branding_sequence_v2`

Isto e uma passada de correcao, nao um recomeco. A v01 acertou o que era mais dificil.

---

## NAO REFACA — isto passou

- **A lei da luz do painel A.** Fornalha no piso, barriga da bigorna e parede lavando em
  laranja, plano superior escuro, pedra distante em azul-violeta. Temperatura fazendo
  trabalho estrutural. Preserve esta composicao.
- **O bico conico da bigorna** como `silhouette_hook`. Le em silhueta. Mantenha.
- **O painel B.** Preto sobre branco e convencao de estudio; minha especificacao original
  pedia transparente e estava apertada sem ganho. Foi relaxada. O painel esta aprovado.
- **A estrutura do painel E**: 16x16 nativo presente, ampliacao marcada com `4X`.
- **Toda a rota de proveniencia.** `assemble_model_sheet.py` sem primitivas, fontes em
  `raw/` com sha256, `model_sheet_lineage.json`. Reaproveite o assemblador.

---

## CAUSA TECNICA A CORRIGIR PRIMEIRO

**As 14 fontes brutas sao JPG.** `wordmark_forja_v02.jpg` tem 66.030 cores unicas; o painel D
final tem 13. O ringing e o blocking do JPEG sobrevivem a quantizacao e viram o salpico que
esta dentro das letras e da pedra. Isso nao e dither com funcao de material — e artefato de
compressao, e a direcao proibe dither sem papel.

Duas saidas, escolha uma e declare no lineage:

1. gerar as fontes em PNG lossless; ou
2. manter JPG e inserir uma passada de posterizacao/denoise **antes** do remap de paleta no
   assemblador.

Sem isso, qualquer correcao de luz vai continuar chegando suja no PNG final.

---

## BLOCKERS, na ordem de consequencia

### 1. Wordmark do painel D — o item de maior impacto

Ele vira `img_logo_engine_v2`. Errar aqui contamina o ato 2 inteiro.

- **Reiluminar de baixo.** Hoje cada letra tem uma calota clara e espessa na aresta
  superior. Nao existe fonte de luz superior nesta cena. A massa de luz vai para a aresta
  **inferior**, com chanfro de 45 graus e 1px de luz de chanfro; o topo fica em sombra fria.
- **Trocar para a rampa de ferro de PAL1.** Hoje esta azul-ardosia, lendo como pedra fria.
  Use: sombra fria violeta-azul em 1-3, corpo de ferro em 4-8, metal aquecido em 9-12, e a
  folga de highlight em 13-14 com canal maximo `<= 0xCC`. Sobre azul-ardosia a varredura
  especular do ato 2 nao significa nada.
- **Marca de ferramenta assimetrica em exatamente uma letra.** As 5 estao uniformes, o que
  cai no `generic_blocker` "wordmark centrado e simetrico". Uma mossa, um corte, uma rebarba
  — algo que so uma letra tem.
- **Altura util de 64px**, conforme a secao 9.

### 2. Martelo do painel A

- Esta **iluminado por cima**, dentro do painel cuja funcao e provar a iluminacao inferior.
  A face superior da cabeca esta mais clara que a inferior. Inverta.
- Esta pequeno demais e sem cunha, entao falha como `silhouette_hook` numero 2. Aumente e
  de a ele um lado plano e um lado em cunha, legivel em preto chapado.

### 3. Brasa do painel E — 4 quadros como rotacao real

Hoje sao 4 manchas amarelas parecidas. A regra e literal: quatro desenhos parecidos nao
formam rotacao. Desenhe **um** nucleo emissivo e gire-o, mantendo o volume reconhecivel
quadro a quadro. Sem contorno: brasa e luz, nao objeto.

### 4. Estilhaco do painel E — 4 angulos genuinos

Os quadros 1 e 4, e 2 e 3, ja sao espelhos entre si. Como o runtime gera as orientacoes por
flip H/V, isso colapsa as 16 orientacoes esperadas para cerca de metade. Os 4 precisam ser
angulos distintos, pensados para que o flip **acrescente** variedade em vez de repetir.

---

## REWORK menor, pode entrar na mesma passada

### 5. Parede do painel A

A alvenaria le como grade quase regular — o `generic_blocker` "grid de pedra regular e
visivel (cookie-cutter)". Quebre a modularidade: fiadas irregulares, blocos de tamanhos
diferentes, uma ou duas pedras faltando ou trincadas. E troque o salpico por hachura por
cluster, que e a gramatica de material que a direcao pede para pedra.

### 6. Painel C — devolver os rotulos de indice

Os rotulos se perderam. Os checks mecanicos de folga de highlight e de ciclo de brasa passam
porque o gate le a tabela de paleta do PNG, nao o painel — entao nada de mecanico foi
perdido. Mas o painel C existe para a revisao humana conferir a olho, e sem rotulo ele nao
cumpre a funcao. Rotule por indice, na ordem PAL0, PAL1, PAL2, PAL3.

---

## Entrega

- `data/source_art/branding_v2/model_sheet_forge_v02.png`
- `model_sheet_lineage.json` atualizado, incluindo a decisao sobre o formato das fontes
- `doc/authoriality_gate_report.json` revalidado
- autocritica nova: a da v01 foi honesta e util, mantenha o mesmo padrao

Rode antes de me chamar:

```bash
python3 tools/sgdk_wrapper/validate_model_sheet_contract.py \
  --model-sheet data/source_art/branding_v2/model_sheet_forge_v02.png \
  --output doc/model_sheet_contract_report.json
python3 tools/sgdk_wrapper/art_diagnostic.py
python3 tools/sgdk_wrapper/art_quality_gate.py
```

Continua valendo: nenhum pixel pode nascer de primitiva, e voce pode encerrar dizendo que a
arte nao atingiu o nivel se for verdade. Isso e entrega honesta, nao falha.

**PARE depois da v02.** Os 8 assets finais so comecam com o model sheet aprovado pelo curador
humano.
