# 15 - Diretrizes de Producao de Assets Visuais

**Status:** Definitivo
**Plataforma:** Mega Drive / Genesis via SGDK 2.11
**Projeto:** Pequeno Principe: Cronicas das Estrelas

> **REGRA:** Este documento e de leitura obrigatoria para qualquer agente de IA ou humano
> que gere, edite, revise ou importe assets graficos para este projeto.
> Nenhum asset entra no projeto sem satisfazer TODAS as especificacoes aqui descritas.
> Violacao de qualquer item resulta em rejeicao imediata do arquivo.

---

## 1. OBJETIVO

Produzir pixel art de excelencia para a plataforma 16-bits, extraindo o maximo do hardware
do Mega Drive sem jamais violar seus limites fisicos. A economia de tiles e VRAM e
fundamental, mas nao deve sacrificar o impacto visual.

O nivel de qualidade almejado e o de obras-primas da plataforma: jogos como Gunstar Heroes,
Castlevania Bloodlines, Sonic 3 e Streets of Rage 2 demonstram que restricao nao e
desculpa para arte fraca.

---

## 2. DIRECAO DE ARTE E CONTEXTO VISUAL

### 2.1 Referencia visual canonica

O arquivo `doc/Concept art.jpg` e a biblia visual do projeto. Todo asset deve ser
coerente com ele em paleta, contornos, ornamentacao e escala.

### 2.2 Identidade do estilo

| Atributo | Diretriz |
|----------|----------|
| Estilo geral | Mistura de delicadeza narrativa com pixel art preciso de 16-bits |
| Contornos | Vivos, levemente irregulares, como giz de cera sobre papel |
| Massas de cor | Planas e decididas, sem hesitacao |
| Dithering | Usado como linguagem visual (textura intencional), nunca como acidente ou simulacao de gradiente |
| Tons | Pasteis quentes, sem gradientes complexos |
| Iluminacao | Direcional simples, consistente dentro de cada cena |

### 2.3 Coerencia de estilo

Todos os sprites e tiles de uma mesma cena devem seguir:

- O mesmo peso visual de contorno (espessura de outline consistente).
- A mesma direcao de luz (a menos que a cena mude explicitamente — ex: Lampiao antes/depois de acender).
- A mesma proporcao de detalhe: um sprite NPC nao pode ser mais detalhado que o player na mesma cena.
- A mesma linguagem de dithering: se o cenario usa dithering ordenado 2x2, os sprites devem ser compattiveis.

### 2.4 Proporcao e escala

- O tamanho do sprite e ditado pela sua importancia na cena e pelo budget de VRAM.
- Player: 16x24 (placeholder) ou 32x32 max (asset final). Sempre presente, sempre legivel.
- NPCs/marcos: devem ter escala proporcional ao player.
- Projéteis/particulas: menores possiveis (8x8 ou 16x16).
- **Eliminar espacos transparentes** desnecessarios ao redor do sprite para economizar tiles.
- **Recortar ao tile grid (8x8)** desde a concepcao — nao como ajuste posterior.

### 2.5 Animacao

- Frames devem ser logicos: cada pose intermediaria deve existir naturalmente entre a anterior e a proxima.
- Demonstrar peso e inercia compativeis com a fisica do jogo (fix16/fix32).
- Minimo de frames para fluidez, maximo de impacto por frame:
  - Idle: 2-4 frames
  - Walk: 4-6 frames
  - Jump: 2-3 frames (subida, apice, queda)
  - Acoes especiais: 2-4 frames
- Priorizar keyframes expressivos sobre transicoes suaves. Na TV CRT, 3 bons frames vencem 8 genericos.

### 2.6 Leitmotivs por planeta

Cada planeta tem identidade visual propria que os assets devem respeitar:

| Planeta | Tom visual | Paleta dominante |
|---------|-----------|------------------|
| B-612 | Intimidade, por do sol | Laranjas, ocres, dourados |
| Rei | Escala vertical, majestade | Purpuras, vermelhos, dourados |
| Lampiao | Calor, luz, contraste | Ambar, azul frio (topo), laranja quente (base) |
| Deserto | Silencio, vastidao, vento | Beges, amarelos palidos, azul profundo |

Para planetas expandidos (v2.0), consultar `doc/11-gdd.md` secao 5.2.

---

## 3. TECNICAS AVANCADAS DE PIXEL ART PARA HARDWARE

