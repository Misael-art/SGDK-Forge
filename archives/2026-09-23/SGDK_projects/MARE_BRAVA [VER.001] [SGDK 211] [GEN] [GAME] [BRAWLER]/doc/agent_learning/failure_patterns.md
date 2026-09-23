# Failure Patterns

Registre aqui falhas, falsos positivos, tentativas ruins e decisoes que nao devem ser repetidas sem nova evidencia.

| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |
|---|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log/screenshot/hash] |

## Regras

- Falha sem evidencia deve ser marcada como hipotese.
- Solucao nao comprovada nao vira recomendacao.
- Se a falha indicar risco canonico, classifique como `needs_human_review`.


## L02 proporcao estilizada ignorada por modelos de imagem

- Data: 2026-07-03
- Contexto: prompts pediram explicitamente proporcao arcade 3.5 heads para sprites de 44-56px
- Falha observada: modelos entregaram anatomia realista (~6.5 heads) em todos os sheets de personagem; o downscale direto para altura de jogo vira borrao (provado no contact sheet)
- Causa provavel: modelos de imagem generalistas nao obedecem instrucao textual de proporcao estilizada com confiabilidade
- Mitigacao: pedir anatomia realista de proposito (identidade, roupa, pose) e declarar a compressao para 3-4 heads como etapa pixel autoral obrigatoria; atualizar template de prompt pack e concept_art_direction_system
- Evidencia: data/source_art/taina_model_sheet/taina_turnaround_v01.png e data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png
- Classificacao: candidato_canonico
- Candidato: regra de prompts de personagem no concept-art-direction

## L03 texto diegetico emergente apesar do negative prompt

- Data: 2026-07-03
- Contexto: prompts de cenario com negative prompt 'no text'
- Falha observada: modelo inseriu texto diegetico (fita 'interditado por sindicato', selo de uniao em caixote) no painel da arena 3
- Causa provavel: elementos textuais fazem parte do vocabulario visual de docas/interdicao no treino do modelo
- Mitigacao: gate de concept classificar texto emergente como aceito_diegetico ou rejeitado em vez de reprovar automaticamente; neste caso foi ACEITO como narrativa ambiental do GDD; conversao a tiles precisa de politica para texto legivel
- Evidencia: data/source_art/cais_world/cais_arena3_beirada_ringout_v01.png
- Classificacao: candidato_canonico
- Candidato: politica de texto diegetico nos gates de arte

## L05 nomes de arquivo humanos quebram higiene

- Data: 2026-07-03
- Contexto: humano salvou os concepts gerados manualmente
- Falha observada: nomes com espacos, acentos e dois-pontos (invalido em Windows) e dois arquivos na pasta errada, apesar do padrao declarado no prompt pack
- Causa provavel: prompt pack declarou o padrao de pasta mas nao o nome exato de arquivo por prompt
- Mitigacao: prompt pack deve dar o nome de arquivo exato por prompt; agente normaliza para portable_descriptive_v1 no recebimento como rotina
- Evidencia: renomeacao registrada no changelog de 2026-07-03
- Classificacao: local_note

## L06 incompatibilidades do framework em pwsh linux

- Data: 2026-07-03
- Contexto: primeira producao completa do framework num host Manjaro Linux com pwsh 7.6
- Falha observada: OrderedDictionary rejeitado pelo Test-JsonSchema; ConvertFrom-Json converte datas ISO em DateTime sem -DateKind String; .agent local precisa ser symlink absoluto; heuristica do GDD nao le acentos; higiene acusa literais de caminho em texto historico; validate_resources usa -WorkDir; audit_project_learning chama py
- Causa provavel: framework desenvolvido e testado apenas em Windows PowerShell
- Mitigacao: fix ja commitado no validador do brawler; varrer validadores irmaos e adicionar CI multiplataforma (chips de curadoria abertos)
- Evidencia: doc/changelog/changelog.md de 2026-07-03 e commit do fix no wrapper
- Classificacao: candidato_canonico
- Candidato: varredura pwsh linux nos validadores (chips task_0721942b task_7b255b45 task_1e7be1cf)

## L07 falso verde de contrato em fase de planejamento

