# Route Exploration Board - METAL_SLUG_URBAN_SUNSET

Este documento registra rotas visuais alternativas para a cena urbana, sem quebrar o fluxo canonico de curadoria.

## Fontes deste estudo

- source original: [source.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/data/source/source.png)
- crop de estudo: [city_cropped_448x224.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/data/city_cropped_448x224.png)
- caso canonico do workspace: [route_exploration_board.md](/F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/.agent/lib_case/art-translation/case_scene_route_variants_city_crop/route_exploration_board.md)

## Regra central

As alternativas podem variar atmosfera, temperatura global, contraste, dithering e peso entre `BG_A` e `BG_B`.

As alternativas nao podem variar:

- perspectiva
- geometria principal
- enquadramento
- papel estrutural da rua, predios e viaduto

## Rotas vivas

### Rota A - High-Key Haze

- leitura: ceu claro, ambiencia luminosa, vitrines e janelas mais destacadas
- vantagem: look moderno e limpo, com bom impacto imediato
- risco: enfraquece a fantasia de sunset dramatico do caso original

### Rota B - Duplicata de A

- estado: mesma imagem da rota A
- regra: tratar como duplicata, nao como nova direcao

### Rota C - Grid Alignment

- leitura: board de alinhamento e verificacao de grade
- uso: diagnostico de composicao e pixel lock
- regra: nao promover como arte final

### Rota D - Cool Evening

- leitura: ceu azul frio, contraste termico mais claro entre ar e luz interna
- vantagem: separacao de planos potencialmente melhor e `BG_B` mais legivel
- risco: pode afastar demais a cena da assinatura "urban sunset"

### Rota E - Anime Style

- leitura: recomposicao em filosofia de anime background, com sombra chapada, massas limpas e ceu em bandas largas
- vantagem: transforma gradiente e textura em blocos de cor mais claros para o Mega Drive, com forte potencial de reuse
- risco: se exagerar na limpeza, pode empobrecer a aspereza material do caso original e afastar a cena do peso "Metal Slug"

### Rota F - Anime Background Reference

- leitura: fundo ilustrado noturno, com linework fino, rampas controladas e janelas quentes sobre ceu azul-petroleo
- origem: referencia humana aprovada em [Gemini_Generated_Image_riu4i2riu4i2riu4.png](</C:/Users/misae/Downloads/Gemini_Generated_Image_riu4i2riu4i2riu4.png>)
- vantagem: define com mais precisao o que "anime" significa para esta cena
- risco: a promocao direta ainda gera pressao alta de tiles; precisa de reducao estrutural mais cuidadosa
- regra:
  - esta rota substitui o entendimento anterior de `anime_style` como alvo estetico
  - o teste `anime_style` anterior fica registrado apenas como tentativa rejeitada

### Rota G - Anime Line-First

- leitura: a cena passa primeiro por `line art only`, depois por promocao Mega Drive do traco, e so entao recebe pintura por massas amplas
- origem:
  - [estilo anime.png](</C:/Users/misae/Downloads/estilo anime.png>)
  - [estilo anime somente com os traços.png](</C:/Users/misae/Downloads/estilo anime somente com os traços.png>)
  - [estilo anime recolorido pela IA 16 cores.png](</C:/Users/misae/Downloads/estilo anime recolorido pela IA 16 cores.png>)
- vantagem:
  - corrige o erro anterior de misturar desenho, paleta e budget no mesmo passo
  - produz linhas mais firmes e massas de cor mais controladas
  - ja tem duas promocoes que cabem no budget real
- perfis vivos:
  - `anime_linefirst_balanced`: mais claro, mais proximo do board recolorido, `1261` tiles totais, score `0.7184`
  - `anime_linefirst_cohesive`: mais noturno e coeso com a referencia anime, `1248` tiles totais, score `0.6988`
- risco:
  - ainda simplifica materiais mais do que o metodo padrao do projeto
  - precisa de congelamento humano explicito antes de substituir o default

## Recomendacao de curadoria

- manter A e D como referencias de atmosfera
- tratar E como tentativa rejeitada de interpretacao
- tratar F como alvo estetico correto para a linha anime
- tratar G como o primeiro processo anime que fechou budget de forma reproduzivel
- usar C apenas como board tecnica
- escolher a rota final antes de nova rodada de budget e runtime
- o default continua sendo o metodo padrao atual ate existir `perceptual win` + `system win` e congelamento explicito do usuario
- apos a escolha, registrar em `route_decision_record` e preservar a linguagem nas proximas iteracoes
