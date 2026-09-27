# HUD, FX e proxima etapa de cenario — 2026-09-25

## Escopo e identidade

Pedido atual e do MUGEN -> SGDK/Mugenesis_Demo; trabalho REX desconsiderado.
Inspecao no checkout `7cf00ed8` com alteracoes locais preexistentes preservadas.
O piloto 750,1 permanece no worktree isolado anterior; esta rodada parte do
projeto principal e NAO incorpora silenciosamente esse piloto ou PR21.

Referencias recebidas copiadas com hashes em
`rascunho/inputs/hud_review_2026_09_25/inputs_manifest.json`.
Sao referencias de composicao/legibilidade; screenshots nao provam alocacao de
CRAM, resolucao original, tecnicas internas ou desempenho de outro jogo.

## Diagnostico confirmado

| Item | Causa observada | Encaminhamento |
|---|---|---|
| Retrato com buracos e cores erradas | Fonte 9000,0 possui paleta propria. Gerador tratava indices como os do corpo; indices nao mapeados viravam zero. Fonte tem 623 pixels opacos, saida antiga 394: perda de 229 pixels opacos. PNG antigo tambem omitia transparencia explicita para viewers. | Traduzir RGB da paleta propria para slots estaveis opacos do lutador; preservar mascara e excluir slot livre/roupa. |
| Barra centralizada | Constantes `POW_P1_X=18`, `POW_P2_X=21` | Ancorar P1 nos tiles 1..5 e P2 nos tiles 34..38; carga cresce para o centro. |
| Estrela cortada | Estrela ocupa WINDOW linhas 4/5; limpeza do combo ocupa 5/6 e apaga sua metade inferior. | Estrela nas linhas 3/4, combo nas linhas 5/6. |
| Combo de dois digitos | Area limpa tem 10 tiles, mas dois digitos + HITS ocupam 12 | Limpar largura efetiva de 12 tiles para evitar residuos. |
| SUPER sem comportamento visual completo | HUD apenas copia energia para comprimento | Indicacao cheia, alternancia de tiles da barra e descarga quadratica de 24 atualizacoes; energia de gameplay nao e alterada. |
| Retrato muda com flash | Usa PAL1/PAL2, tal como corpo | A cor base pode ser estabilizada entre roupas; isolamento do flash continua uma decisao de ownership, nao solucionado por PNG. |

Os retratos-fonte pequenos ja sao pixel art legivel. A referencia pintada grande
nao e automaticamente superior para um HUD de 32x32. Dithering deve preservar
olhos, boca e contorno; ruido extra nao substitui contraste. O termo "drifting"
foi interpretado como dithering. Transparencia externa deve usar indice zero,
sem remover preto opaco ou converter pele em buracos.

## Alteracoes desta rodada

- `portrait_image` no gerador corrige paleta/mask; testes artificiais verificam
  RGB por indice proprio, preto opaco, slot de roupa, FX livre e alpha exportado.
- `fight_hud_motion.h` separa apresentacao da energia real. Teste C executa o
  codigo real e verifica simetria dos cantos, separacao estrela/combo, monotonia,
  chegada a zero, maior velocidade inicial e recarga durante descarga.
- `fight_hud.c` usa essas regras, reinicializa caches entre entradas e mostra
  SUPER enquanto energia real >=3000. Alterna tiles existentes a cada 12 ticks,
  sem piscar a linha inteira de paleta. Mensagem usa fonte autoral do pacote.
- Conversor HUD acrescenta seis tiles de texto SUPER, sem alterar offsets dos
  tiles anteriores. Acrescimo: 192 bytes de pixels residentes; budget da cena
  completa ainda exige medicao. Dois fundos nao ganham uma linha de paleta extra.
- Copia de prova em `rascunho/processado/hud_review_2026_09_25/build_project`.
  Fonte 9000,0 corrigida em `portrait_palette_fixed.png` no diretorio pai.

Os testes da branch principal passaram: 73 passed, 0 failed, 0 skipped em
36.80 s. Isso corresponde aos 70 anteriores + 3 novos; nao confundir com os
74 do outro worktree de integracao do piloto.

A sincronizacao final inclui `portrait.png`, todos os 19 PNGs do HUD,
`hud_gen.h` e `hud_conversion_report.json`. O recibo historico v1 cobre a
primeira etapa; `integration_receipt_v2.json` registra os PNGs finais com hash
e a identidade da ROM observada. O manifesto de proveniencia manteve
`placeholder`, registrou a correcao de paleta; auditoria retornou `OK`,
125 simbolos visuais e zero bloqueios.

## Evidencia de ROM e limites observados

- ROM normal isolada: SHA `f5eb26a3b057c3439c344aa9d8863386dc6eb9662dc3f20ebe7356aee0b62d1d`,
  bundle `out/hud_review_2026_09_25/normal/blastem-linux-20260925T144223Z-420049`.
  Screenshot + SRAM + VDP dump selados mostram retrato corrigido, barras em
  cantos e combate. Snapshot da janela BlastEm: 59,4 fps; nao e taxa sustentada.
