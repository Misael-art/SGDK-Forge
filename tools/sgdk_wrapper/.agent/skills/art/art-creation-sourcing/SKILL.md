---
name: art-creation-sourcing
description: Use quando o projeto estiver sem arte utilizavel e precisar escolher, especificar ou auditar sourcing de assets por IA ou fontes livres antes da conversao para SGDK. Nao use para converter assets existentes, julgar estetica final ou traduzir imagem-fonte forte para VDP.
---

# Art Creation & Sourcing

Use esta skill quando o projeto estiver no Cenario 3 (sem nenhuma arte) e o usuario precisar decidir como criar ou obter os assets.

---

## Regra de Contexto Primeiro

Antes de gerar prompt, buscar asset externo ou propor codigo de suporte, emita um `context_pack_manifest`.

Este manifesto e a forma canonica de RAG v1 do workspace: recuperacao controlada de arquivos locais, manifests, source cases, skills e headers SGDK. Nao depende de banco vetorial e nao substitui a hierarquia de verdade.

Leia sob demanda:

- `references/context_orchestration_v1.md` para `context_pack_manifest`, `asset_lineage_record`, `style_memory_index` e `qa_correction_loop`
- `references/master_style_manifest.md` para manter identidade visual entre o primeiro e o decimo asset
- `../art-direction-selector/SKILL.md`, `doc/03_art/17_concept_art_direction_system.md` e `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` antes de escrever `master_style_manifest` novo
- `references/image_generation_capability_routing.md` antes de declarar bloqueio de geracao visual
- `../art-conversion-pipeline/references/canonical_asset_structure.md` para separar fonte premium, raw, processed, debug lab e `res/`
- `tools/sgdk_wrapper/schemas/project_bible.schema.json`, `visual_dna_manifest.schema.json`, `design_inheritance.schema.json` e `art_gameplay_direction_gate.schema.json` quando o asset nascer autoral e precisar de rastro machine-readable
- `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/benchmark_usage_policy.md` antes de usar benchmarks em brief ou prompt
- `doc/03_art/18_live_scene_bar.md` (ou o brief) antes de qualquer prompt; o piso e o oficio Rheo/Pigsy, nao "pixel art sprite sheet Mega Drive"

Ferramenta local:

```powershell
python tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/scripts/build_context_pack_manifest.py --project "<projeto>" --output "<projeto>/out/logs/context_pack_manifest.json"
```

Regra:

- nao pedir ou emitir Chain of Thought; use artefatos de decisao rastreaveis
- nao gerar proposta visual sem declarar quais fontes canonicas foram consultadas
- nao gerar prompt, buscar asset ou aceitar imagem sem `concept_art_direction_brief`, `art_direction_decision_record` e `master_style_manifest`; manifest legado sem decision record fica `art_direction_pre_canonical` e nao fecha AAA novo
- nao gerar prompt, buscar asset ou aceitar imagem de model sheet, background,
  sprite art, key pose, animation strip, sprite sheet final, FX sheet, HUD
  heroico, title/menu ou asset critico sem `art_gameplay_direction_gate`
  aprovado ou explicitamente `needs_review` com bloqueio de promocao
- usar os `prompt_descriptors` tecnicos do `art_style_catalog.json`; nomes de artistas, estudios, marcas, jogos ou IP ficam como referencias tecnicas e nunca como comando de copia; RheoGamer/PigsyRetro sao barra de oficio (`quality_bar`), nunca comando de copia nem source_art
- se a arte gerada por IA for personagem animado, carregar `art/sprite-animation` antes de qualquer prompt de imagem
- falha de API/CLI nao bloqueia se houver geracao nativa inline no chat; registrar `generated_inline_pending_persistence` quando a imagem renderizou mas ainda nao foi salva
- `local_author_pixel_rasterization` e `procedural_renderer` so podem gerar `debug_lab`, `visual_lab_control` ou `placeholder`; nunca fonte final de personagem, cenario, boss, HUD heroico ou asset AAA
- arte premium aceita precisa existir em `data/source_art/` com `premium_source_manifest` antes de conversao, promocao para `res/` ou alegacao de entrega
- nao promover arte bruta de IA para `res/`; ela deve passar por conversao, validacao pixel-rigida, julgamento visual e budget
- se `doc/10-memory-bank.md` nao existir no projeto, registre fallback para `doc/06_AI_MEMORY_BANK.md`

