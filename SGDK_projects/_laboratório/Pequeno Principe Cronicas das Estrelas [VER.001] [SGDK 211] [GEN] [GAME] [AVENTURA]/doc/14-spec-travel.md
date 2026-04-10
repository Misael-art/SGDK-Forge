# 14 - Especificacao Tecnica: Cenas de Viagem

**Versao:** 1.0
**Referencia de hardware:** Mega Drive VDP (315-5313), 68000 @ 7.67 MHz, NTSC 60Hz

> **REGRA:** Cada cena de viagem e um modulo de gameplay autonomo.
> O jogador controla ativamente o Pequeno Principe durante a viagem (exceto onde indicado).
> Nenhuma viagem tem game over — o principe sempre chega ao destino.
> Dificuldade e puramente estetica/emocional, nunca punitiva.

---

## 0. FILOSOFIA DAS VIAGENS

No livro, o Pequeno Principe viaja entre planetas de formas magicas e poeticas.
Cada viagem e uma **aventura ludica** que ensina uma virtude atraves da experiencia.
O gameplay muda radicalmente entre viagens, transformando cada transicao em
uma surpresa que explora uma tecnica diferente do Mega Drive.

**Principios:**
- Sem morte, sem game over, sem punição — o principe sempre chega.
- Obstaculos sao poeticos (nuvens, estrelas cadentes, ventos), nunca hostis.
- Cada viagem dura 30-90 segundos de gameplay ativo.
- A virtude e comunicada pela mecanica, nao por texto.
- 60fps obrigatorio. Se o efeito nao cabe, simplifica.

---

## 1. MAPA COMPLETO DE VIAGENS

### Fluxo do jogo expandido

```
B-612 (casa)
  │ VIAGEM A: Cavalgando Estrela (pseudo-3D)          ─ Virtude: CORAGEM
  ▼
Planeta do Rei
  │ VIAGEM B: Surfando Cometa com Rede (shmup horiz.) ─ Virtude: DETERMINACAO
  ▼
Planeta do Vaidoso
  │ VIAGEM C: Guinchado por Passaros (shmup vertical)  ─ Virtude: HUMILDADE
  ▼
Planeta do Bebado
  │ VIAGEM D: Deslizando em Arco-Iris (vertical contemplativo) ─ Virtude: COMPAIXAO
  ▼
Planeta do Homem de Negocios
  │ VIAGEM E: Carona na Estrela Amiga (palette cycling 3D) ─ Virtude: CONFIANCA
  ▼
Planeta do Acendedor
  │ VIAGEM F: Subindo a Arvore Cosmica (DMA streaming rotacao) ─ Virtude: PERSEVERANCA
  ▼
Planeta do Geografo
  │ VIAGEM G: Barco Espacial Artesanal (tile rotation) ─ Virtude: CRIATIVIDADE
  ▼
Planeta da Serpente (portal da Terra)
  │ VIAGEM H: Aviaozinho Monomotor (particulas/poligonos) ─ Virtude: ESPERANCA
  ▼
Deserto das Estrelas (Terra)
  │ VIAGEM I: Danca com a Raposa (multi-jointed sprites) ─ Virtude: AMIZADE
  ▼
Jardim das Rosas
  │ VIAGEM J: Torre dos Ventos (raster distortion) ─ Virtude: FIDELIDADE
  ▼
Poco no Deserto
  │ VIAGEM K: Voo Final para Casa (rotacao/zoom software) ─ Virtude: SABEDORIA
  ▼
B-612 (retorno) → CREDITS
```

**Total: 12 planetas/locais + 11 viagens**

---

## 2. VIAGEM A — CAVALGANDO ESTRELA

### Contexto narrativo
O Principe monta em uma estrela amiga que dispara pelo cosmos. Ele precisa desviar
de asteroides e nuvens cosmicas enquanto a estrela avanca em velocidade absurda.
A estrela e entusiasmada mas um pouco desastrada — o principe precisa ter CORAGEM.

### Referencia tecnica
Panorama Cotton (pseudo-3D / Space Harrier style)

### Gameplay
- Visao atras do principe (into-the-screen).
- D-pad move o principe no plano XY da tela.
- Asteroides e nuvens vem da profundidade (Z) em direcao ao jogador.
- Nao ha tiros — apenas desvio.
- Colidir com obstaculos causa um "tropeço" visual (flash + desaceleracao breve), nunca morte.
- Estrelas douradas no caminho podem ser "tocadas" para um efeito visual de brilho.
- Duracao: ~60 segundos.

### Arquitetura de engine
1. **Chao 3D:** Line scroll por scanline no Plane B. Linhas inferiores rolam mais rapido.
   - Tabela de velocidade pre-calculada (LUT) com 112 entradas (linhas 112-224).
   - Palette cycling nas faixas do chao para simular avanco.
