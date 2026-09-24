# Diagnóstico do SGDK Forge: produção de jogos Mega Drive ponta a ponta

Auditoria iniciada em 06/09/2026; documento concluído em 07/09/2026. Escopo: workspace e capacidade de produção, não avaliação final de um jogo. Estado: **diagnosticado; capacidade AAA ponta a ponta não demonstrada**. Alterações de implementação propostas neste documento não foram executadas.

## 1. Parecer executivo

O Forge possui uma base relevante: wrapper central, contratos por domínio, ferramentas de conversão e medição, instrumentação, automação de emulador, memória operacional e controles contra promoção indevida. Há código, ROMs e evidências de laboratório; não se trata de um framework apenas conceitual.

Entretanto, **não há sustentação nos artefatos examinados para afirmar que o Forge já gera, de forma repetível, jogos completos iguais ou superiores às referências apresentadas**. A principal distância está entre competência descrita, integração funcional e qualidade observada em produto completo. Aumentar o catálogo de técnicas não resolve sozinho essa distância.

Três prioridades imediatas:

1. Restabelecer confiança na cadeia de medição/build/evidência: cópias desatualizadas, identidade incompleta do SDK e CI sem alvo dourado.
2. Fechar um slice autoral com arte, animação, jogabilidade e áudio simultaneamente aprovados na mesma ROM.
3. Levar esse piloto do início ao fim e repetir a produção de outro trecho por outro agente, medindo retrabalho e dependência humana.

A ambição pode continuar alta. O critério de avanço deve ser uma experiência jogável melhor, com prova reproduzível. “AAA” aqui é um objetivo de acabamento, resposta, coerência, conteúdo e confiabilidade; não uma propriedade que surge da quantidade de efeitos ou de JSONs aprovados.

## 2. Método, limites e rastreabilidade

Foram lidos o framework, regras, memória global, registros de técnicas e gêneros, plano visual, código de build/CI/template e relatórios de projetos. O inventário em `project_inventory.json` cobre os diretórios imediatos de `SGDK_projects`, com hash de `out/rom.bin` quando presente e quatro nomes de relatórios. Não é inventário recursivo de toda evidência histórica. A busca dos laudos visuais também considerou laboratórios.

Executamos a guarda de ambiente, o meta-gate de medição e três suites direcionadas. Nenhuma ROM foi recompilada ou executada nesta auditoria. Portanto, os diagnósticos de runtime usam evidência histórica declarada, sem recertificação de FPS, áudio ou gameplay. Relatório antigo com blocker é prova do estado daquele relatório; não prova, sozinho, que o defeito persiste na ROM atual.

O checkout já continha alterações e projetos não rastreados. O commit-base está em `git_head.txt`; o contexto sujo foi registrado no snapshot de orquestração. O diagnóstico considera o conteúdo observado, incluindo modificações locais, e não equivale a revisão exclusiva do commit. Os principais hashes estão em `source_manifest.json`.

Houve duas revisões independentes concluídas, de código e governança. O revisor de hardware forneceu observações parciais, mas encerrou por indisponibilidade de créditos do serviço; não existe parecer final independente de hardware. O coordenador confirmou diretamente as contagens do registry. Os envelopes dos revisores não satisfizeram todos os vínculos de entrada exigidos pelo harness; os resultados dessa validação foram preservados. Seus apontamentos foram tratados como pistas e conferidos localmente, sem apresentar o conselho como integralmente validado.

A auditoria é consultoria sobre o workspace. Não se aplicou adoção metodológica de jogo à raiz, nem se alteraram os manifestos de todos os projetos: isso seria migração de produção fora do pedido de diagnóstico. A autorização para registrar documento e plano foi usada apenas para o pacote documental e memória da sessão.

## 3. Evidência quantitativa

