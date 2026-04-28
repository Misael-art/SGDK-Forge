# Workflow: Plan

Use este fluxo para qualquer trabalho multi-arquivo ou que altere estado, wrapper, budgets ou docs.

1. Carregue a hierarquia de verdade do projeto.
2. Classifique o pedido em escopo real, extensao planejada ou correcao operacional.
3. Liste arquivos afetados.
4. Declare riscos em hardware, build e documentacao.
5. Separe implementacao real de arquitetura futura.
6. Se a rota tecnica ainda nao estiver declarada, preencha `workflows/route-decision-gate.md` antes de converter asset, editar `.res` ou escrever runtime.
7. Se a entrega envolver cena `aaa_layered`, preencha `workflows/scene-architecture-triage.md` antes de detalhar VRAM, paleta, `rescomp`, `WINDOW` ou sprite runtime.
8. Registre se a decisao arquitetural da cena sera `adotar`, `adaptar` ou `divergir` do baseline `tilemap streaming guiado pela camera`.
