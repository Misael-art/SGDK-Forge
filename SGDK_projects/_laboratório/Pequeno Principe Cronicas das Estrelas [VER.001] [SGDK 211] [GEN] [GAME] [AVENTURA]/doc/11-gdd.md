# 11 - Game Design Document (GDD)

**Versao:** 2.0
**Plataforma:** Mega Drive / Genesis (NTSC 60Hz, 320x224)
**SDK:** SGDK 2.11
**Genero:** Aventura contemplativa / plataforma leve / multi-gameplay
**Publico:** Jogadores curiosos, estudantes de retro dev, fas de O Pequeno Principe

---

## 1. CONCEITO CENTRAL

O jogador controla o Pequeno Principe em uma jornada entre micro-planetas. Cada planeta ensina uma tecnica visual do Mega Drive enquanto conta um fragmento narrativo inspirado na obra de Saint-Exupery. Cada viagem entre planetas e uma aventura jogavel com gameplay unico que explora outra tecnica do hardware.

**Premissa de design:** O jogo nunca vira um slideshow tecnico. Cada efeito visual serve a narrativa e a emocao. Se o efeito nao serve ao sentimento do lugar, ele nao entra.

**Premissa expandida (v2.0):** O jogo visa explorar toda a capacidade grafica do Mega Drive. O gameplay diverso — que muda radicalmente entre viagens — permite demonstrar diferentes tecnicas visuais dentro de um contexto narrativo coerente. Cada viagem ensina uma virtude humana atraves da mecanica.

**Loop fundamental:**
```
Explorar planeta → Interagir → Absorver encontro → VIAJAR (gameplay ativo) → Proximo planeta
```

---

## 2. PILARES DE DESIGN

| Pilar | Significado | Regra pratica |
|-------|-------------|---------------|
| Pedagogia integrada | O jogo ensina tecnicas do MD sem parecer aula | Cada cena tem 1 tecnica dominante |
| Hardware real | Tudo roda em hardware real sem truques impossiveis | Nenhum efeito pode exceder o budget da cena |
| Narrativa emocional | A historia emociona antes de ensinar | Dialogos curtos, tom poetico, sem exposicao tecnica |
| Ritmo contemplativo | O jogador nunca e apressado | Sem timer, sem game over, sem inimigos letais |
| Progressao por compreensao | Avanca quem entende, nao quem decora | Objetivos claros, resolucao por interacao simples |
| Diversidade de gameplay | Cada viagem e uma experiencia nova | 11 tipos de gameplay diferentes nas viagens |
| Virtude por mecanica | Cada viagem ensina uma virtude sem texto | A mecanica comunica, nao o dialogo |

---

## 3. CONTROLES

### Nos planetas (exploracao)

| Botao | Acao | Contexto |
|-------|------|----------|
| LEFT/RIGHT | Caminhar | Sempre (exceto dialogos e menus) |
| A | Interagir | Perto de elemento interativo; planar curto no ar |
| B | (reservado) | Sem uso no slice atual |
| C | Viajar / Pular | Quando planeta resolvido (viajar); plataformas (pular) |
| START | Pausar | Sempre durante gameplay |
| UP/DOWN | Navegar | Menus, codex, pause |

### Nas viagens (gameplay ativo)

| Botao | Acao | Varia por viagem |
|-------|------|------------------|
| D-pad | Mover/guiar | Direcao contextual (horizontal, vertical, 360) |
| A | Acao especial | Contexto da viagem (esquivar, balançar, soprar, dancar) |
| B | (reservado) | - |
| C | Pular (onde aplicavel) | Viagem J (Torre) |
| START | Pausar | Sempre |

**Regra:** Nenhum botao tem dupla funcao no mesmo contexto. Cada viagem define seu mapeamento.

---

## 4. MECANICAS

### 4.1 Movimentacao (planetas)
- Caminhada horizontal com aceleracao/desaceleracao em fix16.
- Pulo com gravidade em fix32 (curva suave).
- Planar curto: segurar A no ar reduz gravidade temporariamente.
- Sem corrida. Sem dash. Sem wall jump. O ritmo e lento de proposito.

