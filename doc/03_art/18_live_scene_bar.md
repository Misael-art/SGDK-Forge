# Barra viva da cena — piso visual do Sgdk Forge

Ultima atualizacao: 2026-08-29
Status doutrinario: `INCORPORADO` como piso de julgamento
Status de prova em ROM do Forge: `NAO_INICIADA`

> Handles nao sao a barra. O ofício observado e a barra.
> Qualquer agente que assumir este workspace DEVE entender o que
> isso significa antes de gerar, converter, julgar ou promover arte.

Contrato machine-readable: `doc/03_art/live_scene_bar.json`
Parametros de concepcao (tetos): `doc/03_art/live_scene_bar_parameters.json`
Schema de laudo: `tools/sgdk_wrapper/schemas/live_scene_bar_report.schema.json`
Brief curto: `tools/sgdk_wrapper/.agent/references/live_scene_bar_agent_brief.md`
Plano para chegar la: `doc/03_art/19_plan_pixel_art_live_scene_capability.md`

---

## 1. Por que esta barra existe

A barra comercial de 1994 (`doc/03_art/00_visual_quality_bar.md`) continua
necessaria: Streets of Rage 2, Sonic 3, Gunstar Heroes, Contra Hard Corps,
Castlevania Bloodlines.

Ela **nao e suficiente**. Em 2026 a cena homebrew do Mega Drive ja opera
acima do piso de muitos jogos originais da epoca, porque conhece o VDP
depois de 30 anos e traduz arte de outras plataformas sem fingir hardware
que nao existe.

O operador fixou o piso vivo na **cena atual** do Mega Drive. Rheo e Pigsy
continuam as duas escolas-mae. Os ponteiros abaixo **completam** o oficio
(palco, paleta de roster, audio, luta, 3D honesto). Nenhum e source_art.

