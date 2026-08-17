# AGENTS.md — MegaDrive_DEV

> **Ponto de entrada obrigatorio para qualquer agente de IA neste workspace.**
> Diga `[Contexto MD Carregado]` antes de propor qualquer acao.

---

## REGRA FINAL DE FERRO

**"Se nao foi visto rodando no emulador, nao existe."**
Intencao nao e validacao. ROM rodando em 60fps constantes sim.

---

## FRAMEWORK CANONICO DE AGENTES

O workspace usa o framework `.agent` centralizado em `tools/sgdk_wrapper/.agent/`.
Cada projeto recebe uma materializacao local via bootstrap automatico.

```
tools/sgdk_wrapper/.agent/
  ARCHITECTURE.md          ← leia para entender o framework
  rules/SGDK_GLOBAL.md     ← regras sempre ativas
  agents/                  ← personas especializadas
  skills/                  ← conhecimento por dominio
  workflows/               ← runbooks operacionais
  scripts/                 ← automacoes de auditoria
```

**Politica de sobrescrita: `.agent` local existente nao e sobrescrita.**

### Compatibilidade Codex Skills

Para descoberta nativa de skills pelo Codex em nivel de repositorio, o workspace expõe `.agents/skills` como ponte de compatibilidade.

- `.agents/skills` aponta para `tools/sgdk_wrapper/.agent/skills`
- a fonte canonica continua sendo `tools/sgdk_wrapper/.agent/skills`
- nao duplique nem edite skills em uma segunda arvore paralela

### Bootstrap consultivo comum

