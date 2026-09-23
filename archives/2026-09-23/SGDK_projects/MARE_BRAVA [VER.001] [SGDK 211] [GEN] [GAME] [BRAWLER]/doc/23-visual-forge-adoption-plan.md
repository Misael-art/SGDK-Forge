# 23 — Plano de adocao do Visual Forge no MARE_BRAVA

**versao:** 1.1.0
**registro:** 2026-08-30
**status:** `partially_implemented_p1_cli_first`
**claim ceiling:** `technical_conversion_tested_no_visual_pass`

## Autoridade e proposito

Este plano ancora no projeto o diagnostico compartilhado em:

`../../doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md`

O estado machine-readable desta reconciliacao vive em:

`doc/contracts/visual_toolchain_reconciliation_v01.json`

Ele nao substitui GDD, memory bank, source of truth, contratos de arte, reports
de budget ou evidencia. Ele resolve o handoff entre a construcao da ferramenta
e a retomada artistica do jogo.

## Estado reconciliado da TAÍNA

- A prancha `taina_reseed_authorial_model_sheet_source_v01.png` e a fonte de
  identidade aprovada.
- As tres imagens 1086x1448 foram aprovadas artisticamente como referencias de
  construcao; tamanho/modo de cor impede apenas promocao direta.
- A pasta `rejected/` e nomenclatura historica inadequada, nao julgamento
  artistico vigente.
- Nenhuma candidata 48x64 foi aprovada como lineart final.
- GIMP 3.2.4 passou preflight `python-fu-eval` headless. Automacao de ponteiro
  foi encerrada; GUI e humana/opcional e ainda nao existe operacao GIMP de
  producao registrada.
- Um conversor pode gerar `basic_control`, nunca declarar por isso `elite`.
- A TAÍNA final precisa ser reconstruida no grid nativo e passar fidelidade.

## Ordem de trabalho

### Gate 0 — verdade e ferramenta

1. validar `visual_source_of_truth_taina_v02.json`;
2. reconciliar wording/path/status sem apagar hashes ou historico;
3. manter P0/P1 testados e fechar apenas os subcomandos ainda declarados
   incompletos, sem reimplementar `convert`;
4. provar que a ferramenta nao sobrescreve source nem promove sozinha;
5. reconciliar `runtime_probe.c/.h` com o wrapper canonico antes de usar nova
   telemetria em claims.

### Gate 1 — TAÍNA lineart

1. gerar `basic_control` deterministico da fonte aprovada;
2. usar o basic apenas como miniatura/controle de proporcao;
3. obter de produtor visual capaz uma `elite` construída diretamente em 48x64,
   lineart hard-edge 1 px; CLI/headless apoia conformidade, não autoria;
4. criar board Base/Contornos/Volumes/Sombras/Iluminacao/Final;
5. avaliar topologia, 3.5 heads, rosto, olhos, cabelo, guarda, faixa,
   bandagens, assimetria e contato com o chao;
6. emitir `model_sheet_to_sprite_fidelity_report`;
7. rejeitar `technical_pass_visual_fail` e retornar a lineart, sem polir erro.

### Política de continuidade

- seguir `workflows/causal-persistence-loop.md` quando uma ferramenta falhar;
- duas tentativas equivalentes sem evidência encerram a rota, não o projeto;
- operação determinística usa CLI-first;
- gate humano bloqueia somente os ramos dependentes da decisão;
- registrar blocker folha e próxima ação causal no memory bank.

### Gate 2 — TAÍNA color/paleta

1. congelar lineart aprovada;
2. definir slots por material;
3. reservar index 0 e compactar PLTE;
4. produzir palette vitality e contraste em fundo claro/escuro;
5. color blocking, sombras e highlights em etapas;
6. aprovar leitura nativa 320x224 e ampliacao 8x;
7. promover somente depois de pixel, visual, lineage e optimization reports.

### Gate 3 — TAÍNA movimento minimo do slice

- idle/guarda;
- locomocao necessaria ao slice;
- jab/ataque primario;
- hurt;
- acao adicional somente se estiver no escopo vigente.

Cada strip exige pivots, foot contact, timing/spacing, impact/recovery quando
aplicavel, preview animado do output final e aprovacao humana.

### Gate 4 — segundo personagem

Somente depois da TAÍNA fechar o gate visual minimo:

1. escolher o personagem exigido pelo vertical slice, conforme GDD/roster;
2. repetir source validity, visual DNA, lineart, paleta e movimento;
3. medir as duas entidades simultaneamente no pior quadro;
4. impedir que o segundo personagem reduza a TAÍNA abaixo da barra aprovada.

### Gate 5 — CAIS

O cenario atual e probe tecnico. A reautoria precisa:

- kit modular autoral;
- landmarks do cais e narrativa ambiental;
- faixa jogavel legivel;
- BG_B atmosferico e subordinado;
- BG_A estrutural sem competir com personagens;
- foreground/oclusao apenas quando servir composicao/gameplay;
- tile-aware multi-paleta;
- exact/H/V/HV dedup;
- streaming/janela ativa para mundo largo;
- ecology/FX com funcao, nao decoracao;
- comparacao `original/basic/elite/rom`;
- `scene_tilemap_conversion_report`, conflito por tile, flag report e budget.

### Gate 6 — FX, HUD, audio e combate

- FX em nascimento/pico/dissipacao e ligado ao evento de jogo;
- HUD deixa de ser telemetria/debug;
- audio implementado e validado com gameplay;
- combate minimo comprovado, inclusive invulnerabilidade ainda pendente;
- pior quadro: TAÍNA + segundo personagem + inimigo/boss aplicavel + HUD + FX;
- separar custo ROM, VRAM residente, preload, DMA por frame e scanline.

### Gate 7 — ROM e closeout

- selecionar rota de build pelo wrapper;
- build sem reconstruir durante captura;
- ROM selada por SHA-256;
- BlastEm obrigatorio;
- screenshot, SRAM, VDP dump e metricas do mesmo hash;
- visual delivery, live scene bar, validation, freshness e closeout coerentes;
- sete eixos de QA reportados;
- claim final limitado ao menor gate provado.

## Blockers atuais preservados

- `accepted_native_lineart_missing`;
- `visual_source_document_drift`;
- `visual_toolchain_p0_pending`;
- `runtime_probe_project_copy_stale`;
- `visual_lineage_scan_read_failed` (o validador de source of truth excede a
  profundidade de chamada ao ler JSONs do projeto; corrigir o parser/gate sem
  alterar arte para mascarar a falha);
- `validation_report_missing_or_stale`;
- `build_output_report_missing_or_stale`;
- `taina_fidelity_not_passed`;
- `second_character_visual_not_passed`;
- `cais_final_art_not_passed`;
- `audio_not_closed`;
- `budget_not_closed`;
- `live_scene_bar_report_missing_or_failed`;
- `ready_for_aaa=false`.

## Politica de retorno do agente

Ao final de cada ciclo, o agente deve retornar:

1. objetivo atacado;
2. arquivos criados/alterados;
3. testes executados e resultados;
4. outputs visuais apresentados;
5. blockers removidos, novos ou mantidos;
6. status tecnico, visual, budget e emulador separados;
7. hash da ROM quando houver build;
8. proxima acao causal;
9. lacunas honestas e qualquer dependencia externa.

Nenhum retorno pode usar `pronto`, `AAA`, `final` ou `entregue` sem os reports
correspondentes e evidencia fresca.
