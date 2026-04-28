# 00 - Diretrizes do Modelo

Este worktree existe para servir como base segura e editavel.

Regras:
- projeto novo ou escopo ainda difuso deve passar primeiro por `planning/game-design-planning` antes de abrir arte ou runtime;
- projeto novo, reseed ou cena sem familia tecnica declarada deve emitir `route_decision_record` via `workflows/route-decision-gate.md` antes de converter asset, editar `.res` ou escrever runtime;
- cena com parallax, foreground/oclusao, source grande ou referencia interna deve passar por `scene_architecture_triage` e medir janela/painel antes de assumir `IMAGE` residente;
- build, clean, rebuild e run sempre via wrapper;
- assets brutos entram em `res/data/`;
- saida final pronta para o SGDK fica em `res/`;
- alteracoes estruturais devem ser refletidas na documentacao;
- codigo novo deve preservar legibilidade e limites do Mega Drive.
- menu, title screen e front-end devem nascer com identidade declarada no GDD, nao como placeholder tardio.
- os gates finais de `visual_lab_aprovado`, `audio`, `hardware_real` e `ready_for_aaa` devem ter trilha explicita em `doc/14-plano-de-provas-qa.md`.
