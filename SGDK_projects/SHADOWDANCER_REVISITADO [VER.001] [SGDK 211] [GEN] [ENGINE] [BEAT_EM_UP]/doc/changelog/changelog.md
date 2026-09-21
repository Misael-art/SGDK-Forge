# Changelog

## 2026-09-21 - conversao inicial SGDK 2.11

- criada copia canonica do engine em `SGDK_projects` sem alterar a origem;
- normalizados nome, `.mddev/project.json`, contexto e metodologia;
- explicitado `NONE` nos tilesets e mapas para compatibilidade com tile cache;
- removido heap do cache e substituido por buffers estaticos com limites;
- trocado DMA imediato por `DMA_queueDma` no callback do mapa;
- centralizados held/pressed do input e mantida ordem de loop SGDK;
- adicionados bounds de colisao e camera com dead zone/clamp;
- adicionados contratos de cena, QA, memoria, proveniencia e diagnostico de arte.
- build SGDK 2.11 concluido pela rota `linux_wine_bridge`, com ROM de 524288 bytes e SHA-256 `ee071686940c7f2f853b3f3120f9f2baf8d1bc4e5e0d3aeaf8081501a725eb54`;
- registrados snapshots versionados do build e dos 17 simbolos visuais para auditoria de frescor;
- registrados relatórios de conversao do tilemap, flags e conflitos de paleta.
- revalidado o projeto apos a renomeacao para `[BEAT_EM_UP]`; a validacao de recursos fecha sem erro de build/recursos, mantendo pendentes apenas os gates de closeout visual e BlastEm.
- registrada revisao formal `review_passed_with_risk`, sem API SGDK inventada, heap, float/double ou DMA imediato; permanecem pendentes somente provas de runtime e budget.

Status: buildado_emulator_pending; a validacao visual, o BlastEm e as medicoes de runtime ainda estao pendentes.
