## 2026-09-26 — Retomada de fidelidade ao Suzaku original

- Direcao vigente: preservar pixels/composicao DEF/SFF; conceitos V1–V16 ficam historicos. Plano: `doc/mugen/suzaku_source_fidelity_recovery_2026_09_26.md`.
- Auditoria offline com hashes e self-check7/7: quinze cores proprias melhoram erro RGB; PAL3 compartilhada e condicional, nao adotada. 446 tiles e teto da alocacao historica, nao do VDP. Camera e movimento autonomo do ceu exigem reconciliacao.
- Corrigido arredondamento divergente de `stage_measure` usando `vdp_word`; novos testes reproduzem defeito antes da correcao. Suite completa do conversor: 133 passed. Relatorios historicos de cores nao foram revalidados automaticamente.
- Nenhum novo asset promovido, build ou gate visual/runtime fechado. Arte e cena continuam pendentes; metricas offline nao aprovam qualidade.

## 2026-09-26 — Experimentos de backdrop e reutilização do piso

- Avaliada a economia de paleta: a skill visual já cobria compartilhamento e
  direção de rampas, mas faltava explicar o backdrop. As skills canônicas agora
  documentam que `VDP_setBackgroundColor` escolhe um índice CRAM global 0..63;
  não recebe RGB nem carrega uma cor. O budget separa CRAM, tiles, mapas,
  residência e DMA, e exige verificar planos inferiores e o empréstimo PAL0 do
  super.
- V15 (índice 0 no céu e backdrop CRAM[3]): reconstrução RGB exata, mas ResComp
  subiu 915→924 tiles e a pior janela 543→547. Não há economia neste candidato.
- V16 repete um módulo de piso 64x8 já existente: 846 tiles/29.624 bytes,
  pior janela de 42 colunas 510. Reduz 33 tiles da janela de V13, porém supera
  em 64 a estimativa histórica de 446. A cadência visual repetida aguarda review.
- Criado mock V13/V16 para leitura de composição em três câmeras; é montagem
  estática. Arte permanece em staging, sem `res/`, runtime ou ROM. Relatório e
  limites em `doc/mugen/suzaku_candidate_review_2026_09_26.md`.

## 2026-09-25 - Sonda VRAM sob dois lutadores e registro de arquitetura Suzaku

- ROM test-only `37fd9eb8...44ac11` mediu allocator em BlastEm: pool600, minimo247 livres, maior bloco72, pico11 sprites, zero falhas em 2.941 amostras. Dois Ken max-power; sem stage; audio dummy. 116/1200 quadros acima do budget; 59,9 fps e snapshot, nao desempenho sustentado.
- Criados `doc/mugen/vram_residency_probe_2026_09_25.json` e `stage_architecture_record_2026_09_25.json`; o segundo mantem paired resident, streaming e flat como rotas nao-promovidas. O piso repetitivo 32px continua rejeitado.
- AI concept do castelo foi identificado como `concept_only`, painterly e fora do runtime; provenance registrado em `doc/art/stage_concept_provenance_2026_09_25.json`. O stage continua vindo do pacote MUGEN privado; nenhum asset foi adicionado a `res/`.
- Suite/conversor e assets de producao nao foram alterados nesta etapa de registro.

## 2026-09-25 - Paridade Hadouken aprovada e sonda CRAM PAL1 observada

- O usuario confirmou que a estrategia de cinco pixels perifericos + divisao em recortes 24x24/32x32 foi bem-sucedida e manteve a paridade visual. A aprovacao permanece hash-bound a `750,1`, SHA `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`.
- O build corrigido atribui o slot 6 `0xE82` a PAL1/PAL2 nas 12 variantes. ROM candidata normal SHA `52311f4f84d37887cecbe766055bff236794f073d3997f8c53355eacf11912aa`; ROM de evento SHA `794dd6e8ffbf45f96cb744dd2cbfe19730bcddba7dc9c304e307376db0ff4398`, vista no BlastEm com bundle selado `out/mugenesis_evidence/hadouken_750_1_palette_corrected/blastem-linux-20260925T115621Z-3988558`. Frames 64/66 mostram o projétil azul; 75/76 mostram a aproximacao e a transicao para flash depois que ele desaparece.
- Para isolar o compartilhamento de CRAM, uma ROM test-only dispara o Hadouken, injeta `flash_lvl[0]=3` quando o projetil esta ativo e congela a simulacao mantendo a renderizacao. BlastEm observou a mesma ROM SHA `9ce731d5ba7d48d69e277f3116b198c55a7522fc37136fd641ff4b3f35efd46c`, bundle `out/mugenesis_evidence/flash_projectile_cram_probe_frozen/sessions/blastem-linux-20260925T130718Z-45717`. SRAM em `0x1F00` registra `CRAM 02 01 00 49` (flash level 2 apos render, projetil ativo, nao removendo). O screenshot mostra corpo P1 e projetil na mesma PAL1 clareados juntos; P2 permanece normal.
- A sonda prova somente o efeito visual de CRAM partilhada sob flash forçado; nao executa HitDef nem prova impacto natural simultaneo, timing/cadencia de gameplay ou performance. Stage 3 shake foi desativado nessa ROM para isolar a paleta; audio dummy, performance claim `unproven`.
- Aprendizado local foi atualizado para curadoria futura em `doc/agent_learning/success_patterns.md`; `audit_project_learning.ps1 -Mode Capture/Audit` deve atualizar o ledger antes do closeout. Nenhuma promocao canonica automatica (`canonical_promotion_performed=false`). `palette-check` segue FAIL em 24/15; auditoria de proveniencia integrada: 127 simbolos/0 bloqueios; hygiene: 0 bloqueios apos limpeza; `validate_resources`: 12 erros/20 avisos. Suite da worktree principal: 70 passed/0 failed/0 skipped, asserts intactos e escopo separado da copia integrada temporaria.

- Fechamento da cópia integrada: suíte completa no worktree PR21+PR22 passou 74/74, 0 skips. As três chamadas do `build_host.sh` foram adaptadas para `bash` por modo git 100644; o teste estrutural agora confirma explicitamente o estado pós-piloto 15 índices/9 classes estáveis/6 variáveis e preserva FAIL 24/15, sem relaxar asserts. A suíte de baseline na workspace principal (70/70) permanece um escopo separado.
- O helper de integração foi reaplicado duas vezes e retornou `already_applied` em ambas; SHA dos seis arquivos de saída (res, C, manifesto, paleta e dois sheets) permaneceu idêntico. `integration_idempotence` e o resultado 74/74 estão no relatório de integração. Capture/Audit local resultou em 48 lições e 30 candidatos, sem warnings ou blockers; a proposta `lesson_9e62ed31b1a9f329` exige revisão humana. A aprendizagem permanece local para curadoria futura; nenhuma promoção canônica ocorreu.