2. **Sprites escalonados:** Cada obstaculo tem 4-6 tamanhos pre-desenhados.
   - Projecao: `screenX = (worldX << 8) / Z + 160`, `screenY = (worldY << 8) / Z + 112`.
   - Z decrementa por frame. Quando Z < threshold, sprite muda para proximo tamanho.
3. **Object pool:** Array fixo de 16 obstaculos. Flag ativo/inativo.
4. **HUD:** Window plane (fixo, nao scrolla).
5. **Ceu:** Plane A com estrelas em parallax lento.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (chao) | 64 | Padrao repetitivo com 4 variantes de cor |
| Tiles VRAM (obstaculos) | 256 | 4 obstaculos x 6 tamanhos x ~10 tiles cada |
| Tiles VRAM (principe) | 32 | Sprite traseiro, 2 frames (normal + tropeço) |
| Tiles VRAM (ceu) | 48 | Estrelas e nebulosas |
| Paletas | PAL0 chao+ceu, PAL1 obstaculos, PAL2 principe, PAL3 efeitos |
| Sprites HW | 20-30 | 16 obstaculos (1-4 sprites cada) + principe (4) |
| Sprites/scanline | Max 16 (conservador) | Obstaculos espalhados em Y para evitar conflito |
| DMA/frame | 4500 bytes | Hscroll table + sprite tiles (animacao de escala) |
| Line scroll | 112 linhas (chao) | Per-scanline no Plane B |
| H-Int | Desabilitado | Tudo calculado no VBlank |
| LUTs | ~1 KB ROM | Tabela de perspectiva + profundidade |
| CPU | ~70% | Projecao 3D de 16 objetos + line scroll |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\Space Invaders SGDK [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]`
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\SGDK 3D Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]`

---

## 3. VIAGEM B — SURFANDO COMETA COM REDE

### Contexto narrativo
O Principe captura um cometa com sua rede de borboletas e surfa sobre ele horizontalmente
pelo espaco. Detritos cosmicos, aneis de planetas e nuvens de poeira estelar passam voando.
Ele precisa manter o equilibrio e a DETERMINACAO para nao soltar a rede.

### Referencia tecnica
Thunder Force IV (shmup horizontal com parallax massivo)

### Gameplay
- Scroll horizontal automatico (o cometa avanca).
- D-pad move o principe verticalmente no cometa.
- Obstaculos vem pela direita: aneis de Saturno, asteroides, chuvas de meteoros.
- Botao A: "puxar rede" — abaixa o principe rente ao cometa (esquiva).
- Sem tiros. Foco em esquiva e ritmo.
- Tocar em estrelas cadentes cria rastro de brilho (efeito visual).
- Duracao: ~75 segundos.

### Arquitetura de engine
1. **Parallax infinito:** Line scroll per-scanline no Plane B.
   - 6 faixas de velocidade: nebulosa distante (0.25px), estrelas medias (0.5px),
     nuvens (1px), detritos proximos (2px), superficie do cometa (4px), particulas (6px).
2. **Distorcao de calor:** Sine wave LUT aplicada ao hscroll das linhas da cauda do cometa.
   - 32 entradas de seno, amplitude 2-4 pixels.
3. **Tiros massivos como tiles:** Chuvas de meteoros desenhadas no Plane A via tile swap.
   - Nao contam para limite de sprites.
