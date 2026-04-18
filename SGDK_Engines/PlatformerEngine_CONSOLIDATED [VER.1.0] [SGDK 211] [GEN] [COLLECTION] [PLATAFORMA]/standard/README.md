## PlatformerEngine

Este projeto faz parte do ecossistema **MegaDrive_DEV** (SGDK 2.11).

### Build / Run (obrigatorio via wrapper canonico)
- uild.bat: compila o ROM usando 	ools\sgdk_wrapper\
- un.bat: executa em emulador (auto-build se necessario)
- clean.bat: limpa artefatos
- ebuild.bat: clean + build

### Regras para Agentes de IA (obrigatorio)
- **Nao duplicar** logica de build nesses .bat. Toda logica fica em F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\.
- **Hierarquia de verdade / governanca**: siga AGENTS.md, CLAUDE.md e a documentacao do projeto (ex.: doc/ e doc/10-memory-bank.md quando aplicavel).
- **SGDK / Mega Drive**: sem loat/double, sem malloc/free em gameplay loop, sem inventar APIs, respeitar budgets de VRAM/DMA/sprites.
- **Ciclo de producao**: planejar â†’ implementar â†’ build pelo wrapper â†’ validar (emulador) â†’ atualizar docs (handoff).

### Estrutura esperada do worktree
\inc, \res, \src, \doc, \.mddev, \out (artefatos), alÃ©m dos wrappers .bat.