## 2026-09-25 - Suite completa apos integracao isolada do piloto

- `python3 -m pytest tools/mugen2sgdk_forge/tests -q -ra`: 65 passed, 9 failed, 0 skipped na worktree de integracao. Oito testes de runtime host nao iniciaram porque `tests/host/build_host.sh` tem modo versionado 100644 e o runner o executa diretamente. Um teste estrutural de Ken esperava 14 indices de corpo ja aplicados; o `palette-check` atual mede 15 indices e uma remapacao candidata 15->6 (14 classes depois da fusao). Nenhum teste/assert foi alterado ou ignorado; falhas e diagnósticos em `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.

## 2026-09-25 - Hadouken: limites de paleta e probe de sobreposicao

- palette-check no Ken segue FAIL: 14 classes de corpo, 8 slots estaveis, 6 variaveis e 9 cores de FX sem gemeo estavel; necessidade 23/15, excesso de 8. O piloto Hadouken aprovado nao resolve as outras familias.
- Revisao do contact sheet e preview temporal confirma que o AIR candidato mantém 8 elementos e 3 vazios, mas a aprovação humana continua vinculada apenas ao SHA 750,1. Nenhuma outra pose foi promovida a res/.
- Duas capturas BlastEm dedicadas à sobreposicao flash+projétil foram inconclusivas: `blastem-linux-20260925T111012Z-3803658` (ROM `b16dafef...`) virou combo corpo a corpo; `blastem-linux-20260925T111400Z-3817781` (ROM `7705fe58...`) mostrou contato/2 hits sem o projétil. Encerrado esse ciclo após duas tentativas. Interacao CRAM nao provada; proxima tentativa depende de gatilho de projetil deterministico, sem novo chute de timing. Relatorio: `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.

## 2026-09-25 - Primeira observação Hadouken 750,1 (captura supersedida)

- O teste isolado do candidato aprovado foi buildado sem defines de entrada (ROM SHA `18e14682263e4ce6acbd475d451e3cbdde63fbf2d1c29a0ac795e9060f85fca8`) e observado em BlastEm por ROM de teste separada com `MG_TEST_SCRIPT`/`MG_TEST_FIREBALL` (SHA `68d3ee9064f1f14097aaa947fa52b0d5f58885313ffa8bba91438b20657beb24`). Bundle selado: `out/mugenesis_evidence/hadouken_750_1_fireball/blastem-linux-20260925T103514Z-3548982`; quadros 60 e 61 mostram a pose 750,1 aprovada e o projétil em voo, preservando a leitura visual aprovada.
- Resultado registra aprendizado local: edição mínima de cinco pixels + decomposição em 24x24/32x32 atingiu 25 tiles/2 sprites e manteve a paridade aprovada; a captura confirma o evento em ROM. Lição local ficou qualificada como E3_blastem em audit_project_learning (47 lições/30 candidatos); generalização segue limitada e nenhuma skill canônica foi alterada (canonical_promotion_performed=false).
- Limites: apenas o quadro 750,1 está aprovado; não aprova as outras poses AIR. Captura de burst 90 frames, áudio dummy e CPU acima do budget em 897/1200 amostras da ROM de teste; sem claim de 60 fps sustentado ou qualidade de áudio. Medição da cena com a integração candidata e gate perceptivo completo continuam pendentes. Nenhuma alteração foi promovida à ROM principal.

## 2026-09-25 - Hadouken 750,1: teto 26/2 atingido em staging

- Busca geometrica confirmou minimo de 28 tiles/2 sprites para o candidato indexado sem alteracao de pixel. Uma variante de baixo impacto remove cinco pixels de brilho periferico do indice 6; preserva 1149/1154 pixels opacos e a celula 56x32. SHA-256 `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`.
- Dois recursos `SPRITE` em staging, posicionados em `(0,4)` e `(24,0)`, compilam no ResComp 3.95 com 9 e 16 tiles, um sprite de hardware cada: **25 tiles/2 sprites** simultaneos. A recomposicao das duas partes e pixel a pixel identica a variante; os tres PNGs passam `forge_art.pixel_contract`. Comparacao 1x/4x, fontes, hashes, assembly e limites em `doc/mugen/fx_pilot_hadouken/budget25_split_report.json`.
- O usuario aprovou a variante visualmente com paridade em relacao a pose aceita; aprovacao vinculada ao SHA e comparacao no `budget25_user_approval_2026_09_25.md`. Integracao de runtime, custo da cena completa e evidencia BlastEm continuam pendentes. Nenhum arquivo de producao em `res/` foi modificado nesta retomada.

## 2026-09-25 - Captura de aprendizado e gate de proveniencia do piloto

- `audit_project_learning.ps1 -Mode Capture` atualizou o ledger local para 47 licoes e 30 candidatos. A nova estrategia entrou como `promotion_candidate` local, encaminhada a owners existentes e ainda sem promocao canonica (`canonical_promotion_performed=false`).
- PR #21 continua aberta e fora da branch #22. Os quatro testes de proveniencia passaram em worktree isolada (`f3b92bb9`); isso nao integra a protecao na branch do piloto. A simulacao de merge aponta conflitos documentais de curadoria. Nenhuma reconversao ou alteracao em `res/` foi feita.
- Proximo gate tecnico: incorporar a protecao de proveniencia em worktree dedicada, reconciliar os conflitos sem perder Stage 3, repetir os testes e fazer a conversao em copia antes de integrar o piloto.

## 2026-09-25 - Hadouken AIR 750/751 staged; compiled budget conflict

