# 07 - Sprite Animation Standards — Mega Drive AAA (v1 DRAFT)

Status: `DRAFT_APROVADO` — Aprovado como doutrina de trabalho; POC e ROM continuam pendentes

---

## Objetivo

Definir regras rigidas para animacao de sprites no Mega Drive que garantam fluidez, economia de VRAM, consistencia de massa e leitura em 320x224. Toda animacao produzida no workspace DEVE obedecer este documento.

---

## 1. PRINCIPIOS DE ANIMACAO PARA PIXEL ART 16-BIT

### 1.1 Regras Absolutas

- Cada frame de animacao DEVE manter a mesma massa visual dominante do personagem. Variacao de bounding box entre frames de um mesmo ciclo NAO DEVE exceder 8px em qualquer eixo (largura ou altura).
- O centro de gravidade do sprite DEVE permanecer estavel ao longo do ciclo. O ponto de ancoragem (pivot) DEVE ser definido uma unica vez por personagem e NAO DEVE mudar entre frames, exceto em animacoes de pulo ou queda onde o deslocamento e intencional.
- Squash e stretch NAO existem como deformacao elastica no Mega Drive (nao ha scaling por hardware). A ilusao de squash e stretch DEVE ser construida por frames discretos pre-renderizados com proporcoes levemente alteradas (ex: frame de agachamento mais largo e baixo).
- Anticipation (preparacao antes de uma acao) DEVE existir em TODA animacao de ataque e pulo. Minimo: 1 frame de preparacao antes do golpe ou salto.
- Follow-through (continuacao apos acao) DEVE existir em animacoes de ataque. Minimo: 1 frame de retorno apos o frame de impacto.
- Toda animacao DEVE ser legivel frame por frame. Se um frame isolado nao comunica a pose com clareza, esse frame DEVE ser redesenhado.

### 1.2 Principios de Timing

O timing de animacao e definido em VBlanks (1 VBlank = 1/60 seg em NTSC).

#### Tabela de Timing por Acao (Obrigatoria)

| Acao | Frames de Arte | VBlanks por Frame | Duracao Total | Referencia |
|------|---------------|-------------------|---------------|------------|
| Idle | 4-6 frames | 8-12 VBlanks | 32-72 VBlanks (0.5-1.2s) | SoR3: 4f idle respirando |
| Walk | 6-8 frames | 4-6 VBlanks | 24-48 VBlanks (0.4-0.8s) por ciclo | Shinobi III: 6f walk cycle |
| Run | 4-6 frames | 3-4 VBlanks | 12-24 VBlanks (0.2-0.4s) por ciclo | Sonic 3: 4f run |
| Jump (subida) | 2-3 frames | 3-4 VBlanks | 6-12 VBlanks | Sonic 3: 2f jump ascend |
| Jump (queda) | 2-3 frames | 3-4 VBlanks | 6-12 VBlanks | Sonic 3: 2f jump descend |
| Ataque leve | 3-5 frames | 2-4 VBlanks | 6-20 VBlanks (0.1-0.33s) | SoR3: 3f jab |
| Ataque pesado | 4-7 frames | 3-5 VBlanks | 12-35 VBlanks (0.2-0.58s) | SoR3: 5f heavy punch |
| Dano (hurt) | 2-3 frames | 4-6 VBlanks | 8-18 VBlanks | Shinobi III: 2f hit react |
| Morte | 3-6 frames | 5-8 VBlanks | 15-48 VBlanks | SoR3: 4f death fall |

#### Regras de Timing

- Acoes rapidas (ataque, dash) DEVEM ter menos VBlanks por frame para transmitir velocidade.
- Acoes lentas (idle, dano) DEVEM ter mais VBlanks por frame para transmitir peso ou hesitacao.
- O frame de impacto de um ataque DEVE durar no minimo 2 VBlanks e no maximo 4 VBlanks.
- PROIBIDO: animacao com todos os frames no mesmo timing (parece mecanica, nao organica).
- OBRIGATORIO: variar o timing dentro do ciclo quando a acao tiver aceleracao ou desaceleracao natural.

### 1.3 Cadencia por Genero