### 4.2 Interacao (planetas)
- Botao A perto de elemento interativo dispara evento.
- Raio de interacao: 18-20 pixels conforme o planeta.
- Primeira interacao: resolve objetivo + dialogo + voz + SFX.
- Interacoes subsequentes: dialogo alternativo.

### 4.3 Dialogos
- Renderizados em window plane (nao scrollavel).
- Speaker identificado por nome.
- Maximo 4 linhas por encontro.
- Botao A avanca/fecha dialogo.
- Durante dialogo: input de movimento bloqueado.

### 4.4 Progressao
- Linear: B-612 → (viagem) → Rei → ... → B-612 retorno → Credits.
- Cada planeta tem 1 objetivo binario (resolvido/nao resolvido).
- Botao C so funciona quando planeta resolvido.
- Nao ha backtracking.
- Nao ha colecao, inventario ou moeda.

### 4.5 Viagens (gameplay ativo entre planetas)
- **MUDANÇA v2.0:** Viagens sao cenas jogaveis com gameplay unico.
- Cada viagem tem mecanica propria (shmup, pseudo-3D, plataforma, contemplativo, etc.).
- Nenhuma viagem tem game over — o principe sempre chega.
- Obstaculos causam efeito visual (flash, tropeço), nunca morte.
- Cada viagem ensina uma virtude (coragem, determinacao, humildade, etc.).
- Duracao: 30-90 segundos de gameplay ativo.
- Especificacao completa: `doc/14-spec-travel.md`.

### 4.6 Codex
- Desbloqueado por planeta E por viagem ao resolver/completar.
- Acessivel pelo menu de pausa.
- 5 linhas por entrada.
- Nao e necessario ler o codex para progredir.

---

## 5. ESTRUTURA DE CENAS

### 5.1 Fluxo completo do jogo

```
BOOT → TITLE → STORY →

B-612 (casa) ──VIAGEM A──► Planeta do Rei
                            ──VIAGEM B──► Planeta do Vaidoso
                                          ──VIAGEM C──► Planeta do Bebado
                                                        ──VIAGEM D──► Planeta do Homem de Negocios
                                                                      ──VIAGEM E──► Planeta do Acendedor
                                                                                    ──VIAGEM F──► Planeta do Geografo
                                                                                                  ──VIAGEM G──► Planeta da Serpente
                                                                                                                ──VIAGEM H──► Deserto das Estrelas
                                                                                                                              ──VIAGEM I──► Jardim das Rosas
                                                                                                                                            ──VIAGEM J──► Poco no Deserto
                                                                                                                                                          ──VIAGEM K──► B-612 (retorno)
                                                                                                                                                                        → CREDITS

PAUSE ←→ CODEX (acessivel de qualquer cena via START)
```

### 5.2 Planetas

| ID | Nome | Tecnica dominante | Elemento interativo | Speaker | Virtude associada |
|----|------|--------------------|---------------------|---------|-------------------|
| 0 | B-612 | Line scroll curvo + palette cycling + hilight | Rosa | ROSA | Cuidado |
| 1 | Planeta do Rei | Parallax multicamada + column scroll | Trono | REI | Autoridade justa |
| 2 | Planeta do Vaidoso | Sprite reflection + palette flash | Espelho | VAIDOSO | Auto-conhecimento |
| 3 | Planeta do Bebado | Screen wobble + desaturacao | Garrafa | BEBADO | Compaixao |
| 4 | Planeta do Homem de Negocios | Tile counter + number rain | Livro de contas | CONTADOR | Desapego |
| 5 | Planeta do Acendedor | H-Int split + heat wobble + hilight | Lampiao | ACENDEDOR | Dedicacao |
| 6 | Planeta do Geografo | Map scroll + minimap overlay | Mapa | GEOGRAFO | Curiosidade |
| 7 | Planeta da Serpente | Shadow mode + fade to black | Circulo na areia | SERPENTE | Aceitacao |
| 8 | Deserto das Estrelas | Line scroll vento + miragem | Marco estelar | VENTO | Silencio |
| 9 | Jardim das Rosas | Palette cycling floral + multi-sprite | Canteiro | ROSAS | Unicidade |
| 10 | Poco no Deserto | Column scroll profundo + echo | Poco | AVIADOR | Essencial invisivel |
| 11 | B-612 (retorno) | Todos os efeitos combinados (showcase) | Rosa (de volta) | ROSA | Sabedoria |

### 5.3 Viagens

| ID | De → Para | Tipo de gameplay | Virtude | Tecnica |
|----|-----------|------------------|---------|---------|
| A | B-612 → Rei | Pseudo-3D (Space Harrier) | Coragem | Line scroll + sprite scaling |
| B | Rei → Vaidoso | Shmup horizontal | Determinacao | Parallax + tile swap |
| C | Vaidoso → Bebado | Shmup vertical | Humildade | Line scroll + tile swap |
| D | Bebado → Homem de Neg. | Vertical contemplativo | Compaixao | Palette cycling + flickering |
| E | H. de Neg. → Acendedor | Pseudo-3D (corrida) | Confianca | Palette cycling 3D |
| F | Acendedor → Geografo | Plataforma vertical | Perseveranca | DMA streaming rotacao |
| G | Geografo → Serpente | Top-down livre | Criatividade | Tile rotation |
| H | Serpente → Deserto | Shmup horizontal intenso | Esperanca | Particulas + parallax |
| I | Deserto → Jardim | Semi-interativo | Amizade | Multi-jointed sprites |
| J | Jardim → Poco | Plataforma vertical | Fidelidade | Raster distortion |
| K | Poco → B-612 | Top-down contemplativo | Sabedoria | Software rotation+zoom |

### 5.4 Telas de suporte

| Tela | Descricao | Interacao |
|------|-----------|-----------|
| Boot | Inicializacao silenciosa | Nenhuma |
| Title | Nome do jogo + "pressione START" | START inicia |
| Story | Texto introdutorio | A avanca pagina |
| Pause | Menu com CONTINUAR / CODEX | UP/DOWN + C |
| Codex | Entradas tecnicas desbloqueadas | UP/DOWN navega, C volta |
| Credits | Texto de encerramento | A volta ao titulo |

---

## 6. CACHECOL (SISTEMA DE PARTICULAS SIMPLES)

O cachecol do Pequeno Principe e a assinatura visual do jogador.

- 5 segmentos ligados por mola em sinFix16.
- Cada segmento segue o anterior com atraso de fase.
- Vento (variavel por planeta) influencia a amplitude.
- Renderizado com sprites de hardware (1 tile por segmento).
- Damping progressivo: segmentos distais se movem menos.
- **Nas viagens:** cachecol simplificado (3 segmentos) para economizar sprites.

**Budget:** 5 sprites de 8x8 em planetas, 3 sprites em viagens.

---

## 7. PLAYER (SPRITE DE HARDWARE)

### Estado atual (placeholder — slice de 4 planetas)
- 6 tiles procedurais (corpo 16x16 + variantes de direcao).
- 3 sprites de hardware para corpo.
- Total: 3 (corpo) + 5 (cachecol) = 8 sprites de hardware.

### Estado alvo (assets finais)
- Sprite sheet real via rescomp com animacoes: idle, walk, jump, glide, interact.
- Meta-sprite gerenciado pelo SGDK sprite engine.
- Budget maximo: 4 tiles x 4 tiles (32x32 pixels) por frame.
- Paleta dedicada: PAL2 (fixa em todas as cenas).
- **Variantes de viagem:** Principe montado, pilotando, dançando, voando — cada viagem pode ter sprite sheet propria carregada no inicio da cena.

---

## 8. AUDIO

### Modelo
- XGM2 como driver principal.
- SFX via WAV samples carregados em `resources.res`.
- BGM via VGM/XGM.

### Inventario atual (slice de 4 planetas)
| Tipo | Arquivo | Uso |
|------|---------|-----|
| WAV | voice_rose.wav | Fala curta ao resolver B-612 |
| WAV | voice_king.wav | Fala curta ao resolver Rei |
| WAV | voice_lamp.wav | Fala curta ao resolver Lampiao |
| WAV | voice_wind.wav | Fala curta ao resolver Deserto |
| WAV | fx_bloom.wav | SFX de resolucao B-612 |
| WAV | fx_throne.wav | SFX de resolucao Rei |
| WAV | fx_lamp.wav | SFX de resolucao Lampiao |
| WAV | fx_star.wav | SFX de resolucao Deserto |