- O usuario aprovou a cor compartilhada do slot 6: CRAM `0xE82`, RGB de autoria canonico `(34,136,238)`. Aprovacao registrada em `doc/mugen/fx_pilot_hadouken/slot6_user_approval_2026_09_25.md`; ela nao aprova os pixels indexados.
- Cinco candidatos indexados foram preparados em `rascunho/processado/fx_pilot_hadouken/`. O AIR conserva 8 elementos/3 vazios, tempos, offsets, eixos e hitboxes. Mascara alfa preservada e preto opaco mapeado ao indice 15.
- ResComp `BALANCED FAST`: tiles para 750,0..4 = 24/28/12/8/16; sprites = 2/2/1/1/1. O quadro 750,1 excede o teto de 26 tiles. `TILE FAST` reduz 750,0/1 a 22/26 tiles, mas usa 3 sprites em ambos. Compilacao da sequencia de 8 frames preserva os vazios e timers. ResComp `BALANCED MEDIUM/SLOW` e `TILE MEDIUM` medem 25 tiles/3 sprites; `SPRITE MEDIUM/SLOW`, `TILE SLOW` e `NONE FAST` medem 28/2. Sweep de 13 combinacoes (inclui BALANCED MAX=25/3 e SPRITE/TILE MAX=28/2) (AIR completo ou probe isolado 750,1, escopo indicado no JSON) nao encontrou combinacao que cumpra ambos os tetos.
- `palette-check` no estado de producao pre-piloto: 14 classes de corpo + 9 cores FX exatas sem gemeo estavel = 23/15 (falha por 8); SHA de fonte/manifesto em `candidate_sequence_slot6_e82_report.json`. Nao leu os assets em staging; precisa ser repetido depois de integracao aprovada.
- Comparacao 1x e preview temporal mostram o candidato mais claro e menos variado em azul que a fonte; aprovacao visual vinculada aos hashes ainda pendente. `forge_art.pixel_contract` reporta 5/5 como `technical_candidate` sem blockers; builder reproduz os cinco PNGs byte a byte em copia isolada. Os checks de pixel e cor passaram 20/20 cada, sem promover status visual. Sem alteracao em `res/`, build integrado ou captura BlastEm. Relatorios e hashes: `doc/mugen/fx_pilot_hadouken/candidate_sequence_slot6_e82_report.json`.

# Changelog Canonico - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## 2026-09-25 - Stage 3: matriz controlada fechada; bursts de impacto ainda inconclusivos

- Compiladas e capturadas em BlastEm as variantes base, flash-only, shake-only e ambas, todas com `MG_TEST_SCRIPT`, P2 parado e mesma configuracao. A mudanca em `src/mg/mg_fight.c` adiciona apenas defines de teste para excluir cada efeito; no build normal ambos seguem ativos.
- Quatro janelas MDRT fecharam 1200 amostras pos-warmup. Todas mediram 250 (20,8%) acima do budget, CPU maxima 145, 9 sprites/linha, 248 px/linha e nenhuma violacao dos limites de H40. A matriz nao mostra delta agregado entre estes efeitos sob esse roteiro; nao prova 60 fps sustentados.
- Hashes completos, flags, configuracao, sessoes, artefatos, audio sidecars e limites de interpretacao: `doc/mugen/stage3_matrix_2026_09_25.json`. Os bundles estao em `out/mugenesis_evidence/stage3_matrix/`.
- Suite inicial do branch: 70 passed, nenhum skip reportado. Apos adicionar os defines de teste, o caso dirigido `test_impact_fx_shake_on_heavy_flash_on_hit` passou (1/1); a suite completa nao foi repetida porque nao houve integracao de producao.
- `freshness_audit.ps1` executado depois das capturas: warning, 1 report stale (`validation_report`), 2 obrigatorios ausentes (`scene_contract_compile`, `res_graph`), zero errors. Os bundles individuais estao frescos; os findings sao blockers de closeout ja nao satisfeitos por este piloto.
- Folhas de contato dos bursts foram revisadas. Um burst complementar de 90 quadros na ROM `both` mostra o flash do defensor em torno dos quadros 83-85. Uma analise posterior do probe de power alto identifica deslocamento transitório do lutador/sombra contra o HUD fixo na ROM `both`; a contribuicao do shake Stage 3 continua sem isolamento de EnvShake e sem aprovacao de qualidade. Detalhes, offsets e hashes em `doc/mugen/stage3_event_probe_2026_09_25.json`.
- Uma tentativa foi rejeitada porque recebeu `rom.out` (ELF de link) em vez de `rom.bin`; o bundle preto ficou preservado como diagnostico e foi excluido das conclusoes. A captura corrigida com `rom.bin` selou sem blockers.
- O flash-only historico `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623` segue valido apenas para sua sessao separada (71/1200); nao e base nem membro desta matriz.
- Sem mudanca em `res/`, sem build integrado de arte Hadouken e sem claim de qualidade de audio ou FPS sustentado. A cor do slot 6 foi aprovada; aprovacao visual do candidato e resolucao do teto compilado continuam pendentes.

## 2026-09-25 - Probe visual de Stage 3 com power alto

- Capturas base e `both` com `MG_TEST_FULL_POWER`, mesmos parametros BlastEm, 150 quadros por burst e bundles selados. Hashes completos, flags, sessoes e limites estao em `doc/mugen/stage3_event_probe_2026_09_25.json`.
- O impacto/recoil aparece nas duas sequencias; o flash do defensor aparece na captura `both`. As sequencias nao estao alinhadas o bastante para atribuir o flash apenas por esta comparacao.
- Na captura `both`, comparacao de pose e ancora de sombra registra transiente de tela relativo ao HUD: o lutador casa com 95-98% dos pixels apos deslocamento de +4,+4 pixels da captura nos quadros 26-28; retorna/reverte nos quadros 29-31. O HUD permanece em (0,0). Isso comprova movimento visual no ROM observado; a captura base nao esta fase-sincronizada e o runtime combina shake Stage 3 com EnvShake legado, entao atribuicao exclusiva e aprovacao perceptiva seguem pendentes.
- As capturas de evento nao provam FPS sustentado nem qualidade de audio. Metodo, artefatos e hashes dos quadros em `doc/mugen/stage3_event_probe_2026_09_25.json`.
- Segunda e ultima alternativa visual do Hadouken documentada em `doc/mugen/fx_pilot_hadouken/alternative_study_2026_09_24.md`: SHA `7df530ee8a86926b9544baf28195481e4cc14ff6b4110742a423c8726a42b2b2`. O source-audit bloqueia traducao direta por motion blur; fica apenas como referencia. A pose aceita pelo usuario continua escolhida. Slot 6 e integracao seguem pendentes.

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
- Baseline reportada no handoff `9530c0a1` = 5,8% (70/1200). ROM so com flash construida (`595116bc`). Capturas pendentes no envio do PR.
- Suite: 70 testes.

## 2026-09-24 - Continuidade segura: pose Hadouken e checkpoint de captura Stage 3