| Genero | Caracteristica de Animacao | Referencia |
|--------|---------------------------|------------|
| Plataforma | Ciclos curtos (4-6f), resposta imediata, animacoes de transicao rapidas | Sonic 3, Shinobi III |
| Beat-em-up / Luta | Ciclos medios (6-8f), anticipation obrigatoria, hit confirm claro | SoR3, Contra Hard Corps |
| Aventura / RPG | Ciclos maiores (6-10f), animacao mais expressiva, idle elaborado | Monster World IV |
| Plataforma acao | Hibrido: ciclos curtos para movimento, medios para ataque | Comix Zone, Earthworm Jim |

---

## 2. PIPELINE DE PRODUCAO DE SPRITE SHEETS

### 2.1 Ordem Canonica de Animacoes

Toda sprite sheet DEVE seguir esta ordem. Animacoes sao organizadas em bandas horizontais, uma acao por linha.

```
Linha 0: IDLE         (4-6 frames)
Linha 1: WALK         (6-8 frames)
Linha 2: RUN          (4-6 frames)  — se aplicavel ao genero
Linha 3: JUMP_UP      (2-3 frames)
Linha 4: JUMP_DOWN    (2-3 frames)
Linha 5: ATTACK_LIGHT (3-5 frames)
Linha 6: ATTACK_HEAVY (4-7 frames) — se aplicavel ao genero
Linha 7: HURT         (2-3 frames)
Linha 8: DEATH        (3-6 frames)
```

Excecao: generos que NAO usam todas as acoes (ex: puzzle) DEVEM omitir linhas, nao inserir linhas vazias.

### 2.2 Formato de Sprite Sheet

