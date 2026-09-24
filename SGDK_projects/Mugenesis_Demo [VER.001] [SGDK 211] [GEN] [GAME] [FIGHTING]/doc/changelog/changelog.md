# Changelog Canonico - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## 2026-09-24 - Etapa 3 (v2): shake + flash sob a REGRA 1 (capturas BlastEm pendentes)

- Trazido do WIP 29d99535 para a main atual.
- Flash com **tabela de swap pre-declarada** por lutador (REGRA 1c), montada no inicio da luta.
- **Bug corrigido:** o flash passava um buffer de PILHA ao `PAL_setColors(..., DMA_QUEUE)`. O SGDK so copia no VBlank, entao a fonte ja estaria morta.
  - O stub do host agora enfileira o ponteiro e copia no `host_vblank()`, depois de sujar a pilha.
  - O mutante com buffer de pilha reprova.
- **Oraculo independente:** as 15 cores exatas em todo acerto, inclusive o 2o golpe dentro do hitshake (88 re-disparos).
- **Contrato testado:**
  - PAL0/PAL3 intocadas (35 708 quadros);
  - nunca trava (401 quadros de hitstop);
  - 14 acertos de projetil a mais de 120 px;
  - troca de round/KO devolve a paleta exata (32);
  - superpause dirigida.
  - Mutantes (spill em PAL3, congelar na superpause) reprovam.
- **Limites:** a ausencia de spill em projeteis so se decide com os FX migrados para a linha do lutador (hoje eles estao em PAL3). O runtime nao tem pausa de jogo, so hitpause/superpause.
- Base `9530c0a1` = 5,8% (70/1200). ROM so com flash construida (`595116bc`). Capturas adiadas por memoria do host (1,0 GiB livre).
- Suite: 70 testes.

## 2026-09-24 - Fusao sem perda 6 -> 1 aplicada + pacote do piloto de FX (hadouken)

- **Conversor:** funde slots de corpo com a mesma palavra VDP em TODAS as variantes (padrao ligado; `--no-merge-slots` desliga).
  - Ken: 6 -> 1; o indice 6 fica livre para efeito.
  - Prova: 0 divergencias em 772 704 pixels opacos x 12 variantes (67 sheets de corpo) + retrato (75 px movidos).
- **Bug pego no caminho:** a sombra escolhia o slot mais escuro e caia no slot liberado (palavra 0x000 = preto).
  - Agora slot livre e explicito, nunca "palavra 0".
  - Testes + mutante.
- **ROM** `9530c0a1...`: 5,8% (70/1200); pico de CPU 145, 10 sprites/linha, 288 px/linha. Antes: 5,7% (68). Os tiles mudam de conteudo, e o dedup/DMA pode variar.
- **Proveniencia:** a reconversao apagaria notas escritas a mao no manifesto e no audio; essas mudancas foram revertidas.
- **Pacote do piloto:** `fx-pilot`, em `doc/mugen/fx_pilot_hadouken/` (brief, contrato de quadros, papeis da paleta, orcamento, catalogo de FX, hashes). Pixels ficam fora do Git.
- **Achado:** a paleta de efeitos compartilhada leva o nucleo preto do hadouken a vermelho (216,0,0) e colapsa 5 azuis em 1.
  - O `current_md` do pacote e referencia a NAO seguir.
  - Sem correcao na linha antiga: os efeitos migram para a linha do lutador.
- **Revisao do PR #20** (`followup_pr20_b54a82db.md`):
  - transparencia da fonte so no indice 0;
  - limites numericos do orcamento (26 tiles, 2 HW), com o texto do brief gerado deles;
  - catalogo com a FONTE das 15 familias. Hadouken: 58,7% dos pixels visiveis mudam > 10 dE hoje; preto -> vermelho com dE 102,7.
- Suite: 68 testes.

## 2026-09-24 - REGRA 1: contrato de paletas + validacao no conversor (migracao aguarda arte)