- Fonte Hadouken `source_750_1.png` validada por hash, mascara e nucleo preto opaco. Anexo e copia (56x28 RGBA) coincidem em mascara e pixels visiveis; RGB oculto dos 414 transparentes difere. Aceite vinculado a hashes em `user_source_approval_2026_09_24.md`; cobre a direcao visual da fonte, nao a paleta ou integracao.
- Uma alternativa ImageGen foi arquivada em `data/raw_ai/hadouken_fx_pilot_2026-09-24/` como `visual_lab_control`. Forge-art rejeitou a fonte de IA por RGBA nao indexado, 8 bpp, dimensoes fora da grade e ausencia de contrato de index 0. A fonte original permanece selecionada.
- Estudo de catalogo com 15 familias ranqueou `0xE82`/RGB `(36,144,252)` como slot FX provisional; pior media de familia 37,4 dE. Contrato segue sem decisao de cor, sem reconversao ou integracao.
- Conversao tecnica isolada de `source_750_1.png` para candidata indexada 56x32, 4bpp e PLTE de 16 entradas, com mascara e preto opaco preservados; hash `4f9f30abcfa23dc6d7db21369d64c689d3b1d2d61764c8bfca68e57bc1a75d66`. Forge-art passa como `technical_candidate`; repeticao reproduz o mesmo SHA. A candidata usa o slot 6 `0xE82` apenas como hipotese (RGB canonico `(34,136,238)`), sem alterar `palette_roles.json`.
- Contato 1x/3x mostrou rampa mais quente e achatada que a fonte aprovada, portanto nao ha resultado melhor comprovado. AIR preview da fonte manteve 8 elementos, 3 vazios e duracoes. Estimativa estatica = 26 tiles 8x8 / 2 celulas de sprite hardware; compilado/scanline nao medidos. Workset hash-bound permite apenas auditoria, validacao pixel e conversao tecnica. Sem alteracao de `res/`, build ou ROM.
- ROM flash-only local identificada pelo SHA-256 completo `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`. Captura BlastEm `161051Z-3448566`: 71/1141 (6,2%) acima do budget, max 10 sprites/linha e 280 px/linha. Nao satisfaz 1200 quadros; burst nao observou impacto.
- Repeticao isolada `161519Z-3457713` foi rejeitada por screenshot solido preto, audio vazio e SRAM/VLAB incompletos. A/B continua pendente: existem capturas avulsas `fx_*` na raiz de `out/`, mas cada uma tem apenas 32 amostras em ROM/contador diferente; nao servem para matriz controlada de 1200 quadros. Host apos falha: 1,7 GiB disponiveis, 11 GiB swap usados; nenhuma nova execucao iniciada.
- Recheck isolado da PR21 `f3b92bb9` (sem mudar branch nem fazer merge): teste de proveniencia 4/4; suite completa 61 passed, 11 skipped (Ken/stage de terceiros ausentes). PR21 continua aberta; a protecao ainda nao esta na PR22 `7cf00ed8`.
- Preview read-only de combinacao PR22 + PR21 encontrou conflitos de conteudo em changelog e tres arquivos de curadoria (`lessons_2026-09-24_mugenesis.json`, `mugen_intake_index.json/.md`). Nenhum merge/cherry-pick foi feito; resolver depois da decisao sobre a PR21.
- Governanca do projeto: primeira classificacao inferida como `technical_demo` (teto de claim igual; mudanca futura ainda requer confirmacao humana); validadores de contexto passaram em planning/implementation. Hygiene manifest atualizado para schema vigente, sem caminho absoluto externo; hygiene passou (0 blockers).
- Claims metodologicos: `critical_motion=required` para Hadouken 750/751; road physics e modular boss fora deste piloto. Skills canonicas visual/runtime declaradas. A metodologia continua bloqueada apenas por `perceptual_motion_unvalidated` (quatro eixos sem evidencia do candidato integrado); nao foram preenchidos com sinais de ROM de outra arte.
- `validate_resources.ps1` atualizado: 12 erros, 19 warnings, 123 verificacoes; hygiene passou. Permanecem blockers de movimento perceptivo, GDD insuficiente para AAA, ponte de agentes degradada, visual delivery, audio, res graph, technique manifest, conversao/cor de tilemap, freshness e scene closeout. Os erros de raiz orphan e entrada externa foram resolvidos; sprites grandes de Ken continuam acima do limite interno indicado pelo validador.
- Recheck do host 19:47Z: PSI de memoria ainda alto (`some avg10=16,04%`, `full avg10=13,48%`), 690 MiB disponiveis no fim da medicao, 14 GiB de swap usado; nao reiniciar a captura Stage 3. O seletor BlastEm sem blockers so atesta rota/dependencias, nao capacidade atual do host.
- Host recuperado em 23:55Z (5,6 GiB disponiveis; PSI quase zero): nova captura flash-only BlastEm selada em `out/mugenesis_evidence/stage3_matrix/flash_only/blastem-linux-20260924T235547Z-112747`, ROM SHA-256 `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`. Janela MDRT exata 1200: 71/1200 (5,9%) acima do budget, CPU max 145, 10 sprites/linha, 288 px/linha; sem overflow. Screenshot/SRAM/VDP/audio presentes; burst mostrou combate/projetil, mas nao o hit flash/shake. Titulo marcou 58,4 fps sem provar cadencia sustentada. Capturas das outras tres variantes permanecem pendentes.
- Recheck operacional: preflight SGDK escolheu `linux_wine_bridge` (1 lint preexistente); seletor BlastEm escolheu `linux_flatpak_blastem`, sem blockers de rota. Memoria atual 641 MiB disponiveis / swap 13 GiB, pior que checkpoint anterior; ciclo Stage 3 permanece fechado apos duas tentativas, sem novo processo de emulador.
- Reaudit dos snapshots antigos `fx_*` no `out/` da raiz: todos sao amostras de 32 quadros em ROMs/contadores diferentes; nao compoem a matriz controlada Stage 3 de 1200 quadros. Captura flash-only local em `stage3/161051Z-3448566` segue em 71/1141 (6,2%), incompleta; segunda tentativa rejeitada permanece. Host atual apos suite: 1,3 GiB disponiveis e 14 GiB swap usados, portanto o ciclo permanece encerrado apos duas tentativas.

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

## Fechamento tecnico desta rodada (2026-09-25)

- ROM isolada final SHA-256 `f5eb26a3b057c3439c344aa9d8863386dc6eb9662dc3f20ebe7356aee0b62d1d`, identica ao bundle BlastEm `out/hud_review_2026_09_25/normal/blastem-linux-20260925T144223Z-420049/`. A sonda de estado do HUD usa ROM separada `24183495bb4e43fefbc3447ca53db9bb05cfd24773e1bc0128b8ec75e75ba871`, em `out/hud_review_2026_09_25/probe/blastem-linux-20260925T144644Z-432661/`; nao comprova gameplay natural, FPS sustentado ou audio.
- Os 19 PNGs finais do HUD foram sincronizados da compilacao isolada; `rascunho/processado/hud_review_2026_09_25/integration_receipt_v2.json` registra os hashes. Todos passaram no `pixel_contract` como `technical_candidate`, sem blockers. O retrato usa PLTE no grid autoral 0x22, transparencia do indice zero e mascara do sprite fonte.
- `validate_resources` anterior encontrou 14 erros e 20 avisos em 123 recursos: 11 limites de sprite preexistentes e tres status bloqueados. Nenhum recurso `mg_hud` causou erro; o gate global permanece reprovado. O retrato precisa de moldura nativa desenhada e avaliacao estetica; a imagem gerada em alta resolucao e apenas conceito.