> **OBJETIVO:** Estas tecnicas separam pixel art competente de pixel art obra-prima.
> O artista (humano ou IA) deve aplicar cada tecnica sempre que o contexto da cena
> tornar oportuno. Nao sao opcionais — sao o caminho para rivalizar com Thunder Force IV,
> Castlevania Bloodlines e Sonic 3 usando as mesmas restricoes de hardware.
>
> **PRINCIPIO:** Nao basta "reduzir cores" de uma imagem. E preciso projetar a arte
> para o hardware — usar o VDP como ferramenta criativa, nao como limitacao.

### 3.1 CRT Dithering — A Textura de Giz de Cera

O sinal de video composto do Mega Drive "borra" padroes de pixels alternados na TV CRT.
Isso nao e defeito — e uma ferramenta de arte que os melhores artistas da era 16-bits
dominavam. Neste projeto, e o mecanismo que recria a textura de giz de cera e pastel
do universo do Pequeno Principe.

**Como funciona:**
- Dois pixels vizinhos de cores diferentes (ex: laranja + amarelo em xadrez 1x1)
  sao misturados opticamente pelo sinal composite da TV CRT.
- O resultado e uma terceira cor que nao existe na paleta — criada de graca pelo hardware.
- Isso efetivamente **dobra** o numero de cores percebidas sem custo de VRAM ou paleta.

**Padroes recomendados:**

| Padrao | Uso | Efeito na CRT |
|--------|-----|---------------|
| Xadrez 1x1 (checkerboard) | Texturas de terreno, ceu, pele | Blend suave das 2 cores = cor intermediaria |
| Hachura vertical (colunas alternadas) | Superficies verticais, cortinas, cascatas | Blend com leve direcionalidade |
| Hachura horizontal (linhas alternadas) | Ceu, agua, nevoeiro | Blend horizontal, bom para gradientes atmosfericos |
| Hachura diagonal | Sombras, profundidade | Textura com ritmo visual, simula profundidade |
| Xadrez 2x2 (blocos alternados) | Texturas grossas, pedra, terra | Mistura mais visivel, textura "granulada" |

**Regras de aplicacao:**

1. **Projetar para CRT primeiro, verificar em LCD depois.** O resultado em LCD sera
   um padrao de pontos visivel — isso e aceitavel. O resultado em CRT e que define a qualidade.
2. **Usar dithering como linguagem, nao como remendo.** Dithering ordenado e intencional
   (xadrez, hachura) — nunca error diffusion ou dithering aleatorio.
3. **Respeitar a distancia de visualizacao.** Dithering 1x1 funciona em areas grandes
   (ceu, terreno). Para detalhes pequenos (rosto, maos), usar cores solidas.
4. **Limitar a 2 cores por padrao de dithering.** Misturar 3+ cores no mesmo padrao
   cria ruido visual em vez de textura.
5. **O dithering substitui gradientes — nunca o contrario.** Onde o concept art mostra
   transicao suave, o pixel art deve usar dithering. Nunca tentar simular gradiente
   com multiplas cores solidas em faixas finas.

**Exemplo concreto — textura de giz de cera:**
```
Conceito: area dourada com textura artesanal
Cores da paleta: Index 3 = ocre (#CC8844), Index 4 = amarelo claro (#EEAA44)
Padrao: xadrez 1x1 alternando index 3 e 4
Resultado CRT: tom dourado quente com textura manual implicita
Custo: 0 cores extras, 0 tiles extras, 0 DMA
```

### 3.2 Paleta Quente Dinamica — Color Cycling via VDP

O Mega Drive pode trocar qualquer cor da CRAM (Color RAM) a cada frame via
`PAL_setColors()` no VBlank. Isso cria animacoes de cor que nao consomem tiles,
nao consomem DMA de tilemap e custam apenas 2 bytes por cor trocada.

**Onde aplicar neste projeto:**

| Cena | Efeito | Implementacao |
|------|--------|---------------|
| B-612 (por do sol) | Ceu que transiciona de dia para noite | 4 estados de paleta rotacionando a cada 32 frames. Faixas grossas de ceu com dithering nas bordas. 0 tiles trocados, ~12 bytes DMA/frame |
| Lampiao (acender/apagar) | Zona quente que se ilumina gradualmente | Paleta inferior muda de escura para iluminada via H-Int split |
| Deserto (calor) | Miragem com oscilacao de cor | 2 cores de areia alternando levemente a cada 8 frames |
| Travel (transicao) | Espacosideral pulsando | Estrelas mudam de brilho com cycling de 3 frames |

**Regras para o artista:**

