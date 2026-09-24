# Visual Quality Bar — Mega Drive AAA

## Piso vivo (2026) — leia primeiro

A pergunta "isso poderia estar em um jogo comercial AAA de 1994?" continua
obrigatoria e **nao fecha** `aaa_game`.

O piso de qualquer acao visual neste workspace e o oficio da cena viva,
nao o handle:

- documento: `doc/03_art/18_live_scene_bar.md`
- JSON: `doc/03_art/live_scene_bar.json`
- brief: `tools/sgdk_wrapper/.agent/references/live_scene_bar_agent_brief.md`

`RheoGamer` = densidade arcade no VDP legal. `PigsyRetro` = traducao de
arte rica para pixel nativo. Completam o piso: Pyron (palco ~980 tiles),
Chev (segundo passe, 320x224 4:3), Diggo (YM2612 com identidade),
MXRetroDev (carta de paletas do roster), Shannon (3D/DMA/FPS honesto),
Daniel Moura (HAMOOPIG: luta e contrato). Citar os nomes e entregar
chapado e reprovacao. Pixels/PCM dos trabalhos deles nunca entram em
`data/source_art`.

Sem `out/logs/live_scene_bar_report.json`, o claim visual nao existe.

---

Toda entrega visual DEVE ser comparável aos maiores clássicos de 16-bits. O Benchmark exige especificamente:
- Streets of Rage 2
- Sonic 3
- Gunstar Heroes
- Contra Hard Corps
- Castlevania Bloodlines

## Proibido:
- cores chapadas sem variação
- ausência de dithering
- ausência de shading
- ausência de textura
- tiles repetitivos sem disfarce (cookie-cutter grid)
- sprites sem volume

## Obrigatório:
- uso de pelo menos 3 níveis de cor por material (luz, cor base, sombra)
- contraste claro entre foreground / mid / background (distinção de brilho atmosférico)
- leitura clara de silhueta nos sprites principais
- textura perceptível nos materiais
- uso de dithering quando for necessário disfarçar transições ou economizar gradiente de paleta

## Piso de contraste (curadoria 2026-08-17)

Adjetivo de direcao sem numero vira defeito. Elemento descrito como "leve", "discreto" ou
"sutil" continua tendo que ser lido:

- **discricao e sobre tamanho e peso tipografico, nunca sobre luma**;
- todo elemento de leitura tem **piso de luma e rampa de no minimo 3 passos**;
- nenhum indice deve concentrar mais de ~70% da tinta de um asset;
- contraste se mede **contra o fundo real onde o asset vive**, nao no vacuo.

Caso: um wordmark entregue com 99% da tinta num unico indice de luma 38, sobre um fundo de luma
media 46 — contraste de -8, ou seja mais escuro que o proprio fundo.

## Teste final:
"Isso poderia estar em um jogo comercial AAA de 1994?"

Se a resposta não for um categórico "SIM" → REFAZER COMPLETAMENTE.

Segundo teste, obrigatorio para `aaa_game`:
"Isto passa os 12 checks da barra viva (`18_live_scene_bar.md`)?"

Se a resposta nao for um categorico "SIM" com laudo em disco → o teto e
`needs_review`. Nao e entrega.

## Complemento: Assinatura Do Projeto

Visual AAA nao basta se o jogo parece generico. Para projeto novo, reseed,
vertical slice ou claim AAA, cruzar esta barra com:

- `doc/07_game_design/00_creative_director_radar.md`
- `doc/creative_director_radar.json`

Pergunta obrigatoria:

"Esta imagem, cena, HUD, title screen ou efeito prova a personalidade especifica
do jogo, ou apenas mostra que o agente sabe fazer algo correto?"

Se for apenas correto:

- emitir `signature_gap`;
- propor o menor movimento de direcao que tornaria a cena memoravel;
- atualizar GDD/spec/TDD antes de implementar;
- validar em BlastEm antes de promover.

## Complemento: Traco Autoral

Em projeto `aaa_game`, "bonito", "arcade", "anime", "16-bit" ou "CPS2-like"
nao sao estilos suficientes. Todo asset critico precisa de um contrato de traco
autoral antes de gerar, aceitar ou converter:

- `line_signature`: como o contorno, linhas internas e bordas de sombra se
  comportam;
- `silhouette_hooks`: 3 marcas que sobrevivem em preto puro;
- `face_grammar`: sobrancelha, olho, nariz, boca, cabelo e atitude facial;
- `hand_foot_grammar`: tamanho, angulo e leitura de contato/impacto;
- `costume_asymmetry`: marcas de roupa/acessorio que nao podem sumir;
- `material_marks`: como madeira, corda, rede, pele, tecido, couro, metal e
  agua sao desenhados;
- `generic_blockers`: lista do que faria o asset parecer de outro jogo.

Sem esse contrato, o asset fica no maximo `needs_review` e deve receber blocker
`authorial_line_contract_missing` ou `generic_prompt_style_blocker`.
