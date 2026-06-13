# 00 - Diretrizes do Modelo

Este worktree existe para servir como base segura e editavel.

Regras:
- antes de qualquer arte, runtime ou build, classificar `doc/project_methodology_manifest.json` e executar `workflows/project-methodology-adoption.md`;
- o nome real do diretorio, `.mddev/project.json` e `project_methodology_manifest.json` devem permanecer coerentes com o documento do workspace `doc/PADRAO_NOMENCLATURA.md`, sem `__PROJECT_NAME__`;
- todo material operacional, evidencia e experimento deve permanecer dentro do projeto;
- tecnica catalogada deve ser declarada por `registry_id` e tags em `doc/technique_usage_manifest.json`;
- projeto novo ou escopo ainda difuso deve passar primeiro por `planning/game-design-planning` antes de abrir arte ou runtime;
- projeto novo, reseed ou cena sem familia tecnica declarada deve emitir `route_decision_record` via `workflows/route-decision-gate.md` antes de converter asset, editar `.res` ou escrever runtime;
- cena com parallax, foreground/oclusao, source grande ou referencia interna deve passar por `scene_architecture_triage` e medir janela/painel antes de assumir `IMAGE` residente;
- build, clean, rebuild e run sempre via wrapper;
- assets brutos entram em `res/data/`;
- saida final pronta para o SGDK fica em `res/`;
- alteracoes estruturais e tecnicas usadas devem ser refletidas em `doc/13-spec-cenas.md`, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`;
- `freshness_audit` e obrigatorio antes do closeout para detectar documentacao ou evidencia obsoleta;
- codigo novo deve preservar legibilidade e limites do Mega Drive.
- menu, title screen e front-end devem nascer com identidade declarada no GDD, nao como placeholder tardio.
- os gates finais de `visual_lab_aprovado`, `audio`, `hardware_real` e `ready_for_aaa` devem ter trilha explicita em `doc/14-plano-de-provas-qa.md`.