## 2026-09-25 — curadoria e coordenacao da continuidade MUGEN

Pedido humano autoriza curadoria e planejamento da continuidade SGDK/SMS.
Parecer canonico por ID em `doc/curation/2026_09_25_mugen_coordination/` do
workspace: 24 instrucoes pendentes promovidas com qualificacoes; nove
formulacoes nao promovidas/corrigidas; sete aprendizados novos; cinco
promocoes anteriores preservadas. Ledger herdado nao foi promovido em bloco.
Prompts novos em `doc/prompts_modelo/prompt_mugen_sgdk_completion_2026_09_25.md`
e `prompt_mugen_sms_port_2026_09_25.md` no workspace. Escopo ampliado pelo
usuario inclui cenario/musica no SGDK; executor deve sincronizar contexto/GDD
antes da producao. Esta rodada nao alterou gameplay/ROM nem executou uma nova
aprovacao audiovisual. Instrucoes SMS sao plano, nao port implementado.

## 2026-09-25 — Suzaku: gate de conversao e custo da camera

- Adicionado `stage-candidate` ao conversor com saida 4bpp indexada,
  preservacao das sete cores HUD PAL0[9..15], hashes, mapa de camadas,
  contagem de tiles com flips e limite explicito. Resultado acima do budget
  sai com codigo 1 e nao promove assets.
- Corrigida a largura da vista para cobrir o curso da camera: 520/624 px,
  em vez de 512/512. Com a fonte real: uniao de 1366 tiles, pico visivel
  845, contra regiao medida de 446 tiles com emprestimo bgfx na ROM atual.
- Registrado plano de modularizacao e verificacao em
  `doc/mugen/stage_suzaku_route_2026_09_25.md`. Cenario e audio ainda nao
  foram integrados nem vistos na ROM final.
- Build atual SHA `05a27a06...` confirmou 446 tiles de regiao hipotetica do
  palco e passou pelo wrapper; a prova de controle `IMAGE BEST` usou 719
  tiles, nao foi integrada. BlastEm mostrou a ROM atual ainda sem cenario.
- Os cues PSG simples pararam de encerrar XGM2. A captura solicitada como
  menu exibiu luta: `MG_DIRECT_FIGHT=1` vence o parametro de cena do runner;
  audio do menu nao foi validado. `E0` no backlog exige perfil de entrada real.
- Perfil de menu separado (`-DMG_DIRECT_FIGHT=0`) ROM `1898bdc7...` foi
  observado no BlastEm com `scene_id=2`; audio presente, escuta/loop pendentes.
  O runner agora bloqueia divergencia de cena e ID ausente antes de publicar
  evidencia canonica (3 testes dirigidos).
- `.agents/skills` corrigida de copia obsoleta para link canonico; backup em
  `out/agent_bridge_backup/`, guard aprovado. Closeout global mediu 27 erros
  e 7 avisos antes da correção da ponte; os demais blockers persistem.
- Builder VGM do branding corrigido: campos de total/loop/rate no cabecalho
  v1.70 e teste independente, faixa regenerada SHA `7a65bfa6...`.
  ROM menu corrigida `f08d3fcd...` passou no build/BlastEm. Audio float32
  permaneceu presente tambem na ROM anterior em janela comparavel; a correcao
  e de conformidade tecnica, sem claim de melhoria audivel ou loop aprovado.
- Rebuild principal apos o VGM: ROM `20034654...` observada no BlastEm em
  cena 3, ainda com fundo solido. VRAM 174/446 tiles; captura unica nao
  valida 60 fps sustentado, arte de palco ou audio de luta.
- `res_graph` corrigido para ignorar rascunhos na descoberta padrao:
  11 manifests/484 issues falsos -> 3/161 declaracoes OK/1 aviso real;
  teste de escopo aprovado. Validador da ponte corrigido para link relativo.
  Closeout anterior terminou 28 erros/7 avisos, antes da revalidacao das
  duas correcoes; sem mudanca no status de entrega.

## 2026-09-25 — Medicao de animacao e bandas de parallax do Suzaku

- `stage-measure` aceita `--crop-top`; `stage_measure` registra e mede
  animacoes AIR/BGCtrl, frames, duracoes, offsets, flips, referencias ausentes,
  padroes por frame e deduplicacao exata entre camadas estaticas.
- Suzaku: tres eventos BG5; 51 frames/278 ticks, 9 padroes compartilhados,
  janelas nao sobrepostas e coincidentes com o ciclo AIR. Relatorio de fonte
  `rascunho/processado/stage_takeover/suzaku_measure_v2.json`, SHA
  `b357e7e252337c01b521cdc68981ac25489d15adae34e0dd15507e5d99012257`.
- Crop16 mapeia exatamente as faixas de BG_A `[0,176)`, `[176,212)`,
  `[212,224)` para os deltas das camadas frontais. A ideia requer HSCROLL_LINE
  e continua candidata. Padroes fonte: 700 no grupo frontal sem reuse; BG_B 1.021 unicos
  apos 378 reusos entre quatro layers (959 sem BG0a); custo de viewport, ResComp, paleta, VBlank e ROM
  ainda nao medidos. Nenhuma arte foi integrada.
- `test_stage.py` + `test_stage_candidate.py`: 18/18 passaram. Esta mudanca
  atualiza pipeline de medicao/docs; nao alterou runtime nem justifica build
  ou claim audiovisual.
- Criados TDD/camera/technique contracts do projeto e sincronizados `doc/15-tdd.md` e `doc/13-spec-cenas.md`. H-scroll e world768 continuam candidatos com blockers; os contratos nao registram promocao nem substituem budget/ROM.

## 2026-09-25 — Viewport e tradeoff de scroll no Suzaku

- `stage-bands` percorre as 449 posicoes inteiras, aplica deltas nativos e
  `xscale` interpolado, estima tiles por viewport/transicao e grava previews
  RGBA de fonte. O mapa frontal mede 816 px/102 colunas; 128 colunas cobrem o
  curso com nametable de 8 KiB. Pico de 460 padroes fonte, 14 acima do budget
  total estimado de 446 antes de BG_B; a candidata de paleta reduz a 431, mas
  muda cerca de 69% dos pixels e continua sem aprovacao.
