# Núcleo visual nexialista v01 — Vegetable Valley

**Data:** 2026-08-31
**Estado:** `locked_visual_direction` + `locked_composition_reference_only`; v03-A aprovado em escopo limitado para uma pose idle nativa 32×32; `res_promotion=false`
**Escopo:** primeiro ciclo visual; nenhum arquivo em `res/` foi alterado.

## Verdade operacional

O projeto já possui um runtime jogável com 5 bandas de parallax, boss Whispy Woods, abilities e evidência BlastEm. Essa evidência prova execução, desempenho e composição do placeholder; não aprova arte nativa. O diagnóstico canônico encontrou `2_res_inadequate_check`: 22 recursos ativos, 22 legíveis, 0 ausentes e 0 bloqueios de build; em `data/`, existem 78 fontes, das quais 42 legíveis, 28 que exigem conversão e 8 inadequadas. As fontes P1–P4 e R1–R3 foram inspecionadas somente como evidência histórica/negativa.

### Reconciliação documental

| Campo | Vigente | Obsoleto/contraditório | Decisão harmonizada | Evidência |
|---|---|---|---|---|
| Estado de arte | `doc/10-memory-bank.md`: R1 entregue, P1–P4 arquivadas/reprovadas, sem master aprovado | gate antigo dizia `template_seed_only` e ausência total de fonte | gate agora reconhece runtime placeholder + novo candidato sem promovê-lo | `doc/contracts/visual_delivery_gate_report.json` |
| Direção do personagem | DNA v03 candidate; `model_sheet_challenger_v01` | revised_checks antigos declaravam correções sem prova visual | gate agora é `needs_rework`; checks não comprovados; v02 é challenger novo | `doc/art/model_sheet_route/visual_dna_manifest.json`, `doc/contracts/model_sheet_gate.json` |
| Contexto de trabalho | jogo existente, contexto `aaa_game`, teto vertical slice | metodologia dizia `lifecycle=new` e claims `review_required` | manifesto marcado como `existing`; `critical_motion` e `modular_boss` required; `road_physics` not_applicable | `doc/project_methodology_manifest.json` |
| Proveniência do runtime | 22 símbolos visuais ativos eram não declarados | ausência de `doc/asset_provenance_manifest.json` | manifesto criado; placeholders procedurais ficam honestamente como `placeholder` e não podem ser finais | `doc/asset_provenance_manifest.json` |
| GDD/spec | documentos genéricos de template | memória e código já descrevem loop, parallax e boss | escopo confirmado, identidade/proveniência e gates separados foram reconciliados | `doc/11-gdd.md`, `doc/13-spec-cenas.md`, `src/scenes/scene_stage.c` |

## Fontes permitidas e proibidas

Permitidas: documentação vigente, geometria observada do runtime, model-sheet route como estudo, novos concepts gerados nesta sessão e assets autorais locais explicitamente aprovados. Proibidas como fonte de pixels: rips de ROM, imagens de internet, sprites comerciais, P1–P4 rejeitadas, placeholders ativos, painéis comparativos e screenshots do jogo.

Metadados do fan game: “Fan game derivado da identidade de Kirby/Nintendo/HAL, com execução gráfica original, sem reutilização ou extração de pixels dos jogos de referência.” `derivative_license_status=unlicensed_noncommercial_fan_work`; `commercial_distribution=false`; `pixel_source=new project-authored execution`; `ripped_pixels=false`. Não chamar o personagem de propriedade intelectual original.

## Gramática visual proposta

- **Forma:** massa redonda com braços curtos separados por entalhe de contorno; pés pequenos e assentados; inimigos compactos com silhueta assimétrica.
- **Luz/material:** uma luz superior-esquerda; cinco degraus de corpo com área decrescente; terminador inferior-direito; contorno dedicado; olhos ovais com brilho mínimo; nada de gradiente suave.
- **Contraste:** hero > inimigo/FX > terreno jogável > BG_A estrutural > BG_B distante.
- **Atmosfera:** ar quente e aberto, distante azul/ciano, terreno verde-âmbar; a tensão vem do espaçamento de ameaça e do vento que reage ao verbo de sugar.
- **Movimento:** folhas e fitas de vento seguem a direção da inalação; o pé de contato ancora o personagem; foreground entra como oclusão controlada, não como ruído.
- **Leitura 320×224:** faixa superior silenciosa para HUD; plataforma e gap com borda de colisão nítida; hero e inimigo separados por espaço negativo e pelo FX.