- Contrato: PAL0 cenario, PAL1/PAL2 lutador (corpo + efeitos), PAL3 HUD; emprestimos declarados (fundo de super na linha do cenario; flash na linha do lutador).
- `palette-check`: reprova personagem com mais de 15 slots; excecao so com `--waiver` registrado. 3 testes; suite 56.
- **Correcao pos-parecer:** o medidor decodificava a palavra VDP com a mascara errada (branco = 109). Agora usa `vdp_rgb` do conversor, com vetores de hardware em teste.
- Ken, exato: 14 classes de corpo (8 estaveis + 6 de roupa); os slots 1 e 6 sao iguais em todas as variantes (fusao sem perda, verificada) -> 1 slot livre; efeitos com 9 cores sem par.
- Necessidade exata: **23 de 15**. Orcamento realizavel do piloto: 8 + 6 + 1.
- Remap automatico dos efeitos para as cores do corpo: dE 20,7 e 67% dos pixels > 10 dE (descartado).
- Waiver registra mas nao aprova (rc=1); entrada invalida da rc=2. Suite: 62 testes.
- Opcoes registradas; prioridade do usuario: reautoria dos efeitos por agente grafico dedicado.
- Dimensao avaliada: x 5/6 (proporcao CPS2) = -17% no maior quadro e -14% na soma. So medicao; pixel final exige redesenho.
- Registro: `doc/mugen/palette_contract_rule1.md`. O memo do Suzaku foi atualizado (PAL0 compartilhada, VRAM 180/452). Nada foi migrado e nenhuma cor foi cortada.

## 2026-09-24 - Dieta de VRAM da luta + especial compacto no rodape (REGRA 2)

Todas as medicoes usam a janela fixa de 1200 quadros (sonda corrigida, trazida da etapa 3).

- **Reserva do corpo: 147 -> 102 tiles por lutador** (o maior sheet de CORPO, nao o de efeito).
  - Em 8 lutas no host (normal + energia cheia), nenhum sheet de efeito caiu no slot fixo (35 sheets).
  - Uma guarda manda um sheet maior ao pool em vez de transbordar; teste proprio, e o mutante sem a guarda reprova.
- **Fundo de super carregado so no super** (emprestimo da regiao que sera do cenario).
  - ROM roteirizada com KO por super: pico de CPU 253 -> 263 no quadro do upload; quadros acima do orcamento iguais (730/1200).
  - O fundo 730 aparece correto (burst `ko_diet_vis`).
- **Especial (REGRA 2):** 5 tiles por lado (1/3 dos 14), centrado no rodape, em BG_A linha 26 (y 210-215).
  - Na captura, a sombra/pe mais baixo fica em y 204, sem sobreposicao.
  - O WINDOW perde 28 celulas (a linha 3 ficou vazia).
- **VRAM livre para cenario: 90 -> 180 tiles** (452 com o emprestimo do fundo de super). ROM `2aaf1830...`.
- **Luta normal: 5,5% -> 5,7%** acima do orcamento (66 -> 68 de 1200); pico de CPU 144, 10 sprites/linha, 288 px/linha, iguais.
- **Achado preexistente (main tambem):** no super, 424 px/linha e 128 quadros acima de 320 px -- sprites cortados em linhas. Nao mexido aqui.

## 2026-09-24 - E4.0: Suzaku Castle (SSF2) -- intake, parser, medicao e memo: NO-GO para inclusao direta

