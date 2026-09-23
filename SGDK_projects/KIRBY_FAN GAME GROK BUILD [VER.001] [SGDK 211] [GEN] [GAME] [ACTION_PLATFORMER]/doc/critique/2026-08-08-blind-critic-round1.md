# Crítico cego — Rodada 1 (2026-08-08)

**Modo:** capturas lado a lado sem identidade de fonte (painel `out/evidence/blind_critic/`).
**Referências no painel:** capturas reais de ROMs Mega Drive no forge (homebrew AAA Celestial Chase + Blue Circuit) + nossa cena.
**Critério:** qualidade visual no teto Alien Soldier / Gunstar Heroes / Dynamite Headdy / SoR2 / homebrew AAA moderno.

---

## 1. Painel (julgamento cego)

| Letra | Leitura visual (sem saber a fonte) |
|---|---|
| **A / B** | Cena sci-fi densa: pseudo-3D de estrada, boss multi-parte com metal/brilho, HUD integrado, partículas, silhueta do jogador com volume e shading em faixas. Leitura imediata de “MD no teto da plataforma”. |
| **C** | Interior industrial escuro, tilework legível, pouca cor, HUD debug, silhuetas mínimas. Parece tech-demo / slice cinza, não showcase AAA. |
| **D** | Plataforma pastoral: céu em bandas, montanhas geométricas, colinas + árvores, terreno com gap, personagem rosa redondo, inimigo peach. Limpo, legível, 60 fps “de manual” — mas **pouca densidade de detalhe**. |

### Quem é o “nosso”?

**D.**
Motivos acionáveis (não genéricos):

1. **Silhuetas de montanha = triângulos sem textura interna** — refs AAA quebram silhueta com degraus, overhangs, hachura, segundo tom.
2. **Personagem com ~3 faixas de rosa + contorno** — A/B usam mais degraus de valor e metal/reflexo; D parece sprite “limpo de placeholder”.
3. **Midground (colinas) uniforme** — poucas anomalias (só árvores isométricas iguais); refs variam massas e interrompem o horizonte.
4. **Ausência de FX de gameplay no frame** — sem smear, hit flash, partículas de poeira, sombra; a cena parece “estática de marketing de protótipo”.
5. **Nuvens listradas** — leitura de tile/nuvem barata; refs usam volume ou overlap de camadas.

Confiança da identificação: **alta** (~95%). Não há hesitação: D não compete com A/B no mesmo nível.

---

## 2. Revelação (MAPPING_SECRET)

| Letra | Fonte real |
|---|---|
| A / B | Celestial Chase visual benchmark (gameplay BlastEm) |
| C | Blue Circuit (demo) |
| **D** | **KIRBY_FAN GROK BUILD — `stage_layers_r3`** |

---

## 3. Scores por subsistema (crítico)

Escala 0–10, âncora: 9–10 = “poderia passar por cartucho comercial 93–95 / homebrew ZPF–Asteborg”.

| Subsistema | Score | Comentário |
|---|---|---|
| Parallax / profundidade | **6** | 4 camadas existem e medem certo; leitura ainda “três faixas empilhadas”, não desfiladeiro rico |
| Raster / céu | **6.5** | Gradiente H-int ok; nuvens fracas; falta distorção/água R3–R4 na fatia |
| Personagem (Kirby) | **5.5** | Rosa sólido (Index 0 ok); poucas poses lidas no frame, volume baixo vs Treasure |
| Cenário / tiles | **5** | Terrain legível; montanha/colina ainda “builder procedural elegante”, não pixel art de cartucho |
| Game feel visual | **4** | Sem hit-stop/flash/smear visíveis no frame de prova |
| Densidade AAA | **4.5** | Espaço negativo grande (faixa creme); refs enchem o quadro |
| **Total visual** | **~5.3** | Crítico **não hesita**; aponta D com facilidade |

---

## 4. Gaps acionáveis (ordem de ROI)

| # | Gap | Ação concreta | Owner | Pronto quando |
|---|---|---|---|---|
| G1 | Montanhas planas | Quebrar silhueta: 2–3 tons por face, snowcap, degraus 4–8 px, 1 overhang por pico | `build_dreamland_layers.py` | captura onde crítico não diz “triângulo” |
| G2 | Árvores clonadas | 3 silhuetas distintas + offset Y; 1 tronco torto por 128 px | idem | nenhuma árvore idêntica em 160 px |
| G3 | Nuvens listradas | Redesenhar 2 blobs com 3 tons (7/8/4) sem hachura diagonal | sky builder | 0 listras regulares |
| G4 | Kirby “flat” | +2 frames de walk legíveis no sheet; cheek + foot contrast; smear frame no dash | `build_kirby_sheet.py` | 8 frames com centro opaco e pe distinguível |
| G5 | Mid band vazia (creme) | Descer colinas 8–16 px OU inserir camada de arbustos em sprites (camada 5) | stage + layers | <30% da altura em “faixa lisa” |
| G6 | Zero FX no frame de prova | Captura playtest no frame de inhale/hit com partículas | harness scene | ≥1 FX lido no painel cego |
| G7 | Trilha placeholder | Substituir VGM por loop com baixo + lead + arpejo + noise | audio builder | gate audio + crítico “soa a cartucho” |

---

## 5. Veredito da rodada

- **Crítico identificou o nosso (D) sem dificuldade.**
- Loop FASE 2 **não para** — gaps G1–G3 e G7 são a fila imediata.
- Hardware gates PASS **não** enganam o crítico: budget ok ≠ AAA.

Painel: `out/evidence/blind_critic/panel_blind.png`
Segredo: `out/evidence/blind_critic/MAPPING_SECRET.json`