- Corrigida conclusao factual: color code 0 dos planos A/B e transparente e
  revela a camada inferior; portanto `BG 3 mask=1` pode ser representado. A nota
  local do *Genesis Software Manual* (rev. 1992-02-20, p.62) tem SHA-256
  `47bcdf170f9554942c99cd2d9a789ba09482fde15d25039cad1f1d1b26580a51`. O probe
  frontal nao achou indice 0 opaco visivel nas 449 posicoes; o caso MUGEN
  `mask=false` continua exigindo remapeamento nao-zero se aparecer na viewport.
- `stage-source-view` agora reporta speed efetivo por layer/scanline. `stage-plane-
  tradeoffs` escolhe dois speeds por linha agregando as cameras left/center/right:
  19.655/215.040 amostras de pixel (9,14%) remapeadas, erro medio estimado
  0,04105 px/pixel/frame, maximo 0,803572 px/frame em y=62. O drift acumulado
  desde o anchor x=224 tem media 2,10254 px/pixel e maximo 45 px em y=62/BG3,
  evidenciando que erro/frame baixo nao garante alinhamento nos extremos.
  `stage-plane-preview` gera candidato derivado da fonte; pixels de indices diferentes: 9.625/0/6.356
  nas tres cameras. Tudo segue em `rascunho/processado/stage_takeover/`, com
  ceiling de analise; nao e tilemap VDP nem aprovacao estetica.
- O source-view completo requer >2 speeds em 72/32/72 linhas left/center/right,
  chegando a quatro. A atribuicao/precomposicao para BG_A/B ainda precisa de
  direcao visual; pode haver costuras porque a classificacao seleciona speeds
  por scanline. Custo ResComp, conflito de paleta por tile, mapa/cache, DMA,
  VBlank, animacoes BGCtrl e camera runtime seguem pendentes.
- Nenhum arquivo foi promovido a `res/`; runtime e ROM nao mudaram. Nao foi
  feita prova nova em BlastEm nem aprovado movimento, audio ou performance.
- Verificacao: suite completa do conversor **103 passed**; higiene passou com
  zero blockers; contexto `technical_demo/implementation` passou. O validador
  metodologico continua corretamente bloqueado por `perceptual_motion_unvalidated`
  (sem os quatro sinais e aprovacao humana). Learning capture/audit: 58 licoes,
  30 candidatos, nenhuma promocao canonica.
- O adendo Suzaku atualizou `doc/13-spec-cenas.md`; `scene_contract_compiler.ps1
  -Mode lab -WarnOnly` regenerou `scene-contracts.json`: 3 cenas, lint `ok`, nove
  achados informativos. O adendo segue pre-producao e nao e uma cena runtime.
- Freshness havia marcado `scene_contract_compile` + `emulator_session` stale;
  o primeiro foi recompilado. `emulator_session.json` permanece referente a ROM
  de teste Hadouken `68d3ee90...`, nao ao `out/rom.bin` `20034654...`; nao prova a
  ROM atual. Auditoria final de freshness apos compilacao ainda pendente.
  Nenhum gate de runtime foi aprovado neste checkpoint.

## 2026-09-25 — Suzaku: varredura completa e comparação de rotas

- `stage-source-view` ganhou varredura da câmera inteira, amostrando as 449
  posições do curso e agregando 32.184.320 amostras por scanline sem guardar
  rasterizações intermediárias. O report permanece em `rascunho/` e amarrado ao
  SHA da fonte; os previews continuam limitados a left/center/right.
- `stage-plane-tradeoffs` compara duas funções objetivo. O discreto remapeia
  5,03% das amostras, erro médio estimado0,02415 px/amostra/frame, drift máximo
  45px; o contínuo minimax remapeia14,33%, erro0,04757 e reduz o máximo a22,5px.
  Previews hash-bound mostram alteração visível da relação telhado/castelo nos
  extremos; nenhuma rota aprovada.
- Relatórios, limites e hashes registrados em
  `doc/mugen/stage_suzaku_route_2026_09_25.md` e
  `doc/mugen/stage_architecture_record_2026_09_25.json`; backlog D1/D2 continua
  aberto com reautoria de composição como próximo passo.
- Suite completa do conversor: **108 passed**. Nenhum asset foi copiado para
  `res/`; runtime e ROM seguem sem Suzaku e não houve nova captura BlastEm.
- Validações finais: hygiene passed/0 blockers; contexto `technical_demo` com
  0 blockers; metodologia bloqueada somente por `perceptual_motion_unvalidated`.
  `validate_resources -CloseoutGate` encerrou com 27 erros/7 avisos em 123
  checks, incluindo 11 sprites Ken acima de 16 internos, GDD insuficiente,
  gates visual/audio ausentes, divergência do budget e reports de tilemap/
  paleta ausentes. Não foram usados waivers.
- Freshness warning: um stale, a sessão de emulador antiga da ROM Hadouken;
  nenhum artefato obrigatório ausente. Aprendizado local: 59 lições/30
  candidatos, sem promoção canônica. Não houve captura BlastEm do Suzaku.

## 2026-09-26 — Perfis semânticos de scroll e portfólio VDP

- Adicionado `stage-plane-profile` para avaliar mapas de velocidade por layer
  contra o sweep integral, rejeitando sweeps esparsos, linhas ausentes, totais
  inconsistentes e perfis com mais de dois speeds por scanline. Seis testes
  dirigidos cobrem cálculos, preservação source-speed, colisões e inputs ruins;
  a suite completa do conversor terminou com **114 passed**.
- Dois perfis Suzaku foram gerados e comparados nos extremos. `castle_anchor_front_preserve`
  moveu 43,73% das amostras, com drift máximo de 120,4999 px e lua parcialmente
  fora do quadro. `sky_anchor_castle_front_merge` moveu 28,57%, drift máximo
  45,0000 px, e expôs um vazio magenta no extremo direito. Nenhum perfil ou
  asset foi aprovado; a necessidade de reautoria de overlap/ownership segue.
- Escrito `doc/mugen/stage_plane_ownership_study_2026_09_26.md` e registrado em
  `doc/agent_learning/failure_patterns.md` que dois rates numericamente válidos
  não garantem a imagem coerente. Portfólio condicional de fallback de VDP em
  `doc/mugen/vdp_optimization_options_2026_09_26.md`; não é recomendação de
  implementação sem pico medido e revisão humana.