4. **Entidades:** Object pool de 32 atores (obstaculos + estrelas decorativas).
5. **Colisao:** AABB simples (retangulos).

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (parallax BG) | 192 | 6 camadas de cenario cosmico |
| Tiles VRAM (cometa+principe) | 64 | Superficie + principe em 3 poses |
| Tiles VRAM (obstaculos) | 128 | Aneis, asteroides, meteoros |
| Tiles VRAM (efeitos Plane A) | 48 | Meteoros massivos via tile swap |
| Paletas | PAL0 ceu, PAL1 cometa, PAL2 principe, PAL3 efeitos |
| Sprites HW | 30-40 | Obstaculos + particulas + principe |
| Sprites/scanline | Max 16 | Design de nivel evita clustering vertical |
| DMA/frame | 5000 bytes | Hscroll (448) + tile swap (~2000) + sprite anim |
| Line scroll | 224 linhas (tela inteira) | Per-scanline |
| H-Int | Opcional | Distorcao de calor pode usar H-Int ou LUT no VBlank |
| CPU | ~75% | Parallax 6 camadas + 32 entidades + colisao |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\Jogo de Nave [VER.0.5] [SGDK 211] [GEN] [GAME] [SHMUP]`

---

## 4. VIAGEM C — GUINCHADO POR PASSAROS

### Contexto narrativo
Uma revoada de passaros migratórios agarra o Principe pelo cachecol e o carrega
verticalmente pelo ceu. Ele balanca entre eles, desviando de nuvens de tempestade
e relampagos enquanto aprende HUMILDADE — ele nao controla os passaros, apenas confia.

### Referencia tecnica
M.U.S.H.A. (shmup vertical agressivo)

### Gameplay
- Scroll vertical automatico (ascendente — os passaros sobem).
- D-pad move o principe horizontalmente.
- Nuvens de tempestade sao obstaculos grandes (tile swap no Plane A).
- Relampagos sao avisos visuais (flash de paleta) seguidos de zona de perigo.
- Sem tiros. O principe "confia" nos passaros.
- Botao A: "balançar" — oscila o principe lateralmente (esquiva ampla).
- Penas douradas flutuam como coletaveis visuais (pontuacao estetica).
- Duracao: ~60 segundos.

### Arquitetura de engine
1. **Scroll vertical:** Tilemap rola continuamente para baixo (ascensao).
2. **Line scroll agressivo (Plane B):** Simula profundidade do abismo abaixo.
   - Linhas inferiores rolam mais rapido, criando vertigem.
3. **Tile swap:** Nuvens gigantes desenhadas no Plane A, trocando tiles dinamicamente.
4. **Relampago:** Color cycling full-palette (flash branco em 2 frames).
5. **Passaros:** 4-6 sprites animados flanqueando o principe (meta-sprites simples).

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (cenario) | 160 | Ceu, nuvens, camadas de profundidade |
| Tiles VRAM (nuvens Plane A) | 96 | Obstaculos massivos via tile swap |
| Tiles VRAM (principe+passaros) | 80 | Principe balancando + 6 passaros |
| Paletas | PAL0 ceu, PAL1 nuvens, PAL2 principe, PAL3 passaros+efeitos |
| Sprites HW | 25-35 | Principe (4) + 6 passaros (3 cada) + penas (8) |
| Sprites/scanline | Max 16 | Passaros distribuidos em Y |
| DMA/frame | 4000 bytes | Vscroll + tile swap nuvens + sprite anim |
| Line scroll | 112 linhas (metade inferior) | Efeito de abismo |
| Column scroll | 0 | - |
| H-Int | Desabilitado | Flash de paleta via VBlank |
| CPU | ~65% | Mais leve que A/B — menos projecao |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\Space Invaders SGDK [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]`
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\NEXZR MD [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]`

---

## 5. VIAGEM D — DESLIZANDO EM ARCO-IRIS

### Contexto narrativo
O Principe encontra um arco-iris cosmico que conecta dois mundos. Ele desliza sobre
ele como um toboga de luz, enquanto estrelas e bolhas de cor flutuam ao redor.
A viagem e contemplativa e ensina COMPAIXAO — a beleza existe para todos.

### Referencia tecnica
Space Megaforce / Super Aleste (vertical otimizado, particulas massivas)

### Gameplay
- Scroll vertical automatico (descendente — deslizando).
- D-pad move o principe lateralmente sobre o arco-iris.
- Sem obstaculos perigosos. Apenas estetica interativa.
- Botao A: "tocar estrela" — ao passar perto de uma estrela, ela explode em particulas coloridas.
- Transparencia simulada via sprite flickering (bolhas de cor).
- Foco em ritmo e contemplacao visual.
- Duracao: ~45 segundos.

### Arquitetura de engine
1. **Arco-iris:** Palette cycling agressivo no Plane B.
   - 8 faixas de cor rotacionam a cada 2 frames.
   - Simula fluxo de luz sem trocar tiles.
2. **Particulas:** Object pool de 48 particulas (sprites 8x8).
   - Flickering intencional: 24 pares/impares alternando por frame.
   - Olho humano ve 48 simultaneas a 60fps.
3. **Bolhas de transparencia:** Sprites com paleta alternando entre cor e transparente
   a cada frame (pseudo-alpha blending).
4. **Estrelas interativas:** Ao pressionar A perto, particula "explode" em 8 direcoes.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (arco-iris) | 48 | Padrao repetitivo + palette cycling |
| Tiles VRAM (estrelas+bolhas) | 32 | Formas simples reutilizadas |
| Tiles VRAM (principe) | 16 | Deslizando, 2 frames |
| Tiles VRAM (particulas) | 8 | 1 tile x 8 cores via paleta |
| Paletas | PAL0 arco-iris (cycling), PAL1 estrelas, PAL2 principe, PAL3 particulas |
| Sprites HW | 40-50 | 48 particulas (flickering) + principe (4) |
| Sprites/scanline | Max 20 (usando flickering) | Metade visivel por frame |
| DMA/frame | 2500 bytes | Palette cycling (64 bytes) + sprite tables |
| Line scroll | 0 | Nao necessario |
| H-Int | Opcional | Palette cycling por faixa pode usar H-Int |
| CPU | ~55% | Cena mais leve — foco em beleza, nao em CPU |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\Space Invaders SGDK [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]`
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\NEXZR MD [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]`

---

## 6. VIAGEM E — CARONA NA ESTRELA AMIGA

### Contexto narrativo
Uma estrelinha simpática oferece carona, mas ela e miope e voa muito rapido.
O Principe precisa gritar direcoes ("esquerda!", "direita!") enquanto a estrela
dispara em velocidade absurda. Ensina CONFIANCA — confiar em alguem mesmo quando
a situacao parece fora de controle.

### Referencia tecnica
Mickey Mania — Moose Chase (palette cycling 3D, fuga em profundidade)

### Gameplay
- Visao atras do principe (into-the-screen), como Viagem A, mas mais rapida.
- O principe monta na estrela que avanca automaticamente.
- D-pad esquerda/direita: "guiar" a estrela (com delay — ela demora a obedecer).
- Asteroides e nebulosas vem pela frente.
- O chao cosmico e feito inteiramente com palette cycling (sem scroll de tiles).
- Flash de perigo: asteroides piscam antes de aparecer.
- Duracao: ~45 segundos.

### Arquitetura de engine
1. **Chao 3D via palette cycling puro:**
   - Plane B desenhado com faixas horizontais de cores alternadas.
   - CRAM atualizado a cada frame: cores "giram" criando ilusao de avanco.
   - Zero tiles trocados. Zero DMA de tilemap. Apenas 32 bytes de paleta por frame.
2. **Escala do principe e estrela:**
   - Sprite fixo (nao escala — visto de tras, tamanho constante).
3. **Obstaculos:** Pre-renderizados em 8 tamanhos. Projecao Z simples.
4. **Delay de controle:** Input do jogador e buffered com 4 frames de atraso.
   - Mecanica central: antecipar, nao reagir.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (chao) | 16 | Faixas simples — cycling faz o trabalho |
| Tiles VRAM (obstaculos) | 192 | 3 tipos x 8 tamanhos x ~8 tiles |
| Tiles VRAM (principe+estrela) | 48 | Montado na estrela, 3 poses |
| Paletas | PAL0 chao (cycling), PAL1 obstaculos, PAL2 principe, PAL3 flash |
| Sprites HW | 20-25 | 12 obstaculos + principe+estrela (8) |
| Sprites/scanline | Max 14 | Conservador — poucos sprites por linha |
| DMA/frame | 2000 bytes | Palette cycling (32) + sprite escala (~1500) |
| Line scroll | 0 | Palette cycling substitui scroll |
| H-Int | Desabilitado | Cycling no VBlank |
| CPU | ~60% | Projecao simples + palette swap |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\SGDK 3D Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]`