- Intake: `rascunho/entrada_bruta/ssf2_01_ryu.zip` (sha256 d781b8d5...), inventario versionado, registro em `project_hygiene_manifest.json`.
- Parser de stage (`parsers/stage.py`): [BG] normal/parallax/anim, [Camera]/[PlayerInfo]/[Bound]/[StageInfo]/[Shadow], [BGCtrlDef]/[BGCtrl] e as [Begin Action]. 0 avisos no .def real.
- `stage-measure`: medicao por camada e por plano composto, mais o orcamento real da luta lido da ROM (`6bbef58a...`).
- Numeros: o stage pede ~1280 tiles e 56 cores. A luta deixa 90 tiles e 8 cores (PAL0 1-8). O stage congelado em 320 px ainda pede 708 tiles.
- O briefing nao batia com o .def: 10 secoes (nao ~23); 320x240 (nao ha 384->320; o corte e vertical); nao ha bandeira nem chamas.
- Memo: `doc/mugen/stage/e4_suzaku_viabilidade.md`. Suite: 52 testes.

## 2026-09-24 - Q3: indice de intake MUGEN -> owners

- `python3 -m mugen2sgdk_forge intake-index` gera `doc/curation/mugen_intake_index.{json,md}` a partir do registro de licoes + parecer mais recente.
- Cada linha: licao, fonte@commit, blob sha1, owner resolvido contra o repo, status, proxima acao. O indice nao guarda status proprio nem promove nada.
- `--check` reprova indice desatualizado, owner inexistente e promocao sem `canonized_in`. Estado atual: 12 licoes, 0 problemas. Suite: 43 testes.

## 2026-09-24 - Q2: regressao focal do SuperPause

- Personagem sintetico (sem terceiros), com valores distintos por parametro, compilado e executado no host.
- Verifica o espelhamento do X com facing -1, os ticks exatos de pausa e movetime, o dono, o power e qual som tocou.
- Mutacao de indice ou do espelho reprova o teste. Suite: 41 testes.

## 2026-09-24 - Q1: proveniencia no schema canonico + falso positivo do neg1_masks

- O conversor gravava enums fora do schema, e o manifesto inteiro invalido gerava 125 "sem proveniencia" falsos.
- Agora: procedural_composed_from_authored + placeholder + hash do pacote + licenca NAO verificada, por simbolo.
- O auditor segue o array ate o destino (chamada VDP/DMA, tipo grafico SGDK, campo de struct -> usos).
  - Tabela logica: informativa.
  - Pixel renomeado ou nao resolvido: continua bloqueando.
- Auditoria do projeto: rc=0, sem bloqueios. As outras 17 arvores nao tem arrays desse tipo (sem mudanca).

## 2026-09-24 - Etapa 1: desempenho com audio real (29,3% -> 8,5%)

- Captura com audio real (disk). O denominador pos-warmup agora e exportado; o quociente bruto antigo subestimava.
- Sonda: px por linha (limite de 320 em H40) e varredura so nas fronteiras; o laco antigo custava ~10% do quadro.
- VM: frente leve para constantes e var(n); pilha por ponteiro. O trace do host e identico (md5 b47cfeef...).
- Maximos: 10 sprites e 288 px por linha. PCM real custa ~4 pontos. Nenhum efeito visivel removido.

## 2026-09-23 - P6: catalogo de 180 efeitos registrado (consultivo)

- Aderencia avaliada: 10+ ja em uso com ROM citada, 7 candidatos priorizados, eixos fora de escopo justificados. Nada implementado.

## 2026-09-23 - P3: memo de multiplexacao dos aneis (NO-GO)

- Medido: pior quadro de anel 107 tiles / 3,4 KB DMA; simulador 16 sprites/linha (ok).
- Multiplex 16x16 estoura (21/linha); 32x32 fica perto do limite (18) e perde fidelidade. Nada implementado.

## 2026-09-23 - P5: sombra pontilhada sob o lutador (memo comparativo)

- Memo: doc/hud/p5_shadow_memo.md (dither x flicker x blinking x Shadow/Highlight, com custos medidos).
- Vencedora: dither em sprite 32x8 (+1 sprite/lutador, 0 paleta, 4 tiles, 0 DMA/quadro); estouro residual
  0,20% tratado por prioridade (sombra descartada primeiro), nao por flicker.