## As duas rotas

Rota A agora sempre comeca por `context_pack_manifest`, `concept_art_direction_brief`, `art_direction_decision_record`, `master_style_manifest`, `art_gameplay_direction_gate` para asset critico e `art_generation_brief`. O prompt de imagem vem depois desses artefatos, e cada resultado precisa de `asset_lineage_record`.

Quando uma geracao for aceita como fonte artistica, o primeiro destino canonico e `data/source_art/`, nao `res/`. `data/raw_ai/` guarda saidas brutas; `data/debug_lab/` guarda controles procedurais; `data/processed/` guarda candidatos convertidos. O handoff para conversao deve incluir `premium_source_manifest` e lineage com caminho real existente.

Para personagem, inimigo ou boss animado, a Rota A tambem exige `asset_kind_declaration`, `animation_state_plan`, `pose_roster`, `frame_budget_table`, `pivot_and_scale_contract` e `art_gameplay_direction_gate` de `sprite-animation` antes do primeiro `visual_proof_anchor`. O agente deve gerar model sheet, key poses e strips por acao antes de montar sheet final; prompt generico de "sprite sheet completo" e bloqueado. `key_pose_sheet` nunca equivale a `animation_strip`; cada strip deve conter uma unica acao e um `motion_phase_map`.

Para personagem critico, heroi, lutador, boss, NPC expressivo ou asset autoral,
a geracao/concepcao tambem deve produzir `lineart_blocking_1px` antes de
`color blocking`: lineart hard-edge de 1 px, em uma unica cor escura temporaria
(azul escuro, roxo escuro ou equivalente), sem AA/blur, sem degraus
desnecessarios, double corners ou pixels orfaos. A etapa existe para julgar
forma, roupa, cabelo, anatomia e silhueta antes de saturacao, rampas e shading.

Antes de declarar `BLOCKED_IMAGE_TOOLING`, emita `tooling_capability_report` e `generation_channel_decision`. A ausencia de ferramenta callable nao prova ausencia de imagem: se o chat renderiza imagem inline, a rota segue como `native_chat_inline_generation`.

```
Sem Arte
   │
   ├── ROTA A: GERACAO COM IA ─────────────────────────────────
   │     1. Definir spec visual (bible artistica resumida)
   │     2. Gerar uma fonte/pose semantica por vez
   │     3. Persistir, medir e classificar como visual_source
   │     4. Reinterpretar no grid com native-sprite-production
   │     5. Validar pixel, visual, escala e budget separadamente
   │     6. Aprovar e somente entao promover para res/
   │
   └── ROTA B: BUSCA E DOWNLOAD NA WEB ────────────────────────
         1. Identificar estilo visual do jogo
         2. Buscar em repositorios de assets livres (CC0/CC-BY)
         3. Baixar sprite sheets e tilesets
         4. Avaliar compatibilidade (dimensoes, estilo)
         5. Classificar: nativo, conversao tecnica ou traducao interpretativa
         6. Validar lineage/licenca e seguir a skill dona antes de res/
```

---

## ROTA A: Geracao com IA

### Passo 1 — Bible artistica resumida (obrigatorio)

Antes de gerar qualquer arte, definir:

```markdown
## Art Direction Decision Record

**selected_style_id:** (ex: analog_cel_anime_90s)
**catalog_path:** tools/sgdk_wrapper/.agent/references/art_style_catalog.json
**auto_selected:** true/false
**confidence:** 0.0-1.0
**top_candidates:** (minimo 3 com motivo)
**rejected_candidates:** (motivo curto)
**clone_risk_policy:** authoriality_gate_required
**prompt_descriptor_policy:** neutral_technical_descriptors_only

## Concept Art Direction Brief

**visual_purpose:** funcao da arte no jogo
**gameplay_readability_goal:** leitura esperada em 1 frame
**style_selection_method:** production_driven/gameplay_driven/tone_driven/market_driven
**nine_style_axes:** dimensionalidade, fidelidade, cor, luz, formas, materiais, UI, movimento e VFX
**five_approval_gates:** escopo, silhueta, valores, paleta e polish/VFX com sinal de gameplay

## Master Style Manifest

**style_anchor_id:** (ex: project_aegis_style_v1)
**Estilo visual:** (ex: "anime anos 90", "arcade briga de rua", "sci-fi dark")
**Resolucao de sprite principal:** (ex: 32x32 px = 4x4 tiles)
**Paleta dominante:** (ex: cores frias, azul/cinza com detalhes laranja)
**Referencias de jogos MD:** (minimo 3 jogos)
  - Referencia 1: [jogo] — herdar: [o que herdar]
  - Referencia 2: [jogo] — herdar: [o que herdar]
  - Referencia 3: [jogo] — herdar: [o que herdar]
**Personagem principal:** (nome, descricao fisica, equipamento)
**Paleta proposta (hex 9-bits):**
  - Cor base: #XXXXXX
  - Sombra: #XXXXXX
  - Destaque: #XXXXXX
  - Contorno: #000000
**Line weight alvo:** 1 px ou regra equivalente por escala
**Lineart blocking:** `lineart_blocking_1px` para personagem critico antes de cor
**Iluminacao:** top-left/top-down declarada e constante
**Limite de drift:** default 15% para variancia cromatica/valor antes de `revisar`
```