1. **Projetar areas de cycling como blocos de cor solida + dithering nas bordas.**
   O cycling troca a cor; as bordas em dithering criam transicao suave entre as faixas.
2. **Marcar na entrega quais indices da paleta serao animados por cycling.**
   Ex: "Index 5 e 6 sao cores de cycling do ceu — serao trocadas pela engine."
3. **Usar no maximo 4-6 cores de cycling por cena.** Cada cor = 2 bytes de DMA.
   6 cores = 12 bytes — irrelevante no budget. Mas trocar 15 cores por frame
   pode causar flash visivel se o timing nao for perfeito.
4. **Nunca desenhar gradiente como tiles diferentes.** Se o efeito pode ser feito
   com cycling + dithering, usar cycling. Tiles de gradiente consomem VRAM;
   cycling consome zero.

### 3.3 Shadow / Highlight — Iluminacao Nativa do VDP

O VDP do Mega Drive possui o modo Hilight/Shadow (`VDP_setHilightShadow(TRUE)`)
que altera matematicamente o brilho de cada pixel renderizado:

- **Normal:** cor como definida na paleta.
- **Shadow:** cor escurecida em ~50% (bit shift nos valores RGB).
- **Highlight:** cor clareada em ~50%.

O modo e controlado por prioridade de tiles e sprites. Tiles com prioridade alta
em certas configuracoes forcam highlight/shadow nas areas cobertas.

**Onde aplicar neste projeto:**

| Cena | Efeito | Como o artista deve desenhar |
|------|--------|------------------------------|
| B-612 | Halo de luz ao redor da rosa | Desenhar cenario em tons medios. O halo sera gerado pelo VDP clareando a area — nao desenhar halo na arte |
| Lampiao | Luz do poste iluminando a area proxima | Desenhar a cena como se fosse noite total. A iluminacao e gerada pelo hardware ao redor do sprite do lampiao |
| Planeta da Serpente (v2.0) | Escurecimento progressivo | Cenario em tons normais; shadow mode escurece tudo exceto o circulo de luz |

**Regras para o artista:**

1. **Nunca desenhar halos de luz ou sombras ambientais na arte.** O VDP calcula isso.
   Se voce desenhar um halo amarelo na arte, o VDP vai clarear o halo desenhado,
   resultando em branco estourado.
2. **Projetar paletas em tons medios quando a cena usa hilight/shadow.** O VDP
   vai clarear e escurecer — se a paleta ja tiver brancos, o highlight satura.
   Se ja tiver pretos, o shadow desaparece.
3. **Testar a paleta nos 3 estados** (normal, shadow, highlight) antes de entregar.
   Cada cor deve ter resultado aceitavel nos 3 brilhos.
4. **A arte nao deve "precisar" de highlight para funcionar.** O modo shadow/highlight
   e um bonus atmosferico. A arte deve ser legivel mesmo com o modo desabilitado.

**Tabela de referencia — comportamento de cores no modo Hilight/Shadow:**

| Cor original (3 bits por canal) | Shadow (escurecido) | Highlight (clareado) |
|--------------------------------|--------------------|--------------------|
| (7,7,7) branco | (3,3,3) cinza | (7,7,7) branco (saturado) |
| (4,4,4) cinza medio | (2,2,2) cinza escuro | (6,6,6) cinza claro |
| (7,4,0) laranja | (3,2,0) marrom | (7,6,4) pessego |
| (0,0,2) azul noite | (0,0,1) azul profundo | (4,4,6) azul acinzentado |

### 3.4 Parallax Curvo Matematico — Arte Projetada para Scroll por Linha

O scroll por linha (H-Int ou tabela de hscroll) permite mover cada scanline
independentemente. Quando o artista desenha o cenario sabendo disso, o resultado
e ilusao de profundidade, curvatura e dimensionalidade impossivel em arte estatica.

**Onde aplicar neste projeto:**

| Cena | Efeito | Como desenhar |
|------|--------|---------------|
| B-612 | Planeta esférico girando | Chao em faixas horizontais de terra; o scroll curvo faz girar mais rapido no centro |
| Rei | Parallax multicamada | BG_B em 3 faixas de velocidade; detalhes alinhados para nao "quebrar" quando se moverem em velocidades diferentes |
| Deserto | Miragem de calor | Linhas inferiores com dithering horizontal que sera distorcido pelo sine scroll |

**Regras para o artista:**

1. **Desenhar cenarios em faixas horizontais com independencia visual.**
   Cada faixa deve funcionar visualmente mesmo se deslocada 8-16 pixels em relacao a faixa de cima.
   Nao desenhar detalhes verticais que cruzem muitas faixas — eles vao "quebrar"
   quando o scroll deformar.
