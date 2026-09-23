# Prompt mestre — implementar Visual Forge e fechar as lacunas do MARE_BRAVA

**versao:** 1.1.0
**registro:** 2026-08-30
**tipo:** prompt operacional de implementacao, testes, aplicacao e retorno
**claim ceiling deste arquivo:** `documentado`

## Prompt para copiar integralmente

```text
[Contexto MD Carregado]

Voce e o agente principal responsavel por IMPLEMENTAR, TESTAR, INTEGRAR E
APLICAR a nova toolchain visual do workspace SGDKForge, e depois continuar o
MARE_BRAVA ate o menor fechamento AAA que possa ser honestamente provado.

Nao entregue apenas diagnostico, plano, esqueleto, pseudocodigo ou uma primeira
candidata. Trabalhe por milestones verificaveis, preserve o estado entre
iteracoes e continue enquanto houver uma acao segura, autorizada e causal que
remova blockers. Pare somente em gate humano real, dependencia externa sem
alternativa segura ou bloqueio comprovado. Quando parar, informe exatamente a
lacuna, as tentativas e o proximo input necessario.

BUDGET OPERACIONAL:
- nenhum teto de tokens/tempo foi especificado pelo owner;
- nao invente um teto;
- use checkpoints compactos por milestone;
- evite reabrir arquivos ja compreendidos sem mudanca de hash;
- use cache, reports e memoria para sobreviver a continuacoes de sessao;
- conclusao e definida pelos gates, nao por cansaco, numero de tentativas ou
  aparencia de progresso.

WORKSPACE:
/mnt/sdcard/Projects/Sgdk Forge

PROJETO ALVO:
/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects/MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

ARTEFATOS DE ENTRADA OBRIGATORIOS:
1. AGENTS.md e /home/misael/.codex/RTK.md.
2. doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md.
3. doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md.
4. tools/sgdk_wrapper/.agent/references/production_truth_protocol.md.
5. tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md.
6. tools/sgdk_wrapper/.agent/workflows/causal-persistence-loop.md.
7. skills: aaa-pipeline-guardian, art-conversion-pipeline,
   art-translation-to-vdp, megadrive-pixel-strict-rules,
   visual-excellence-standards, megadrive-vdp-budget-analyst,
   sgdk-build-wrapper-operator, emulator-vdp-evidence-curator e
   sgdk-code-reviewer quando codigo/runtime entrar.
8. No projeto: doc/10-memory-bank.md, doc/11-gdd.md, doc/13-spec-cenas.md,
   doc/00-diretrizes-agente.md, doc/23-visual-forge-adoption-plan.md,
   doc/contracts/visual_toolchain_reconciliation_v01.json,
   doc/contracts/visual_source_of_truth_taina_v02.json,
   doc/art/characters/taina/taina_reseed_native_translation_contract_v01.json,
   doc/art/characters/taina/visual_dna_manifest.json,
   doc/art/quality_reference_board.md e doc/human_approval_record.md.

REGRA DE FERRO:
"Se nao foi visto rodando no emulador, nao existe."
BlastEm e o gate de entrega. BizHawk pode complementar diagnostico, nunca
substituir o BlastEm.

DECLARACAO INICIAL DE CAPACIDADE:
Antes da primeira mutacao, execute o preparo/sonda exigidos pelo workspace e
declare exatamente um estado:
- capaz_com_prova_agora;
- capaz_apos_preparo_medido;
- nao_capaz_neste_host.

Nao use essa declaracao para encerrar cedo. Se uma GUI falhar, continue pelo
core CLI. Se uma dependencia opcional faltar, implemente ou use o fallback
documentado sem relaxar os gates.

PERSISTENCIA CAUSAL E CUSTO:
- trabalhe no blocker folha e meca um delta por tentativa;
- duas tentativas equivalentes sem evidencia nova encerram a rota, nao o projeto;
- operacao deterministica por screenshot/ponteiro e
  `interaction_channel_mismatch`: mude para CLI/headless;
- use forge-art para VDP/indexacao, Pillow/ImageMagick para mecanica e GIMP
  batch somente para operacao estatica registrada depois do preflight;
- GIMP GUI e humano/opcional; nao gere Python-Fu arbitrario pelo prompt;
- gate humano bloqueia apenas ramos dependentes; continue ramos realmente
  independentes e registre tudo no memory bank.

VERDADE DE PRODUCAO:
Classifique sempre separadamente:
- host_executor;
- toolchain_wrapper;
- rom_runtime;
- creative_quality.

Uma camada bloqueada nao prova falha nas outras. Nunca altere C ou asset para
consertar um erro que ainda pertence ao host/toolchain.

OBJETIVO A — RECONCILIAR SEM APAGAR HISTORICO

1. Audite o worktree e preserve mudancas existentes do usuario/outros agentes.
2. Trate doc/contracts/visual_toolchain_reconciliation_v01.json como a
   reconciliacao operacional vigente.
3. Harmonize, com historico append-only e hashes preservados:
   - as tres imagens 1086x1448 sao artisticamente aprovadas como referencias
     de construcao;
   - elas nao sao assets runtime e nao podem entrar diretamente em res/;
   - a prancha autoral permanece a fonte de identidade;
   - nenhuma lineart 48x64 esta aceita;
   - GIMP batch 3.2.4 passou preflight headless, mas possui zero operacoes de
     producao registradas; pointer automation nao e rota canonica;
   - a pasta/referencias `rejected/` precisam deixar claro que o nome e
     historico e nao rejeicao artistica vigente;
   - doc/04-recursos-e-pipeline.md precisa apontar para data/source_art,
     data/processed e res/;
   - runtime_probe.c/.h do projeto deve ser comparado ao modelo canonico e
     reconciliado somente se a diferenca for compreendida e testada.
4. Rode validators de contexto, metodologia, higiene, source of truth e
   freshness aplicaveis.
5. Gere um report de reconciliacao com divergencias removidas e restantes.
6. Existe evidencia de `visual_lineage_scan_read_failed` por profundidade de
   chamada ao ler JSONs. Reproduza, crie regressao positiva/negativa e corrija
   o parser/gate; nao altere assets ou relaxe o contrato para obter verde.

OBJETIVO B — IMPLEMENTAR O VISUAL FORGE NO NUCLEO COMPARTILHADO

Nao crie ferramenta canonica dentro do projeto. O core deve viver em
tools/image-tools e/ou tools/sgdk_wrapper, com schemas no wrapper e testes na
suite CI compartilhada. Decida a divisao por ADR depois de inspecionar o prior
art, sem duplicar logica.

Arquitetura minima:
- CLI `forge-art` com inspect, convert, translate, palette, atlas, tiles,
  validate, compare e promote;
- extensoes `forge-rom symbols/banks` e `forge-scene budget` podem entrar
  depois do core visual, mas nao podem ser esquecidas;
- jobs imutaveis por SHA-256;
- cache versionado;
- `--dry-run`, `--explain`, `--resume`, output JSON e codigos de erro;
- escrita atomica, rollback e locks para concorrencia;
- source nunca sobrescrito;
- nenhuma promocao automatica para res/;
- manifest de versoes, dependencias, origem e licenca.

Implemente uma biblioteca unica de cor:
- vdp_code 0..7 por canal;
- palavra CRAM;
- authoring RGB {00,22,44,66,88,AA,CC,EE};
- display RGB separado;
- rgb24_to_vdp_color;
- vdp_color_to_authoring_rgb;
- vdp_color_to_display_rgb;
- snap_rgb_to_vdp_grid;
- distancia RGB/HSV/OKLab;
- golden vectors contra headers/ResComp SGDK 2.11.

Proibido:
- tabelas divergentes copiadas em varios scripts;
- RGBA4444 tratado como CRAM;
- Lanczos/bilinear/bicubico para pixel art final;
- median-cut global tratado como direcao de arte;
- RGBA como output final de sprite;
- PLTE 256 com poucas cores unicas;
- remover transparencia compondo sobre preto;
- modificar input in-place;
- depender de mouse/GUI para o pipeline passar.

ROTAS OBRIGATORIAS:

1. technical_conversion
   - arte nascida pixel ou quase nativa;
   - nearest-neighbor;
   - index 0;
   - ate 15 cores visiveis;
   - PNG P, PLTE <=16, bit depth adequado;
   - grid 8x8;
   - bbox/pivot/baseline;
   - report tecnico;
   - pode gerar `basic_control` para high-res, mas nunca final.

2. assisted_native_translation
   - concept/high-res/IA, personagem heroico e cenario autoral;
   - semantic parse antes de pixels;
   - lineart 1 px no grid nativo;
   - paleta por material;
   - `original/basic/elite`;
   - fidelity e visual gate;
   - promocao somente apos pixel + visual + budget + emulator.

PALETA E DITHERING:
- index 0 isolado;
- 15 cores visiveis por paleta;
- slots semanticos por material;
- palette vitality;
- Bayer opt-in e deterministico;
- dither permitido em ceu/agua/pedra/nevoa/metal quando funcional;
- dither desligado para lineart, olhos, rosto, maos, outline e hit signal;
- nao chamar dither de alpha/blending.

SPRITES/ATLAS:
- envelope comum;
- bbox justo;
- bottom-center;
- pivots/contact points;
- strips por acao;
- remover islands/residuos;
- separar FX;
- motion GIF/WebP do output final;
- frame delta, foot contact, pivot overlay;
- determinismo, sem KMeans aleatorio ou fundo inferido cegamente.

TILES/CENARIOS:
- hashes estaveis exact/H/V/HV;
- tilemap flags preservados;
- heatmap de reuso;
- multi-paleta tile-aware;
- conflito por tile = blocker;
- world total != resident window;
- scene tilemap conversion report;
- modularidade, metatiles, streaming e seam policy;
- whole-image conversion apenas como basic/compare_flat honesto quando
  aplicavel, nunca como elite automaticamente.

FLIP DE BACKGROUND:
Implemente/canonize somente depois de testar:
- reversao de colunas + XOR de HFLIP;
- mascarar indice e preservar atributos;
- nenhum baseTileIndex somado a palavra com attrs;
- buffer estatico/rect write;
- bounds/VRAM/overlap;
- fixtures assimetricas normal/H/V/HV;
- API SGDK 2.11 confirmada nos headers;
- BlastEm e tilemap flag report.

ROM/SYMBOL/BANK:
Depois do core visual, implemente sem prejudicar P0/P1:
- parser CLI/JSON de symbol/map;
- ultimo simbolo e gaps corretos;
- ROM/RAM/codigo/dados/audio/arte separados;
- mapper/bancos parametrizados, sem hardcode SSF2;
- overlap, overflow, ocupacao e fragmentacao;
- heatmap usa SHA/canonical bytes, nunca hash() do Python;
- MAP Blocks permanece sugestao/debug, nunca colisao final.

LICENCAS E REFERENCIAS:
- SoftLK-tools/SLK_img2pixel: backend opcional se licenca CC0 for confirmada no
  snapshot incorporado;
- Tiled Palette Quantization: adaptar apenas sob MIT confirmado;
- sgdk-symbol-usage: base/referencia mediante licenca confirmada;
- Aseprite scripts, Ether e ferramentas Vagno: adaptadores/conceitos;
- nao copie repositorio publico sem licenca explicita;
- Oeste Editor/Discord ficam pendentes ate conteudo/licenca auditavel;
- registre URL, commit/tag, hash, licenca e arquivos incorporados.

OBJETIVO C — TESTAR O VISUAL FORGE COMO PRODUTO

Antes de aplicar no jogo, implemente e rode:

UNITARIOS:
- 512 cores e round-trip;
- limites/empates de snap;
- OKLab deterministico;
- alpha 0/255 e alpha parcial rejeitado;
- index 0;
- PLTE 1/16/17/256;
- bit depth 1/2/4/8;
- dimensoes irregulares/multiplos de 8;
- nearest vs filtros proibidos;
- exact/H/V/HV;
- simbolo final, gaps, bancos vazios e overflow.

GOLDEN/INTEGRACAO:
- cor comparada ao SGDK 2.11/ResComp;
- sprite 48x64 transparente;
- 15 cores + index 0 passa;
- 16 cores visiveis falha;
- tile com conflito de sub-paleta falha;
- atlas com pivot/footline;
- background 320x224 multi-paleta;
- tilemap assimetrica espelhada;
- fixture SGDK buildada e observada no BlastEm.

RESILIENCIA:
- mesma entrada/spec/versao gera mesmo SHA;
- interrupcao + resume;
- output parcial nao substitui aprovado;
- cache invalida por schema/tool;
- input corrupto falha fechado;
- dependencia opcional ausente gera explicacao/fallback seguro;
- source read-only intacto;
- concorrencia sem colisao;
- failure injection em save, quantizacao, ResComp e captura.

SELF-CHECK:
Toda ferramenta de medicao precisa de fixture que passa E fixture que reprova.
Rode validate_measurement_tools.py e corrija qualquer stale relevante antes de
usar as leituras em claims.

Nao relaxe testes existentes para obter verde. Se um teste antigo consagra
comportamento incorreto, primeiro crie regressao vermelha que prova o defeito,
depois atualize codigo e expectativa com justificativa/ADR.

OBJETIVO D — APLICAR NO MARE_BRAVA

TAÍNA:
1. valide a fonte de verdade;
2. gere basic_control deterministico sem promover;
3. crie elite em canvas nativo 48x64;
4. produza seis etapas: Base, Contornos, Volumes, Sombras, Iluminacao, Final;
5. preserve 3.5 heads, anatomia, rosto/olhos, cabelo, guarda, faixa,
   bandagens, roupa, materiais, assimetria e contato;
6. avalie em 1x, 8x e 320x224 sobre fundos claro/escuro;
7. emita model_sheet_to_sprite_fidelity_report;
8. se technical_pass=true e visual_pass=false, volte a lineart; nao polir o
   erro, nao usar candidata ruim como nova fonte;
9. apos lineart aprovada, faça paleta por material e idle/guarda;
10. produza os strips minimos do slice, com pivots, timing, motion preview,
    impact/recovery/hurt conforme contrato;
11. somente entao promova para res/ e integre.

GATE HUMANO:
Quando a aprovacao humana for obrigatoria, apresente um painel objetivo com
fonte, basic, elite e leitura em ROM. Nao promova enquanto aguarda. Continue
trabalho independente seguro: testes, reports, toolchain, cenario semantic
parse ou outro item nao dependente. Registre a decisao humana no arquivo
canonico quando recebida.

SEGUNDO PERSONAGEM:
Depois da TAÍNA atingir o piso visual minimo, avance para o personagem exigido
pelo vertical slice. Repita source validity, visual DNA, lineart, paleta,
movimento e budget. Meça ambos no mesmo pior quadro.

CAIS:
O cenario atual e probe tecnico e esta fraco para o claim AAA. Reautorar como:
- kit modular autoral;
- landmarks e narrativa ambiental;
- faixa jogavel legivel;
- BG_B atmosfera/respiracao;
- BG_A estrutura;
- atores como pico de leitura;
- foreground/oclusao com funcao;
- tiles/paletas/reuso/streaming medidos;
- ecology/FX ligados ao gameplay/mundo;
- original/basic/elite/rom;
- budget e BlastEm.

DEMAIS LACUNAS DO SLICE:
- FX com nascimento/pico/dissipacao e consequencia;
- HUD deixa de ser debug;
- audio real e validado;
- combate minimo funcional, incluindo invulnerabilidade ainda pendente;
- camera, colisao e input conforme contratos;
- pior quadro com personagens + HUD + FX;
- visual delivery e live scene bar.

OBJETIVO E — BUILD, EVIDENCIA E CLOSEOUT

1. Antes do primeiro build da sessao, rode preflight e
   select_sgdk_build_route.py.
2. Obedeça a rota selecionada. Nao misture Linux/Windows ou culpe C por LTO.
3. Use wrappers centrais.
4. Separe compilacao, link, ROM e pos-processamento.
5. Sele a ROM por hash e proiba rebuild durante captura.
6. BlastEm obrigatorio.
7. Screenshot, SRAM, visual_vdp_dump, metricas e manifesto do mesmo SHA.
8. Budget separa ROM, VRAM residente, preload, DMA/frame, animation window,
   scene-local e scanline.
9. Rode code review formal quando C/.res/runtime mudar.
10. Rode validation, freshness, promotion claims e scene closeout.
11. Atualize changelog, project memory bank e global memory quando a mudanca
    afetar o framework.
12. Execute audit_project_learning -Mode Capture; nao canonize aprendizado
    automaticamente sem a politica de curadoria.

GATES DE ACEITACAO DA FERRAMENTA:
- CLI/schemas implementados;
- unit/golden/integration/resilience/failure-injection verdes;
- source nunca sobrescrito;
- basic/elite/status impossiveis de confundir;
- sprite, background e tilemap ponta a ponta;
- oraculo SGDK/ResComp confirmado;
- report reproduzivel por outro agente;
- docs/memoria/changelog sincronizados.

GATES DE ACEITACAO DO MARE_BRAVA:
- TAÍNA visualmente aprovada e integrada;
- segundo personagem no mesmo piso;
- CAIS reautorado e aprovado;
- FX/HUD/audio/combate do slice fechados;
- budget do pior quadro fechado;
- ROM vigente observada no BlastEm;
- sete eixos de QA;
- live_scene_bar_report passed;
- validation/freshness/closeout sem blockers;
- aaa_pipeline_gate_report permite o claim.

Se a ferramenta estiver pronta mas o jogo nao, declare a ferramenta
`implemented` e o jogo no menor status provado. Nao confunda os dois.

PROTOCOLO DE INSATISFACAO:
Para cada asset/rota critica:
- gere;
- audite pisos numericos e semanticos;
- rejeite se um piso falhar;
- registre sintoma, diagnostico tecnico, heuristica preventiva e mudanca;
- execute minimo de 3 rounds quando houver geracao artistica, salvo se uma
  falha estrutural tornar o round seguinte inutil antes de correcao;
- nao reduza threshold para passar;
- depois de maximo razoavel de rounds sem ganho causal, declare lacuna honesta
  e mude a estrategia, nao apenas o seed.

FORMATO OBRIGATORIO DO RETORNO FINAL:

1. RESULTADO
   - o que foi realmente implementado;
   - status da ferramenta;
   - status do MARE_BRAVA.

2. ARQUIVOS
   - lista de arquivos criados/alterados e papeis.

3. TESTES
   - comando;
   - exit code;
   - passed/failed/skipped;
   - motivo de skip;
   - reports gerados.

4. ARTE
   - fonte/basic/elite/rom;
   - candidatos aprovados/rejeitados;
   - technical_pass e visual_pass separados;
   - aprovacao humana pendente ou registrada.

5. HARDWARE
   - ROM cost;
   - VRAM resident set;
   - preload DMA;
   - per-frame DMA;
   - active animation window;
   - worst scanline;
   - parecer cabe/cabe com recuo/nao cabe.

6. ROM/EVIDENCIA
   - SHA-256/tamanho;
   - rota de build;
   - BlastEm;
   - screenshot/SRAM/VDP dump/metricas;
   - freshness.

7. BLOCKERS
   - removidos;
   - mantidos;
   - novos;
   - proxima acao causal por blocker.

8. CLAIM HONESTO
   - documentado/implementado/buildado/testado_em_emulador/validado_budget;
   - ready_for_aaa true somente se todos os gates provarem.

Nao termine o retorno com "feito" se houver lacunas. Termine com a verdade do
estado e o proximo passo executavel.
```

## Observacao de uso

Este prompt autoriza implementacao dentro do workspace e do projeto indicado,
preservando o worktree. Nao autoriza copiar codigo sem licenca, publicar,
enviar mensagens externas, apagar historico ou relaxar gates.