---

## 7. VIAGEM F — SUBINDO A ARVORE COSMICA

### Contexto narrativo
Uma arvore gigantesca conecta dois planetas. O Principe amarra baloes ao seu corpo
e sobe circulando o tronco em espiral. A arvore parece girar ao redor dele.
Ensina PERSEVERANCA — subir devagar mas sem desistir.

### Referencia tecnica
Mickey Mania — Mad Doctor Tower (DMA streaming de rotacao pre-renderizada)

### Gameplay
- Visao lateral. O principe sobe (scroll vertical lento).
- O tronco da arvore "gira" no fundo (animacao pre-renderizada via DMA).
- D-pad esquerda/direita: o principe circula o tronco (muda a fase da rotacao).
- Galhos aparecem como plataformas temporarias (Plane A).
- Botao A: soltar/puxar balao (controle de altitude fina).
- Passaros pousam nos galhos e cantam quando o principe passa.
- Duracao: ~75 segundos.

### Arquitetura de engine
1. **Tronco rotativo (Plane B):**
   - 16-24 frames de rotacao pre-renderizados e comprimidos na ROM.
   - DMA streaming: a cada 2-4 frames de jogo, novos tiles do tronco sao
     injetados na VRAM via DMA durante VBlank.
   - O tronco ocupa ~128 tiles. DMA transfere ~4 KB por update.
   - Compressao LZ4W no cartucho, descompressao em buffer RAM.
