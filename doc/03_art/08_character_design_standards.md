# 08 - Character Design Standards — Mega Drive AAA (v1 DRAFT)

Status: `DRAFT_APROVADO` — Aprovado como doutrina de trabalho; POC e ROM continuam pendentes

---

## Objetivo

Definir regras rigidas de design de personagem para sprites do Mega Drive que garantam leitura em 320x224, identidade visual forte, economia de paleta e funcionamento em contexto de gameplay. Todo personagem produzido no workspace DEVE obedecer este documento.

---

## 1. PROPORCOES POR ESCALA

### 1.1 Tabela de Escalas Canonicas

| Escala | Uso | Tiles | Leitura Facial | Detalhe de Material | Referencia |
|--------|-----|-------|----------------|--------------------|-----------| 
| 16x16 (2x2) | Item, projetil, particula grande | 4 | PROIBIDO tentar rosto | Cor e silhueta bastam | Sonic rings, SoR items |
| 16x24 (2x3) | NPC pequeno, inimigo basico | 6 | PROIBIDO tentar rosto | Silhueta + cor funcional | Shinobi III inimigos basicos |
| 24x32 (3x4) | Protagonista de plataforma, inimigo medio | 12 | Olhos legiveis (2-3px), boca implicita | Outline + 2 tons por material | Sonic, Shinobi III protagonista |
| 32x32 (4x4) | Protagonista versatil, inimigo forte | 16 | Olhos + boca minima, expressao por postura | 3 tons por material (luz/base/sombra) | Comix Zone, Earthworm Jim |
| 32x48 (4x6) | Protagonista de luta/aventura | 24 | Rosto legivel com expressao | Material completo, dithering funcional | SoR2/SoR3 protagonistas |
| 48x48 (6x6) | Boss medio, personagem especial | 36 | Expressao detalhada | Material rico, contraste dramatico | SoR2 bosses |
| 48x64+ (6x8+) | Boss grande, splash | 48+ | Retrato completo | Detalhe maximo permitido pelo hardware | Contra Hard Corps bosses |

### 1.2 Regras Absolutas de Proporcao

- O tamanho do sprite DEVE ser escolhido ANTES de qualquer arte. A escala NAO DEVE mudar depois que a sheet comecou.
- A cabeca DEVE ocupar entre 25% e 35% da altura total do sprite para personagens humanoides.
- Excecao: personagens SD (super-deformed) podem ter cabeca de ate 45% da altura.
- O corpo DEVE ter proporcao internamente consistente. Se bracos sao grossos, pernas DEVEM ser proporcionais.
- PROIBIDO: sprite com corpo detalhado e cabeca de palito, ou vice-versa.

---

## 2. LEITURA FACIAL EM BAIXA RESOLUCAO

### 2.1 Regras por Tamanho

| Altura do Sprite | Olhos | Boca | Expressao | Tecnica |
|------------------|-------|------|-----------|---------|
| <= 16px | PROIBIDO | PROIBIDO | Pela silhueta e cor do corpo | Cor solida, forma geometrica |
| 17-24px | 1-2px, contraste maximo contra rosto | PROIBIDO (implicita por sombra) | Pela postura e inclinacao da cabeca | Ponto claro sobre fundo escuro |
| 25-32px | 2-3px, com highlight de 1px | Opcional (1px de linha escura) | Postura + olhos + sombra facial | Highlight de olho obrigatorio |
| 33-48px | 3-4px, com pupila distinguivel | 2-3px, com sombra de labio | Olhos + boca + sobrancelha implicita | Rampas faciais de 3-4 tons |
| 49px+ | Detalhe completo de iris, sobrancelha | Detalhe de labio e sorriso/expressao | Retrato expressivo | Paleta dedicada se necessario |

### 2.2 Regras Absolutas de Rosto

- Os olhos DEVEM ter o contraste mais alto de todo o sprite. Se o fundo do rosto e tom medio, os olhos DEVEM ser preto + branco puro.
- Em sprites <= 32px de altura, a expressao DEVE ser comunicada pela postura do corpo e inclinacao da cabeca, NAO por detalhes faciais.
- PROIBIDO: tentar desenhar nariz em sprites <= 24px de altura. O nariz e implicito pela sombra lateral do rosto.
- PROIBIDO: usar mais de 1px para sobrancelha em sprites <= 32px.
- O highlight do olho (1px branco ou claro) DEVE existir em QUALQUER sprite >= 24px. Sem highlight, o olho parece morto.

---

## 3. SILHUETA POR ARQUETIPO

### 3.1 Regras de Silhueta

A silhueta e a forma do sprite quando reduzida a preto puro sobre branco. Todo personagem DEVE ser identificavel apenas pela silhueta.

| Arquetipo | Caracteristica de Silhueta | Regra |
|-----------|---------------------------|-------|
| Heroi | Compacto, centrado, simetria axial, pose heroica | DEVE ser a silhueta mais limpa e legivel da tela |
| Boss | Grande, assimetrico, massa exagerada, forma intimidadora | DEVE ocupar pelo menos 3x a area do heroi |
| Inimigo basico | Distinto do heroi por forma E tamanho | NAO DEVE ser confundivel com o heroi mesmo em silhueta |
| Inimigo forte | Massa intermediaria entre basico e boss | DEVE ser visualmente mais ameacador que o basico |
| NPC | Neutro, nao compete visualmente | DEVE ter menos contraste e menos saturacao que o heroi |
| Item/Power-up | Forma geometrica simples, contorno forte | DEVE ser reconhecivel instantaneamente |

### 3.2 Teste de Silhueta (OBRIGATORIO)

Antes de aprovar qualquer sprite de personagem critico:
1. Converter o sprite para preto puro (todos os pixels nao-transparentes = preto).
2. Colocar sobre fundo branco.
3. Responder: "E possivel identificar o personagem e sua funcao apenas pela forma?"
4. Se NAO: REPROVAR. Redesenhar silhueta antes de adicionar cor.

---

## 4. COLOR CODING FUNCIONAL

### 4.1 Hierarquia Cromatica

| Funcao | Estrategia de Cor | Regra |
|--------|------------------|-------|
| Heroi | Cores quentes ou vibrantes (azul forte, vermelho, amarelo) | DEVE ser o elemento mais saturado da cena |
| Inimigo | Cores frias ou agressivas (roxo, verde escuro, cinza) | DEVE contrastar com heroi por matiz |
| NPC | Tons terrosos, neutros, baixa saturacao | NAO DEVE competir com heroi |
| Item coletavel | 1-2 cores saturadas isoladas (amarelo ouro, verde vida) | DEVE ser reconhecivel a distancia |
| Projetil | Cor de alta luminancia (branco, amarelo, ciano) | DEVE ser visivel sobre qualquer fundo |
| Perigo ambiental | Vermelho, laranja (associacao universal de perigo) | DEVE usar cores que o jogador associa a dano |

### 4.2 Regras Absolutas de Cor

- O heroi DEVE ser o elemento com maior saturacao na tela durante gameplay. Se o fundo competir, o fundo DEVE ser dessaturado.
- Inimigos do mesmo tipo DEVEM usar a mesma paleta. Variantes DEVEM ser criadas por palette swap, NAO por sprites separados.
- PROIBIDO: heroi e inimigo basico com cores dominantes identicas.
- PROIBIDO: item coletavel com cor que se confunde com cenario.

---

## 5. ROSTER MANAGEMENT

### 5.1 Paleta Compartilhada

O Mega Drive tem 4 paletas de 15 cores visiveis. Em gameplay tipico:

| Paleta | Uso Recomendado |
|--------|----------------|
| PAL0 | Background (cenario) |
| PAL1 | Heroi principal |
| PAL2 | Inimigos (compartilhada por todos) |
| PAL3 | HUD + itens + FX OU segundo personagem |

### 5.2 Regras de Compartilhamento

- Ate 4 personagens em tela DEVEM funcionar com no maximo 2 paletas de sprite (PAL1 + PAL2).
- Para roster de luta com multiplos personagens selecionaveis, cada personagem DEVE funcionar na mesma paleta base (PAL1), diferenciado por palette swap de 3-5 cores.
- O palette swap DEVE alterar a cor dominante do personagem (roupa, armadura, cabelo), NAO as cores estruturais (outline, sombra base, pele).
- Cores compartilhadas entre todos os personagens do roster:
  - Outline principal (1 cor: preto ou escuro)
  - Pele base + sombra (2-3 cores)
  - Highlight universal (1 cor: branco quente)
- Cores variantes (2-5 cores por personagem):
  - Cor dominante da roupa
  - Cor secundaria (detalhe, equipamento)
  - Highlight da roupa

### 5.3 Tabela de Palette Swap Minima

```
PAL1 base:    [transp] [outline] [sombra_pele] [pele] [highlight_pele]
              [sombra_roupa] [roupa_base] [roupa_destaque]
              [detalhe1] [detalhe2] [detalhe3]
              [sombra_geral] [highlight_geral] [cor_livre] [cor_livre]

Swap jogador 2: trocar indices 5-7 (roupa) e 8-10 (detalhe)
Swap dano:      trocar indices 5-10 para vermelho/branco piscante
Swap power-up:  trocar indices 5-10 para cores mais luminosas
```