- Cada frame DEVE ter exatamente o mesmo tamanho (largura x altura).
- Dimensoes do frame DEVEM ser multiplos de 8 (8x8, 16x16, 24x24, 24x32, 32x32, 32x48, etc.).
- O bounding box DEVE ser o menor retangulo que contenha o personagem no frame de maior extensao do ciclo. Todos os outros frames DEVEM usar esse mesmo bounding box.
- PROIBIDO: frames com tamanhos diferentes dentro da mesma sprite sheet.
- Fundo DEVE ser transparente (magenta #FF00FF como index 0).
- Nenhum frame DEVE conter anti-aliasing, alpha parcial ou gradientes suaves.

### 2.3 Consistencia de Massa

- A area preenchida (pixels nao-transparentes) entre frames adjacentes NAO DEVE variar mais de 15%.
- O contorno principal (outline) DEVE manter forma reconhecivel em todos os frames.
- Volumes grandes (tronco, cabeca) DEVEM manter posicao relativa estavel. Variacoes sao permitidas apenas em membros (bracos, pernas).
- PROIBIDO: frame onde o personagem "some" ou encolhe mais de 20% sem justificativa de gameplay (agachamento, encolhimento intencional).

### 2.4 Pivot Point

- O pivot (ponto de ancoragem para posicionamento em tela) DEVE ser definido na base central do personagem (centro horizontal, base dos pes).
- O pivot NAO DEVE mudar entre frames de um mesmo ciclo.
- Excecao unica: animacoes aereas (pulo, queda) podem deslocar o pivot vertical em ate metade da altura do sprite.

---

## 3. ECONOMIA DE VRAM ENTRE FRAMES

### 3.1 Regras de Reuso

- Frames simetricos (olhar esquerda/direita) DEVEM usar flip horizontal do hardware (flag H-Flip no .res). NAO DEVE haver sprites duplicados para direcao oposta.
- Frames adjacentes com poucas diferencas (ex: idle frame 1 vs idle frame 2) DEVEM compartilhar tiles identicos. A diferenca visual DEVE se concentrar nos tiles que mudam (bracos, pernas), nao no torso inteiro.
- Tiles identicos entre frames diferentes DEVEM ser identificados e declarados como reuso no `tile_reuse_plan` da traducao.

### 3.2 Budget de VRAM por Ciclo

| Escala do Sprite | Tiles por Frame | Frames Maximos Residentes | VRAM Maxima do Ciclo |
|------------------|----------------|--------------------------|---------------------|
| 16x16 (2x2) | 4 tiles | 8 frames | 256 bytes (8 tiles unicos) |
| 24x32 (3x4) | 12 tiles | 6 frames | 2304 bytes (72 tiles unicos) |
| 32x32 (4x4) | 16 tiles | 6 frames | 3072 bytes (96 tiles unicos) |
| 32x48 (4x6) | 24 tiles | 4 frames | 3072 bytes (96 tiles unicos) |
| 48x64 (6x8) | 48 tiles | 3 frames | 4608 bytes (144 tiles unicos) |

- OBRIGATORIO: antes de aprovar uma sprite sheet, calcular tiles unicos totais e comparar com o budget acima.
- Se o ciclo completo exceder o budget, o agente DEVE propor estrategia de streaming (carregar frames sob demanda via DMA) ou reducao de frames.
- SGDK automatiza DMA de sprite frames quando usando `SPR_addSprite()` com `SPR_FLAG_AUTO_VRAM_ALLOC`. O agente DEVE confirmar que o modo automatico comporta o ciclo antes de aprovar.

### 3.3 Implementacao SGDK

#### Declaracao no .res

```
SPRITE player_sprite "sprite/player_sheet.png" 4 4 FAST 5
```

Parametros: `name "path" w_tiles h_tiles compression anim_timing`

- `w_tiles` e `h_tiles`: tamanho de cada frame em tiles (ex: 4 4 = 32x32px)
- `compression`: `FAST` (padrao), `BEST` (menor tamanho), `NONE`
- `anim_timing`: VBlanks entre frames automaticos (0 = manual)

#### Controle de Animacao no Codigo

```c
// Adicionar sprite
Sprite* player = SPR_addSprite(&player_sprite, x, y, TILE_ATTR(PAL1, FALSE, FALSE, FALSE));

// Trocar animacao (linha da sheet)
SPR_setAnim(player, ANIM_WALK);

// Trocar frame manualmente
SPR_setFrame(player, frameIndex);

// Animacao automatica com loop
SPR_setAutoAnimation(player, TRUE);
SPR_setAnimationLoop(player, TRUE);

// Detectar fim de animacao (para encadear acoes)
if (SPR_isAnimationDone(player)) {
    SPR_setAnim(player, ANIM_IDLE);
}

// Callback de troca de frame (para sincronizar gameplay)
SPR_setFrameChangeCallback(player, &onFrameChanged);
```

---

## 4. METRICAS DE VALIDACAO

### 4.1 Metricas Obrigatorias

| Metrica | Threshold de Aprovacao | Metodo de Medicao |
|---------|----------------------|-------------------|
| `animation_fluidity` | Transicao entre frames adjacentes NAO apresenta salto de massa visivel em 320x224 | Inspecao visual frame-by-frame em BlastEm |
| `frame_economy` | >= 25% de tiles reutilizados entre frames do mesmo ciclo para sprites >= 24x32 | Contagem de tiles duplicados via hash de tile |
| `timing_feel` | Cadencia comparavel ao benchmark do genero (tabela 1.2) | Contagem de VBlanks por frame vs tabela |
| `mass_consistency` | Variacao de bounding box preenchido <= 15% entre frames adjacentes | Contagem de pixels nao-transparentes por frame |
| `pivot_stability` | Desvio do pivot <= 0px horizontal, <= 4px vertical (exceto aereo) | Sobreposicao de frames com marca de pivot |

### 4.2 Checklist de Validacao (SIM/NAO)

- [ ] Todos os frames tem o mesmo tamanho (largura x altura)?
- [ ] Dimensoes sao multiplos de 8?
- [ ] Index 0 da paleta e transparente (#FF00FF)?
- [ ] Maximo 15 cores visiveis na paleta?
- [ ] Todas as cores dentro do grid 9-bits?
- [ ] O personagem e reconhecivel em CADA frame isolado?
- [ ] A silhueta se mantem legivel em fundo claro E escuro?
- [ ] Existe anticipation antes de ataque/pulo?
- [ ] Existe follow-through apos ataque?
- [ ] O timing varia dentro do ciclo (nao e metronomico)?
- [ ] Flip horizontal cobre a direcao oposta sem frame duplicado?
- [ ] O budget de VRAM do ciclo completo cabe na configuracao da cena?
- [ ] A animacao roda no BENCHMARK_VISUAL_LAB sem flicker nem corrupcao?
- [ ] A cadencia e comparavel ao benchmark do genero?

---

## 5. BENCHMARKS OBRIGATORIOS

Toda sprite animada critica DEVE ser comparada com pelo menos 1 dos seguintes:

| Jogo | Aspecto de Referencia | Quando Usar |
|------|----------------------|-------------|
| Streets of Rage 3 | Animacao de luta fluida, peso nos golpes, roster diverso | Beat-em-up, personagem de luta |
| Shinobi III | Movimento agil, transicoes rapidas, animacao de ninja | Plataforma de acao, personagem rapido |
| Sonic 3 & Knuckles | Responsividade, ciclos curtos, animacao de plataforma | Plataforma, personagem de alta velocidade |
| Comix Zone | Expressividade em escala media, personalidade nas poses | Personagem expressivo, genero hibrido |
| Monster World IV | Charme em escala pequena, idle elaborado | Aventura, RPG, personagem fofo |
| Earthworm Jim | Animacao exagerada, humor via frames, follow-through forte | Plataforma com personalidade forte |

---

## 6. ANTI-PADROES (PROIBIDOS)

| Anti-Padrao | Diagnostico | Consequencia |
|-------------|-------------|--------------|
| Frames com massa completamente diferente | O personagem "pulsa" ou parece trocar de corpo entre frames | REPROVAR e redesenhar frames discrepantes |
| Animacao que so funciona rapida | Em frame-by-frame as poses nao fazem sentido | REPROVAR — cada frame DEVE ser uma pose legivel |
| Sprite sheet com frames desalinhados | Personagem "treme" durante animacao | REPROVAR — alinhar por pivot e recortar |
| Ignorar custo de VRAM do ciclo | ROM corrompe ou flicker aparece | REPROVAR — recalcular budget antes de promover |
| Todos os frames com mesmo timing | Animacao parece robotica | REPROVAR — variar VBlanks por frame |
| Flip horizontal no PNG em vez de no hardware | Dobra o custo de VRAM sem ganho | REPROVAR — usar H-Flip do VDP |
| Animacao de ataque sem anticipation | Golpe "aparece" sem preparacao | REPROVAR — adicionar frame de preparacao |
| Animacao de ataque sem follow-through | Golpe termina abruptamente | REPROVAR — adicionar frame de retorno |
| Ciclo de walk com frames impares sem loop | Animacao "pula" ao reiniciar | REPROVAR — garantir que frame 0 e frame N se conectam |

---

## 7. INTEGRACAO COM SKILLS EXISTENTES

| Skill Existente | Relacao |
|----------------|---------|
| `sprite-animation` | Skill operacional desta competencia |
| `megadrive-pixel-strict-rules` | TODA validacao pixel-rigida se aplica a cada frame individual |
| `visual-excellence-standards` | Metricas de silhueta, paleta e detalhe valem por frame |
| `art-translation-to-vdp` | Sprite sheets traduzidas DEVEM seguir este documento |
| `megadrive-vdp-budget-analyst` | Budget de VRAM DEVE considerar ciclo de animacao completo |
| `art-conversion-pipeline` | Sheet convertida DEVE respeitar formato e pivot deste documento |

---

## 8. FLUXO DE TRABALHO

```
1. Definir personagem e genero
2. Consultar tabela de timing do genero (secao 1.3)
3. Definir escala do sprite e budget de VRAM (secao 3.2)
4. Produzir sprite sheet no formato canonico (secao 2.1)
5. Validar pixel-rigido (megadrive-pixel-strict-rules)
6. Medir metricas de animacao (secao 4.1)
7. Rodar checklist (secao 4.2) — TUDO deve ser SIM
8. Implementar no BENCHMARK_VISUAL_LAB
9. Compilar e rodar em BlastEm
10. Comparar com benchmark do genero (secao 5)
11. Apresentar para aprovacao humana
12. Se aprovado: CANONIZAR. Se reprovado: registrar no Feedback Bank e corrigir.
```