2. **Marcar na entrega as faixas de scroll.** Ex: "Linhas 0-40: ceu estatico.
   Linhas 41-100: parallax lento. Linhas 101-184: scroll curvo rapido."
3. **Para cenarios curvos (B-612), desenhar a area central mais detalhada.**
   O centro da curvatura e onde o olho do jogador foca — o scroll e mais rapido
   ali, entao precisa de mais informacao visual para nao parecer borrado.
4. **Evitar padroes repetitivos obvios em areas de scroll rapido.** O olho
   percebe repeticao quando tiles identicos passam rapido. Adicionar variacao
   sutil (1-2 pixels de diferenca) nos tiles de terreno.
5. **Backgrounds para parallax devem ter profundidade implicita na arte.**
   Elementos mais distantes: menos detalhe, cores mais frias/apagadas.
   Elementos mais proximos: mais detalhe, cores mais quentes/saturadas.
   O scroll faz o resto.

### 3.5 A Regra do Contorno Sepia — Proibicao do Preto Puro

Para manter a identidade visual de "livro infantil em pastel", este projeto
adota uma regra absoluta de contorno:

> **NUNCA usar preto puro (RGB 0,0,0 / VDP 0,0,0) como cor de contorno.**

**Por que:**
- O Mega Drive tem apenas 512 cores. Preto puro e o valor mais extremo do espectro.
- Em uma paleta pastel com tons quentes, o preto puro "mata" a leveza e cria
  contraste agressivo que nao pertence ao universo poetico do Pequeno Principe.
- O preto puro deve ser reservado exclusivamente para areas de ausencia total
  de luz (espacos vazios do cosmos, interior de buracos) e nunca para contornos.

**O que usar no lugar:**

| Contexto | Cor de contorno recomendada | Valor VDP (3 bits) |
|----------|---------------------------|-------------------|
| Personagens e NPCs | Marrom sepia escuro | (1,1,0) ou (2,1,0) |
| Vegetacao e terreno | Verde muito escuro | (0,1,0) ou (1,1,0) |
| Ceu e elementos celestes | Azul marinho profundo | (0,0,1) ou (0,0,2) |
| Estruturas e objetos | Marrom grafite | (1,1,1) ou (2,1,1) |
| Personagens quentes (Rosa, Lampiao) | Borgonha escuro | (2,0,0) ou (2,1,0) |

**Regras:**
1. **O contorno e sempre uma cor escura da mesma familia cromatica do objeto.**
   Contorno da rosa = borgonha. Contorno do principe = sepia. Contorno do ceu = azul marinho.
2. **Uma unica cor de contorno por sprite.** Nao use 3 tons de contorno
   no mesmo personagem — isso desperdia slots de paleta.
3. **O contorno de giz deve ter irregularidade controlada.** Linhas retas
   perfeitas de 1px parecem digitais. Adicionar 1 pixel de "respiro" a cada
   8-12 pixels de contorno (um desvio de 1px para dentro ou fora) cria
   a sensacao manual de giz de cera.
4. **Excecao: o cosmos.** O espaco entre estrelas e preto puro (0,0,0).
   Isso e ausencia de luz, nao contorno. E o unico uso aceitavel de preto puro.

### 3.6 Catalogo de Tecnicas por Cena

A tabela abaixo mapeia quais tecnicas avancadas o artista DEVE considerar ao
produzir assets para cada cena. A coluna "Obrigatorio" indica tecnicas que
devem estar presentes; "Oportunidade" indica onde podem ser aplicadas se
o budget permitir.

| Cena | CRT Dithering | Color Cycling | Shadow/Highlight | Parallax Curvo | Contorno Sepia |
|------|:------------:|:------------:|:---------------:|:--------------:|:--------------:|
| B-612 | Obrigatorio (textura do solo) | Obrigatorio (ciclo dia/noite) | Obrigatorio (halo) | Obrigatorio (curvatura) | Obrigatorio |
| Rei | Obrigatorio (textura do palacio) | Oportunidade (bandeiras) | Nao usar | Obrigatorio (parallax 3 faixas) | Obrigatorio |
| Lampiao | Obrigatorio (textura da noite) | Obrigatorio (acender/apagar) | Obrigatorio (halo do lampiao) | Oportunidade (heat wobble) | Obrigatorio |
| Deserto | Obrigatorio (textura da areia) | Oportunidade (miragem) | Nao usar | Obrigatorio (scroll de vento) | Obrigatorio |
| Travel | Oportunidade | Obrigatorio (transicao) | Nao usar | Nao usar | Obrigatorio |
| Telas de texto | Nao usar | Nao usar | Nao usar | Nao usar | Obrigatorio |

