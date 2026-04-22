<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-04-21T22:53:07.2112938-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 0
- Ultimo build versionado: build_v001
- ROM vigente: `b3359b94962ea82511fff16fde2e9cd8b7143f3ee9ff88b2a63ef74f0f56ac68` (`131072` bytes)
- Validation summary: errors=0 warnings=0
- Blockers vigentes: nenhum
- Evidencia de emulador: sem_sessao
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=nao_testado audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank

## Estado operacional

- projeto: `BENCHMARK_VISUAL_LAB_V2`
- estado: `buildado`
- fase atual: fundacao implementada com placeholders e contratos canonicos de budget em atualizacao
- objetivo vigente: manter GDD, spec de cenas, budget e `.agent` local coerentes antes de promover assets reais ou validar cenas no emulador

## Regras vigentes desta abertura

- progresso em uma entrega por vez
- cada etapa depende de validacao humana antes da seguinte
- aprendizados podem ser registrados como observacao local, mas nao sobem para curadoria canonica sem validacao explicita do diretor
- nenhuma cena sera declarada `testada_em_emulador`, `validado_budget` ou `ready_for_aaa` antes de evidencia fresca em BlastEm e laudo de budget por cena
- separar sempre ROM/compressao, VRAM residente, DMA de preload, DMA por frame, janela ativa de animacao e pior scanline

## Verdade atual

- existe `project_brief`, `core_loop_statement`, `feature_scope_map`, `scene_roadmap`, `first_playable_slice` e `front_end_profile`
- existem `src/`, `res/`, `out/rom.bin`, `doc/changelog` e `out/logs/validation_report.json`
- o build vigente esta limpo na validacao estrutural, com ROM `b3359b94962ea82511fff16fde2e9cd8b7143f3ee9ff88b2a63ef74f0f56ac68`
- `res/resources.res` ainda esta em modo placeholder code-only; nao ha assets reais aprovados para budget final
- nao existe evidencia BlastEm vinculada a esta ROM; `testado_em_emulador=false`
- `validado_budget=false`; os novos campos de budget semantico estao documentados, mas ainda nao medidos com assets reais
- a V1 serve como referencia historica e banco de aprendizado, nao como baseline automatico de implementacao

## Curadoria pendente

- pontos de aprendizado herdados da V1 permanecem como referencia operacional
- promocao desses pontos para workflow, skill, regra ou `lib_case` depende de validacao humana apos uso real na V2
- proxima etapa segura: introduzir assets por cena somente depois de preencher `doc/07-budget-vram-dma.md` e manter `doc/13-spec-cenas.md` com `scene_local_scope`, `vram_resident_set`, `per_frame_dma_cost` e fallback por cena