### Passo 2 — Prompts de FONTE, nao de sprite final

Pedir "pixel art sprite sheet Mega Drive, no AA, 15 cores" ao gerador
como fonte final e `pixel_art_prompted_as_final` (barra viva, axioma P1).
O gerador entrega fake pixel art. A barra manda: fonte forte → traduzir.

**Estrutura de prompt de fonte premium:**

```
Pintura/concept do [SUJEITO] em [POSE/ACAO], [MATERIAL DOMINANTE],
luz [DIRECAO] dura, silhueta legivel, volume em 3 planos de valor,
fundo simples ou chroma so se for recorte. Estilo descrito por
descritores tecnicos do catalogo — nunca nome de jogo/artista/IP.
```

**Exemplos alinhados a barra:**

```
# Personagem (fonte, depois lineart 1px no tamanho alvo):
full-body character concept, three-quarter stance, readable silhouette,
hard directional light from upper left, leather and metal materials
with clear light/base/shadow, isolated subject, flat backdrop

# Inimigo de rua (densidade arcade = escala do GDD, nao 24x32 no prompt):
stocky fighter concept, weight in the hips, costume asymmetry,
impact-ready pose, material ramps visible, no background clutter

# Cenario (fonte de plano, depois reautoria em tiles — nunca dump):
wide establishing painting of a dock at dusk, foreground structure
vs distant atmosphere, one focal mass, lighting that will survive
a 9-bit ramp, composition that can split into BG_B sky and BG_A ground
```

**Depois da fonte, nao no gerador:**
- lineart 1 px no tamanho alvo (48x64 / 64x96 / o que o GDD travar)
- paleta semantica 9-bit com papel por slot (R2/P5)
- strips por acao unica; video→harvest para movimento
- tileset por modularizacao, nao pela pintura inteira (R4)

**Dicas:**
- Herdar `style_anchor_id`, paleta alvo, iluminacao e line weight do `master_style_manifest`
- Nunca usar "Streets of Rage inspired" / "Shinobi quality" / handles Rheo/Pigsy como comando de copia; herdar so o eixo tecnico (silhueta, rampa, densidade)
- Green screen so como bruto; o SGDK final sai indexado com index 0
- Se o gerador devolver fake pixel art, rejeitar e regenerar como concept — nao "corrigir" com quantize

### Passo 3 — Ferramentas de geracao de imagem

A partir de 2026-07-09, a geracao em Rota A passo 3 e **native-first**.
O agente usa `imagegen_circuit.py`/`imagegen_tool.py route` para registrar a
decisao, mas se a sessao atual expõe uma ferramenta nativa de imagem
(`native_chat_image_generation_callable` ou `native_chat_inline_generation`),
esse e o caminho primario. Nao bloquear concept art por Bonsai sem licenca,
host AMD ou ComfyUI offline quando o modelo atual consegue gerar a imagem.
Bonsai/ComfyUI sao fallback local opt-in quando nativo/API nao existem.

```powershell
# Dry-run read-only (sempre funciona; auto-detecta Codex/ChatGPT nativo)
.\tools\ai_imagegen\run_imagegen_circuit.ps1 preflight `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --style-manifest "<P>/doc/art/master_style_manifest.json" `
    --write-decision `
    --json