No primeiro uso de uma sessao em qualquer superficie de agente/IDE (`.cursor`, `.serena`, `.superpowers`, `.trae`, `.agents`, `.claude`), rode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1
```

Essa guarda chama o preparo automaticamente, valida pontes de skills, instala/prepara Graphify quando necessario, serializa updates concorrentes por lock global e deixa o grafo consultivo `fresh`. Graphify deve ser usado somente via `pwsh` e pelo wrapper `tools/sgdk_wrapper/graphify_forge.ps1`; nunca use `graphify query` direto e nunca trate `graphify-out/` como fonte de verdade.
Ela tambem prepara a camada opcional `ai-memory` de forma controlada via `tools/sgdk_wrapper/prepare_ai_memory_integration.ps1`: cria apenas marcadores `.ai-memory.toml`, politica local e report consultivo. Nao instala hooks/MCP globais, nao roda bootstrap/auto-improve e nunca substitui memory bank, learning ledger, validators, Graphify, changelog ou evidencia de emulador. Politica: `doc/AI_MEMORY_POLICY.md`.
O menu canonico `tools/sgdk_wrapper/show_agent_menu.ps1` tambem chama essa guarda automaticamente, exceto se `SGDK_SKIP_AGENT_ENVIRONMENT_GUARD=1`.

---

## MENU DE SESSAO / MODOS DE OPERACAO

Quando o usuario pedir `menu`, `modo`, `iniciar`, `abrir sessao` ou quando a intencao inicial estiver ambigua, use:

- workflow: `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md`
- estado: `doc/agent_session_state.json`
- schema: `tools/sgdk_wrapper/schemas/agent_session_state.schema.json`
- renderizador: `tools/sgdk_wrapper/show_agent_menu.ps1`

Modos canonicos:

```
[CRIAR NOVO PROJETO DE JOGO DE MEGA DRIVE] -> create_new_project
[ANALISAR PROJETO EXISTENTE]              -> analyze_existing_project
[TREINAR AGENTE]                          -> train_agent
[LABORATORIO]                             -> laboratory
[CURADORIA]                               -> curation
```

Regra de uso:

- pedido direto e claro nao deve ser atrasado pelo menu;
- troca de modo exige consentimento humano;
- troca de perspectiva exige `tools/sgdk_wrapper/.agent/workflows/perspective-switch-gate.md`;
- treino vive em `SGDK_projects/_agent_training/`;
- laboratorio vive em `SGDK_projects/_agent_laboratory/`;
- curadoria canonica so pode alterar `tools/sgdk_wrapper/.agent/`, `tools/sgdk_wrapper/` ou `doc/` com aprovacao humana explicita, testes e memoria atualizada;
- o estado de sessao e auxiliar e nunca substitui memory bank, GDD, TDD, manifests, reports ou evidencia de emulador.

---

## HIERARQUIA DE VERDADE

| # | Fonte | Autoridade |
|---|-------|------------|
| 1 | `doc/10-memory-bank.md` | Estado operacional real |
| 2 | `doc/11-gdd.md` | Design e escopo do jogo |
| 3 | `doc/13-spec-cenas.md` | Budget real por cena |
| 4 | `doc/00-diretrizes-agente.md` | Regras de processo |
| 5 | `doc/project_context_manifest.json` | Tipo de trabalho e bloqueios proporcionais |
| 6 | `doc/12-roteiro.md` | Roteiro e dialogos |
| 7 | `doc/03-arquitetura.md` | Estrutura de codigo |
| 8 | `.mddev/project.json` | Manifesto estrutural |
| 9 | Headers SGDK `sdk/sgdk-2.11/inc/` | API definitiva |
| 10 | Suposicao / memoria | Ultima prioridade — nunca especular |

---

## RESTRICOES NAO NEGOCIAVEIS

```
❌ float / double        — use fix16/fix32
❌ malloc / free         — use buffers estaticos no loop
❌ APIs SGDK 1.60        — ver tabela de migracao
❌ DMA fora do VBlank    — apenas seguro no VBlank callback
❌ Logica de build em projeto — apenas em tools/sgdk_wrapper/
❌ Inventar API do SGDK  — verificar header antes de usar
❌ Declarar "pronto" sem ROM rodando no emulador
❌ Grafico desenhado por codigo como personagem, inimigo, boss ou cenario final
❌ Simbolo visual em res/*.res sem proveniencia declarada
❌ Fechar orcamento sem medir o degrau seguinte — folga nao medida e timidez
```

---

## DOUTRINA DE AUDACIA

**O teto do hardware e o alvo, nao a margem de seguranca.**

Entregar uma cena a 40% do orcamento sem ter medido ate onde dava nao e prudencia: e uma
decisao que ninguem tomou. Antes de fechar qualquer budget, meca o degrau seguinte. Se 32
objetos cabem, meca 48 e 64. Pare quando **medir** o estouro, nao quando sentir receio.

**Audacia e sobre a ambicao, nunca sobre o claim.** Empurre o que voce tenta; meca o que voce
afirma. Quanto mais ousado o alvo, mais rigorosa precisa ser a medicao. Ambicao alta com claim
medido e o padrao. Ambicao baixa desperdica hardware. Claim alto sem medicao e falso verde, e
o resto deste documento ja bloqueia isso.

**Direcao de arte, level design e as premissas do projeto vencem a densidade** — mas por
declaracao, nunca por omissao. "Menos sprites porque a cena precisa respirar" e razao
legitima; silencio nao e.

**Falsa audacia** e a que parece ousada e piora o resultado: flicker para mascarar overflow,
efeito sem consequencia, densidade que destroi leitura de silhueta. O canon bloqueia cada uma,
e nenhuma vira permitida em nome de ser ousado.

O VDP impoe **dois** limites por scanline ao mesmo tempo — H40: 20 sprites e 320 pixels; H32:
16 e 256. Para sprites de 16px eles fecham no mesmo ponto, o que faz parecer que existe so um.

```bash
python3 tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --input <cena>.json
```

`unexploited_headroom` e emitido abaixo de 60% de utilizacao. E aviso, nunca blocker: limpa-se
declarando `headroom_justification`. O objetivo e forcar decisao consciente, nao proibir cena
leve.

Regra completa e casos canonicos: `SGDK_GLOBAL.md` secao 30.

---

## DIRETRIZ DE BLOQUEIO ESTETICO

**Nenhum pixel de personagem, inimigo, boss ou cenario pode nascer de codigo.**

Grafico procedural — primitivas, poligonos, retangulos, preenchimento solido, seja
desenhado em C no runtime ou em Python por `PIL/ImageDraw` no pipeline — e permitido
**apenas** para telemetria, debug visual de elemento invisivel ao jogador e elemento
transitorio de interface como barra de progresso simples.

Toda entrega visual consome arquivo de imagem externo importado por `res/resources.res`
com `IMAGE`, `SPRITE`, `TILESET`, `TILEMAP` ou `MAP`, em pixel art indexada respeitando
15 cores visiveis por bloco mais o index 0 transparente.

**Um PNG desenhado por primitiva nao satisfaz essa regra por estar em disco.** O que
decide e a proveniencia declarada, nao o formato nem o nome do arquivo:

```
doc/asset_provenance_manifest.json   ← um registro por simbolo visual do .res
  source_kind: hand_authored_pixel | ai_generated | photo_or_render_derived
             | procedural_composed_from_authored | procedural_primitive | sgdk_builtin
  acceptance_status: final | placeholder | debug_lab | visual_lab_control
```

`source_kind: procedural_primitive` nunca pode ter `acceptance_status: final`.
`procedural_composed_from_authored` exige fonte autoral persistida com hash.

Enforcement executavel — roda antes de qualquer claim de entrega visual:

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root "SGDK_projects/<projeto>" \
  --shared-builder-root tools/image-tools
```

O auditor casa o `.res` com os builders que escrevem cada arquivo; declarar
`hand_authored_pixel` para um asset escrito por builder de primitivas e detectado e
bloqueado. Blockers: `asset_provenance_undeclared`, `procedural_asset_promoted_to_res`,
`procedural_source_kind_declared_final`, `procedural_composed_without_authored_source`,
`runtime_authored_tile_pixels_outside_debug`, `resources_res_missing_for_visual_delivery`.

Unica excecao: projeto com `validator_fixture: true` em `doc/project_context_manifest.json`
pode compilar sem asset externo, e em troca fica preso a `delivery_claim_ceiling` de
`none`, `concept`, `lab` ou `exercise` — nunca sustenta claim de entrega visual.

Regra completa: `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` secoes 8.2 e 17.

**Cada projeto carrega essa diretriz e seu proprio estado medido** em
`doc/00-diretrizes-agente.md`, entre os marcadores `diretriz-bloqueio-estetico v1`.
Agente que assume continuidade le esse bloco antes de tocar em arte. Projeto novo herda
o bloco do template `tools/sgdk_wrapper/modelo/`. Para injetar ou atualizar:

```bash
python3 tools/sgdk_wrapper/apply_aesthetic_directive.py \
  --all-projects SGDK_projects --shared-builder-root tools/image-tools
# --check falha com exit 1 se algum projeto estiver sem a diretriz ou com medicao velha
```

---

## VOCABULARIO DE STATUS

| Termo | Significado |
|-------|-------------|
| `documentado` | Existe apenas em docs |
| `implementado` | Codigo existe, nao buildado |
| `buildado` | Compila, nao testado |
| `testado_em_emulador` | Rodou com evidencia rastreavel; BlastEm fecha gate e BizHawk apenas complementa |
| `validado_budget` | VRAM/DMA/sprites confirmados |
| `placeholder` | Asset ou logica provisoria |
| `parcial` | Incompleto mas funcional |
| `futuro_arquitetural` | Fora do escopo atual |

---

## PIPELINE DE PRODUCAO

Ordem **canonica** (cena AAA, machine-readable): `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`  
Roteamento curto: `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`  
Narrativa + skills reais (sem nomes de agentes inexistentes): `tools/sgdk_wrapper/.agent/workflows/production-loop.md`.

Antes de qualquer trabalho em projeto novo ou antigo:

- quando houver bootstrap, falha de executor, build inconsistente, recuperacao de
  runtime, captura ou disputa entre status tecnico e criativo, siga
  `tools/sgdk_wrapper/.agent/workflows/production-diagnostic-triage.md` antes de
  atribuir causa ou alterar codigo;
- execute `tools/sgdk_wrapper/adopt_project_methodology.ps1`
- classifique `doc/project_context_manifest.json` com `aaa_game`, `technical_demo`, `exercise`, `game_review` ou `consulting`
- valide o contexto com `tools/sgdk_wrapper/validate_project_context.ps1`; `unclassified` bloqueia producao, review final e consultoria
- valide `doc/project_hygiene_manifest.json` com `tools/sgdk_wrapper/validate_project_hygiene.ps1`
- mantenha todo material especifico do projeto dentro dele; entradas externas usadas devem ser copiadas para `rascunho/` e registradas com hash; diretorios copiados exigem inventario verificavel
- use `portable_descriptive_v1` em material ativo: ASCII, sem espacos, minusculas e nomes descritivos em `snake_case`/`kebab-case`
- remova caminhos absolutos para outros workspaces de codigo, scripts, manifestos e documentacao ativa; a referencia operacional deve apontar para a copia local
- classifique `doc/project_methodology_manifest.json`
- mantenha nome do diretorio, `.mddev/project.json` e metodologia coerentes com `doc/PADRAO_NOMENCLATURA.md`
- projeto novo/reseed deve passar por `tools/sgdk_wrapper/validate_project_name.ps1`; projeto antigo nao e renomeado automaticamente
- declare `freshness_audit` entre as validacoes metodologicas obrigatorias
- declare `project_context` entre as validacoes metodologicas obrigatorias
- siga `tools/sgdk_wrapper/.agent/workflows/project-methodology-adoption.md`
- siga `tools/sgdk_wrapper/.agent/workflows/project-context-classification.md`
- nao infira claims de movimento critico, road physics ou boss modular por palavras soltas
- rode `tools/sgdk_wrapper/audit_project_learning.ps1 -Mode Audit`; carregue primeiro o indice compacto, nao todas as licoes

**Enforcement pratico para IAs**: regra Cursor `/.cursor/rules/megadrive-sgdk-aaa-pipeline.mdc`; preflight `tools/sgdk_wrapper/preflight_host.ps1`; CI local opcional `tools/sgdk_wrapper/ci/run_golden_validate.ps1`.

Nenhum passo pode ser pulado.

**Regras do loop:**
- Feature creep bloqueado na etapa 1 (se nao esta no GDD, nao entra)
- Assets nao validados nao entram no build
- ROM nao testada nao e entregue
- Evidencia obrigatoria em cada transicao
- Mudanca de implementacao ou arquitetura exige atualizar `doc/10-memory-bank.md` e `doc/changelog/changelog.md`
- GDD e TDD devem declarar as tecnicas escolhidas, seus registry IDs/tags, funcao no jogo, owner, budget e fallback
- Ao fechar trabalho relevante, rode `audit_project_learning.ps1 -Mode Capture`; ele pode aprender apenas dentro do projeto e nunca aplicar proposta canonica automaticamente

---

## FILOSOFIA MAXIMALISTA

Nao basta FX isolado. E obrigatorio:
- Combinar FX com efeito colateral fisico real
- Timeline de cena com variacao temporal (nao estatico)
- Todo efeito deve ter ligacao direta com o gameplay

---

## ANTI-ALUCINACAO

| Alucinacao | Realidade |
|-----------|-----------|
| Alpha blending | Nao existe — apenas Highlight/Shadow |
| Terceiro plano BG | Apenas BG_A + BG_B + WINDOW |
| `int` e 16 bits | GCC 68000: `int` = 32 bits — use `u16`/`s16` |
| DMA fora de VBlank | Apenas seguro no VBlank |
| Gradiente suave | Max 61 cores — fade = troca de paleta |
| `PAL_getColors(4 args)` | SGDK 2.11: 3 args `(index, dest, count)` |
| Sombra assada no sprite | Use shadow bit do VDP |

---

## MIGRACAO SGDK 1.60 → 2.11

| 1.60 | 2.11 |
|------|------|
| `VDP_setPalette(pal, data)` | `PAL_setPalette(pal, data, DMA)` |
| `VDP_setPaletteColors(idx, data, n)` | `PAL_setColors(idx, data, n, DMA)` |
| `PAL_setPaletteDMA(pal, data)` | `PAL_setPalette(pal, data, DMA)` |
| `SPR_addSpriteEx(def,x,y,attr,idx,flags)` | `SPR_addSprite(def,x,y,attr)` |
| `SPR_FLAG_AUTO_SPRITE_ALLOC` | `SPR_FLAG_AUTO_VRAM_ALLOC` |

Ferramentas: `fix_migration_issues.ps1`, `autofix_sprite_res.ps1`, `validate_resources.ps1`

---

## GATE DE ENTREGA

So declare "pronto" com todos os 7 eixos de QA reportados:

```
✅ build: sucesso → out/rom.bin existe
✅ validation_report: limpo
✅ boot_emulador: ok (BlastEm obrigatorio no gate; BizHawk so complementa telemetria)
✅ gameplay_basico: funcional
✅ performance: estavel (60fps)
✅ audio: ok
✅ memoria operacional canonica atualizada (`doc/10-memory-bank.md` no projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace)
```

### Evidencia Canonica de Emulador

- BlastEm continua sendo o gate obrigatório de entrega.
- Quando o projeto gerar um bloco visual canônico em SRAM, a evidência mínima aceita passa a ser:
  - screenshot dedicado da janela do BlastEm
  - `save.sram`
  - `visual_vdp_dump.bin`
- Nessa modalidade, o quicksave nativo do BlastEm é opcional e não bloqueia sozinho o status `testado_em_emulador`.

---

## ARQUITETURA DO WORKSPACE

```
sdk/sgdk-2.11/           ← toolchain (gitignored)
tools/sgdk_wrapper/      ← fonte unica de logica de build + framework .agent
tools/emuladores/        ← BlastEm, BizHawk, Exodus, GensKMod
SGDK_templates/base-elite/  ← template canonico
SGDK_projects/           ← jogos
SGDK_projects/_agent_training/   ← treino controlado do agente
SGDK_projects/_agent_laboratory/ ← laboratorio controlado do agente
SGDK_Engines/            ← engines
doc/                     ← documentacao do workspace
```

Naming convention: `NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]`

Material especifico de projeto nao pode ficar na raiz do workspace. Dependencias compartilhadas canonicas permanecem em `tools/sgdk_wrapper/`, `sdk/sgdk-2.11/` e `tools/emuladores/`; rascunhos e entradas copiadas ficam em `<projeto>/rascunho/`. Material ativo nao pode depender de caminho absoluto para outro workspace/projeto.

O build e o closeout devem usar `sdk/sgdk-2.11/` deste workspace; `GDK` herdado de outro workspace nao e dependencia canonica.

---

## REFERENCIA RAPIDA

| Necessidade | Arquivo |
|-------------|---------|
| Framework .agent | `tools/sgdk_wrapper/.agent/ARCHITECTURE.md` |
| Regras globais | `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` |
| Menu/modos de sessao | `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md` |
| Preparo comum dos agentes | `tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md` |
| Triagem host/toolchain/runtime/criativo | `tools/sgdk_wrapper/.agent/workflows/production-diagnostic-triage.md` |
| Protocolo de verdade de producao | `tools/sgdk_wrapper/.agent/references/production_truth_protocol.md` |
| Preparar ambiente dos agentes | `tools/sgdk_wrapper/prepare_agent_environment.ps1` |
| Guard de ambiente dos agentes | `tools/sgdk_wrapper/assert_agent_environment.ps1` |
| Integracao ai-memory consultiva | `tools/sgdk_wrapper/prepare_ai_memory_integration.ps1` |
| Politica ai-memory | `doc/AI_MEMORY_POLICY.md` |
| Renderizar menu de sessao | `tools/sgdk_wrapper/show_agent_menu.ps1` |
| Estado de sessao | `doc/agent_session_state.json` |
| Troca de perspectiva | `tools/sgdk_wrapper/.agent/workflows/perspective-switch-gate.md` |
| Pipeline AAA (JSON) | `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json` |
| Pipeline AAA (tabela) | `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md` |
| Loop de producao | `tools/sgdk_wrapper/.agent/workflows/production-loop.md` |
| Classificacao de contexto | `tools/sgdk_wrapper/.agent/workflows/project-context-classification.md` |
| Matriz humana de contexto | `doc/04_project_context_document_matrix.md` |
| Adocao metodologica | `tools/sgdk_wrapper/.agent/workflows/project-methodology-adoption.md` |
| Validator de contexto | `tools/sgdk_wrapper/validate_project_context.ps1` |
| Validator metodologico | `tools/sgdk_wrapper/validate_project_methodology.ps1` |
| Higiene e isolamento | `tools/sgdk_wrapper/validate_project_hygiene.ps1` |
| Aprendizado local seguro | `tools/sgdk_wrapper/audit_project_learning.ps1` |
| Painel humano de proficiencia | `doc/05_technical/93_16bit_hardware_mastery_matrix.md` |
| Registry tecnico machine-readable | `doc/05_technical/93_16bit_hardware_mastery_registry.json` |
| Preflight host | `tools/sgdk_wrapper/preflight_host.ps1` |
| Diretriz de bloqueio estetico | `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` (8.2 e 17) |
| Proveniencia de asset (contrato) | `tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json` |
| Proveniencia de asset (auditor) | `tools/sgdk_wrapper/audit_procedural_asset_provenance.py` |
| Injetar diretriz nos projetos | `tools/sgdk_wrapper/apply_aesthetic_directive.py` |
| Gate de compreensao de marca | `tools/sgdk_wrapper/validate_brand_comprehension_gate.py` |
| Doutrina de audacia | `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` secao 30 |
| Pressao de scanline (2 limites) | `tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py` |
| Pixel strict rules | `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/` |
| Budget VDP | `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/` |
| Migracao batch | `doc/migrations/MIGRATION_BATCH_211.md` |
| Nomenclatura | `doc/PADRAO_NOMENCLATURA.md` |
| Emuladores | `tools/emuladores/` |
