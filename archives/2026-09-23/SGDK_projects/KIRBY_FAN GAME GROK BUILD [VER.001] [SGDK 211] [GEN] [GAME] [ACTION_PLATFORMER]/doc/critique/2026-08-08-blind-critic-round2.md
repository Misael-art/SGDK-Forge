# Crítico cego — Rodada 2 (2026-08-08)

**Modo:** capturas lado a lado sem identidade de fonte.
**Painel:** `out/evidence/blind_critic_r2/panel_blind.png`
**Critério:** teto Alien Soldier / Gunstar Heroes / Dynamite Headdy / homebrew AAA (Celestial Chase).

---

## 1. Painel (julgamento cego)

| Letra | Leitura visual (sem saber a fonte) |
|---|---|
| **A** | Pastoral Kirby-like: céu amarelo plano, **montanhas triângulo puro**, nuvens retangulares, checker de terra, colinas vazias. Parece protótipo FASE 1 — densidade baixa, zero mid-band. |
| **B** | Pastoral denser: cumulus orgânicos, montanhas com ridgeline e 2 tons, **faixa de pinheiros** entre montanha e colina, dirt com pedras, gaps com tufts FG. Personagem rosa redondo legível. Ainda “procedural elegante”, não cartucho 94. |
| **C** | Interior industrial escuro, tilework de corredor, HUD debug, silhuetas mínimas. Tech-demo / slice cinza. |
| **D** | Sci-fi denso: pseudo-3D de estrada, boss multi-parte com metal/brilho, HUD integrado, partículas, silhueta do jogador com volume. Leitura imediata de “MD no teto”. |

### Quem é o “nosso” (GROK BUILD R4)?

**B.**
Motivos acionáveis:

1. **Única cena pastoral com mid-band de floresta + ridgeline multi-lobo** — A tem triângulos e sem floresta; B é a evolução R4 documentada.
2. **Bayer/grão nas faces das montanhas** ainda delata builder procedural (D usa metal facetado; A usa flat fill).
3. **Árvores da colina = clones em espaçamento regular** (~65 px).
4. **Kirby com poucas faixas de valor** vs volume de D.
5. **Sem FX de gameplay no frame** (poeira existe no código mas o frame de prova está “em pose”).

Confiança: **alta (~90%)**. Hesitação residual só entre A e B (mesmo gênero); A é claramente o predecessor mais pobre.

---

## 2. Revelação (MAPPING_SECRET)

| Letra | Fonte real |
|---|---|
| A | KIRBY_FAN GAME CLOUDE (stage_after_water) |
| **B** | **KIRBY_FAN GROK BUILD — `stage_r4_latest`** |
| C | Blue Circuit |
| D | Celestial Chase visual benchmark (gameplay) |

---

## 3. Scores por subsistema

Âncora: 9–10 = cartucho comercial 93–95 / ZPF–Asteborg.

| Subsistema | R1 | R2 | Comentário |
|---|---|---|---|
| Parallax / profundidade | 6 | **7.0** | Forest band + 5 faixas; ainda “empilhado”, não desfiladeiro |
| Raster / céu | 6.5 | **7.0** | Cumulus ok; sem distorção/água |
| Personagem (Kirby) | 5.5 | **5.8** | R3 AI sheet; volume ainda curto vs Treasure |
| Cenário / tiles | 5 | **6.5** | R4 removeu triângulo/checker; grão Bayer + clones de árvore |
| Game feel visual | 4 | **5.5** | Dust no código; frame de prova ainda estático |
| Densidade AAA | 4.5 | **6.2** | Mid-band preenchida; D ainda enche o quadro melhor |
| **Total visual** | ~5.3 | **~6.5** | Crítico ainda identifica B sem dificuldade vs D |

---

## 4. Gaps acionáveis R2 (ROI)

| # | Gap | Ação | Pronto quando |
|---|---|---|---|
| R2-G1 | Grão Bayer nas montanhas | Faces sólidas + transição só na aresta; snowcap em manchas; 1 overhang/degrau por pico | crítico não diz “textura de dither” |
| R2-G2 | Árvores clonadas | 3 silhuetas (round/tall/wide) + offset Y + 1 tronco torto/128px | nenhuma idêntica em 160 px |
| R2-G3 | Forest = barra sólida | Variação de altura + gaps no topo (sky holes) + 3 profundidades legíveis | silhueta de pinheiros, não muro |
| R2-G4 | Grama fina / terra “noise” | Tufts em clusters, strata horizontal de dirt, flores irregulares | leitura de “tile de cartucho” a 1× |
| R2-G5 | Kirby flat | cheek highlight + foot contrast no sheet (sem quebrar idx0) | 5 faixas de valor legíveis a 32px |
| R2-G6 | FX invisível no frame | captura com land dust no frame de prova OU idle dust trail | ≥1 puff lido no painel |
| R2-G7 | Trilha procedural | Furnace YM2612 algo 2/3 | crítico “soa a cartucho” |

---

## 5. Veredito

- R4 **melhorou** vs R1 (5.3 → 6.5) e vs irmão CLOUDE (painel A).
- Crítico **ainda aponta B com facilidade** frente a D (Celestial Chase ~8–9).
- Próximo ROI: **R2-G1…G4 density pass** nesta sessão; G5–G7 em seguida.

Painel: `out/evidence/blind_critic_r2/panel_blind.png`
Segredo: `out/evidence/blind_critic_r2/MAPPING_SECRET.json`