# Run real pelo circuit apenas para backend local. Se preflight retornar
# native_chat_image_generation_callable/native_chat_inline_generation, use a
# ferramenta nativa da sessao, salve em data/source_art/ e registre lineage.
.\tools\ai_imagegen\run_imagegen_circuit.ps1 run `
    --project "<NOME DO PROJETO>" `
    --asset-role concept_art `
    --prompt "..." `
    --seed 42 `
    --json
```

Veja o runbook completo em `tools/sgdk_wrapper/.agent/workflows/ai-imagegen-circuit.md`.

**Escopos Bonsai (v1, license-gated):**

| Escopo | Significado | Aceito |
|---|---|---|
| `concept_art` | Imagem-fonte forte para re-trabalho VDP | sim |
| `tileset_concept` | Conceito de tileset antes de modularizar | sim |
| `dither_mask` | Mascara 1-bit dithered como base de mapeamento H/S | sim |
| `contrast_study` | Estudo de contraste branco/preto + material | sim |
| `animated_sprite_final` | Sprite animado pronto para `res/` | **nao** |
| `hud_final` | HUD heroico pronto para `res/` | **nao** |
| `res_direct` | Asset para `res/` direto | **nao** |
| `aaa_final_asset` | Asset final AAA direto | **nao** |

**Opcoes de canais (em ordem de prioridade, espelha image-generation-routing):**

| Canal | Qualidade | Disponibilidade |
|---|---|---|
| Native chat (callable ou inline) | Excelente | Quando o chat expõe |
| API/CLI externa (OpenAI, Ideogram, etc.) | Muito bom | Billing + chave |
| Local ComfyUI (`imagegen_tool.py generate`) | Bom | Local |
| Local Bonsai 4B (`imagegen_circuit.py run` com `--asset-role concept_art` etc.) | Bom (1-bit friendly) | NVIDIA/Apple Silicon + license ack |
| `procedural_renderer` | Placeholder | `debug_lab` apenas |

**Para gerar via API (automacao):**
```python
# Usar Claude API com tool use para coordenar geracao
# O agente art-creator usa esta skill para gerar prompts
# e pode chamar APIs externas de imagem via MCP ou HTTP
```

### Passo 4 — Pos-gerado: classificacao e handoff obrigatorios

Toda arte gerada por IA precisara de ajuste antes do SGDK:

```bash
# 1. Inspecionar o que foi gerado
python tools/sgdk_wrapper/art_diagnostic.py --project "<projeto>"

# 2. Para sprite/objeto/FX autoral, criar e validar o record operacional
python3 tools/sgdk_wrapper/validate_native_sprite_production.py \
  --project-root "<projeto>" \
  --record "<projeto>/doc/art/<asset>/native_sprite_production_record.json"

# 3. Se a fonte estiver perto do padrao e a rota for apenas tecnica, executar
# forge-art convert com spec registrada. A saida continua technical_candidate.
PYTHONPATH=tools/sgdk_wrapper python3 -m forge_art convert \
  --project-root "<projeto>" \
  --spec "<projeto>/doc/art/<asset>/conversion_spec.json"
```

`fix_png_transparency_final.py` e `batch_resize_index.py` sao rotas depreciadas
e falham fechado. GIMP GUI/ponteiro nao e automacao de producao; operacao
deterministica usa CLI/headless, e decisao de forma usa autoria visual/nativa.

---

## ROTA B: Busca e Download na Web

### Repositorios recomendados

| Site | URL | Licenca | Qualidade |
|------|-----|---------|-----------|
| OpenGameArt | opengameart.org | CC0/CC-BY/GPL | Variada — filtrar por "16-bit" |
| itch.io Assets | itch.io/game-assets | Variada (muitos CC0) | Alta — buscar "16-bit pixel art" |
| Kenney | kenney.nl | CC0 | Media — estilo simples mas limpo |
| GameArt2D | gameart2d.com | Pago/Free | Alta qualidade |
| Spriters Resource | spriters-resource.com | Fair Use | Sprites de jogos comerciais MD |

### Estrategia de busca eficiente

**Termos de busca recomendados:**
```
"16-bit sprite" + [genero do jogo]
"Sega Genesis style" + [personagem/cenario]
"retro platformer sprite sheet" transparent
"beat em up character sprites" free CC0
"pixel art tileset" 8x8 16-bit
"side scroller background" pixel art free
```