---

## 4. ESPECIFICACOES TECNICAS ABSOLUTAS

> **Estas sao restricoes fisicas do hardware. Violacao causa erro de compilacao no SGDK
> ou falha de renderizacao no hardware real. Nao sao sugestoes.**

### 3.1 Modo de cor

| Regra | Especificacao |
|-------|---------------|
| Modo de cor | **Cores Indexadas (Indexed Color Mode)** — obrigatorio |
| Profundidade | 4 bits por pixel (16 indices) |
| Formato de exportacao | `.PNG` ou `.BMP` estritamente indexado |
| Color space | sRGB |

### 3.2 Paleta: 16 cores (15 visiveis + 1 transparente)

| Indice | Uso |
|--------|-----|
| **Index 0** | Cor de transparencia — **obrigatorio usar cor solida de alto contraste** |
| Index 1-15 | Dados visuais do sprite/tile |

**Cor padrao de transparencia deste projeto:** Magenta `#FF00FF`.

Se o asset usar fundo que nao e magenta puro no index 0, sera rejeitado.

### 3.3 Paleta mestre do Mega Drive

O VDP do Mega Drive usa 9 bits de cor (3 bits por canal: R, G, B), resultando em 512 cores possiveis.
Os valores validos por canal sao: `0x00`, `0x22`, `0x44`, `0x66`, `0x88`, `0xAA`, `0xCC`, `0xEE`.

**Todo hex de cor no asset deve mapear para um valor valido do VDP.**

Cores fora dessa grade serao arredondadas pelo SGDK e o resultado pode nao ser o esperado.

### 3.4 Dimensoes

| Regra | Especificacao |
|-------|---------------|
| Grid de tiles | **8x8 pixels** — todas as dimensoes devem ser multiplos de 8 |
| Sprites | Tamanhos validos: 8x8, 8x16, 8x24, 8x32, 16x8, 16x16, 16x24, 16x32, 24x8, 24x16, 24x24, 24x32, 32x8, 32x16, 32x24, 32x32 |
| Sprite sheets | Largura e altura totais devem ser multiplos de 8 |
| Tilemaps | Largura e altura devem ser multiplos de 8 |

### 3.5 Nitidez

- Bordas de pixel **limpas e duras** (Hard Edges).
- Cada pixel ocupa exatamente 1 unidade no grid — sem sub-pixel, sem blur.
- Zoom de exportacao: **1x** (escala nativa). Nunca exportar em 2x, 4x ou qualquer escala ampliada.

### 3.6 Entregaveis obrigatorios por asset

Todo asset entregue deve incluir:

1. **Arquivo de imagem** (.PNG ou .BMP indexado, 1x).
2. **Barra visual de paleta** numerando as 16 cores de 0 a 15 com seus codigos hexadecimais.
3. **Mapa de indices** descrevendo o que cada cor representa (ex: "Index 3 = pele", "Index 7 = contorno").
4. **Dimensoes em tiles** (ex: "3x4 tiles = 24x32 pixels").
5. **Contagem de tiles unicos** (para estimar impacto na VRAM).

---

## 4. RESTRICOES CRITICAS — O QUE NAO FAZER

> A presenca de **qualquer** item abaixo resulta em **rejeicao imediata** do arquivo.

### 4.1 Transparencia

| PROIBIDO | CORRETO |
|----------|---------|
| Fundo quadriculado (checkerboard) para simular transparencia | Cor solida `#FF00FF` no index 0 |
| Pixels semi-transparentes (alpha entre 0% e 100%) | Pixels 100% opacos ou 100% transparentes (index 0) |
| Canal alpha com gradiente | Sem canal alpha — usar paleta indexada |

### 4.2 Sombras e iluminacao

| PROIBIDO | CORRETO |
|----------|---------|
| Sombra de chao (drop shadow) sob o personagem/objeto | Sem sombra — a engine gera dinamicamente |
| Iluminacao "assada" (baked lighting) que cria cores fora da paleta | Iluminacao implicita na escolha das 15 cores |
| Brilhos (glows) com cores extras | Brilho representado por 1 cor clara da paleta (highlight) |
| Rim light que adiciona cor 16+ | Rim light dentro dos 15 slots |