Heranças técnicas estudadas, sem copiar pixels: `Monster World IV` (textura orgânica modular e clareza cromática), `Shinobi III` (silhueta contra fundos em movimento e uso de foreground) e `Gunstar Heroes` (energia de FX por clusters e ritmo de impacto). O catálogo consultado foi `storybook_gouache_nature` + `kodomo_round_cartoon` como âncoras técnicas, ambos somente `inspiration_only`; não são fontes visuais.

## Rotas controladas

O painel [route_exploration_panel_v01.png](../../rascunho/nexialist_visual_nucleus_v01/route_exploration_panel_v01.png) mantém a mesma geometria e altera um eixo dominante por vez:

| Rota | Eixo alterado | Força | Risco | Decisão |
|---|---|---|---|---|
| A — Sunlit Cultivation | temperatura atmosférica | pertencimento imediato a Vegetable Valley, melhor separação do hero | pode ficar alegre/genérica se não houver assinatura de vento/terreno | **recomendada** |
| B — Twilight Orchard | densidade/acabamento material | clima mais autoral e contraste dramático | pode escurecer pés, inimigo e borda de colisão | alternativa condicionada a teste 1x |
| C — Turquoise Weather | energia/exagero de forma | melhor impacto de FX e landmarks vegetais | risco de fundo competir com o jogador | alternativa para bioma/variante |

A Rota A está agora registrada como `locked_visual_direction`, vinculada ao asset_id e SHA no `visual_direction_gate.json`. B/C continuam apenas alternativas comparativas; não foram misturadas na direção travada.

## Model sheet challenger

[model_sheet_challenger_v01](../../rascunho/nexialist_visual_nucleus_v01/revised_character_model_sheet_v01.png) é evidência de tentativa e está em `visual_gate=needs_rework`, `promotable=false`, `translation_authorized=false`. O [challenger v02](../../rascunho/nexialist_visual_nucleus_v01/model_sheet_challenger_v02.png) foi gerado com o v01 anexado explicitamente como referência; é candidato novo, não revisão fiel nem fonte canônica. O painel registra os defeitos observáveis e os testes de silhueta pura.

O [challenger v03-A](../../rascunho/nexialist_visual_nucleus_v01/model_sheet_challenger_v03_a_cluster_strict.png), SHA-256 `989d1a2398e9609dffe3e4f673e95b73e081ddffdcba9764829684498d8c6241`, foi aprovado como fonte do model sheet e para `single_idle_native_key_pose_translation` em `32x32`. Continua `visual_source`, não é arte nativa, não aprova o turnaround completo e não autoriza outras poses, sprite sheet, animação, `res/` ou runtime. O [challenger v03-B](../../rascunho/nexialist_visual_nucleus_v01/model_sheet_challenger_v03_b_silhouette_first.png) permanece `comparison_only`.

## Cena-dourada e layers

[vegetable_valley_golden_scene_concept_v01.png](../../rascunho/nexialist_visual_nucleus_v01/vegetable_valley_golden_scene_concept_v01.png) está aprovado somente como referência de composição, iluminação, profundidade, camadas e densidade. A tradução semântica é `BG_B` para céu/nuvens/montanhas distantes, `BG_A` para hills/terreno/ledge/gap, foreground/priority para folhas/grama e sprites para herói/inimigos/pickups/FX. Não é bitmap de conversão, asset nativo ou autorização para `res/`. `WINDOW` continua reservado ao HUD; não existe terceiro plano.

Os contratos estão em `layer_plan.json`, `scene_semantic_decomposition.json` e `tile_kit_inventory.md`. A estratégia é `scene_local_preload`, com kit modular 8×8 e fallback `compare_flat` se a residência de tiles exceder o budget.

## Paleta preliminar

O contrato em `palette_contract.json` compara A (PAL2 dedicada ao herói, PAL3 inimigo/FX), B (herói/inimigo harmonizados, foreground em PAL1) e C (herói dedicado, FX dedicado, inimigo compatível). O painel [palette_distribution_study_v01.png](../../rascunho/nexialist_visual_nucleus_v01/palette_distribution_study_v01.png) apresenta cada alternativa em thumbnail 4:3, ampliação nearest e mesma composição. Não há quantização nesta etapa; slots de Shadow/Highlight permanecem reservados até auditoria nativa.