2. **Galhos (Plane A):** Tilemap com plataformas que scrollam verticalmente.
3. **Baloes:** 3-5 sprites animados acima do principe.
4. **Passaros:** Sprites decorativos nos galhos.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (tronco) | 128 | Atualizados via DMA streaming |
| Tiles VRAM (galhos) | 96 | Plataformas e folhagem |
| Tiles VRAM (principe+baloes) | 48 | Principe + 5 baloes |
| Tiles VRAM (passaros) | 16 | Decorativos |
| ROM (frames tronco) | ~48 KB comprimido | 24 frames x ~2 KB cada |
| Paletas | PAL0 tronco, PAL1 galhos+folhas, PAL2 principe, PAL3 baloes |
| Sprites HW | 20-25 | Principe (4) + baloes (5) + passaros (8) |
| Sprites/scanline | Max 12 | Poucos sprites — foco no BG animado |
| DMA/frame | 5500 bytes | Tronco tiles (~4000) + hscroll + sprites |
| Line scroll | 0 | Opcional para efeito de profundidade |
| H-Int | Desabilitado | DMA pesado — nao sobra para H-Int |
| CPU | ~80% | Descompressao + DMA + fisica de baloes |

**ATENCAO:** Esta e a cena com maior consumo de DMA. O budget de 5500 bytes/frame
esta dentro do limite de 7200 mas com margem apertada. Testar em Blastem obrigatorio.

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\SGDK 3D Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]`

---

## 8. VIAGEM G — BARCO ESPACIAL ARTESANAL

### Contexto narrativo
O Principe construiu um barquinho voador com madeira, tecido e imaginacao.
Ele navega pelo oceano de estrelas em visao top-down, girando livremente.
Ilhas flutuantes, baleias cosmicas e correntes de vento decoram o caminho.
Ensina CRIATIVIDADE — com pouco material, muito se pode fazer.

### Referencia tecnica
Vectorman — Buggy Stage (tile rotation com padrao repetitivo)

### Gameplay
- Visao top-down. Barco no centro.
- D-pad gira o barco (rotacao livre 360 graus).
- Botao A: "soprar vela" — acelera na direcao atual.
- O "oceano estelar" gira ao redor (padrao repetitivo de tiles rotacionado).
- Ilhas flutuantes sao sprites que o barco pode contornar.
- Baleias cosmicas emergem e mergulham (sprites grandes, pre-escalonados).
- Sem colisao de dano. Tocar na baleia causa "onda" visual.
- Duracao: ~60 segundos (chegar ao destino marcado no horizonte).

### Arquitetura de engine
1. **Oceano rotativo (Plane B):**
   - Padrao visual abstrato que se repete (tiling seamless).
   - 16-32 frames de rotacao pre-renderizados.
   - DMA atualiza o bloco-base de tiles (~32 tiles).
   - Como o plane inteiro repete o padrao, trocar 32 tiles faz TUDO girar.
2. **Barco (sprites):** 16-24 sprites pre-desenhados em angulos (0-360, step 15-22 graus).
3. **Ilhas e baleias (sprites):** Object pool de 8 entidades.
4. **Direcao + fisica:** Tabela de seno/cosseno para movimento.
   - `vx = speed * cosFix16(angle)`, `vy = speed * sinFix16(angle)`.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (oceano base) | 32 | Atualizados via DMA a cada giro |
| Tiles VRAM (ilhas) | 64 | 4 ilhas diferentes |
| Tiles VRAM (barco) | 64 | 16 angulos x 4 tiles |
| Tiles VRAM (baleias) | 48 | 2 tamanhos x 12 tiles |
| ROM (frames oceano) | ~16 KB comprimido | 32 frames x ~512 bytes |
| Paletas | PAL0 oceano, PAL1 ilhas, PAL2 barco+principe, PAL3 baleias |
| Sprites HW | 20-30 | Barco (4) + ilhas (8) + baleias (8) + particulas (8) |
| Sprites/scanline | Max 14 | Entidades espalhadas pela tela |
| DMA/frame | 3500 bytes | Oceano tiles (~2000) + sprite swap + hscroll |
| Line scroll | 0 | - |
| H-Int | Desabilitado | - |
| CPU | ~70% | Trigonometria via LUT + DMA + colisao |

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\SGDK 3D Demo [VER.001] [SGDK 211] [GEN] [ESTUDO] [3D]`

---

## 9. VIAGEM H — AVIAOZINHO MONOMOTOR

### Contexto narrativo
O Principe encontra um aviaozinho monomotor abandonado (referencia ao aviador do livro).
Ele decola e voa por entre nuvens, explosoes de cor e ventos cruzados numa viagem
intensa mas maravilhosa. Ensina ESPERANCA — mesmo em tempestade, o destino existe.

### Referencia tecnica
Batman & Robin MD — Batwing stage (particulas, parallax agressivo, poligonos software)