**Filtros obrigatorios ao avaliar asset:**
1. Licenca: CC0 (melhor) ou CC-BY (dar credito) — nunca usar assets sem licenca explicita
2. Resolucao base compativel com redimensionamento para multiplos de 8
3. Estilo visual coerente com o jogo (comparar com bible artistica)
4. Sprite sheet organizado (frames em grid regular)

### Avaliacao de sprite sheet baixado

```bash
# Verificar o que foi baixado
python tools/sgdk_wrapper/art_diagnostic.py --project "<projeto>"

# Identificar dimensoes e modo
magick identify -verbose "<sprite_sheet>.png" | head -30

# Verificar grid de frames (para sprite sheets)
# Largura/altura deve ser divisivel pelo tamanho do frame
# Ex: 192x32 px com frames 32x32 = 6 frames horizontais
```

**Checklist de avaliacao:**

- [ ] Licenca verificada e compativel (CC0 ou CC-BY)
- [ ] Sprite sheet tem grid regular de frames
- [ ] Dimensoes de frame compativeis com multiplos de 8
- [ ] Estilo visual coerente com bible artistica
- [ ] Numero de cores visiveis <= 15 (ou redutivel sem perda critica)
- [ ] Fundo transparente ou removivel

### Download e organizacao

```
data/
  raw/                  ← assets baixados sem modificacao
    sprite_sheet_cc0.png
    tileset_urban_cc0.png
  production/           ← assets cortados e prontos para conversao
    player_idle.png     ← frame recortado do sprite sheet
    player_walk_01.png
  ASSETS_CREDITS.md     ← registro de licencas e origens
```

**ASSETS_CREDITS.md (obrigatorio para CC-BY):**
```markdown
# Creditos de Assets

| Asset | Origem | Autor | Licenca | URL |
|-------|--------|-------|---------|-----|
| player_idle.png | OpenGameArt | Autor X | CC-BY 4.0 | url |
| stage1_bg.png | itch.io | Estudio Y | CC0 | url |
```

### Corte de sprite sheet

Para extrair frames de um sprite sheet com ImageMagick:

```bash
# Cortar grid de sprites (ex: sheet 192x32 com frames 32x32)
magick "<sheet>.png" -crop 32x32 +repage +adjoin "production/frame_%02d.png"

# Cortar frame especifico (x_offset, y_offset, w, h)
magick "<sheet>.png" -crop 32x32+0+0 +repage "production/player_idle.png"
magick "<sheet>.png" -crop 32x32+32+0 +repage "production/player_walk_01.png"
magick "<sheet>.png" -crop 32x32+64+0 +repage "production/player_walk_02.png"
```

---

## Decisao: qual rota escolher?

| Fator | Rota A (IA) | Rota B (Web) |
|-------|-------------|--------------|
| Controle visual total | Sim | Parcial |
| Estilo unico garantido | Sim | Dificil |
| Velocidade | Media | Alta |
| Qualidade pixel art | Media-alta | Alta (se bom repositorio) |
| Custo | API de imagem | Gratis (CC0) |
| Coerencia visual entre assets | Alta (mesmo prompt) | Media (mixer de estilos) |
| Recomendado para | Jogos originais com identidade visual propria | Prototipos, jams, projetos educacionais |

**Regra geral:** para personagem principal e arte central do jogo → Rota A com ajuste manual. Para tiles de background e assets secundarios → Rota B com curadoria.

---

## Saida esperada desta skill

Para o usuario decidir a rota, entregar:

```markdown
## Analise de Arte — <Nome do Projeto>

**Assets necessarios identificados:**
- [ ] Sprite do jogador (32x32 px, ~8 frames de animacao)
- [ ] 3 tipos de inimigos (24x32 px)
- [ ] Tileset de cenario fase 1 (256 tiles unicos estimados)
- [ ] HUD icons (8x8 px a 16x16 px)

**Rota A (IA):**
- Estimativa: X assets, Y prompts necessarios
- Ferramentas: Stable Diffusion + photo2sgdk
- Tempo estimado de ajuste manual: Z horas

**Rota B (Web):**
- Repositorios sugeridos: OpenGameArt, itch.io
- Termos de busca: [lista]
- Assets CC0 encontrados possivelmente compativeis: [lista com URLs]

**Recomendacao:** [Rota A / Rota B / Hibrido] porque [justificativa]
```

## Memoria de Estilo

Consistencia vence brilho isolado.