## Budget preliminar

O laudo em `budget_preliminary.json` é `cabe com recuo`, pois o baseline medido tem 25/80 sprites, 18/20 por scanline, 1792 B/frame de DMA e CPU p99 até 60% na cena de ability, enquanto a nova arte ainda não tem tiles `rescomp` nem residência real. A meta desta cena é ≤16/20 no pior frame antes de integração. O próximo degrau foi medido offline em `golden_scene_sprite_layout.json` e `next_density_sprite_layout.json`; o recuo preserva hero, inimigo, colisão e direção do vento antes de remover detalhes opcionais.

## Teto honesto do claim

`locked_visual_direction` para a Rota A, `locked_composition_reference_only` para a cena-dourada e `single_idle_native_key_pose_translation_authorized_pending_native_gates` para o v03-A. Não é `visual_pass`, `ready_for_res`, `runtime_candidate`, `testado_em_emulador` nem `ready_for_aaa`. Não há autorização para alterar `res/`, substituir placeholders, produzir outras poses ou alegar coesão em cena viva.

## Próxima ação causal

Próxima ação causal autorizada: comparar BASIC e ELITE em 1× e solicitar decisão humana por `asset_id`/SHA; somente após essa decisão podem ser executados ResComp, integração e evidência de emulador. Outras poses, sheet e `res/` continuam bloqueadas.

## Decisão humana e challenger v03

`decision=rework_before_native_translation` foi registrado para `model_sheet_challenger_v02`, SHA-256 `0d9be1e502eddedf1a364498180102fdc6e49b8ff7a48fa580d4b1ed36b8880a`, aceito somente como `turnaround_volume_reference_only`. O v02 não é fonte de pixels, acabamento ou model sheet canônico.

Foram produzidos dois challengers controlados: `cluster_strict` (A) preserva o volume do v02 com clusters mais duros; `silhouette_first` (B) simplifica os internos para leitura em 32×32. O v03-B foi gerado sem referência de imagem depois de duas tentativas com referência explícita serem bloqueadas pelo filtro; por isso é um novo challenger, não uma revisão fiel.

Os probes em `mechanical_scale_probes/` incluem 32×32, 64×64 nearest, 256×256 nearest, composição 320×224 e silhueta preta 32×32. Eles são `mechanical_scale_probe`. A medição de microcores high-res é somente um bloqueio de uso como sprite nativo; não rebaixa nem rejeita o v03-A como fonte visual/model sheet.

Teto máximo atual: `single_idle_native_key_pose_translation_authorized_pending_native_gates`.

## Pose idle nativa — candidatos v01

O v03-A foi reinterpretado em grade nativa 32×32, sem quantização direta, sem reutilizar o probe mecânico e sem produzir sheet. A ordem registrada foi silhueta, lineart 1 px, blocking por material, topologia, sombra principal, highlight mínimo e limpeza de clusters. BASIC e ELITE usam a mesma silhueta, lineart, pose, pivot `(16,31)`, baseline `y=30` e bbox `[0,1,32,31]`.

| Candidato | SHA-256 | Paleta | Estado |
|---|---|---:|---|
| `native_idle_key_pose_basic_v01` | `473bcdeab5b1b7edf7d32aeafe4d5d7f49aedb780684e94fddfde66c5aec3ecd` | 9 cores visíveis | `technical_candidate`, aprovação visual humana pendente |
| `native_idle_key_pose_elite_v01` | `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29` | 12 cores visíveis | `technical_candidate`, aprovação visual humana pendente |

Os PNGs são P/4bpp, índice 0 transparente, alpha binário e cores RGB333. Os probes 64×64 e 256×256 são derivados exclusivamente dos PNGs nativos por repetição de índice; o teste em `native_idle_key_pose_scale_exactness_report.json` passou 2× e 8× para as duas variantes. Os registros completos estão em `doc/art/nexialist_visual_nucleus_v01/native_idle_key_pose_*_native_sprite_production_record.json`. Nenhum candidato está autorizado para `res/`, animação, integração ou runtime.