| Verificação | Resultado observado | Significado e limite |
|---|---|---|
| Guarda comum de ambiente | `ready`; Graphify `fresh` | Preparo consultivo passou; não prova toolchain nem emulador |
| Meta-gate de medição | 19/19 self-checks passaram; resultado global `BLOCKED` | Existem 23 cópias/fontes ativas divergentes e 3 ocorrências arquivadas; exige triagem |
| Roteador de revisão | 44/44 verificações passaram | Testa contratos do roteador |
| Harness de orquestração | 71/71 verificações passaram | Testa regras de orquestração, não a qualidade dos agentes |
| Contratos canônicos de fixture | 10/10 testes passaram | Exercita hash, amostragem, observação e limites de claim |
| Registry técnico | 114 entradas | Mistura técnicas, doutrinas e gates; não representa 114 funcionalidades de runtime |
| Estados no registry | 39 `documented`; 33 `gap_pure`; 21 `incorporated`; 15 `partial`; 6 `candidate_with_evidence` | Zero entradas marcadas `blastem_proven` ou `senior_default`; registro pode estar atrasado frente a provas locais |
| Laudos `live_scene_bar_report.json` localizados pelo revisor | 3, todos `needs_review` | Duas cópias FR2 e uma TAIKETSU; nenhum `passed` localizado nessa busca |

A primeira tentativa das suites Python falhou por `jsonschema` ausente no Python do sistema. A rota já prevista no repositório, `uv run --with jsonschema`, permitiu executá-las. Isso é uma dependência de executor resolvida, não defeito dos testes. Os logs iniciais e finais foram preservados.

## 4. O que já merece ser preservado

- Separação entre build, execução, budget e aprovação criativa; proveniência e quarentena de placeholders.
- Medição dos dois limites por scanline e testes positivos/negativos dos instrumentos.
- Contratos de camera, input, colisão, streaming, áudio, transições e cenas; fonte central de build.
- Política de arte autoral, tradução nativa e revisão visual: o problema dominante é completar a produção no piso exigido, não inventar outra proibição.
- Evidências históricas úteis: por exemplo, BLUE_CIRCUIT delimita observações NTSC/PAL a uma cena e não as transforma em aprovação global de gameplay/áudio/visual.
- Planejamento de maestria e da barra visual já existente. Este plano deve alimentar os documentos 94 e 19, evitando uma terceira arquitetura paralela.

## 5. Lacunas prioritárias

### F01 — Medição local divergente da fonte central — P0 de confiabilidade

O meta-gate atual emitiu `measurement_tool_stale_copy` e `project_source_mirror_stale`: cinco ocorrências de ferramentas e dezoito de fontes/headers de probe, totalizando 23. O self-check central verde não torna uma cópia antiga confiável. Evidência: `measurement_tools_report.json` e seu log.

Correção: separar customização legítima, cópia obsoleta e arquivo morto; produzir diffs por projeto e migrar apenas os instrumentos ativos após regressão. A política de não sobrescrever `.agent` local continua válida. Aceite: meta-gate sem divergência ativa não explicada; fixture negativa exercita ambos os limites de scanline; nova ROM e evidência para qualquer projeto cuja instrumentação mude. Não recertificar automaticamente ROMs antigas.

### F02 — CI dourada aceita ausência do alvo — P0 de confiabilidade

`tools/sgdk_wrapper/ci/run_golden_validate.ps1:39–61` busca `BENCHMARK_VISUAL_LAB` e depois `AAA EFFECT LAB - *`. Não há alvo correspondente no checkout observado. Após o guard generalista, a ausência retorna sucesso antes do preflight. Mesmo com alvo, esse script valida recursos; não implementa uma CI completa build→playtest.

Correção: referência explícita e mantida a uma fixture existente, com distinção entre suite contratual e integração E2E. Zero alvos obrigatórios deve falhar ou declarar estágio não executado, nunca sucesso E2E. Aceite: caso negativo sem alvo, build limpo, percurso observado no BlastEm, hash único e relatório completo. Preservar o guard generalista, que tem valor próprio.

### F03 — Cache do SDK pode servir dependência antiga — P1

`build_sgdk_wine_bridge.sh:54–68` identifica a cópia do SDK pelo hash de `makefile.gen`. Alterar header, fonte de biblioteca ou compilador mantendo esse arquivo pode conservar o staging antigo. É uma deficiência estática confirmada da chave; não foi reproduzida uma ROM errada nesta sessão.

Correção: inventário de conteúdo do SDK e ferramentas, fingerprint dos parâmetros de biblioteca e invalidação das saídas dependentes. Aceite: mudar header, compilador e fonte em fixtures controladas invalida o estágio correto; relatório identifica o SDK realmente consumido.

### F04 — Build Linux acoplado ao host — P1

O mesmo bridge fixa `/mnt/sdcard/sgdk_forge_wine_211`, mapeamento Wine e permissões Flatpak específicas (`:34`, `:155`, `:215`). Há risco de falha em outro host e disputa de alias entre workspaces.