---

## 6. METRICAS DE VALIDACAO

| Metrica | Threshold de Aprovacao | Metodo de Medicao |
|---------|----------------------|-------------------|
| `silhouette_recognition` | Personagem identificavel em silhueta preta pura sobre branco | Teste visual descrito na secao 3.2 |
| `palette_sharing_efficiency` | >= 40% de cores compartilhadas entre personagens do roster | Contagem de cores identicas entre paletas |
| `readability_at_native` | Rosto/expressao legivel em screenshot 320x224 nativo, nao ampliado | Inspecao visual em BlastEm sem zoom |
| `archetype_distinction` | Heroi, inimigo e NPC distinguiveis em screenshot com todos presentes | Inspecao visual com 3+ personagens em tela |
| `color_hierarchy` | Heroi e o elemento mais saturado da tela | Comparacao de saturacao media: heroi vs fundo vs inimigo |

---

## 7. CHECKLIST DE VALIDACAO (SIM/NAO)

- [ ] O tamanho do sprite foi definido ANTES de comecar a arte?
- [ ] A proporcao cabeca/corpo esta dentro de 25-35% (ou 45% para SD)?
- [ ] O personagem passa no teste de silhueta (secao 3.2)?
- [ ] Os olhos tem o contraste mais alto do sprite?
- [ ] A expressao e comunicada pela postura, nao por micro-detalhes faciais?
- [ ] O heroi e o elemento mais saturado da tela?
- [ ] Inimigos sao distinguiveis do heroi por forma E cor?
- [ ] A paleta cabe no slot designado (PAL1/PAL2)?
- [ ] Palette swap de jogador 2 funciona trocando apenas 3-5 cores?
- [ ] O personagem e legivel em 320x224 nativo (sem zoom)?
- [ ] O personagem NAO desaparece em fundo claro NEM em fundo escuro?
- [ ] O budget de tiles por frame cabe no budget de VRAM da cena?
- [ ] O sprite segue `megadrive-pixel-strict-rules` integralmente?

---

## 8. ANTI-PADROES (PROIBIDOS)

| Anti-Padrao | Diagnostico | Consequencia |
|-------------|-------------|--------------|
| Rosto detalhado demais em sprite pequeno | Detalhes viram borrão em tela nativa | REPROVAR — simplificar para escala |
| Personagem que some no fundo | Outline fraco ou saturacao proxima do BG | REPROVAR — reforcar outline e contrast |
| Roster onde todos parecem iguais | Mesma silhueta e mesma cor dominante | REPROVAR — redesenhar por arquetipo |
| Silhueta que so funciona em zoom | Detalhes legiveis apenas em editor ampliado | REPROVAR — avaliar sempre em 1x |
| Paleta desperdicada em tons proximos | Cores quase iguais ocupando slots separados | REPROVAR — fundir tons e realocar |
| Heroi menos vibrante que inimigo | Inimigo rouba atencao visual | REPROVAR — ajustar saturacao do heroi |
| Palette swap que muda outline | Personagem perde identidade visual | REPROVAR — outline e estrutural, nao variante |

---

## 9. BENCHMARKS OBRIGATORIOS

| Jogo | Aspecto de Referencia | Quando Usar |
|------|----------------------|-------------|
| Comix Zone | Personagem expressivo em escala media, personalidade por pose | Heroi com carisma |
| Monster World IV | Charme em escala pequena, proporcoes SD funcionais | Personagem fofo, aventura |
| Streets of Rage 2 | Roster diverso com paleta compartilhada, silhuetas distintas | Beat-em-up, roster |
| Sonic 3 | Leitura instantanea, design iconico, paleta minima eficiente | Plataforma, mascote |
| Vectorman | Personagem mecanico com material legivel, dithering funcional | Personagem robotico/mecanico |
| Contra Hard Corps | Roster militar compacto, acao rapida, leitura em caos visual | Acao intensa, sprites pequenos |

---

## 10. INTEGRACAO COM SKILLS EXISTENTES

| Skill | Relacao |
|-------|---------|
| `character-design` | Skill operacional desta competencia |
| `megadrive-pixel-strict-rules` | TODA validacao de pixel se aplica a cada frame |
| `visual-excellence-standards` | Metricas de silhueta, contraste e material guiam o design |
| `07_sprite_animation_standards` | O design DEVE antecipar as necessidades de animacao (pivots, massa) |
| `art-translation-to-vdp` | Personagens traduzidos de fonte high-res DEVEM seguir este documento |
| `megadrive-vdp-budget-analyst` | Roster completo DEVE caber no budget de paleta + VRAM da cena |