- Data: 2026-07-03
- Contexto: cadeia de contratos de design 100 por cento valida com projeto sem ROM nem arte
- Falha observada: audit_game_design_contracts emitiu ready_for_aaa=true em pre-producao, criando impressao de prontidao
- Causa provavel: auditor nao cruza evidencia de runtime antes de conceder o status maximo
- Mitigacao: slice_scope_contract como guarda anti-falso-verde local; no canonico, emitir design_contracts_ready em planejamento e reservar ready_for_aaa para quando houver evidencia
- Evidencia: doc/contracts/slice_scope_contract.json e parecer curatorial de 2026-07-03
- Classificacao: candidato_canonico
- Candidato: novo status design_contracts_ready no auditor (chip task_1e7be1cf)

## L08 ledger e derivado dos markdowns e nao editavel a mao

- Data: 2026-07-03
- Contexto: agente escreveu licoes estruturadas direto em learning_ledger.json
- Falha observada: audit_project_learning -Mode Capture regenerou o ledger a partir dos markdowns e sobrescreveu as licoes escritas a mao
- Causa provavel: o ledger e artefato DERIVADO (extract_project_learning.py parseia success/failure patterns por secoes ## com campos '- Campo: valor'); escrever nele viola o contrato da ferramenta
- Mitigacao: curar licoes SEMPRE nos markdowns no formato do parser (Data, Contexto, Falha observada/Padrao observado, Causa provavel, Mitigacao, Evidencia, Classificacao, Candidato) e deixar o capture derivar o ledger
- Evidencia: doc/agent_learning/learning_ledger.json regenerado em 2026-07-03
- Classificacao: local_note

## L09 falso blocker de Bonsai/ComfyUI quando ha geracao nativa

- Data: 2026-07-09
- Contexto: MARE_BRAVA precisava continuar gerando concept/source assets; a sessao Codex atual possui ferramenta nativa de imagem, mas o relatorio antigo `generation_channel_decision.json` marcava `license_blocked` por Bonsai sem licenca e host AMD
- Falha observada: o agente gastou energia tratando Bonsai/ComfyUI como bloqueio principal, apesar de a rota mais simples ser gerar pela capacidade nativa do modelo e salvar como `source_candidate`
- Causa provavel: roteamento local estava defaultando `native_callable=false` quando a flag nao era passada, e docs antigas descreviam Bonsai como gate dominante
- Mitigacao: `imagegen_tool.py`/`imagegen_circuit.py` agora auto-detectam Codex/ChatGPT como `native_chat_image_generation_callable`; skills/docs declaram native-first; Bonsai/ComfyUI so bloqueiam quando nao houver nativo/API
- Evidencia: out/logs/generation_channel_decision.json de 2026-07-09 com `selected_source=native_chat_image_generation_callable` e `next_action=use_native_channel`
- Classificacao: local_note

## L10 iteracao tecnica nao pode substituir a fonte autoral

- Data: 2026-07-28
- Contexto: revisoes de lineart TAÍNA v05 e v07 buscaram resolver escala, grid e pivot dentro da celula 48x64.
- Falha observada: o diretor de arte humano classificou as imagens 05 e 06 da linha do tempo como retrocessos de fidelidade grafica. v05 caiu em proporcao chibi; a sequencia posterior perde cabelo, face e leitura da guarda. O fluxo deixava uma iteracao tecnicamente mais adequada aparentar progresso mesmo quando degradava a identidade.
- Causa provavel: os contratos de identidade e os relatórios de fidelidade existiam, mas faltava uma regra operacional que congelasse a fonte autoral como incumbente e proibisse usar candidatos reprovados como referencia da proxima tentativa.
- Mitigacao: congelar a imagem 04 da linha do tempo como baseline de direcao; antes de cada iteracao, carregar visual DNA, gate arte+gameplay e contrato de traco; declarar `must_preserve`; corrigir apenas um eixo por vez; comparar lado a lado em escala nativa; bloquear promocao e reutilizacao como fonte se qualquer marcador de identidade regredir. Seguir `doc/art/characters/taina/iteration_control_protocol.md`.
- Evidencia: doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v05.json; doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v07.json; doc/art/characters/taina/review/taina_lineart_v04_v05_compare_8x_v01.png; doc/art/characters/taina/review/taina_lineart_v05_v06_v07_compare_6x_v01.png
- Classificacao: local_note
- Candidato: nao_promover_sem_nova_evidencia

## L11 misturar rota Linux e Windows mascara incompatibilidade LTO

- Data: 2026-07-29
- Contexto: compilação da strip `taina_idle_guard` no host Manjaro Linux com o SGDK 2.11 canônico do workspace
- Falha observada: ResComp e fontes C passaram, mas a tentativa de link direto falhou; o fluxo Windows via `.bat`/PowerShell sob Wine também não representava uma rota Linux confiável e o incidente aparentava ser bloqueio do projeto
- Causa provavel: `sdk/sgdk-2.11/bin/gcc.exe` é GCC 13.2.0, enquanto a `sdk/sgdk-2.11/lib/libmd.a` contém LTO produzido por GCC 16.1.0; o agente não possuía um gate explícito que escolhesse a rota pelo host e comparasse a proveniência antes do link
- Mitigacao: executar `select_sgdk_build_route.py` antes do build; em Linux usar staging isolado + `build_sgdk_wine_bridge.sh` e biblioteca sem LTO; em Windows usar `build.bat` e bloquear mismatch até restaurar/reconstruir `libmd.a` com o compilador empacotado; nunca editar C/`.res` quando a evidência localiza a falha no link/toolchain
- Evidencia: out/logs/sgdk_build_route_report.json; out/logs/linux_wine_build_report.json; doc/10-memory-bank.md seção 17
- Classificacao: candidato_canonico
- Candidato: sgdk-build-wrapper-operator deve exigir seleção de rota por host e gate de proveniência LTO

## L12 gerar todos os frames por IA produz morphing em vez de animação

- Data: 2026-07-29
- Contexto: reconstrução da idle guard da TAÍNA a partir da fonte autoral aprovada como imagem 04, com pedido de seis quadros numa única prancha
- Falha observada: a direção de arte voltou no quadro isolado, mas cabeça, corpo, direção do rosto e eixo de apoio foram redesenhados ao longo da sequência; no proxy 48x64 houve 7 px de drift horizontal e 3 px de drift de altura
- Causa provavel: o modelo de imagem resolveu cada pose como uma nova ilustração semanticamente semelhante, sem conservar topologia pixel, pivot e massas do quadro anterior
- Mitigacao: gerar ou desenhar apenas uma pose-mestre; aprová-la em escala nativa; congelar pivot, ground e clusters de identidade; derivar os demais quadros por edição pixel controlada sobre a pose-mestre; medir bbox, contato dos pés e delta antes de qualquer promoção
- Evidencia: doc/art/characters/taina/animation/taina_idle_guard_v02_authorial_reconstruction_report.json; rascunho/taina_idle_guard_v02/taina_idle_guard_native_proxy_v02_8x.png
- Classificacao: candidato_canonico
- Candidato: sprite-animation deve proibir strips gerados de forma independente quando não houver prova de topologia e pivot compartilhados

## L13 captura automatizada sem confirmar cena e janela de input gera falsa evidencia

- Data: 2026-07-29
- Contexto: captura de idle, andar, correr, pulo e jab da ROM com o primeiro recorte do CAIS_01
- Falha observada: a primeira execução manual abriu a cena de boot porque o SRAM foi associado ao basename errado; nas duas tentativas seguintes, toques instantâneos não atravessaram um frame de leitura de `INPUT_pressed`, fazendo pulo e jab parecerem ausentes
- Causa provavel: a automação validava apenas existência do PNG, não identidade da cena nem duração mínima do input; eventos de borda dependem de `keydown/keyup` sustentado por VBlanks suficientes
- Mitigacao: iniciar a ROM pela injeção SBIS oficial com `--target-scene`; confirmar visualmente `SCN:DEMO`; para ações `pressed`, sustentar a tecla por pelo menos alguns frames e capturar dentro da janela ativa; mover qualquer sessão de cena errada para `out/evidence/rejected` e nunca agregá-la à prancha aceita
- Evidencia: `out/evidence/rejected/taina_cais01_runtime_v01_wrong_scene/`; `out/evidence/taina_cais01_runtime_v01/taina_cais01_runtime_contact_sheet_v01.png`; ROM SHA-256 `e1fc0dd5180ffb09f74087248f1d4d363ace93b5c1a74f0e307c1b8f3e05c1c6`
- Classificacao: local_note

## L14 efeito tecnico nao substitui composicao autoral

- Data: 2026-07-29
- Contexto: passe v03 do CAIS_01 com HSCROLL_LINE, reflexo, fumaça, poeira, palette cycling e contraluz funcionando no BlastEm
- Falha observada: apesar da evolução técnica, o céu, a cidade, o piso e os props perderam alinhamento com as fontes aprovadas e passaram a parecer formas genéricas coladas; a técnica elevou o movimento, mas não a autoria visual
- Causa provavel: o passe de efeitos começou antes de existir uma matriz de fonte por região e alterou macrogeometria, landmarks e material marks que deveriam ter permanecido congelados
- Mitigacao: antes de novo passe técnico, registrar source matrix, scene direction record, depth role map e composition schema; congelar massas, faixa jogável, landmarks e materiais; permitir que FX apenas animem, separem ou iluminem essas formas; comparar fonte, basic, elite e BlastEm no mesmo enquadramento
- Evidencia: doc/contracts/cais01_visual_source_matrix_v04.json; doc/art/environments/cais01/review/cais01_runtime_compare_v03_v04.png; ROM SHA-256 `825e687c8f0513f2d2d9f634f980be83426a2b84a457b0ddef6978271bfba429`
- Classificacao: candidato_canonico
- Candidato: visual-excellence-standards deve bloquear FX sobre composição sem source-region lock

## L15 selo de arquivo nao valida semantica de relatorio

- Data: 2026-08-30
- Contexto: cache de `forge-art convert` com job e `output_hashes` resselados.
- Falha observada: remover `metrics` de `conversion_report.json`, recalcular os
  hashes publicados e o selo do estado ainda permitia retorno de cache; os bytes
  estavam coerentes, mas o relatório não obedecia seu schema nem descrevia a
  conversão.
- Causa provavel: o núcleo imutável de jobs valida linhagem e evidência pixel
  genéricas, mas não conhece os campos semânticos de cada produtor de relatório.
- Mitigacao: manter `job.py` genérico e obrigar cada rota a revalidar seu
  relatório publicado. `verify_published_conversion()` valida schema, rederiva
  paleta/métricas, remede o PNG e casa hashes, rota, fonte, spec e estratégias.
- Evidencia: `forge_art.convert` fixture
  `rejects_resealed_invalid_conversion_report`; self-check 103/103.
- Classificacao: candidato_canonico
- Candidato: toda extensão de job com relatório semântico deve fornecer
  verificador pós-publicação específico, sem expandir o contrato genérico.

## L16 automacao de ponteiro nao e rota de producao deterministica

- Data: 2026-08-30
- Contexto: tentativa de construir e exportar lineart 48x64 no GIMP por observacao da area de trabalho e cliques do agente.
- Falha observada: alto consumo de contexto, baixa precisao de pixel e encerramento sem artefato verificavel, apesar de o GIMP possuir modo batch.
- Causa provavel: `interaction_channel_mismatch`; uma operacao automatizavel foi roteada para GUI e o historico documental ainda dizia que a autoria estava em progresso no GIMP recuperado.
- Mitigacao: CLI-first; usar forge-art/Pillow/ImageMagick para mecanica, GIMP batch apenas para operacao estatica registrada e GUI somente humana. Duas tentativas equivalentes sem evidencia encerram a rota, nao o projeto.
- Evidencia: `forge-art gimp-batch-preflight` no GIMP 3.2.4 com sentinel observado; `tools/sgdk_wrapper/.agent/workflows/causal-persistence-loop.md`; memory bank secao 36.
- Classificacao: candidato_canonico
- Candidato: skills/workflows que automatizam imagem devem classificar `interaction_channel_mismatch` e proibir ponteiro como rota produtiva deterministica.