- Forma DERIVADA da silhueta 0,0 do Ken (technical_candidate, aprovacao visual pendente).
- ROM 46a9cd65...: 27,0% acima do orcamento (faixa 23-27% entre capturas).

## 2026-09-23 - P4/P4.1: HUD de luta (arte SFA2 Lifebars convertida)

- Vida amarela drenando com fantasma vermelho (estilo SF), especial azul (mesma arte, cor por paleta),
  tempo, retratos 9000,0, vitorias, "N HITS" junto de quem comba (ancora de evento do P1), ROUND n /
  FIGHT! / K.O. / TIME OVER / DRAW. HUD some durante o fundo de super (nobardisplay).
- Contrato, medicoes e decisoes: doc/hud/p4_hud_contract.md. `convert-hud` no mugen2sgdk_forge.
- ROM b138fb35...: 23,1-26,2% dos quadros acima do orcamento (baseline 22,6%); HUD ~3% do quadro.

## 2026-09-23 - P2: rampas de roupa mais vivas (medidas antes de ajustar)

- Achado: saturacao ja era maxima; defeito real = brilho baixo + degrau colapsado + pouco contraste.
- Alvos T1-T4 e metodo em doc/mugen/p2_palette_calibration.md; `convert-char --vivid-clothing`.
- Turquesa (P1): V 0,85/0,56 -> 0,99/0,71, deltaE 50 -> 63. Vermelho (P2): degraus 5 -> 6, deltaE 90 -> 97.
- Evidencia BlastEm: ROM 5690eafe... (antes 38a67c94...). Desempenho inalterado.

## 2026-09-23 - P1: faiscas ancoradas no ponto de contato + variacao em combo

- Faisca nasce no centro da intersecao Clsn1 x Clsn2 que registrou o acerto (antes: borda frontal do
  defensor + sparkxy, regra MUGEN). Divergencia deliberada, declarada.
- Combo na mesma regiao (relativa ao corpo do defensor, <=16 px, <=90 ticks) percorre 4 variacoes
  sutis (0,0) (+3,-2) (-3,+2) (+2,+3).
- Teste: tests/test_host_runtime.py::test_hit_sparks_anchor_on_contact_and_vary_in_combo
  (alto y~-78 vs baixo y~-6; variacoes 0,1,2,3,0).
- Evidencia BlastEm: ROM de teste f1f4df6a... (-DMG_TEST_SCRIPT -DMG_TEST_COMBO), sessao
  out/mugenesis_evidence/p1_sparks/blastem-linux-20260923T184801Z-674202.
- Desempenho (ROM normal 38a67c94..., CPU x CPU): 860/3811 quadros acima do orcamento = 22,6%
  (antes 23%), pico 159%. Sem regressao.

## 2026-09-23 - Efeitos de super completos (anel, bola de fogo super, fundo de vitoria)

- Quadros grandes divididos em ate 4 sprites; fundo de super em BG_B com animacao de paleta; Helper reduzido.
- Corrigido deslocamento de indice de parametros (SuperPause/PlaySnd).
- ROM ce783a61...; desempenho: 23% dos quadros acima do orcamento (E3b pendente).

## 2026-09-23 - E3: Ken convertido do MUGEN rodando no BlastEm

- Cena de luta hospeda o runtime generico mugen2sgdk_forge; boot direto na luta (MG_DIRECT_FIGHT).
- Ken Masters ADV convertido: 81 sheets, 12 paletas, 33 sons (214 KB), 796 controladores
  (702 diretos, 72 aproximados, 22 sem suporte, todos com motivo no relatorio).
- CPU ativa comandos do .cmd (como a IA do MUGEN); P1 vira CPU apos 5 s ocioso (demonstracao).
- Evidencia BlastEm selada para a ROM da354830...; desempenho ainda acima do orcamento em 16% dos quadros.


## 2026-09-23T01:30:22.2602857Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia
