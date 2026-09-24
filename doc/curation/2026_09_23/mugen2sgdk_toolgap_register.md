# Registro de lacunas e ferramentas — MUGEN

**Proposta; estimativas em dias de trabalho técnico, não garantia de prazo.** Evidência está em validation/, evidence/ e nas fontes do índice. P0 impede closeout; P1 impede fidelidade/AAA; P2 reduz reprodutibilidade.

## O que já funciona e o alcance da prova

|Ferramenta|Verificação desta curadoria|Limite|
|---|---|---|
|Conversor/parser/IR/gerador|39 testes pytest passaram sem skips neste host|Ken/zip local não está disponível em todo CI; classificar direct não prova equivalência|
|Harness C|Movimentos, combate CPU, anel/helper e sparks incluídos na suíte|Stubs não provam VDP/DMA/Z80 nem tempo68000|
|vdp_scanline_simulator|Self-check passou, incluindo pixels/contagem/H32|Não conectado automaticamente à composição completa do conversor|
|Captura BlastEm/seal|Cinco hashes P5 conferidos; imagem inspecionada|Evidência histórica; não nova execução e não áudio|
|audiovisual_review|CLI e owner existem; pipeline HAMOOPIG não transfere aprovação ao Ken|`--self-check` não é opção desse CLI: tentativa retorna2; não declarar medição aprovada por ela|
|Provenance auditor|Executado; bloqueou manifesto inválido e outros findings|Bitmap lógico neg1_masks gera falso positivo; precisa regressão seletiva|
|Adoption/context/hygiene|Adoption não alterou manifests; context/hygiene bloquearam|Falta saneamento do projeto; não ampliar claims|

## Adaptações existentes

Split de quadros esparsos; BGFX por paleta e espelhamento; helper reduzido; pool fixo; bytecode/fixed-point; command gating; HUD de tiles; derivação de sombra/dither. Todas têm custo/limitação no catálogo, e nenhuma justifica ignorar perdas.

|ID/prioridade|Lacuna e evidência|Impacto|Proposta/owner|Esforço|Aceite|
|---|---|---|---|---|---|
|G01 P0|Contexto/higiene/proveniência incompatíveis. validators executados: context=unclassified; higiene blocked; enum fora do schema|Bloqueia entrega e rastreabilidade; efeitos em cascata confundem diagnóstico|Reconciliar manifests existentes; adaptar conversão ao schema sem inventar enum; registrar símbolos/hashes e permissões. Owner: guardian + build-wrapper|1–2 dias|Todos os validadores passam; ausência de permissão continua explícita e limita distribuição|
|G02 P0|Falso positivo em neg1_masks. gerador: bitmap de command gates; runtime apenas operações bitwise; auditor chamou de pixels|Bloqueio indevido pode incentivar bypass perigoso|Auditor com análise de uso/sink e fixtures tabela lógica versus tiles reais; não allowlist por nome. Owner: code-reviewer + provenance|1–2 dias|Bitmap não bloqueia; array de pixels que chega ao VDP continua bloqueado, mesmo renomeado|
|G03 P0|CPU acima do budget e falta de baseline com áudio. P5 591/2191, pico158%; DMA null; audio dummy|Impede combate fluido; aumentar FX antes de fechar custo amplia defeito|Harness determinístico de ROM com perfil por etapa; confrontar baseline/fx-off/fx-on no mesmo input e configuração. Owner: runtime-coder + budget + audio|3–6 dias|Zero deadline perdido no corpus acordado de combate; startup/preload separados; contadores sem saturação; áudio ativo|
|G04 P0|Capacidades truncadas sem prova de rejeição. slices255 no gerador; -1 words limitado8; MAX_CMDS160 PROG/LIVE32|Personagem pode compilar perdendo transições e animações|Preflight de limites e falha explícita com origem; testes abaixo/no/acima; política de pool saturado. Owner: runtime-coder|2–3 dias|Nenhum truncamento silencioso; diagnóstico cita estado/elemento e capacidade; corpus normal preservado|
|G05 P1|Cobertura semântica nominal ausente. 126estados/796controladores no report; teste apenas limiar de estados distintos|Teste vivo não demonstra golpes, throws e defesa corretos|Manifesto state/controller/transition coverage com IDs; host+ROM; oráculos juggle/priority/re-hit/HitOverride. Owner: collision + fighting + runtime|4–7 dias|Cada regra do escopo tem witness/esperado/resultado; estados não alcançados permanecem needs_review|
|G06 P1|Budget automático da composição convertido→SAT. hw_over_limit=[] trata assets; simulador existe; P3 depende de script no histórico|Pode estourar scanline com dois corpos+HUD+FX mesmo assets válidos|Adaptador rescomp/SAT por frame, ambos limites e cenário adversarial; VRAM/dma/preload separados. Owner: budget + streaming|3–5 dias|Inputs/resultados persistidos; self-check passa; teste sintético viola pixels sem violar contagem e é rejeitado|
|G07 P1|Ownership temporal de paleta. PAL0 HUD9..15 versus BGFX1..14; HUD oculto durante super|Cores erradas após retorno/interrupção; teste de asset isolado não detecta|Auditor por slot/intervalo com restauração, shared palette e cenário2personagens. Owner: budget + visual + scene-state|2–4 dias|Colisão simultânea é bloqueada; uso serial com restore é aceito; KO/pause/revanche não deixam cores stale|
|G08 P1|Loss manifest incompleto. 46blend; missing_frame_sprites50; mirror4 e erro0 não reconciliados|Conversão silenciosa elimina intenção artística e regra|Exportar perdas por source_hash/action/element/controller; separar crop/mirror/quantização/omissão/limite. Owner: conversion + runtime|2–4 dias|Toda perda classificada e ligada a output; sem dívida desconhecida no lote aceito; aprovação humana por classe visível|
|G09 P1|Regressão focal SuperPause. pos enums corretos; fixture de schema sem caso explícito; harness só verifica ativação|Erro pode reaparecer sob outro controlador/ordem|Fixture sintética com parâmetros distintos, pos não zero, facing±, time/movetime/sound. Owner: runtime-coder|0,5–1 dia|Asserções de valores gerados e coordenadas/ticks exatos no C; mutação de índice faz teste falhar|
|G10 P1|SND→XGM2 existe, fidelidade sonora não fechada. sounds.py; MG_playSound AUTO; P5 dummy|StopSnd/mix/canais podem interromper vozes; resample linear pode degradar espectro|Contrato de canais SND+PlaySnd/StopSnd, captura real, teste de prioridades e audição A/B. Owner: xgm2-audio-director|3–5 dias|Voz+BGM+impactos sem clipping/cortes indevidos; regiões/driver/ROM registrados; qualidade revisada ouvindo|
|G11 P1|Regressão visual temporal não integrada ao conversor. audiovisual_review existe; bundle P5 só burst0,4s|Frames estáticos ocultam jitter, stalls, restauração e perdas de quadros|Cenários determinísticos hash-bound com AV contínuo, ROIs por ação, busca de regressões e revisão por intervalo. Owner: evidence-curator + visual + animation|4–6 dias|Integridade/cadência/AV-sync/qualidade/coverage independentes; referência pode diferir pixel sem falhar se aproximação autorizada|
|G12 P2|Lições herdadas e documentos stale. the_forge_opening_lessons e README helper/HUD contradizem código|Agente aprende sucesso que pertence a outro projeto|Índice único por lesson ID/commit/evidence/owner; bootstrap separa template/inherited/local; lint de deriva. Owner: learning-loop + doc-sync|2–3 dias|Novo projeto não atribui lições importadas a evidência local; índice não duplica status; fontes antigas preservadas|
|G13 P2|Portabilidade/reprodutibilidade de testes. host exige Ken foraGit; lifebar fixture aponta outro workspace e pode skip|CI verde parcial aparenta cobertura que não existiu|Fixtures sintéticas para semântica e caminhos por manifesto local; relatório obrigatório de skips e corpus privado. Owner: build-wrapper + reviewer|2–3 dias|Clean checkout roda core sem terceiro; integração privada identifica hashes/licença/skip como coverage_gap|
|G14 P2|Entrada de pacote ambígua. Source indexa nomes lowercase e resolve basename fallback|Arquivos homônimos/versões não suportadas podem resolver pacote errado|Diagnóstico de colisões de paths/case e limites de tamanho/contagem para ingestão. Owner: conversion|1–2 dias|Pacote ambíguo é rejeitado com candidatos; SFFv2 recebe unsupported explícito, não sucesso vazio|

## Proveniência e aproximações: contrato proposto

Não adicionar `third_party_mugen_conversion` improvisadamente ao enum. Selecionar source_kind existente que descreva a transformação real e declarar cadeia de autoria/fonte/hash; se o schema não comportar os dados, propor extensão validada antes de escrever campos extras. Ex.: registro lateral versionado `conversion_loss_manifest` com source_package_hash, converter_commit/config_hash, source_object, output_symbol/output_hash, transformation, fidelity, reason, visual_impact, budget_tradeoff, reviewer/verdict e evidence_ids. Vincular seu hash ao manifesto em campo permitido ou à extensão aprovada.

Hash/proveniência não concede licença. `technical_candidate` no relatório do conversor não vira automaticamente acceptance_status canônico. O auditor deve apontar erro de schema como raiz e separar achados dependentes; corrigir neg1_masks não limpa assets de branding de primitivas nem a permissão de terceiros.

## Performance: integração, não criação de doutrina do zero

A hipótese “nenhum skill obriga budget antes de FX” foi **contestada**: budget-analyst linha8 já exige revisão antes de aprovar efeitos, e linhas24/133 cobrem worst-frame/CPU. Proposta G03/G06 torna esse contrato executável no fluxo MUGEN. Perfil precisa de região, relógio, reset, unidade, versão de probe, denominador e áudio. `getSubTick` é76.800/s; usar duração regional real, não transferir1280 nominal a PAL. Report de captura com null nunca vira0.


## Limitação adicional da probe (inspeção da fonte atual)

`src/system/runtime_probe.c` incrementa o contador de frames antes de sair pelos 90 frames de warmup; o contador over_budget só é incrementado depois. Assim, 591/2191 é quociente bruto entre campos, não taxa exata de deadline miss do período medido. Se a ROM histórica usou exatamente este contrato, o denominador pós-warmup seria2101; reconstruir essa identidade antes de substituir o report. A conclusão segura é que há ocorrências acima do limiar100 e nenhuma prova de cadência estável.

A função measure_max_scanline_sprites varre224linhas e conta componentes FrameVDPSprite; não soma pixels por linha. Isso é melhor que amostra de poucas linhas, mas ainda não fecha ambos os limites VDP. O self-check do simulador offline não valida automaticamente essa probe C. Adicionar fixture de largura que passe20sprites e exceda320pixels, e comparar contra SAT/telemetria independente. Registrar overhead do profiler/probe com e sem instrumentação. G03/G06 incluem esse trabalho; valores antigos não viram orçamento aprovado.


Outra fronteira para G04/G06: `draw_part` retorna sem desenhar ao falhar SPR_addSpriteEx e esconde a parte quando SPR_setDefinition falha. É fallback implementado, mas não aprovação de perda visual: contar falhas por objeto/quadro e bloquear aceite de personagem/FX essencial descartado.