| Ponteiro | Papel observado | Nao e |
|---|---|---|
| [RheoGamer](https://x.com/RheoGamer) | densidade arcade no VDP legal | copiar KOF/Fatal Fury/Metal Slug/Mario |
| [PigsyRetro](https://x.com/PigsyRetro) | traducao de arte rica para pixel nativo | copiar SotN/Shinobi/PC-98 |
| [GabrielPyron](https://x.com/GabrielPyron) | palco reautorado ao teto de VRAM (~980 tiles BG+FG), prova em hardware | dump de stage arcade |
| [ReySilveira28](https://x.com/ReySilveira28) | conversao de palco com segundo passe de detalhe; 320x224 honesto | widescreen como gate; Mode 7 de enfeite |
| [RDiggoSilva](https://x.com/RDiggoSilva) | identidade sonora Neo Geo/arcade **traduzida** para YM2612 | dump de sample; PSG generico |
| [MXRetroDev](https://x.com/MXRetroDev/status/1900597106068296043) | carta de paletas **compartilhadas** do roster; alt vs palco | uma paleta por skin sem sistema |
| [birt_shannon](https://x.com/birt_shannon/status/2077723799316013354) | 3D software com DMA, inversao de planos e FPS declarado | tech demo mudo a 60 fps mentiroso |
| [danielmoura79](https://x.com/danielmoura79/status/1824963016586056183) | engine de luta (HAMOOPIG): FSM, frame data, "isso e Mega Drive" | sprite de lutador sem contrato de luta |
| [MegadriveDev](https://x.com/MegadriveDev) | SGDK + XGM/XGM2; DMA/VDP como orcamento | tratar SGDK como teto; slogan de driver sem medir |
| [SokZaJelo](https://x.com/SokZaJelo) | engine de acao com 0 lag frames | lag "de estilo" em plataforma critica |
| [laurent_crouzet](https://x.com/laurent_crouzet) | arrange YM2612 sob carga real de DMA | demo de musica sem a cena pesada |

Mapeados, **nao viram escola nova** (oficio ja coberto):
`masterlinkueibr` → P+C; `StudioVetea` → R densidade; `dantemendes` → honestidade
de port (Y2/P8); `ErikHaliewicz` / `profcelsofontes` / `rael16x` /
`level1_Studio` → laboratorio (scroll, raycast, doubler, 3D). `Genesis8141`
e curadoria de cena, nao axioma.

Citar o handle sem aplicar o ofício e teatro. Copiar os sprites, palcos,
personagens, musicas ou IP deles e `clone_risk` e bloqueia autoria.

---

## 2. Frase que resume o piso

Rheo, 2026-07-21:

> Voce vai precisar dominar o mega drive. Saber o basico sobre a VRAM
> dele, cram tambem. Alem de tomar bastante decisoes artisticas se nao
> for uma pessoa que fizer vai ficar uma merda.

Traducao operacional para o agente:

1. VRAM e CRAM nao sao detalhes de closeout — sao a primeira decisao de arte.
2. Decisao artistica nao e opcional. Sem ela, conhecimento de hardware
   produz lixo visivel.
3. "Cabe no VDP" sem parecer intencional e reprovacao, nao prudencia.

Pigsy demonstra o complemento: arte de PC-98, PSX ou 8-bit so vira Mega
Drive quando alguem escolhe cores 9-bit a mao, parte planos, usa
Shadow/Highlight como ferramenta e compara o resultado em movimento
contra a fonte.

---

## 3. O que cada escola faz — evidencias, nao fama

Evidencia colhida em 2026-08-29 (posts, videos, colaboracoes publicas).
Nao promove projeto alheio a referencia canonica de asset. Promove
**metodo**.

### 3.1 Escola Rheo — densidade arcade no VDP

Trabalhos observados: Real Bout Fatal Fury Genesis; KOF Mega Drive com
Pyron e RDiggoSilva (SGDK + HAMOOPIG); estudo Metal Slug; engine de
plataforma; Pocket Bravery; metasprite de boss (Juggernaut); streaming
de fonte comprimida ROM→VRAM.

Axiomas extraidos (o agente aplica estes, nao os sprites):

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| R1 | A cena deve poder provocar "nem parece Mega Drive" **permanecendo legal** (4 paletas, 64 KB VRAM, 20 sprites/linha H40, 60 fps) | Folga nao medida e timidez. Pobreza visual nao se justifica com "e Mega Drive" |
| R2 | Paleta e orcamento, nao resto | Declarar PAPEL de cada uma das 4 paletas antes de pintar. Exemplo observado: 1 player + 1 inimigos + 1 BG + 1 folga. Folga e decisao, nao acaso |
| R3 | Escala e contagem de frames podem mirar o arcade se streaming e metasprite existirem | Lutador/brawler/boss grande nao nasce 24x32 "porque SGDK". Tamanho vem do GDD + budget medido |
| R4 | Cenario arcade e **reautorado** para teto de tiles, nunca dumpado | Pyron: BG+FG em ~980 tiles. Ilustracao inteira quantizada e `WHOLE_IMAGE_CONVERSION_RISK` |
| R5 | Personagem maior que um sprite e metasprite estável, nao um PNG unico que estoura SAT | Boss/chefao exige `modular_boss_rig_contract` e prova de montagem sem glitch de junta |
| R6 | O que nao esta na luta/cena viva pode ser comprimido e streamado | Fonte, portraits, win quotes, cut-ins: comprimir e DMA; nao residir tudo |
| R7 | 60 fps com animacao completa e nao-negociavel | Frame count alto sem 60 fps e mentira; 60 fps com 2 frames e pobreza |
| R8 | Hardware real (Everdrive) e a verdade; emulador e video | BlastEm fecha gate do Forge; claim "roda no Mega" exige hardware ou declaracao honesta |
| R9 | SGDK e veiculo valido | Nao inventar que AAA exige asm puro. AAA exige ofício |
| R10 | Sem decisao artistica, VRAM/CRAM sozinhos falham | Gate artistico nao e polimento tardio |

### 3.2 Escola Pigsy — traducao de arte rica para pixel nativo

Trabalhos observados: demake Castlevania SotN no MD; remake GG Shinobi
("enhanced 8-bit", analogo Super Mario All-Stars); ports de pixel art
PC-98; tutoriais de conversao high-color, Shadow/Highlight como cor
SNES-like e como transparencia; camera + parallax; rotacao especial
com colaboracao.

Axiomas extraidos:

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| P1 | Fonte de outra plataforma e **materia-prima**, nunca quantizacao cega | PC-98 12-bit/16 cores, PSX, GG, high-res: `art-translation-to-vdp`, nao `quantize()` |
| P2 | Shadow/Highlight e ferramenta de **cor extra** e de **transparencia falsa** | Cena que precisa de agua, vidro, lua, capa, nebula ou SNES-like sem S/H declarado fica abaixo do piso se o hardware permitiria |
| P3 | "Enhanced 8-bit": manter linguagem de desenho e escala, **somar** cores e partir BG/FG para parallax | Port 8-bit→MD que so estica pixels e recusa planos e S/H e reprovacao |
| P4 | Matching 9-bit e curadoria humana de rampa | Cores vizinhas que colapsam no 9-bit exigem escolha, nao nearest-color em massa |
| P5 | Paleta compartilhada e o default adulto | Player divide paleta com vela, inimigo, FX pequeno. Variante cosmética que explode CRAM e recusada |
| P6 | Parallax e upgrade esperado quando ha budget de plano | Um plano chapado onde a fonte pedia profundidade e `layer_plan` ausente |
| P7 | Escalar fonte para 320 nativo com intencao | GG 160 → dobrar e redesenhar, nao "zoom out" com sprites formiga |
| P8 | A atmosfera da fonte deve sobreviver no MD, sem fingir PSX/SNES | `soul_summary` + `must_keep`; downscale que mata atmosfera e fake pixel art |
| P9 | Todo truque e nomeado, comparado a fonte e mostrado **em movimento** | Screenshot estatica nao prova S/H, agua, capa, cycling, rotacao |
| P10 | PC-98 16 cores e professor de disciplina MD | Se a fonte ja vive em 16 cores, o Forge nao tem desculpa para lama de 256 |

### 3.3 Escola Pyron — palco como problema de VRAM

Evidencia: KOF MD com Rheo; "I remade the background to fit on our vram
constraints"; "fit BG + FG in 980 tiles"; "I think thats at least remember
the original artwork"; captura em hardware com RetroTink; CRT 240p/15 kHz
nas tags.

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| Y1 | Palco de luta/brawler tem **teto de tiles medido** (ordem de grandeza: ~980 BG+FG) | Sem `hardware_budget_review` o palco nao fecha. Dump arcade e R4+Y1 falhos |
| Y2 | O alvo e **lembrar** a arte original, nao copiar o sheet | `soul_summary` do palco; layout/tile do arcade em `data/source_art` e clone |
| Y3 | Prova visual de palco inclui hardware ou declaracao honesta de emulador | Video emulador sem essa frase e R8 falho. Pyron tem o mesmo recorte no proprio perfil |

### 3.4 Escola Chev (ReySilveira28) — conversao de palco com segundo passe

Evidencia: conversao Ryuuko no Ken → Art of Fighting Special MD (update
porque "I had missed some details"); concept SF em arte 512x224 que ainda
renderiza 320x224 4:3 "no blind spots or cheats with the tiles"; "We're
not doing this as a hardware demonstration; we just want to make a fun
and beautiful game."

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| C1 | Conversao de palco tem **segundo passe** de detalhe perdido | Primeira quantizacao nunca e elite. Painel original/basic/elite obrigatorio |
| C2 | Autor pode desenhar 512x224 para scroll; o **gate** e 320x224 4:3 | Widescreen de emulador e extra, nunca fecha `testado_em_emulador` |
| C3 | Sem cola de tile, sem ponto cego de camera | Stage que "funciona" escondendo seam ou repetindo cookie-cutter falha |
| C4 | Beleza jogavel vence demo de hardware | Mode 7 / raster de vitrine sem funcao de gameplay e `decorative_only_blocked` |

### 3.5 Escola Diggo — identidade de chip, nao sample dump

Evidencia: soundtrack do KOF MD "like the Neo Geo"; arranjos Furnace
(Pocket Bravery, Shinobi, SSF2, Rayman, Contra) para YM2612; tratado
como autor igual a arte e ao codigo nos posts do time.

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| D1 | Audio **traduz** a identidade da fonte para YM2612/PSG/PCM | Sample-heavy "porque Neo Geo" sem budget de DAC e mentira. Skill: `xgm2-audio-director` |
| D2 | Trilha e co-autora da cena, nao overlay tardio | Slice AAA sem `audio_architecture_card` e identidade de chip fica `needs_review` |
| D3 | Arrange de outra plataforma para o chip MD e o P1 do audio | Copiar PCM da Neo/SNES para `data/` e clone, nao traducao |

### 3.6 Escola MX — carta de paletas do roster (post canonico)

Evidencia primaria: [paletas compartilhadas do FFMD](https://x.com/MXRetroDev/status/1900597106068296043)
— uma **carta** de paletas do elenco, nao um PNG isolado. Complemento:
alts testadas contra o cenario; 3 temas de cor por personagem; 3p co-op
remove/reposiciona objetos para VRAM; bank-switch instavel → cortou
alts e disse isso em publico; "ferramentas modernas sem talento nao
explicam o resultado".

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| M1 | Recolor de roster e um **sistema CRAM publicado** antes de pintar skins | Sem carta `palette_role_map` / shared slots, cada skin vira 16 cores novas e estoura |
| M2 | Alt palette prova-se **sobre o palco real**, nao no vacuo | Contraste lutador vs BG e check; alt que some no asfalto falha |
| M3 | Teto de ROM/bank e recorte honesto | "Nao coube, cortei X" e status valido. Mentir bank-switch e R8/M3 |
| M4 | Mais atores na tela mudam a **cena** (objetos saem), nao so o claim | 3p/horda sem `vram` de objeto e `unexploited` invertido: e estouro |

### 3.7 Escola Shannon — 3D / DMA com as cartas na mesa

Evidencia primaria: [Genesis 3D Engine Update 8](https://x.com/birt_shannon/status/2077723799316013354).
Buffer 256x160 (+25%) no limite de DMA com vblank estendido; **planos
viram framebuffer 3D** (double buffer linear); **sprites viram o fundo**
estilo Neo Geo (multiplex 114 sprites 16x32); XGM1 no lugar de XGM2
porque o DMA mata o XGM2; ~20 fps **com musica carregada** como
benchmark real; rotacao Z por LUT; dirty min/max tile lines; "no cpu
cycle to be spared"; placeholder ate existir level design.

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| S1 | Se os dois planos pagam uma tecnica, o fundo **muda de superficie** e isso se declara | Inversao plane↔sprite exige `raster_fx_ownership_map` + multiplex medido |
| S2 | DMA, driver de audio e tamanho de buffer sao **um** orcamento | Tech demo 3D sem conta de DMA e `hardware_used_as_excuse` invertido |
| S3 | Benchmark **com** musica | Demo muda e 60 fps de probe nao prova o recorte 3D |
| S4 | FPS real se declara. 20 fps honesto vence 60 fps de mentira | Nao contradiz R7: R7 e 2D arcade. 3D software promete o numero medido |
| S5 | LUT / recuo matematico e oficio, nao vergonha | `experimental_override` so com FPS, DMA e fallback escritos |

### 3.8 Escola HAMOOPIG (Daniel Moura) — luta e um contrato, nao um sprite

Evidencia primaria: [video MD + "nao comprem repros, e gratis, e sim isso
e Mega Drive"](https://x.com/danielmoura79/status/1824963016586056183).
Criador da HAMOOPIG (FSM 100–800, 6-botao, 60 fps, frame data). Rheo:
"Ele quem me ensinou a maioria do que eu sei sobre mega drive e mecanicas
de jogo de luta." Comparativos com SSF2 como **qualidade**, mockup de
palco, fonte "This is real Mega Drive" com dica do Pyron. O Forge ja tem
a engine no workspace.

| ID | Axioma | O que isso obriga no Forge |
|---|---|---|
| H1 | Lutador sem FSM, hitbox, frame data e input 6-botao e fantasia | `fighting_2d_design_contract` / HAMOOPIG. Sprite bonito nao e luta |
| H2 | Comparar com SSF2/SoR2 e eixo de qualidade, nunca sheet em `source_art` | Ja esta na `benchmark_usage_policy` |
| H3 | Reusar a engine que o workspace ja tem em vez de reescrever luta ruim | `SGDK_Engines/` HAMOOPIG e substrato; nao clonar o roster dos videos |
| H4 | Homebrew desta cena e gratuito; repro comercial ameaca o oficio | Nao e gate visual; e etica de distribuicao do Forge |
| H5 | Title/HUD/fonte de luta sao Mega Drive de verdade, nao overlay de debug | Front-end da luta entra na barra (8.3 + esta secao) |

### 3.9 Oficio novo, sem escola extra

Nao duplicar R/P/Y/C/D/M/S/H. So o que ainda nao estava escrito:

| ID | Oficio | Ponteiro | Obrigacao |
|---|---|---|---|
| G1 | SGDK e **base, nao teto** | MegadriveDev | Produtividade pelo wrapper/API 2.11; DMA/multiplex/asm quando a qualidade exigir. Headers `sdk/sgdk-2.11/inc/` vencem fama |
| G2 | Driver de som se **mede** na cena mais pesada | MegadriveDev + Shannon | XGM familia e o padrao. XGM2 **nao** e automaticamente mais leve sob DMA alto (S3). Escolha com musica carregada |
| D4 | Arrange tem de sobreviver ao pior frame de DMA grafico | laurent_crouzet | D1-D3 + teste na cena pesada, nao loop isolado |
| Z1 | Cena critica de plataforma/acao: **0 lag frames** | SokZaJelo | Input-to-display sem frame extra "de feel". Lag e blocker, nao estilo |
| S6 | Multiplex alem do SAT e **opt-in** medido | Shannon | 80 SAT / 20 por linha H40 continuam o piso legal. 1000+ sprites e lab/assinatura, nunca default de produto |

### 3.10 Parametros de concepcao (fonte unica de teto)

Arquivo: `doc/03_art/live_scene_bar_parameters.json`.

Agente **nao redesenha** esses numeros em prompt. Le o JSON. Correcoes
explicitas contra resumo inflado:

- CRAM simultanea = **4** paletas, nao 4–8.
- ~980 tiles BG+FG = teto **observado** de palco denso (Pyron), nao limite
  de silicio.
- 90–97% CPU = observado em demo extrema; **nao e meta**. Declare o medido.
- Widescreen e Mode 7 de vitrine **nao fecham gate**.
- Claim de 60 fps exige cena + audio medidos.

Ordem de construcao (igual `scene-direction-first`, com tetos no passo 4):

`limites → planta em pixel → coreografia → medicao → orcamento → contrato
→ fonte → traducao nativa → segundo passe → ROM → evidencia`

---

## 4. Piso compartilhado (o que "nao aceitar abaixo" significa)

Estes checks sao binarios. Hedging na descricao cega = falhou.

Para `aaa_game`, vertical slice, `ready_for_aaa`, asset critico, HUD
heroico, title, boss, lutador, brawler ou cena assinatura:

1. **Pixel nativo, nao foto encolhida.** Hard edge, grid 8x8, index 0,
   paleta 9-bit `{0,34,68,102,136,170,204,238}`. Fake pixel art de IA
   (AA, blur, gradiente, noise de downscale) e `fake_pixel_art_rejection`.
2. **Material com no minimo 3 degraus** (luz, base, sombra) por materia
   principal. Chapado e piso de 1994 ja reprovado; aqui tambem.
3. **Silhueta lê em 320x224 e em preto-e-branco** no tamanho alvo.
4. **Paleta com papel.** Cada uma das 4 paletas declara o que paga.
   `PALETTE_WASTE` e `palette_vibrancy_lost` reprovam mesmo com tile OK.
5. **Cenario reautorado como tile**, nao ilustracao inteira. Dedup/H-flip
   medidos. Estouro de tiles unicos sem `compare_flat` honesto ou
   modularizacao e reprovacao.
6. **Planos com hierarquia.** BG_B respira, BG_A estrutura, sprite decide.
   Fundo mais agressivo que o jogavel falha.
7. **Hardware a servico da imagem.** S/H, cycling, split, metasprite,
   streaming, parallax: usam-se quando a cena pede, medem-se, nao se
   ostentam vazios nem se omitem por timidez.
8. **Movimento.** Ciclo critico tem GIF/video do **output** + pivots +
   contact. Still nao prova golpe, agua, capa, cycling.
9. **FPS prometido com a densidade prometida.** 2D arcade/luta/brawler:
   60 ou recuo no GDD (R7). 3D software: o numero medido, com musica no
   DMA (S3/S4). 20 fps declarado vence 60 fps de probe mudo.
10. **Comparacao lado a lado** `fonte / basic / elite / rom` quando houver
    traducao. Elite tem de vencer basic. ROM tem de preservar alma.
11. **CRT/240p.** Se so funciona ampliado no LCD, ainda nao existe.
12. **Autoria.** Oficio da cena viva, nunca pixels/PCM dos trabalhos
    citados. `benchmark_used_as: quality_bar`.

Se qualquer item falhar, o maximo status e `needs_review`. Nao e
`elite_ready`. Nao e `delivery`. Nao e `ready_for_aaa`.

---

## 5. Tabela de rejeicao (sintoma → diagnostico → blocker)

| Sintoma | Diagnostico | Blocker |
|---|---|---|
| "Parece homebrew de 2003" | densidade/paleta/escala abaixo do piso vivo | `live_scene_bar_failed` |
| "E Mega Drive, nao tem como" | R1 invertido: limite usado como desculpa | `hardware_used_as_excuse` |
| PNG IA encolhido com 16 cores | P1/P8 ignorados | `fake_pixel_art_rejection` |
| Fundo dumpado, 1000+ tiles unicos, 2% dedup | R4 | `WHOLE_IMAGE_CONVERSION_RISK` |
| Lutador 24x32 em jogo de luta/brawler sem justificativa de GDD | R3 | `sprite_scale_below_genre_density` |
| 4 paletas pintadas sem papel | R2/P5 | `palette_role_undeclared` |
| Agua/vidro/capa sem S/H nem plano, e o budget permitia | P2 | `shadow_highlight_omitted_without_cause` |
| Port 8-bit so com mais resolucao, mesmo plano unico | P3/P6 | `enhanced_8bit_not_applied` |
| Quantize global "passou no PLTE" | P4 | `blind_quantize_as_translation` |
| Screenshot unica de golpe/agua/cycling | P9 | `static_proof_for_motion` |
| 60 fps no probe, 8 frames no heroi | R7 invertido | `fps_without_animation_density` |
| Prompt "pixel art sprite sheet Mega Drive no AA" como fonte final | contradiz sprint 03 e P1 | `pixel_art_prompted_as_final` |
| Citei Rheo/Pigsy/Pyron/Chev/Diggo/MX/Shannon/Daniel no GDD e entreguei chapado | teatro de handle | `name_drop_without_craft` |
| Asset do port deles em `data/source_art` | IP | `clone_risk` / `benchmark_as_source_art` |
| Palco arcade dumpado "porque Pyron" | Y2 invertido | `stage_dump_not_restage` |
| Widescreen 512x224 como prova de gate | C2 | `widescreen_used_as_delivery_gate` |
| Seam/cola de tile no palco | C3 | `stage_tile_cheat` |
| Recolor por personagem sem carta compartilhada | M1 | `roster_palette_unshared` |
| Alt palette so no vacuo, some no palco | M2 | `alt_palette_fails_on_stage` |
| 3 jogadores/horda sem cortar objetos | M4 | `actor_count_without_scene_cut` |
| PCM Neo Geo/SNES como BGM final | D1/D3 | `chip_identity_not_translated` |
| Tech demo 3D sem DMA/musica/FPS real | S2/S3/S4 | `silent_techdemo_fps_lie` |
| Planos viram 3D e o fundo "some" | S1 | `plane_inversion_undeclared` |
| Lutador so com sheet, sem FSM/hitbox | H1 | `fighter_sprite_without_fight_contract` |
| SGDK como desculpa para nao medir DMA | G1 | `sgdk_used_as_ceiling` |
| XGM2 escolhido por slogan sob DMA alto | G2 | `sound_driver_unmeasured` |
| Lag frame em plataforma critica | Z1 | `critical_lag_frames_nonzero` |
| 1000 sprites em produto sem lab/assinatura medida | S6 | `extreme_multiplex_as_default` |

---

## 6. O que NÃO e esta barra

- Nao e ordem para clonar jogos da SNK, Konami, Sega, Nintendo, Capcom
  ou Final Fight/SSF2/Art of Fighting.
- Nao e ordem para copiar paleta, pose, stage layout, HUD, timbre ou silhueta
  dos videos deles.
- Nao e desculpa para cartucho de 15 MB como virtude. Rheo planeja 15 MB
  no KOF porque o conteudo pede; o Forge mede ROM. Tamanho sem ofício e
  desperdicio.
- Nao substitui a barra 1994, o feedback bank, nem `visual-excellence-standards`.
  E o **piso** que essas pecas passam a julgar.
- Nao autoriza `ready_for_aaa` por doutrina. Prova em ROM do Forge ainda
  nao existe para esta barra (`runtime_proof_status: NAO_INICIADA`).

---

## 7. Como qualquer agente usa isto em qualquer acao

Antes de gerar, converter, aceitar, promover ou chamar de AAA:

1. Ler este arquivo (ou o brief) e o JSON.
2. Ler `doc/03_art/live_scene_bar_parameters.json` e aplicar o
   `mode_policy` do modo da sessao (criar / analisar / treinar / lab /
   curadoria).
3. Classificar escolas (pode somar). Nao inventar escola para handle
   mapeado. Aplicar axiomas + 12 checks + tetos do JSON.
4. Gerar **fonte forte** (concept high-res, volume, material) — nao
   "sprite sheet 32x32 Mega Drive" no gerador.
5. Traduzir no grid nativo (lineart 1 px → paleta semantica → dither
   de material). Downscale/quantize cego e anti-padrao.
6. Medir tiles, scanline, DMA, CPU, fps, audio **antes** de fechar
   (parameters.workflow.measure_every_build).
7. Provar no BlastEm a 320x224, em movimento se a cena se move.
8. Emitir `out/logs/live_scene_bar_report.json`. Sem laudo, o claim
   visual nao existe.
9. Se falhar um check: `needs_review` e a proxima acao ataca o blocker,
   nao "mais um build".

Pedido direto de arte em projeto `aaa_game` nao espera menu, mas **nao
pula** os passos 4-8.

---

## 8. Relacao com o resto do framework

| Peca | Papel perante esta barra |
|---|---|
| `00_visual_quality_bar.md` | piso 1994; esta barra e o piso 2026 vivo |
| `03_ai_source_to_vdp_sprint.md` | metodo de traducao; alinhado a P1/P8 |
| `art-translation-to-vdp` | executa P1-P4, P8, R4 |
| `visual-excellence-standards` | juiz; agora reprova abaixo desta barra |
| `megadrive-vdp-budget-analyst` | mede R2, R4, R5, R7 |
| `shadow-highlight-scroll-fx` | executa P2 |
| `xgm2-audio-director` | executa D1-D3 |
| `fighting-game-design` / HAMOOPIG | executa H1-H3, H5 |
| `aaa-pipeline-guardian` | `ready_for_aaa` exige laudo desta barra |
| `benchmark_usage_policy` | handles = qualidade; pixels/PCM deles = bloqueados |

---

## 9. Status honesto deste workspace em 2026-08-29

- Doutrina: escrita e amarrada.
- Capacidade de gerar no nivel desta barra: **nao provada em ROM**.
- Gargalo ja medido em `doc/curation/GRAPHICS_CAPABILITY_REPORT_2026-08-06.md`:
  o Forge e forte em veto e fraco em redesenho nativo que preserve
  anatomia, carisma, material e acting.
- Proximo passo: `doc/03_art/19_plan_pixel_art_live_scene_capability.md`.
