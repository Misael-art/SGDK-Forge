# Revisao visual e KO — 2026-09-12

Estado: implementado, buildado e testado parcialmente no BlastEm NTSC.
Teto: prototype; nao e entrega AAA nem validacao completa de hardware.

## Binario e provas

- ROM: `out/rom.bin`, 2490368 bytes.
- SHA256: `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`.
- Build canonico: `out/logs/visual_ko_verified_build.log`, exit 0.
- Sessao final Musgo x Musgo: `out/emulator_evidence/visual_ko_20260912T162933Z/`.
- Sessao final Ken x Musgo: `out/emulator_evidence/visual_ko_20260912T162753Z/`. O argumento solicitava Musgo, mas a imagem mostra Ken; o teste foi classificado pelo que rodou. O capturador agora compara o nome exibido antes de confirmar.
- Ambos os manifests vinculam o SHA acima; copias da ROM preservadas por sessao. Inputs reais de teclado, sem escrita em RAM/ROM do emulador.
- Videos de janela: 640x480, 60 quadros/s de gravacao, 71,316667 s (Musgo) e 72,7 s (Ken), sem audio. Esse formato inclui escala/letterbox; nao e dump nativo VDP nem prova de 60 fps constantes do loop.
- Titulo final Musgo: 60,5 fps; amostra unica, nao medicao sustentada de performance.

## Cinco pontos solicitados

| Ponto | Mudanca | Prova e limite |
|---|---|---|
| HUD corrompido | Recortes corretos das barras e de uma unica variante KO do atlas; sem contaminacao da linha de numeros | `01_round.png` e quadros de combate das sessoes finais |
| P2 nao zera | Zero preenche todas as 16 colunas; positivo conserva uma coluna; cache nao e invalidado a cada frame | Dois KOs por sessao, `zero_2_result.png`; amostras passam de 4572 pixels amarelos para 0 e voltam a 4572 no round seguinte |
| Cenario quadriculado | Preview solicitado, sem ampliacao de blocos 4x4; 768 tiles representantes, 14 cores opacas, indice zero reservado | Chao sem buracos pretos em capturas finais; ainda ha perda local por reuso aproximado de tiles, nao e reproducao pixel-perfect |
| Musgo sem derrota/vitoria | Queda de 2 frames, derrota deitada e pose de vitoria proprias; dano letal nao relanca duas vezes; round espera pouso | Video final Musgo, sequencia 27–31 s, `zero_2_result.png`; vitoria/derrota sao poses terminais de 1 frame, nao ciclos multiframes |
| Texto ilegivel/fora da fonte | Alfabeto do atlas solicitado, PAL1, painel preto compacto e envio do mapa no VBlank | ROUND 1, KO, PLAYER 1 WINS, A REMATCH, START SELECT legiveis em capturas finais; painel deixa punhos e rosto do vencedor visiveis |

Revanche por A observada nas duas sessoes finais (`rematch_round.png`): ROUND 1, vida cheia e lutadores preservados. Retorno por START observado na ROM intermediaria `4144711f...`, sessao `visual_ko_20260912T161832Z/return_select_or_pause.png`; nao foi repetido no binario final.

`ko_video_contact_sheet.png` e uma amostragem derivada do video final Musgo, 19–30 s, 1 quadro/s. Nao substitui o video; mostra vida positiva, KO, lancamento, descida e pose terminal em ordem temporal.

## Testes e residencia

- `rascunho/temporario/test_health_contract.py`: PASS nas funcoes C reais, ambos os jogadores, 192 transicoes letais, sem relancamento por energia especial, clamp de cura e todos os valores do HUD.
- `rascunho/temporario/test_stage_palette.py`: PASS, indices opacos 1..14, canais 9-bit, hashes fonte/saida e relatorio de 768 tiles.
- Scripts Python compilam; verificacao local de whitespace passou.
- Stage 768 + HUD 249 + inicio 1 = primeiro tile livre 1018; regiao de sprites inicia 1020, com 420 tiles. Guard consulta metadata SGDK antes de carregar.
- Proximo degrau 832 termina em 1082: sobreposicao estatica de 62 tiles, rejeitado. APLIB reduz ROM, nao residencia VRAM.
- Nao medidos: pior DMA, SAT/scanline, fragmentacao/alocacao dinamica e FPS do loop da ROM. Nao ha selo VLAB/VDP/runtime novo.

## Arte, prompt e aprendizado

- Ferramenta: ImageGen, com referencia do idle existente do Musgo. A skill foi usada para criar poses semanticamente distintas; segurar um frame em pe nao produz uma derrota deitada.
- Fonte salva: `data/source_art/musgo/ko_victory_source_v1.png` (SHA256 `5b0772b5678f3e98063f87eee3612601aa65b5df3848879b7f842e3259ee5cb1`).
- Prompt integral salvo: `data/source_art/musgo/ko_victory_prompt.txt`.
- Conversao: `data/source_art/musgo/convert_ko_victory.py`; saidas `res/sprite/musgo/fall_v1.png`, `defeat_v1.png`, `victory_v1.png`; dimensoes, hashes e proveniencia em `rascunho/musgo_ko_victory_report.json` e `doc/asset_provenance_manifest.json`. Arte permanece source_candidate.
- Fonte HUD local `data/source_art/sf_hud/sf_hud_sheet.png` e byte-identica ao atlas solicitado do MSSF2T (SHA256 `1d2c8381841b38dcb2b14319abc73a5febbbd759283076f513bcfda721eb9f9b`).
- Nove licoes locais em `doc/curation/2026_09_12/visual_ko_lessons.json`. Hipotese antiga de cache/residual no reset explicitamente retirada do caderno Musgo; causa demonstrada do relancamento e a chamada EnergyType 2.
- Nenhuma promocao/alteracao do framework canonico nesta revisao.

## Proxima ordem de trabalho

1. Provar P2 vencedor, empate/time-over, START e especiais apos reset na ROM vigente; incluir PAL.
2. Medir pior DMA/SAT/scanline e pool dinamico antes de aumentar o cenario (so 2 tiles livres entre regioes estaticas).
3. Capturar audio isolado e FPS do loop; renovar o bundle canonico completo.
4. Polir enquadramento da derrota junto a borda (corpo parcialmente fora da tela), sombra e perdas de tiles. Vitoria dedicada existe como pose; ciclo multiframes permanece melhoria futura.