- Criado storyboard autoral de transição em
  `doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`: céu/lua em BG_B
  delta0; castelo/muro/telhado em BG_A delta.671875 até y175; bandas frontais
  mantêm sua tabela candidata. Coordenadas, HUD, linha dos pés, prioridades e
  lacunas estão explícitas; é draft, não arte aprovada.
- Nenhum asset entrou em `res/`, runtime e ROM não mudaram, e não houve captura
  BlastEm do Suzaku. Learning capture/audit: 60 lições, 31 candidatos, sem
  promoção canônica. `doc/13-spec-cenas.md` foi sincronizado; compilador de
  contratos: 3 cenas, lint `ok`, 9 informativos. Contexto/higiene passaram; o
  gate metodológico ainda requer avaliação e aprovação perceptiva humana. O
  freshness audit mantém um stale: sessão de emulador Hadouken antiga. O cenário
  segue em pré-produção.

## 2026-09-26 — Suzaku BG_B staging com paleta travada

- `forge-art` ganhou `locked_palette_v1` para comparar uma alteração de plano
  sem re-quantizar os demais planos; `forge-art self-check`: 142/142 fixtures.
- Reautorado um plate de conceito BG_B e gerado um par de planos world640 para
  estudo, mantendo a paleta anterior. ResComp 3.95 mediu 438 tiles pareados e
  408 no controle flat, com economias de 22/17 tiles sobre a comparação anterior.
- Gerados relatório de conversão candidate, auditoria por tile da paleta e
  script reproduzível. A auditoria encontrou zero conflitos; MAP flags seguem
  sem report até decodificação real dos dados APLIB.
- Análise detalhada: `doc/mugen/suzaku_candidate_review_2026_09_26.md`.
  `tools/mugen2sgdk_forge/tests`: 120 passaram.
- Os arquivos permanecem em staging. Câmera/world768, tile flags, budget
  residente/DMA/scanline, BG5, música, integração em `res/`, gameplay/ROM,
  captura BlastEm e aprovação visual ainda estão pendentes.

## 2026-09-26 — Comparação de conceitos Suzaku e mock de contexto

- A comparação de câmera corrigiu falso positivo de repetição: as vistas left,
  center e right se sobrepunham em 160px. O landmark repetido era o mesmo ponto
  do mundo, não tile duplicado.
- Conceito de castelo V2 em 8 cores: ResComp 1.664 tiles pareados, rejeitado
  para o limite estimado. V3 atmosfera locked-six: 446 tiles/16.084 bytes,
  weighted MSE 337.696, sem folga estimada. V3 weighted-eight melhora MSE para
  235.530, mas chega a 571 tiles, 125 acima. Contagens e logs em
  `suzaku_far_overlay_v3_rescomp_measurement_report.json`.
- Criado `suzaku_visual_context_mock_20260926.png` sobre lutadores/HUD de uma
  captura de 2026-09-25, para leitura estática. Report limita a alegação a mock;
  não é build, evidência BlastEm atual ou aprovação.
- A revisão de candidato, o erro de contacto corrigido e os próximos gates
  estão em `doc/mugen/suzaku_candidate_review_2026_09_26.md`. Nenhuma arte foi
  promovida; `res/`, runtime e ROM continuam sem alteração.

## 2026-09-26 — Suzaku: compressão visual recusada e V10 medido

- Um controle V8/V9 preservou pixel a pixel a máscara alfa do plano frontal e
  passou na contagem ResComp para 390/410/436 tiles, mas produziu artefatos
  visíveis por substituição de tiles semânticos. Controle rejeitado para uso.
- V10 foi registrado com proveniência e convertido em 15, 8 e 6 cores: 989,
  961 e 844 tiles completos. A janela máxima com seis cores usa 471 tiles
  alinhada e 494 com prefetch estimado, acima do envelope histórico de 446.
- Contact sheet de HUD/lutadores é mock estático de uma captura antiga. O
  candidato continua fora de `res/`; nada de runtime, ROM ou música foi alterado.
- O catálogo de otimizações agora separa pressão de scanline, CRAM e tile/VRAM:
  flicker de sombra não libera tile; compartilhar cor não libera scanline/DMA.
  Evidências e próximos passos em `doc/mugen/suzaku_candidate_review_2026_09_26.md`.

## 2026-09-26 — BGM Suzaku original: candidato VGM/XGM2

- Gerador de composição staging criou faixa de 8 compassos/16s, 120 BPM,
  validou campos/loop do VGM1.70 e foi convertido por ResComp3.95 para um
  recurso XGM2 bruto de 1024 bytes.
- A faixa mantém canais PCM sem uso para vozes/impactos e usa PSG noise como
  acento, pendente de teste de mascaramento. Não houve audição humana, integração
  runtime, ROM ou aprovação de áudio. Receipts em
  `rascunho/processado/suzaku_fight_audio/`; plano em `doc/17-audio-design.md`.


## 2026-09-26 — BGM Suzaku: audição isolada em BlastEm

- Registrados build/captura da ROM descartável com SHA, cena observada,
  artifacts selados e relatório de áudio PCM derivado do sidecar float32.
- Sinal presente e sem clipping; audição humana, costura, mix e integração
  continuam pendentes. Telemetria relata 74/1200 quadros acima do orçamento
  e pico CPU 146; a causa permanece desconhecida e exige comparação BGM-on/off.
- Produção sem alteração; evidência e recibos em
  `rascunho/processado/suzaku_fight_audio/blastem_auditions/`.

## 2026-09-26 — Suzaku: quadro de coordenadas e custos de camera

- Criados um coordinate board para bounds por layer nas cameras 0/224/448 e uma medicao de tiles limitada pela janela real visivel do HUD.
- A residencia do ring caiu de 955/997 para 679/710 padroes, mas continua acima dos 304 tiles estimados depois das duas sheets de personagem; nenhum asset foi promovido.
- A recomposicao exata por camera preserva visualmente os deltas MUGEN offline, mas o pior passo de 1 px estima ate 19,8 KB de padroes+mapa. Nao integrar essa rota direta sem nova representacao e medicao de VBlank.
- V17 foi classificado como evidencia negativa e reference-only por misturar coordenadas das layers e encurtar o piso.
- Apenas docs, relatorios e scripts de `rascunho/processado/stage_takeover/` mudaram; sem `res/`, C, build ou ROM.
- O budget mismatch 16 vs 600 veio de chamadas por cena: boot usa pool16, fight reabre pool600. `validate_resources` selecionou a primeira chamada textual; o estado de ROM atual tem SHA `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c` e identidade stale/mismatched. Capacidade do palco continua estimativa e requer evidencia fresca.

## 2026-09-26 — Suzaku: quadro-fonte e correção da oclusão do HUD