### Gameplay
- Shmup horizontal. Aviao avanca automaticamente.
- D-pad: mover aviao em todas as direcoes.
- Botao A: "impulso" — aceleracao momentanea para frente.
- Nuvens de tempestade como obstaculos (tile swap no Plane A).
- Relampagos iluminam a cena (palette flash).
- Particulas de chuva e vento (flickering engine).
- Arco-iris surge ao final como recompensa visual.
- Duracao: ~75 segundos.

### Arquitetura de engine
1. **Parallax agressivo (Plane B):** Line scroll per-scanline.
   - Cidade de nuvens com ponto de fuga forcado na arte.
   - 8 faixas de velocidade.
2. **Particulas de chuva:** Engine de flickering.
   - 32 particulas alternando par/impar = 64 percebidas.
   - Sprites 8x8 com velocidade diagonal (vento).
3. **Nuvens massivas:** Tile swap no Plane A.
   - Nao contam para limite de sprites.
4. **Poligonos opcionais:** Se CPU permitir, chefes de nuvem
   com formas geometricas simples (triangulos/quadrilateros)
   desenhadas por software no Plane A.
5. **Flash de relampago:** PAL_setColors full-screen em 2 frames.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (parallax) | 192 | Camadas de nuvens e ceu |
| Tiles VRAM (nuvens Plane A) | 96 | Obstaculos massivos |
| Tiles VRAM (aviao) | 32 | 4 angulos/inclinacoes |
| Tiles VRAM (particulas) | 4 | Gotas de chuva |
| Paletas | PAL0 ceu, PAL1 nuvens, PAL2 aviao, PAL3 efeitos |
| Sprites HW | 40-50 | 32 particulas (flickering) + aviao (4) + detritos (8) |
| Sprites/scanline | Max 20 (flickering) | |
| DMA/frame | 5000 bytes | Hscroll (448) + tile swap (~2500) + palette + sprites |
| Line scroll | 224 linhas (tela inteira) | Per-scanline |
| H-Int | Opcional | Para efeitos de distorcao de nuvem |
| CPU | ~85% | Cena mais pesada. Particulas + parallax + tile swap |

**ATENCAO:** Cena mais exigente em CPU. Otimizacao em assembly pode ser necessaria
para os loops de particulas. Testar extensivamente em hardware real.

### Referencia de codigo
- `F:\Projects\MegaDrive_DEV\SGDK_Engines\Jogo de Nave [VER.0.5] [SGDK 211] [GEN] [GAME] [SHMUP]`

---

## 10. VIAGEM I — DANCA COM A RAPOSA

### Contexto narrativo
Apos chegar a Terra, o Principe encontra a Raposa. Ela o ensina a "cativar".
Nesta cena, o Principe e a Raposa dancam juntos — a raposa e feita de pecas
articuladas que se movem com graca e fluidez. Ensina AMIZADE — criar lacos.

### Referencia tecnica
Gunstar Heroes — Seven Force (multi-jointed sprites, cinematica direta)

### Gameplay
- Cena semi-interativa. O principe e a raposa no centro.
- D-pad: mover o principe ao redor da raposa.
- Botao A: "dançar" — o principe faz um giro e a raposa responde
  com um movimento articulado gracioso.
- A raposa e composta de 8-12 partes articuladas (cabeca, corpo, patas, cauda).
- Cada interacao muda o "nivel de confianca" (visual: a raposa se aproxima mais).
- Apos 5 interacoes, a raposa se senta ao lado e a viagem termina.
- Duracao: ~45 segundos (baseado em interacoes).

### Arquitetura de engine
1. **Raposa articulada:**
   - 8-12 sprites individuais conectados por cinematica direta.
   - Cada segmento tem angulo relativo ao pai.
   - Angulos calculados via LUT de seno/cosseno (sinFix16/cosFix16).
   - Posicao: `childX = parentX + length * cosFix16(angle)`.
   - Animacao: curvas de Bezier simplificadas (LUT pre-calculada).
2. **Cenario:** Simples — campo com flores. Plane A e B estaticos.
3. **Efeitos:** Particulas de flores ao dancar (8 sprites flickering).

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (cenario) | 128 | Campo, flores, arvore |
| Tiles VRAM (raposa) | 48 | 12 partes x 4 tiles |
| Tiles VRAM (principe) | 32 | Animacao de danca |
| Tiles VRAM (particulas) | 4 | Petalas |
| Paletas | PAL0 cenario, PAL1 raposa, PAL2 principe, PAL3 flores |
| Sprites HW | 25-35 | Raposa (12) + principe (4) + petalas (16 flickering) |
| Sprites/scanline | Max 16 | Raposa e principe no centro — concentracao alta |
| DMA/frame | 2000 bytes | Sprite positions + anim frames |
| Line scroll | 0 | Cenario estatico |
| H-Int | Desabilitado | |
| CPU | ~65% | Cinematica de 12 juntas + LUT |