- Um asset nota 8 que pertence ao mundo do jogo vence um asset nota 10 que parece importado de outro projeto.
- Cada novo asset deve declarar qual `master_style_manifest` herdou.
- Cada tentativa aceita ou rejeitada deve gerar `asset_lineage_record`.
- O `style_memory_index` pode ser um JSON simples em `doc/source_cases/` ou `out/logs/`; banco vetorial e apenas futuro opcional.
- `qa_findings` e `correction_request` substituem explicacoes internas extensas.

## Contrato Operacional

### Entrada minima

- confirmacao de que o projeto nao possui arte utilizavel em `/data` ou `/res`
- GDD/spec ou briefing com fantasia, genero, escala e prioridade visual
- politica de licenca aceitavel para assets externos
- lista minima de assets necessarios para o primeiro slice
- `context_pack_manifest` com docs, manifests, source cases, feedback bank, engine profiles e headers SGDK relevantes

### Saida minima

- `context_pack_manifest`
- `tooling_capability_report` quando houver geracao por IA
- `generation_channel_decision` quando houver geracao por IA
- `master_style_manifest`
- `project_bible` quando o projeto ainda nao tiver identidade autoral machine-readable
- `visual_dna_manifest` e `design_inheritance` para personagem principal, boss, cenario autoral ou HUD heroico
- `art_generation_brief`
- decisao de rota: IA, web, hibrido ou bloqueado
- lista de prompts ou fontes candidatas com justificativa
- `asset_lineage_record` para cada asset bruto aceito, rejeitado ou pendente
- `persistence_audit` quando houver imagem inline ou asset prometido para filesystem
- `style_memory_index` quando houver mais de um asset na mesma familia visual
- `qa_findings` e `correction_request` quando houver drift, erro de paleta, escala ou coerencia
- plano de creditos/licencas quando houver asset externo
- assets brutos confinados em `data/raw` ou plano de geracao, nunca promovidos direto para `res`
- handoff claro para conversao ou traducao VDP

### Passa quando

- o `context_pack_manifest` declara as fontes canonicas consultadas antes de qualquer prompt
- `tooling_capability_report` diferencia callable nativo, geracao inline, API/CLI e renderer procedural antes de bloquear
- se uma imagem renderizou inline, o status nao e `blocked_image_tooling`; use `generated_inline_pending_persistence` ate salvar no filesystem
- se nenhuma rota persistivel produzir fonte premium para asset critico, declare `blocked_image_tooling` ou `blocked_no_premium_source` e pare antes do runtime visual de producao
- runtime textual, procedural ou proxy criado depois desse bloqueio e somente `debug_lab` com `lab_not_delivery=true`
- o `master_style_manifest` define paleta, escala, iluminacao, line weight e limite de drift
- personagem critico possui `lineart_blocking_1px` aprovado antes de color blocking, paleta final ou shading
- o benchmark foi usado apenas como qualidade tecnica, escala, densidade ou timing; nunca como fonte visual ou comando de copia
- a geracao de fonte respeitou a barra viva: concept/volume primeiro, nunca sprite sheet Mega Drive como output do gerador
- `live_scene_bar_report` entra no handoff quando o asset for critico ou o projeto for `aaa_game`
- `visual_dna_manifest` e `design_inheritance` existem antes de gerar key poses ou animation strips autorais
- a rota escolhida respeita escopo, licenca e identidade visual do projeto
- nenhuma arte externa entra no build sem credito/licenca rastreavel
- nenhuma arte gerada por IA e tratada como pronta sem conversao e revisao VDP
- assets incoerentes com a memoria de estilo sao rejeitados ou entram em `qa_correction_loop`
- o proximo passo tecnico esta definido sem ambiguidade

### Handoff para proxima etapa

- usar `art-conversion-pipeline` para assets brutos que ja estejam perto do padrao SGDK
- usar `art-translation-to-vdp` quando houver imagem-fonte forte que exige reinterpretacao
- usar `native-sprite-production` quando a reinterpretacao tiver destino
  sprite, sheet, objeto ou FX autoral; o gerador entrega `visual_source`, nao
  promete PNG nativo pela aparencia
- usar `visual-excellence-standards` antes de congelar direcao visual final
- entregar `context_pack_manifest`, `master_style_manifest` e `asset_lineage_record` junto com qualquer asset bruto