- ROM de prova `MG_TEST_HUD_REVIEW`: SHA `24183495bb4e43fefbc3447ca53db9bb05cfd24773e1bc0128b8ec75e75ba871`,
  bundle `out/hud_review_2026_09_25/probe/blastem-linux-20260925T144644Z-432661`.
  Ela **forca** energia 3000/0, uma vitoria e combo 12 nos dois lados, para
  isolar estados visuais. As capturas mostram duas estrelas completas, `12 HITS`
  sem lixo de tile e `SUPER` sobre cada barra cheia. O teste nao prova que esses
  estados surgem naturalmente na mesma luta. Snapshot da janela: 56,2 fps;
  a sonda altera carga e nao pode ser comparada diretamente com a ROM normal.
- Um frame inicial do burst exibe so parte do `SUPER` P1. Pode ser captura na
  transicao de tiles ou oclusao de sprite; a causa nao foi isolada. Sequencia
  posterior exibe o texto completo. A legibilidade sob poses que encostam no
  rodape permanece `needs_review` antes de aprovar a arte final do HUD.
- O VDP dump informa ate 10 sprites/linha (normal) e 16 (probe), mas nao exporta
  a soma de **pixels** de sprites por linha nem DMA. Portanto budget combinado
  e 60 fps constantes seguem sem aprovacao.
- A validacao completa de recursos foi executada apos a sincronizacao.
  Resultado: **14 erros, 20 avisos, 123 recursos verificados**, exit 1.
  Onze erros `VDP_SPRITE_LIMIT` sao em sheets Ken/FX legados (inclusive
  `g42`, `g270`, `g272` e cinco `g8000_*`); os tres restantes sao
  `BLOCKING_STATUS`. Nenhum erro tem recurso HUD como alvo. Metodologia
  `critical_motion` continua bloqueada por evidencia perceptiva; o res graph
  e a reconciliacao de claims tambem bloqueiam entrega. Nao se usa build verde
  como substituto desse validator.
- O primeiro PNG corrigido mantinha RGB digital 0..252, que passou pelo build
  mas falhou no `forge_art.pixel_contract` por estar fora da grade de autoria.
  A exportacao final do retrato consulta `forge_art/vdp_color.py` e usa grade
  `0x22` + marcador magenta `#EE00EE` no indice 0. Indices de pixels e mascara
  alpha nao mudaram. `pixel_contract --validate` devolveu `technical_candidate`,
  4 bpp, PLTE 16, sete cores visiveis, zero blockers. Isto nao e aprovacao
  de moldura ou qualidade do rosto.

## Moldura: candidata ainda nao final

`portrait_frame_concept.png` e fonte gerada a partir da referencia fornecida.
Falhou no contrato nativo: 1254x1254 e 100545 valores RGBA distintos, apesar do
pedido de grade logica 32x32 e oito cores. Ficou `concept_only_not_native_pixel_art`.
Nao foi reduzida e promovida por parecer pixel art. O retrato corrigido conserva
a arte pequena original; moldura e refinamento/dithering continuam pendentes de
autoria nativa e comparacao 1x. Registro em `art_status.json`.

## Rastreamento dos efeitos questionados

- `g6800_fx.png`: animacao AIR 6800, 22 elementos no pacote inspecionado.
  Disparada por Explod no Statedef 6600, Power Charge: time 0, 21, 43 ...373,
  posicao -70,-160. O estado adiciona energia e termina ao soltar comandos
  `hold_b`/`hold_y` ou atingir 3000. Precisa de teste de entrada real e captura;
  existir na exportacao nao prova visibilidade durante esse comando.
- `g8000_0_fx`, `g8000_1_fx`, `g8000_p1_0_fx`, `g8000_p1_1_fx`,
  `g8000_p2_fx`, `g8000_p3_fx`: partes/sheets da animacao AIR 30100, grupo 8000
  (16 elementos no pacote atual). O Statedef 12000 inicia SuperPause com
  `anim=S30100` e posicao -3,-48. Nome p1/p2/p3 de partes nao significa jogador.
- `doc/hud/p3_ring_multiplex_memo.md` documenta estudo, nao implementacao:
  alternativa de 16x16 chegou a 21 sprites/linha; recomendacao NO-GO.
  Reabrir apenas com medicao simultanea de quantidade E pixels por scanline,
  DMA, CPU, animacao e ambos os lutadores. Flip nao reduz automaticamente
  quantidade de sprites desenhados na linha.

## Ordem recomendada para cenario e audio

1. **Consolidar baseline:** conciliar PR21, piloto e HUD em uma branch de
   integracao; preservar hashes e anotacoes humanas. Reexecutar testes na
   combinacao, sem transportar capturas de outra ROM.