Correção: caminhos derivados do workspace ou staging gerenciado, identidade por workspace e lock quando necessário. Aceite: dois workspaces, caminhos com espaços, sem dependência de `/mnt/sdcard`; ausência de colisão em builds concorrentes. Windows exige validação própria; funcionar no Linux atual não demonstra portabilidade.

### F05 — Piso visual e animação ainda não demonstrados como produção repetível — P0 de produto

O próprio `doc/03_art/19_plan_pixel_art_live_scene_capability.md` descreve o veto como mais maduro que a produção nativa. Os três laudos localizados continuam em revisão. Isso não autoriza declarar toda a arte ruim; autoriza dizer que o piso institucional ainda não possui passagem localizada no recorte auditado.

Correção: executar o plano existente sobre um personagem, um inimigo e uma cena autorais. Avaliar silhueta, anatomia funcional, materiais, timing, contato, legibilidade em movimento e coerência com o palco. Aceite: assets persistidos, proveniência, source/basic/elite, animação observada, laudo atual aprovado e decisão humana, todos ligados à ROM. Quantização correta é condição técnica, não aprovação estética.

### F06 — Do template ao produto há integração a fazer — P1

`modelo/src/scenes/scene_demo.c:117–119` toca cue ao atacar; `:178–180` representa jogador por caracteres. É um seed pedagógico, não combate pronto. A troca em `modelo/src/core/app.c:76–99` merece contrato explícito de saída/ownership ao crescer. Não é necessário transformar todo template em jogo genérico gigante.

Correção: manter o seed honesto e criar um caminho de referência testado para integrar input→FSM→hit/hurt/push→feedback→áudio→câmera→transição. Aceite: inimigo recebe dano, jogador pode falhar e retentar, pause/restart e troca de cena não vazam VRAM, callback, sprite ou áudio. Medir entrada recebida, não apenas tecla enviada.

### F07 — Prova de jogo completo não fechada — P0 de produto

`MARE_BRAVA…/doc/aaa_pipeline_gate_report.json:29–30` mantém bloqueios de slice e jogo completo; o GDD TAIKETSU ainda distribui conteúdo/roster/áudio em marcos futuros. As amostras não sustentam campanha completa, final, progressão e mastering. Não inferir cobertura de gênero pelo nome das pastas ou por validador generalista `ok`.

Correção: matriz GDD→conteúdo→runtime alcançável→teste→evidência, com lista de cenas e rotas de falha/retorno. Aceite: início→fim, morte/retry, menus/opções, save/continue se previstos, créditos e pacote final; nenhuma dependência de conteúdo provisório no caminho entregue.

### F08 — Técnicas avançadas têm maturidades diferentes — P1/P2 conforme o piloto

Registry: `software_affine_pseudo3d`, `forward_kinematics`, `sprite_midframe_sat_reuse` e `sat_double_buffering` estão `gap_pure`; `sprite_frame_vram_slot_streaming` e `modular_boss_runtime_gate`, `partial`; `tile_cache_streaming_refcount`, `candidate_with_evidence`. Áudio customizado e PCM ring buffer estão incorporados em doutrina, o que não equivale a driver integrado e certificado em cena pesada.

Correção: benchmark isolado por técnica requerida pelo jogo, seguido de teste combinado no slice. Medir o degrau seguinte com geometria e áudio reais; descrever fallback visual e de gameplay. Não bloquear um bom jogo porque ele não usa FMV, SVP ou SAT mid-frame. Não transformar técnica arriscada em default por ambição.

### F09 — Áudio e desempenho precisam ser demonstrados juntos — P1

A evidência amostrada de projetos não fecha desempenho e áudio globais. O diagnóstico independente de hardware ficou incompleto; os valores parciais citados por ele não foram usados para certificar nem reprovar uma ROM aqui.

Correção: BGM autoral, SFX prioritários, PCM, pause/resume e transições sob a carga máxima de DMA e entidades. Medir CPU/VDP/Z80 com unidades, janela, versão e amostras; gravar áudio efetivo. Aceite: nenhum dropout ou perda de cue crítico no percurso declarado; métricas de pior quadro, não apenas média do FPS do host. Para PAL, objetivo e timing próprios devem estar explícitos.

### F10 — Memória e relatórios misturam estados — P1