### Pendente (jogo completo)
- BGM por planeta (12 temas unicos — contemplativo, loop limpo).
- BGM por viagem (11 temas — ritmicos, acompanham gameplay).
- Vozes para novos speakers (Vaidoso, Bebado, Contador, Geografo, Serpente, Rosas, Aviador).
- SFX de viagem (motor, vento, passaros, agua, trovao, etc.).
- SFX de ambiente por planeta.
- SFX de UI (pausa, navegacao de menu).

---

## 9. REGRAS DE DESIGN QUE NAO PODEM SER VIOLADAS

1. **Sem morte.** O jogador nunca morre, nunca perde, nunca falha.
2. **Sem timer.** Nenhuma cena tem limite de tempo.
3. **Sem inimigos letais.** Obstaculos causam efeito visual, nunca dano real.
4. **Sem coleta obrigatoria.** Nao ha moedas, itens ou inventario.
5. **Sem backtracking.** A progressao e so para frente.
6. **1 tecnica dominante por cena.** Efeitos secundarios sao permitidos se nao competem pelo budget.
7. **4 linhas por dialogo.** Encontros sao curtos. Poesia, nao exposicao.
8. **Codex e opcional.** O jogador nunca precisa ler o codex para progredir.
9. **Window plane para dialogos.** Texto nunca sofre scroll do cenario.
10. **60fps sem excecao.** Se um efeito nao cabe no VBlank, ele nao entra. (Excecao documentada: Viagem K pode rodar a 30fps se necessario.)
11. **Virtude por mecanica.** Cada viagem ensina uma virtude. A mecanica comunica, nao o texto.
12. **Viagens nunca punem.** Colisoes causam tropeço visual, nunca reset ou game over.

---

## 10. ESCOPO DO JOGO COMPLETO

### Implementado (slice v1)
- 4 planetas: B-612, Rei, Lampiao, Deserto.
- Travel nao-interativo (circulos procedurais).
- State machine com 8 estados.

### Planejado (v2.0)
- 12 planetas/locais (incluindo retorno ao B-612).
- 11 viagens jogaveis com gameplay unico cada.
- Codex expandido (12 planetas + 11 viagens = 23 entradas).
- Audio completo (BGM + SFX + vozes).

### Escopo proibido (NAO IMPLEMENTAR SEM REVISAO DO GDD)
- Sistema de inventario ou coleta obrigatoria.
- Combate com dano real ou game over.
- Multiplayer.
- Save/load (avaliar se jogo completo requer — decisao futura).
- Modo PAL (o jogo e NTSC 60Hz).
- Mais de 2 planes de background (hardware nao permite).

---

## 11. GLOSSARIO

| Termo | Significado neste projeto |
|-------|---------------------------|
| Slice | Vertical slice: versao curta e completa do jogo (4 planetas) |
| Placeholder | Grafico gerado por codigo, substituivel por asset real |
| Marco | Tileset real (rescomp) que marca o elemento interativo do planeta |
| Budget | Limite maximo de recurso de hardware permitido na cena |
| Encontro | Momento de dialogo entre player e NPC/elemento do planeta |
| Travel / Viagem | Cena jogavel de transicao entre planetas |
| Codex | Enciclopedia tecnica desbloquavel |
| Virtude | Conceito moral ensinado pela mecanica da viagem |
| Engine de viagem | Modulo de gameplay autonomo para uma viagem especifica |
| Object pool | Array fixo de entidades reutilizaveis (sem malloc) |
| LUT | Look-up table — tabela pre-calculada para performance |
| Flickering | Alternancia de sprites par/impar para dobrar contagem visual |
| Tile swap | Substituir tiles do Plane A/B em tempo real para efeitos massivos |
| DMA streaming | Injetar tiles pre-renderizados na VRAM frame a frame |