### Referencia de codigo
- Engine propria (inspirada em Gunstar Heroes)

---

## 11. VIAGEM J — TORRE DOS VENTOS

### Contexto narrativo
O Principe precisa escalar uma torre impossivel feita de ventos solidificados.
A torre balanca vertiginosamente. Ele sobe agarrado a fitas de vento enquanto
o mundo embaixo gira. Ensina FIDELIDADE — manter-se firme quando tudo balanca.

### Referencia tecnica
Castlevania Bloodlines — Torre de Pisa (raster distortion avancada)

### Gameplay
- Plataforma vertical. O principe sobe a torre.
- A torre inteira balanca (line scroll senoidal no Plane B).
- D-pad: mover horizontalmente. C: pular.
- Plataformas de vento aparecem e desaparecem ritmicamente.
- O principe deve pular no ritmo certo.
- Reflexo na base (Plane A) com distorcao invertida.
- Duracao: ~60 segundos.

### Arquitetura de engine
1. **Torre balancante (Plane B):**
   - Tilemap estatico da torre.
   - H-Int aplica sine wave LUT ao hscroll de cada scanline.
   - 64 entradas de seno, amplitude oscila de 0 a 12 pixels.
   - Fase avanca a cada frame = torre balanca suavemente.
2. **Reflexo na agua (Plane A):**
   - Mesma tecnica mas com sine invertido e amplitude maior.
   - Palette mais escura simula reflexo.
3. **Plataformas ritmicas:** Sprites que aparecem/desaparecem em ciclo.
4. **Efeito de vertigem:** Amplitude da senoide aumenta conforme sobe.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (torre) | 160 | Estrutura detalhada |
| Tiles VRAM (reflexo) | 64 | Versao escura da torre |
| Tiles VRAM (principe) | 32 | Walk, jump, climb |
| Tiles VRAM (plataformas) | 16 | Fitas de vento |
| Paletas | PAL0 torre, PAL1 reflexo(escuro), PAL2 principe, PAL3 vento |
| Sprites HW | 15-20 | Principe (4) + plataformas (12) |
| Sprites/scanline | Max 10 | Poucas entidades |
| DMA/frame | 3000 bytes | Hscroll table (448 x2 planes) + sprites |
| Line scroll | 224 linhas (tela inteira, ambos planes) | Per-scanline via H-Int |
| H-Int | ATIVO | Sine wave distortion — uso intensivo |
| CPU | ~70% | H-Int callback + sine LUT + fisica |

### Referencia de codigo
- Engine propria (inspirada em Castlevania Bloodlines)

---

## 12. VIAGEM K — VOO FINAL PARA CASA

### Contexto narrativo
O Principe, agora sabio, decola para casa. Ele voa sobre um oceano de estrelas
que gira e faz zoom sob seus pes. O mundo se expande e se contrai. Ele ve tudo
o que aprendeu refletido nas constelacoes abaixo. Ensina SABEDORIA — ver o todo.

### Referencia tecnica
Red Zone (rotacao e zoom por software, texture mapping no 68000)

### Gameplay
- Visao top-down. Principe voa para cima.
- O chao de estrelas rotaciona e faz zoom lentamente.
- D-pad: controle direcional fino.
- Botao A: "olhar para baixo" — zoom in no oceano estelar (contemplativo).
- Constelacoes formam as silhuetas dos personagens encontrados (Raposa, Rosa, etc.).
- Sem obstaculos. Pura contemplacao.
- Duracao: ~60 segundos, termina com zoom out ate B-612 aparecer.

### Arquitetura de engine
1. **Chao rotativo com zoom (Plane B):**
   - Texture mapping por software no 68000.
   - Para cada scanline: calcula offset (u,v) da textura baseado em angulo e escala.
   - Resultado escrito na VRAM via DMA agressivo.
   - Textura: padrao estelar de 64x64 tiles (seamless).
   - Rotacao: 1-2 graus por frame.
   - Zoom: escala varia de 0.5x a 2.0x (fix16).
2. **Constelacoes:** Sprites pre-posicionados que aparecem conforme zoom.
3. **Principe:** Sprite fixo no centro (visao top-down).
4. **Transicao final:** Zoom out gradual ate revelar B-612 como ponto central.

### Budget

