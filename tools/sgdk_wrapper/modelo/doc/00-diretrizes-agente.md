# 00 - Diretrizes do Modelo

Este worktree existe para servir como base segura e editavel.

Regras:
- projeto novo ou escopo ainda difuso deve passar primeiro por `planning/game-design-planning` antes de abrir arte ou runtime;
- build, clean, rebuild e run sempre via wrapper;
- assets brutos entram em `res/data/`;
- saida final pronta para o SGDK fica em `res/`;
- alteracoes estruturais devem ser refletidas na documentacao;
- codigo novo deve preservar legibilidade e limites do Mega Drive.
- menu, title screen e front-end devem nascer com identidade declarada no GDD, nao como placeholder tardio.