- Recomposta a fonte MUGEN real na câmera-âncora 224 em BG_B/BG_A; antes da quantização, a reconstrução bate pixel a pixel com o compositor offline. ResComp3.95 mediu 758 tiles/26.736 bytes em 15 cores compartilhadas e 685/24.182 em 8 cores. A conversão de 15 cores tem menor erro RGB que a de 8; nenhuma recebeu aprovação artística.
- Corrigida a hipótese de que todo o retângulo WINDOW y=0..55 escondia o palco: o HUD zera 40x7 células e só escreve elementos em posições escolhidas; zero é transparente. As medições recortadas 516/506 são inválidas para residência de produção. Errata e artefatos hash-bound em `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json` e `doc/mugen/suzaku_source_fidelity_recovery_2026_09_26.md`.
- A conversão de 15 cores também não pode entrar com o ownership atual: PAL0 slots1..8 são do stage, PAL0 slots9..15 do HUD e PAL3 dos efeitos. A migração visual de HUD/FX precisa fechar antes de liberar os 15 slots ao stage; nenhum recurso foi sobrescrito.
- Pool600→446 poderia acrescentar 154 tiles à faixa de assets fixos, mas a sonda só viu pico353 e maior bloco72 sem palco/audio real. Mesmo somando o empréstimo temporário dos 272 tiles BGFX, o teto hipotético516 fica 242 tiles abaixo do frame-âncora completo sem máscara HUD; a oclusão real ainda pode alterar esse custo e não foi quantificada. Nenhuma mudança em `res/`, runtime ou ROM.
- Próximo gate: recomputar a máscara visível real, buscar economia de tiles source-faithful sem recortar céu, resolver mapa por câmera e só então testar compartilhamento de sheets/pools em ROM descartável com audio, super, DMA, fragmentação e cadência instrumentados.

## 2026-09-26 — Suzaku integrado com lutadores, HUD e música

- Adicionado renderer BG_B para o frame âncora Suzaku da fonte e organização de VRAM em 4 bancos com A/WINDOW fixos. ROM observada no BlastEm com os dois lutadores, HUD, super e retorno do cenário.
- Integrada a trilha XGM2 existente no estado de luta; audição humana e cadência de 60fps continuam pendentes.
- Medição em RAM/ROM: pool sprite 430; 353 em uso e bloco livre mínimo49; ainda houve frames acima do orçamento. Stage permanece 8 cores, quadro central estático, sem parallax do source.
- Captura antiga ao início deste registro tornou-se stale depois das builds subsequentes; consultar só o evidence bundle que tenha SHA igual ao ROM final atual.

## 2026-09-27 — Candidatos Suzaku de streaming e dois planos reprovados em runtime

- Foram compilados e capturados, em cópia isolada, o candidato de streaming de câmera e o renderer estático de dois planos. BlastEm chegou à cena de luta, mas `stage_ready=0` em ambos e o fundo ficou vazio; esses builds não são ROMs com cenário funcional.
- Streaming (`2c62c7f5…`): 456 tiles de capacidade, zero residentes, zero restaurações; hipótese de empréstimo BGFX inválido porque usa a mesma faixa-base da VRAM. Estático (`c1b03a49…`): zero restaurações e stage não inicializado; causa ainda sem prova.
- Os gates visuais e de desempenho ficam bloqueados. VLAB contou 50/1200 e 82/1200 quadros acima do orçamento, respectivamente; amostras pontuais de FPS não substituem cadência estável.
- Evidência local, não versionada: `out/mugenesis_evidence/suzaku_stream/canonical` e `out/mugenesis_evidence/suzaku_static_planes/canonical`. Relatório e próximo diagnóstico: `doc/mugen/suzaku_capture_regression_2026_09_27.md`.


## Continuidade 2026-09-27 — diagnóstico físico corrigido

A ROM diagnóstica `bef4dba9d29d9abf9d3e3c604229a08a3465e4fbd4b9a6d60c9eb0b25d9f683d` registrou em SRAM: stage_ready=0, status=CAPACITY, lowBase=650, spriteStart=1010, capacidade=648, requerido=685 (far259 + near426), MG_fightVramNext=492. Evidência: `out/mugenesis_evidence/piece_init/canonical`. O bloqueio da rota estática é falta de37 tiles, não o orçamento estimado de462.

Errata da hipótese de streaming: capacidade456 era parada prematura em TILE_MAX_NUM, não prova de BGFX ausente ou duplicado. `fight_stage_stream.c` agora permite gaps físicos D000/F800 e exclui C000–CFFF/E000–F7FF, com rejeição atômica de overlap. Testes host: 3/3 passaram (bancos estáticos, dois planos e pool stream). Capacidade648+272=920 provada no alocador host; ainda não capturada em ROM com essa correção.

Lição candidata: distinguir teto do alocador SDK de VRAM física; diagnosticar a primeira guarda que retorna e exportar seus operandos, sem inferir estado das etapas não executadas. Manter mapa de ownership por fase e validar restauração do empréstimo. Nenhuma promoção canônica ou aprovação visual nesta etapa. Próxima entrega: piso fiel isolado com movimento, depois módulos do telhado; preservar a ROM principal e comparar cada degrau compilado.


## Captura da guarda corrigida — resultado parcial

ROM `8bf3b933943ad4cda3292ef3952d76ad2c53c1c9ef6f0eae1022dae618f02890`; sessão `out/mugenesis_evidence/piece_stream_guard/sessions/blastem-linux-20260927T105449Z-1338066`. Build concluído. Screenshot inspecionado: cenário presente com jogadores/HUD, mas cores erradas e artefatos nas barras inferiores. Bundle rejeitado: vlab_block_missing, artifact_missing:vdp_dump, artifact_missing:runtime_metrics. Não sustenta teste completo, movimento, orçamento ou FPS.

Causa concreta adicional: `source_stream_pattern_atlas.png` tem paleta diferente de `source_anchor_8_bleed.png`, mas `FIGHT_STAGE_init` carrega `img_suzaku_anchor.palette`. Índice1 do atlas é (102,136,136), enquanto a âncora fornece (34,68,102). A guarda corrigida apenas expôs esse defeito antes invisível. Próxima correção deve vincular explicitamente a paleta do atlas e conferir todos os índices, sem confundir o problema com perda inevitável do VDP.

Ainda investigar separadamente o tempo até telemetria, alinhamento de scroll por linha versus origem comum da tile-row, ordem de vscroll far/near, overlay do HUD e restauração BGFX. O piso isolado em BG_B permite testar perspectiva original sem congelar suas linhas sob a barra. Não promover o streaming completo antes desses testes.