### 4.3 Anti-aliasing e suavizacao

| PROIBIDO | CORRETO |
|----------|---------|
| Anti-aliasing automatico (bordas suavizadas) | Bordas pixeladas, 1px puro |
| Gradientes suaves entre cores | Transicoes abruptas ou dithering intencional |
| Blur ou gaussian filter | Zero filtros pos-processamento |
| Sub-pixel rendering | Cada pixel = 1 cor = 1 indice |

### 4.4 Elementos intrusos

| PROIBIDO | CORRETO |
|----------|---------|
| Linhas de grade (grids) sobre o sprite | Grid apenas como referencia no editor, nunca exportado |
| Bordas de frame ou caixa ao redor | Sprite recortado no limite exato dos pixels visíveis |
| Marcas d'agua ou textos sobrepostos | Sprite limpo, sem anotacoes |
| Elementos de cenario no mesmo arquivo de sprites | Separar: sprites de personagens/objetos em um arquivo, backgrounds em outro |
| Background colorido atras do sprite (exceto index 0) | Fundo = index 0 = cor de transparencia |

### 4.5 Paleta

| PROIBIDO | CORRETO |
|----------|---------|
| Mais de 16 cores no arquivo (incluindo transparente) | Exatamente 16 indices, contagem verificada |
| Cores RGB fora da grade de 9 bits do VDP | Cores mapeadas para os 512 valores validos |
| Paletas duplicadas entre sprites da mesma cena sem justificativa | Reutilizar paleta compartilhada (ex: PAL2 do player) |
| Index 0 preenchido com cor visual (nao-transparente) | Index 0 = `#FF00FF` = transparencia |

---

## 5. OTIMIZACAO DE TILES E VRAM

### 5.1 Principios

O Mega Drive tem 64 KB de VRAM (2048 tiles de 8x8). Cada tile desperdicado e recurso
roubado do cenario, dos efeitos visuais ou de sprites adicionais.

### 5.2 Regras de economia

1. **Projetar para reuso de tiles desde o inicio.**
   - Tiles simetricos: espelhar horizontalmente via atributo de tile (flag H-flip), sem duplicar na VRAM.
   - Tiles repetidos: cenarios devem usar padroes que se repitam, nao arte unica por celula.
   - Tiles compartilhados: sprites que usam mesma cor de preenchimento podem compartilhar tiles de fill.

2. **Eliminar tiles vazios.**
   - Nenhum tile 100% transparente deve ser incluido no sprite sheet.
   - Recortar sprite no bounding box mais apertado possivel (multiplo de 8).

3. **Planar para o tile grid.**
   - Desenhar formas alinhadas ao grid de 8x8 sempre que possivel.
   - Evitar detalhes que caiam na fronteira de 2 tiles desnecessariamente.
   - Um detalhe de 1px que cruza a borda de tile custa 1 tile inteiro de VRAM.

4. **Contagem pre-entrega.**
   - Antes de entregar, contar tiles unicos (descontando flips) e comparar com o budget da cena em `doc/13-spec-cenas.md`.
   - Se exceder o budget: redesenhar para economizar, nao pedir aumento de budget.

### 5.3 Referencia de budget por tipo de asset

| Tipo de asset | Tiles VRAM max (orientacao) | Nota |
|---------------|----------------------------|------|
| Player (corpo) | 16 (4x4 tiles = 32x32) | PAL2 dedicada |
| Player (frame de animacao) | 16 por frame | Tiles que mudam entre frames = DMA por frame |
| NPC / marco | 4-16 | Proporcional a importancia |
| Projetil / particula | 1-4 | Minimo possivel |
| Tile de cenario (unico) | 1 | Projetar para reuso |
| Tilemap de cenario completo | Ver budget da cena | `doc/13-spec-cenas.md` |

---

## 6. PIPELINE DE PRODUCAO

### 6.1 Fluxo para assets gerados por IA

```
1. Especificacao do asset (consultar GDD + spec cenas + bible artistica)
     │
2. Geracao pela IA de imagem
     │
3. Pos-processamento obrigatorio:
     ├── Reduzir para paleta indexada de 16 cores
     ├── Mapear cores para grade de 9 bits do VDP
     ├── Alinhar ao grid de 8x8
     ├── Recortar bordas transparentes
     ├── Preencher index 0 com #FF00FF
     └── Verificar nitidez (zero blur, zero AA)
     │
4. Validacao contra checklist (secao 7)
     │
5. Deposito em tmp/imagegen/inbox/pequeno_principe_v2/
     │
6. Validacao automatizada:
     └── tools/image-tools/validate_pequeno_principe_asset_batch.ps1
     │
7. Promocao (apenas se PASS):
     └── tools/image-tools/promote_pequeno_principe_asset_batch.ps1
     │
8. Declaracao em resources.res
     │
9. Build + teste visual em emulador
```

### 6.2 Pos-processamento: detalhes

| Etapa | Ferramenta sugerida | Criterio de saida |
|-------|--------------------|--------------------|
| Reducao de paleta | Aseprite, GIMP (modo indexado), ImageMagick | Exatamente 16 cores, index 0 = transparencia |
| Mapeamento VDP | Script manual ou comparacao visual | Cada canal R/G/B arredondado para 0x00/0x22/.../0xEE |
| Alinhamento ao grid | Aseprite (grid 8x8), manual | Todas as dimensoes multiplo de 8 |
| Recorte | Trim automatico + pad para multiplo de 8 | Zero tiles 100% transparentes nas bordas |
| Verificacao de nitidez | Zoom 800% e inspecao visual | Zero pixels com cor intermediaria entre vizinhos |

### 6.3 Regra de ouro para IAs de imagem

> IAs generativas (DALL-E, Midjourney, Stable Diffusion, etc.) **nunca** produzem
> assets prontos para o Mega Drive diretamente. O resultado da IA e sempre **materia-prima**
> que deve passar por pos-processamento completo antes de entrar no projeto.

Esperar que uma IA generativa entregue PNG indexado com paleta de 16 cores, sem AA,
sem gradientes e alinhado ao grid de 8x8 e **alucinacao**. Planeje o pos-processamento
como parte integral do pipeline, nao como excecao.

---

## 7. CHECKLIST DE VALIDACAO PRE-APROVACAO

> Todo asset deve passar por TODOS os itens antes de ser aceito no projeto.
> Se qualquer item falhar, o asset e rejeitado e devolvido para correcao.

### Gate 1: Compatibilidade com a cena

- [ ] As proporcoes sao compativeis com a cena do jogo, o contexto narrativo e os limites do hardware?
- [ ] O asset corresponde exatamente a tarefa e a mecanica solicitada?
- [ ] O estilo visual e coerente com `doc/Concept art.jpg` e `doc/08-bible-artistica.md`?
- [ ] A escala e proporcional ao player e aos outros elementos da mesma cena?

### Gate 2: Formato tecnico

- [ ] O arquivo esta em .PNG ou .BMP com modo de cor indexado (Indexed Color)?
- [ ] A paleta tem exatamente 16 cores (15 visiveis + 1 transparente)?
- [ ] O index 0 esta preenchido com a cor de transparencia padrao (`#FF00FF`)?
- [ ] Todas as cores mapeiam para a grade de 9 bits do VDP do Mega Drive?
- [ ] As dimensoes sao multiplos exatos de 8 pixels (largura E altura)?
- [ ] O arquivo esta em escala 1x (nao ampliado)?

### Gate 3: Qualidade de pixel

- [ ] As bordas sao formadas por pixels nitidos, sem blur ou anti-aliasing?
- [ ] Nao ha gradientes suaves ou transicoes de opacidade?
- [ ] O dithering (se presente) e intencional, organizado e compativel com o estilo do projeto?
- [ ] Cada pixel pertence a exatamente 1 indice da paleta — nao ha cores intermediarias?

### Gate 4: Elementos proibidos

- [ ] Nenhuma sombra de chao (drop shadow) foi desenhada sob o personagem/objeto?
- [ ] Nenhum brilho (glow) ou iluminacao assada (baked lighting) cria cores fora da paleta?
- [ ] Nenhum fundo quadriculado (checkerboard) simula transparencia?
- [ ] Nenhuma linha de grade, borda de frame, marca d'agua ou texto esta presente?
- [ ] Nenhum elemento de cenario esta misturado com sprites de personagens/objetos?

### Gate 5: Otimizacao de VRAM

- [ ] O sprite foi recortado no bounding box mais apertado (sem tiles transparentes nas bordas)?
- [ ] A contagem de tiles unicos respeita o budget da cena (`doc/13-spec-cenas.md`)?
- [ ] Oportunidades de H-flip/V-flip foram exploradas para reduzir tiles?
- [ ] O impacto em DMA (tiles de animacao que mudam por frame) foi estimado?

### Gate 6: Documentacao do asset