FR2 possui laudos `doc/` e `out/logs/` associados a ROMs diferentes. A memória global preserva “13/13 projetos compiláveis” sem vínculo atual; `genre_coverage_state.json` contém 2/6 ativos ao lado de 1/38 total e texto de “única cobertura”, sinal de atualização parcial. Esse arquivo já estava modificado pelo usuário e não foi reescrito.

Correção: cabeçalho vigente derivado de hash/relatório e histórico rotulado; uma autoridade por dado. Aceite: nenhuma divergência aritmética ou duas ROMs simultaneamente chamadas de vigente; hash antigo rejeitado. Evitar repetir contagens em prosa em múltiplos arquivos.

### F11 — Escala de conteúdo e fechamento físico ainda exigem prova — P2

Possuir skills de level design, narrativa, áudio e mastering não comprova produtividade de conteúdo nem compatibilidade final. São necessários ritmo, variedade de encontros, curva de aprendizado, economia/save quando aplicáveis e revisão externa de experiência. Hardware real requer campanha específica além do BlastEm obrigatório.

Correção: medir tempo até primeiro slice aprovado, ciclos de retrabalho por asset, defeitos por minuto jogado e esforço para produzir a segunda fase. Planejar matriz de região, controle, SRAM/reset, tamanho/mapper e hardware alvo. Aceite: produção repetida com qualidade comparável e playthrough completo nas configurações assumidas. Superar referências precisa de comparação observada, não só score automático.

## 6. Leitura crítica das referências

A tabela do pedido é um briefing de ambição, não uma especificação de hardware validada. Não foi feita engenharia reversa dos 17 itens. As técnicas específicas não confirmadas por fonte primária nesta auditoria permanecem hipóteses de referência; não devem ser copiadas como fatos para o registry.

| Referência | Capacidade que deve orientar o Forge | Rota e evidência necessária |
|---|---|---|
| Red Zone | Renderização CPU, cenários transformados e vídeo compacto | Separar codec, renderer e cenas; medir pixels/tiles modificados, CPU, DMA e qualidade resultante. FMV não garante jogo melhor |
| Alien Soldier | Chefes grandes, animação articulada e combate legível | Rig/partes, pivôs, colisão, telegraph e streaming; pior scanline e frame com jogador, FX e áudio |
| Batman & Robin | Profundidade, deformação e setpieces raster | Separar tabelas de scroll, H-Int e renderização software; efeito percebido não identifica sozinho o algoritmo |
| Virtua Racing | Polígonos com hardware expandido | SVP é perfil de cartucho separado; toolchain, runtime, emulação e hardware específicos. Não é baseline do 68000 puro |
| Vectorman 1/2 | Volume, materiais e movimento coerentes | Pipeline de fonte/render→pixel nativo→animação; não assumir iluminação dinâmica só porque o sprite parece tridimensional |
| Ranger-X | Paleta e composição de alta riqueza | Investigar mecanismo por cena; mudanças CRAM e Shadow/Highlight têm contratos diferentes. Contar cores em screenshot não identifica a técnica |
| Sonic 2/3 & Knuckles | Sensação de velocidade, física, streaming e especiais | Separar cada jogo/estágio: pseudo-3D não se reduz a line scroll universal. Exigir movimento, colisão e streaming em conjunto |
| Sonic 3D Blast | Vídeo compacto e integração de apresentação | Benchmark de codec/decoder, consumo ROM/RAM/VRAM, upload e transição. Mecanismo exato do vídeo precisa de fonte técnica dedicada |
| Street Fighter II SCE | Resposta de combate e PCM integrado | Qualidade vocal é critério a medir, não atributo garantido por “driver customizado”; avaliar contenção e prioridades |
| Panorama Cotton | Perspectiva e fluxo contínuo de objetos | Testar escala por frames/tiles e técnicas raster conforme cena; H-blank por si só não faz scaling arbitrário de sprites |
| Pier Solar | Conteúdo extenso, banking e áudio expandido opcional | 64 Mbit correspondem a 8 MiB; separar ROM/mapper de VRAM e Sega CD. Não manter “maior da história” como requisito ou fato sem recorte/fonte |
| Tanglewood | Coerência de atmosfera, física, ferramentas e compatibilidade | O autor documenta Assembly 68000, kit Cross Products e ferramentas próprias; isso não implica que SGDK precise ser abandonado [S2] |
| Xeno Crisis | Arena com leitura clara, encontros e áudio | É visão superior, não isométrica [S1]. Medir densidade útil, cues e resposta, sem assumir dezenas ilimitadas de inimigos simultâneos |
| Paprium | Brawler de grande conteúdo com hardware adicional | Datenmeister exige investigação própria; não atribuir planos/sprites extras ao VDP padrão sem prova do mecanismo |
| Demons of Asteborg / Astebros | Unidade visual, animação, encontros e mundo | “Estética 32-bits” é descrição estética, não capacidade física. Comparar pixels e cenas na versão Mega Drive |
| DaemonClaw | Ação e personagens grandes | A página oficial confirma versões/plataformas [S3], não prova a explicação de streaming/FPS da tabela; exigir fonte e medição por versão |
| ZPF | Ritmo, densidade e identidade de shmup | A fonte oficial descreve shmup horizontal, bosses e pontuação [S4]; não confirma alternância temporal como técnica universal |

