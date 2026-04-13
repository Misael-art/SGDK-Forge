# Workflow: AAA Scene Pipeline (roteamento)

Ordem canonica para uma **cena visual** de barra AAA. Detalhe tecnico vive nas **skills** referenciadas; aqui so **sequencia**, **I/O** e **passagem**.

Fonte machine-readable: `pipelines/aaa_scene_v1.json`.

---

| # | Etapa | Entrada minima | Saida minima | Passa quando |
|---|--------|----------------|--------------|--------------|
| 0 | Escopo (humano) | `doc/11-gdd.md`, `doc/13-spec-cenas.md` | Briefing com criterios de aceitacao | Escopo fechado sem creep |
| 1 | `art/art-asset-diagnostic` | `res/`, `res/data/` | Classificacao do cenario de arte | Rota clara (converter / traduzir / gerar) |
| 2 | `art/multi-plane-composition` | Mapa de composicao + spec de cena | `hardware_budget_review` / plano de planos | Planos e parallax acordados |
| 3 | `art/art-translation-to-vdp` | PNG fonte forte | PNG SGDK-validos em `res/gfx/` | Grid 8x8, paleta, leitura por plano |
| 4 | `art/visual-excellence-standards` | Layers por plano | Parecer estetico (ex. `doc/aesthetic_report.md`) | Sem gate visual bloqueante no validador |
| 5 | `hardware/megadrive-vdp-budget-analyst` | `.res`, dimensoes, cena | Decisao `cabe` / recuo / `nao cabe` | Budget explicito antes de prometer ROM |
| 6 | `code/sgdk-runtime-coder` + `scene-state-architect` | Specs + `.res` | `out/rom.bin`, build OK | Compilacao limpa; cena integrada |
| 7 | `validate_resources.ps1` | `res/*.res` | `out/logs/validation_report.json` | `summary.errors == 0` (politica do projeto) |
| 8 | QA humano + `build-validate.md` | ROM + logs | BlastEm + `emulator_session.json` + memory bank | Evidencia rastreavel; 7 eixos quando exigidos |

---

## Dependencias

- **Antes do passo 6**: `tools/sgdk_wrapper/preflight_host.ps1` (Java, make, GDK, Python/Magick recomendados).
- **Nao saltar o passo 5** antes de declarar que o tile budget “cabe”.
- **Regra de ferro do repo**: ver `AGENTS.md` — sem emulador, nao existe.