- [ ] Barra visual de paleta numerada (0-15) com codigos hexadecimais fornecida?
- [ ] Mapa de indices descrevendo o papel de cada cor?
- [ ] Dimensoes em tiles informadas (ex: "3x4 tiles = 24x32 px")?
- [ ] Contagem de tiles unicos informada?

---

## 8. ALUCINACOES COMUNS DE IAs NA GERACAO DE ASSETS

| O que a IA faz | Por que esta errado | O que fazer |
|----------------|--------------------|----|
| Gera imagem em RGB true-color (24/32 bits) | Mega Drive usa 4 bits por pixel, 16 cores por paleta | Converter para indexado, reduzir para 16 cores |
| Aplica anti-aliasing nas bordas dos sprites | Cria cores intermediarias que estouram a paleta | Remover AA manualmente, pixel por pixel se necessario |
| Usa 256+ cores com gradientes suaves | VDP suporta 61 cores simultaneas (4 paletas x 15 + transparencia) | Reduzir para paleta de 15 cores + transparente |
| Gera sombra difusa embaixo do personagem | Sombra sera gerada pela engine; sombra na arte desperdia cores | Remover sombra |
| Simula transparencia com checkerboard | SGDK espera cor solida no index 0 | Substituir por cor solida de transparencia |
| Gera brilho (glow) com gradiente radial | Glow cria dezenas de cores extras | Representar brilho com 1 cor highlight da paleta |
| Exporta em 2x ou 4x de escala | 1 pixel exportado deve = 1 pixel no Mega Drive | Exportar sempre em 1x |
| Deixa bordas transparentes excessivas | Cada tile de 8x8 vazio = desperdicio de VRAM | Recortar ao bounding box apertado (multiplo de 8) |
| Mistura cenario e sprites no mesmo arquivo | Compilacao e pipeline tratam separadamente | Separar em arquivos distintos |
| Usa cores fora da grade de 9 bits | VDP arredonda e resultado visual sera diferente | Mapear para valores validos: 0x00,0x22,0x44,0x66,0x88,0xAA,0xCC,0xEE |
| Gera com resolucao arbitraria | SGDK exige multiplos de 8 | Redimensionar para multiplo de 8 |
| Adiciona efeitos de iluminacao volumetrica | Nao existe iluminacao per-pixel no Mega Drive | Iluminacao e implicita na paleta e no dithering |

---

## 9. EXEMPLOS DE DECLARACAO EM RESOURCES.RES

### Sprite (personagem com animacao)
```
SPRITE spr_prince    "gfx/player/prince.png"    4 4 NONE 0 NONE NONE
```
- `4 4` = largura e altura em tiles (32x32 pixels)
- Palette assignment via codigo

### Tileset (marco ou elemento estatico)
```
TILESET ts_rose_mark    "gfx/landmarks/rose_mark.bmp"    NONE NONE ROW
```

### Paleta
```
PALETTE pal_sprite_stage    "gfx/landmarks/pal_sprite_stage.bmp"
```

### Imagem completa (tela ou background)
```
IMAGE img_title_bg    "gfx/screens/title_bg.png"    NONE NONE
```

---

## 10. INTEGRACAO COM DOCUMENTACAO EXISTENTE

Este documento complementa e nunca contradiz:

| Documento | Relacao |
|-----------|---------|
| `doc/08-bible-artistica.md` | Define a identidade visual e leitmotivs — este documento codifica as regras tecnicas |
| `doc/04-recursos-e-pipeline.md` | Define o pipeline de entrada — este documento detalha as regras de qualidade |
| `doc/13-spec-cenas.md` | Define os budgets por cena — este documento exige validacao contra esses budgets |
| `doc/07-budget-vram-dma.md` | Define o budget global — este documento traduz em regras praticas de tile economy |
| `doc/09-checklist-anti-alucinacao.md` | Gates de codigo — este documento faz o mesmo para assets visuais |
| `doc/00-diretrizes-agente.md` | Regras de agente para codigo — este documento extende para agentes de arte |

---

## 11. REGRAS DE ALTERACAO DESTE DOCUMENTO

1. Nenhuma regra tecnica da secao 3 pode ser relaxada — sao restricoes fisicas do hardware.
2. Novas alucinacoes descobertas na pratica devem ser adicionadas a secao 8.
3. O checklist da secao 7 so pode crescer, nunca encolher.
4. Alteracoes na secao 2 (direcao de arte) requerem alinhamento com `doc/08-bible-artistica.md`.
5. Atualizacoes requerem ordem expressa do usuario.

---

**[Fim das Diretrizes de Producao de Assets]**