Recomendação de escopo: estabelecer **perfil A: Mega Drive padrão**, **perfil B: ROM expandida/mapper** e **perfil C: coprocessador ou expansão**. Aprovar A não aprova B/C. O SGDK oferece suporte a banking; logo “ROM acima de 4 MiB” não deve ser tratada como ausência automática de SDK. Ainda requer integração e teste de fronteira de bancos [S5].

## 7. Como verificar “igual ou superior”

Escolher para cada cena 2–3 referências comparáveis no mesmo gênero, hardware e função. Capturas legais de referência orientam composição e resposta; não viram fonte de pixels. Registrar versão/região e sequência exata comparada. Uma cena de boss não é comparável a uma tela de título.

Separar seis eixos: legibilidade/arte; animação/contato; resposta/game feel; level design/ritmo; áudio; estabilidade/conteúdo. Um eixo técnico excelente não compensa ataque ilegível ou campanha repetitiva. Usar revisão cega quando viável, com critérios previamente escritos e achados concretos por quadro/ação. Preferência estética permanece distinguida de defeito.

O aceite proposto é: nenhum defeito crítico de legibilidade/controle; qualidade visual aprovada; comportamento previsto atingível; pior caso dentro do budget; áudio efetivamente capturado; conteúdo completo; e revisão comparativa favorável no recorte definido. Esse recorte não autoriza dizer que todo o jogo ou todo o Forge supera todas as referências.

## 8. Plano de ação executável

Estimativas abaixo são faixas de esforço de uma pessoa experiente, para planejamento, não promessa de prazo. Arte e revisão humana podem dominar o calendário. Reestimar ao fechar cada marco. Não somar as faixas como previsão garantida de jogo AAA.

| Marco | Ações e entregável | Dono sugerido | Dependência | Aceite | Esforço inicial |
|---|---|---|---|---|---|
| M0 — Verdade operacional | Triar F01, corrigir alvo CI, fingerprints SDK; reconciliar baseline do piloto | Build wrapper + evidence curator | Nenhuma | Instrumentos ativos confiáveis, alvo explícito, build reproduzível e relatório sem falso verde | 3–7 dias |
| M1 — Contrato do piloto | Escolher projeto existente, congelar recorte, storyboard/coreografia/budget; mapa GDD→prova | Planning + scene-state + VDP | Baseline M0 para medições | Uma cena e seu percurso completos definidos, hardware/região e critérios comparativos explícitos | 2–4 dias |
| M2 — Arte e animação | Executar fases do plano visual 19; protagonista/inimigo/cenário/FX autorais e áudio mínimo | Native sprite + art translation + visual + áudio | M1 | Laudo aprovado em ROM, sem promover placeholders; timing e contato vistos | 2–6 semanas |
| M3 — Slice integrado | Combate/colisão/câmera/transição/IA/áudio; stress do degrau seguinte | Runtime + subsistemas | M1; integração final depende M2 | 5–10 minutos propostos de percurso, falha/retry, cena pesada com áudio, sete eixos QA | 2–4 semanas |
| M4 — Repetibilidade | Outro agente produz segundo trecho com o mesmo pipeline; registrar retrabalho | Coordenador + revisão independente | M3 | Qualidade comparável, sem consertos manuais ocultos; custo medido | 1–3 semanas |
| M5 — Produto completo | Expandir somente conteúdo do GDD, começo/fim, save quando aplicável, balanceamento | Design/level/narrativa/runtime/áudio | M4 | Playthrough integral e todos os conteúdos alcançáveis; nenhuma substituição provisória entregue | Reestimar pelo conteúdo real |
| M6 — Mastering e QA | ROM final, regiões, controles, hardware, áudio, regressão e empacotamento | ROM mastering + evidence + QA humano | M5 | Sete eixos; BlastEm; testes físicos declarados; bundle do mesmo hash | 1–3 semanas após conteúdo fechado |
| R&D — Assinaturas avançadas | Boss articulado, raster, streaming combinado; affine/FMV apenas se fizerem parte do alvo | VDP + owner específico | Instrumentos M0 e necessidade M1 | Fixture isolada e posterior prova no jogo com fallback | Estimar por técnica |