2. **Performance antes de mais carga:** matrix Stage3 informa 250/1200 acima
   do budget; probe FIREBALL informa 957/1200 e CPU max147, mas e ROM de teste
   diferente. Nao comparar diretamente nem concluir que a pose causou regressao.
   Medir cena pesada com audio real, mesma janela/inputs, carga do medidor e
   pressao de DMA/scanline. Separar FPS do emulador, progresso da simulacao e
   duracao dos frames capturados.
3. **Paleta global:** continuar migracao das familias para a linha do lutador.
   Checkout principal medido: 23/15; piloto isolado informado: 24/15, ambos
   reprovados em seus respectivos estados. HUD ainda usa PAL0 9..15 no runtime atual;
   contrato PAL3 e destino, nao estado implementado. Liberar PAL0 para Suzaku
   exige concluir esse ownership e testar restauracao de super/raio/flash.
4. **Suzaku estatico com qualidade:** abrir fonte DEF/SFF, escolher enquadramento,
   horizonte, linha do pe e arquitetura medida; nao herdar o numero de camadas
   do arcade. Redesenhar tiles/modulos para VRAM medida com lutadores+HUD+FX.
   Aprovar silhueta do castelo, paleta e leitura dos lutadores antes de animar.
5. **Camera:** ja existe ponto medio dos jogadores, clamp ao palco e limite
   de 4 px/tick. Falta contrato de dead zone/bounding box e testes de corner,
   troca de lados, salto, empurrao e limites com hitboxes. Movimento suave nao
   pode empurrar artificialmente lutador ou mudar alcance de golpe.
6. **Parallax e chao:** tres faixas visuais nao implicam tres planos de fundo
   independentes. Planejar BG_A/B, WINDOW e divisao vertical por faixas. Tabela
   por linha com velocidade crescente em direcao ao rodape, horizonte estavel
   e coordenadas inteiras finais. Linhas 25/26 de BG_A pertencem ao HUD atual;
   manter scroll zero nelas e verificar o espaco do chao. Medir degrau seguinte
   de detalhe/residencia antes de fechar o budget.
7. **Vida ambiental:** nuvens, placas e raio entram por eventos/timelines,
   com owner unico de CRAM e restauracao exata apos super, KO e transicao.
   Ciclos de quadros nao sao interpolacao; variar fase nao exige duplicar arte.
   Objetos destrutiveis entram somente se fizerem parte deste palco/GDD.
8. **Audio:** primeiro inventariar fonte musical, driver e mixagem. A conversao
   atual de vozes usa XGM2/13300 Hz; isso nao certifica qualidade nem implica que
   toda musica deve virar PCM. Avaliar clipping, aliasing, cortes/roubo de canal,
   vozes sobre musica e custo CPU/DMA/Z80 na cena pesada. Captura disk nao equivale
   a escuta aprovada; qualidade "cristalina" exige comparacao auditiva.

## Criterios de aceite da proxima integracao

Mesma ROM em todos os artefatos: rosto legivel em 1x, mascara correta, moldura
autoral aprovada, estrela inteira junto a combo de dois digitos, barras simetricas,
SUPER legivel nas fases do flash, descarga espelhada sem alterar gasto real,
HUD restaurado apos super e round. Depois: percurso de camera ate ambos os
corners, chao sem costura/HUD arrastado, planos sem vazios, restauracao de paleta,
audio ouvido e budgets medidos. Nenhuma aprovacao AAA nesta rodada.

## Fechamento tecnico desta rodada (2026-09-25)

- ROM isolada final SHA-256 `f5eb26a3b057c3439c344aa9d8863386dc6eb9662dc3f20ebe7356aee0b62d1d`, identica ao bundle BlastEm `out/hud_review_2026_09_25/normal/blastem-linux-20260925T144223Z-420049/`. A sonda de estado do HUD usa ROM separada `24183495bb4e43fefbc3447ca53db9bb05cfd24773e1bc0128b8ec75e75ba871`, em `out/hud_review_2026_09_25/probe/blastem-linux-20260925T144644Z-432661/`; nao comprova gameplay natural, FPS sustentado ou audio.
- Os 19 PNGs finais do HUD foram sincronizados da compilacao isolada; `rascunho/processado/hud_review_2026_09_25/integration_receipt_v2.json` registra os hashes. Todos passaram no `pixel_contract` como `technical_candidate`, sem blockers. O retrato usa PLTE no grid autoral 0x22, transparencia do indice zero e mascara do sprite fonte.
- `validate_resources` anterior encontrou 14 erros e 20 avisos em 123 recursos: 11 limites de sprite preexistentes e tres status bloqueados. Nenhum recurso `mg_hud` causou erro; o gate global permanece reprovado. O retrato precisa de moldura nativa desenhada e avaliacao estetica; a imagem gerada em alta resolucao e apenas conceito.
