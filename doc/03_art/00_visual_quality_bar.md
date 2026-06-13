# Visual Quality Bar — Mega Drive AAA

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

## Teste final:
"Isso poderia estar em um jogo comercial AAA de 1994?"

Se a resposta não for um categórico "SIM" → REFAZER COMPLETAMENTE.

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