A preferência já documentada no plano visual é MARE_BRAVA. TAIKETSU está em trabalho ativo e pode ser escolhido pelo proprietário como piloto, mas mudar o foco não é consequência automática desta auditoria. Evitar abrir outro jogo para fugir dos blockers do atual.

### Backlog técnico ordenado

**Primeiro:** instrumentos ativos e evidência fresca; alvo CI obrigatório; fingerprint de SDK. **Depois:** remover dependências fixas do host, selar a rota E2E e produzir o slice. **Na sequência:** biblioteca de padrões extraída do slice aprovado, segundo trecho e conteúdo completo. **Por último ou em ramo isolado justificado:** FMV, affine generalizado, SAT mid-frame, coprocessadores. Essa ordem não reduz a ambição; evita construir técnicas sem produto para validar sua utilidade.

Para áudio, antecipar composição e contrato de canais em M1/M2. Para level design, testar geometria e ritmo antes da arte final. Para arte, não sacrificar qualidade com aumento cego de densidade: medir o degrau seguinte e registrar por que a cena escolheu sua ocupação.

### Indicadores de progresso

- Tempo do briefing até primeiro trecho aprovado em ROM.
- Percentual do conteúdo aprovado do GDD que é alcançável e testado; denominador explícito.
- Tentativas por animação até aprovação e defeitos de contato/identidade restantes.
- Frames acima do budget e perdas de cues na janela pesada com áudio.
- Divergências de hash/relatório e quantidade de passos manuais não documentados.
- Custo e resultado do segundo trecho produzido por outro agente.

Não usar número de skills, linhas de código ou validadores como indicador substituto de qualidade do jogo.

## 9. Decisão e próximo trabalho

Decisão: **revisar a base de confiança e fechar o slice antes de expandir produção cara**. Os achados F01–F04 têm ações técnicas delimitadas; F05–F07 são o centro da capacidade de produto; F08–F11 organizam domínio avançado, repetibilidade e fechamento.

O próximo trabalho concreto recomendado é M0, com regressões negativas e correções em mudanças separadas. Depois, M1 deve fixar o piloto e seus critérios de comparação. Este documento não promove técnica, ROM, arte ou projeto a `ready_for_aaa`.

## 10. Fontes externas consultadas

Acesso na sessão de 06/09/2026. Apenas as afirmações explicitamente associadas abaixo se apoiam nessas fontes; marketing de produto não demonstra algoritmo ou desempenho.

- [S1 — Bitmap Bureau: Xeno Crisis](https://www.bitmapbureau.com/games/xeno-crisis) e [home do estúdio](https://www.bitmapbureau.com/): gênero arena/top-down e plataformas.
- [S2 — Big Evil Corporation: desenvolvimento de Tanglewood](https://blog.bigevilcorporation.co.uk/tag/game-development/): relato do desenvolvedor sobre Assembly, kit e ferramentas.
- [S3 — Neofid: DaemonClaw](https://neofid-studios.com/en-us/pages/daemonclaw): escopo de versões e apresentação do jogo; não valida os claims técnicos do briefing.
- [S4 — Mega Cat: ZPF](https://megacatstudios.com/pages/zpf): características de produto; não valida algoritmo de transparência.
- [S5 — SGDK: ResComp](https://stephane-d.github.io/SGDK/md__s_g_d_k_2bin_2rescomp.html): ALIGN/NEAR e organização de recursos para banking. Para implementar, os headers locais SGDK 2.11 continuam sendo a autoridade de API.

## 11. Artefatos desta auditoria

`project_inventory.json`, `technique_snapshot.json`, `source_manifest.json`, `measurement_tools_report.json`, logs dos testes, pedido/plano de revisão, snapshots de contexto/frontier e resultados parciais de revisão ficam neste diretório. O parecer independente incompleto está explicitamente registrado, sem substituir a conclusão documental do coordenador.