| Recurso | Alocado | Nota |
|---------|---------|------|
| Tiles VRAM (chao) | 256 | Atualizados por software a cada frame |
| Tiles VRAM (constelacoes) | 64 | Silhuetas dos personagens |
| Tiles VRAM (principe) | 16 | Visao top-down |
| ROM (textura) | ~8 KB | Padrao estelar 64x64 |
| ROM (LUTs) | ~4 KB | Tabelas de seno/cosseno + perspectiva |
| Paletas | PAL0 estrelas, PAL1 constelacoes, PAL2 principe, PAL3 efeitos |
| Sprites HW | 15-20 | Principe (4) + constelacoes (12) |
| Sprites/scanline | Max 8 | Cenario e software-rendered, poucos sprites |
| DMA/frame | 6500 bytes | Tiles do chao atualizados massivamente |
| Line scroll | 0 | Software rendering substitui |
| H-Int | Desabilitado | CPU precisa de cada ciclo para rendering |
| CPU | **~90%** | Software rendering e MUITO pesado |

**ATENCAO CRITICA:** Esta e, de longe, a cena mais exigente do jogo.
O rendering por software de rotacao+zoom no 68000 consome quase toda a CPU.
Estrategias de mitigacao:
- Renderizar apenas metade das scanlines (interleaving) e interpolar.
- Reduzir resolucao do chao para tiles de 16x16 (menos calculos).
- Assembly otimizado obrigatorio para o loop de rendering.
- DMA de 6500 bytes esta proximo do limite de 7200. Zero margem para erro.
- Pode ser necessario rodar a 30fps (1 frame de render, 1 frame de display).
- Testar EXTENSIVAMENTE em hardware real. Emuladores podem mascarar timing.

### Referencia de codigo
- Engine propria (inspirada em Red Zone)

---

## 13. TABELA RESUMO DE VIAGENS

| ID | Nome | Tipo | Virtude | Tecnica dominante | CPU% | DMA | Risco |
|----|------|------|---------|-------------------|------|-----|-------|
| A | Cavalgando Estrela | Pseudo-3D | Coragem | Line scroll + sprite scaling | 70% | 4500 | Medio |
| B | Surfando Cometa | Shmup H | Determinacao | Parallax + tile swap | 75% | 5000 | Medio |
| C | Guinchado por Passaros | Shmup V | Humildade | Line scroll + tile swap | 65% | 4000 | Baixo |
| D | Deslizando em Arco-Iris | Vertical contempl. | Compaixao | Palette cycling + flickering | 55% | 2500 | Baixo |
| E | Carona na Estrela | Pseudo-3D lite | Confianca | Palette cycling 3D | 60% | 2000 | Baixo |
| F | Arvore Cosmica | Plataforma vertical | Perseveranca | DMA streaming rotacao | 80% | 5500 | Alto |
| G | Barco Artesanal | Top-down livre | Criatividade | Tile rotation | 70% | 3500 | Medio |
| H | Aviaozinho Monomotor | Shmup H intenso | Esperanca | Particulas + parallax | 85% | 5000 | Alto |
| I | Danca com Raposa | Semi-interativo | Amizade | Multi-jointed sprites | 65% | 2000 | Baixo |
| J | Torre dos Ventos | Plataforma | Fidelidade | Raster distortion | 70% | 3000 | Medio |
| K | Voo Final | Top-down contempl. | Sabedoria | Software rotation+zoom | 90% | 6500 | CRITICO |

---

## 14. ORDEM DE IMPLEMENTACAO SUGERIDA

Baseada em risco e dependencias:

| Prioridade | Viagem | Razao |
|------------|--------|-------|
| 1 | D (Arco-Iris) | Mais simples, serve de template para sistema de travel |
| 2 | E (Estrela Amiga) | Palette cycling — reutiliza logica do B-612 |
| 3 | C (Passaros) | Shmup vertical simples — base para B e H |
| 4 | B (Cometa) | Shmup horizontal — evolui C |
| 5 | A (Cavalgando Estrela) | Pseudo-3D — complexo mas com refs disponiveis |
| 6 | I (Raposa) | Articulacao — engine isolada |
| 7 | G (Barco) | Tile rotation — engine isolada |
| 8 | J (Torre) | Raster distortion — requer H-Int robusto |
| 9 | F (Arvore) | DMA streaming — requer pipeline de assets |
| 10 | H (Aviaozinho) | Mais pesado em CPU — otimizacao necessaria |
| 11 | K (Voo Final) | Software rendering — pode exigir assembly puro |

---

## 15. REGRAS DE ALTERACAO

1. Nenhuma viagem pode ser implementada sem budget validado neste documento.
2. Se CPU% exceder 85% em teste real, simplificar antes de entregar.
3. Viagens com risco CRITICO (K) requerem prototipo isolado antes de integracao.
4. Cada viagem e um modulo independente — nao compartilha engine com outra.
5. Sprites de player devem ser reutilizaveis entre viagens (mesma paleta, PAL2).
6. Toda viagem termina com transicao suave para o estado `planet` do proximo destino.
7. Nenhuma viagem tem game over. Colisoes causam efeito visual, nunca morte.
