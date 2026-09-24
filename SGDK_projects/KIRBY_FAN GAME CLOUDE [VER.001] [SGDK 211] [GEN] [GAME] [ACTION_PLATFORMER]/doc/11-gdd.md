# 11 - Game Design Document — KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

## Identidade e escopo confirmado

Este é um fan game derivado da identidade de Kirby/Nintendo/HAL, com execução gráfica original, sem reutilização ou extração de pixels dos jogos de referência. A execução gráfica original não transforma o personagem ou a identidade derivada em propriedade intelectual original do projeto.

O escopo confirmado da VER.001 é um action platformer para Mega Drive: título, três fases planejadas, Vegetable Valley como primeiro slice jogável, boss Whispy Woods, game over/continue e cinco copy abilities — FIRE, BEAM, CUTTER, STONE e SWORD. A ROM atual prova um subconjunto jogável com título, uma fase, boss, continue e os cinco movesets; isso não fecha o escopo de conteúdo.

## Visão e core loop

O jogador atravessa plataformas e gaps, lê ameaças em camadas de profundidade, aproxima-se do inimigo, usa movimento e inalação para criar uma consequência de gameplay e escolhe/usa a habilidade disponível. O ciclo de 30 segundos é: mover → saltar/posicionar → inalar ou evitar → confirmar o efeito → avançar sob risco de dano.

O visual deve preservar leitura imediata em 320×224: herói como maior prioridade de silhueta, inimigos separados do terreno, bordas de colisão claras e FX com direção causal.

## Feature Scope Map

### Entra no slice

- Movimento, salto, dano, inalação, consumo/efeito de habilidade e cinco movesets.
- Vegetable Valley com parallax existente, terreno, ledge, gap, inimigo vegetal e FX de sucção.
- Câmera H40 320×224, game over/continue e boss já presentes no runtime.

### Entra depois

- Fases 2 e 3 de conteúdo e trilha composta, conforme o planejamento vigente.

### Fora de escopo

- Nesta rodada: sprite sheet completa, animações finais, conversão mecânica da cena-dourada, nova identidade, terceira camada de background e promoção para `res/`.

## Identidade de Front-End

O front-end comunica aventura natural ensolarada, com assinatura de cultivo e profundidade discreta. Parallax, scroll/paleta e uma timeline curta são vida visual; seleção e feedback permanecem subordinados à leitura do menu. Gradientes suaves, sprites comerciais, excesso de brilho e um terceiro plano real são fora de tom e fora do hardware.

## Ambição técnica, visual e sonora

- `quality_promise`: leitura forte em 320×224, resposta de plataforma mensurável e uso consciente de BG_A/BG_B, paleta, raster e sprites.
- `visual_direction`: `locked_visual_direction`, Rota A — Sunlit Cultivation; terreno verde/âmbar, profundidade fria e ribbon ciano de inalação.
- `sound_direction`: SFX de ação claros; a trilha atual é placeholder e não sustenta claim final.
- `gameplay_quality_bar`: o playtest prova estados e movesets; julgamento humano ainda é necessário para física e leitura perceptiva.
- `hardware_strategy`: `scene_local_preload`, kit modular 8×8, BG_B para distância, BG_A para estrutura jogável, foreground esparso e `compare_flat` como recuo.

## Tecnicas Escolhidas

Toda tecnica precisa existir no registry canonico e servir a gameplay, narrativa, leitura, direcao visual ou sonora. Quantidade de efeitos nao substitui coerencia.

| Cena/sistema | Registry id | Tags | Funcao no jogo | Papel visual/sonoro | Owner skills | Budget/evidencia esperada | Fallback |
|---|---|---|---|---|---|---|---|
| Vegetable Valley | pendente de sincronização do registry | `five_layer_parallax`, `semantic_decomposition_required` | separar distância, terreno e ação | herói/inimigo/colisão legíveis | composição multi-plano + budget VDP | provenance, rescomp, residency, scanline, DMA e BlastEm | `compare_flat` |

### Tecnicas rejeitadas ou adiadas

| Registry id | Decisao | Motivo | Condicao para reconsiderar |
|---|---|---|---|
| arte conceitual como bitmap de runtime | rejeitada nesta rodada | não é asset nativo nem prova VDP | tradução manual, pixel-strict e gate nativo |

## Mecânicas core

- Plataforma lateral com movimento, salto, coyote e jump buffer existentes.
- Inalação/consumo como verbo de risco e consequência.
- Cinco copy abilities com movesets existentes, sujeitas a revisão de feel.

## Progressão

O plano é título → três fases → boss Whispy Woods → game over/continue. Apenas o primeiro slice e o boss estão fechados no runtime atual; conteúdo adicional continua backlog confirmado.

## Regras e limites

- Nenhum pixel de personagem, inimigo, boss ou cenário nasce de código ou de rip comercial.
- Nenhuma arte conceitual entra em `res/` sem tradução nativa, proveniência, pixel-strict, orçamento e evidência.
- `WINDOW` é HUD/plano fixo, nunca terceiro plano de cenário.

## First Playable Slice

Vegetable Valley é a primeira entrega jogável: precisa provar movimento, salto, inalação, ameaça, ledge/gap, foreground sem cobrir colisão, cinco movesets e transição para o boss. O loop existe tecnicamente quando os estados ocorrem na ROM; qualidade visual e física exigem revisão humana separada.

## Route Decision Record

- `context_type`: `projeto_existente`.
- `dominant_route`: `locked_visual_direction` → `semantic_scene_decomposition` → `art_translation_to_vdp` após gate.
- `first_skill`: composição multi-plano e excelência visual; geração somente para challenger.
- `first_tool`: diagnóstico de arte, simulador VDP e validadores de proveniência.
- `resource_loading_model`: `scene_local_preload`.
- `asset_strategy`: `mixed_bg_tiles_foreground_sprite_graft`, com `compare_flat` como fallback.
- `evidence_required`: provenance, pixel-strict, rescomp, residency, DMA, scanline, runtime metrics, screenshot BlastEm, SRAM/VDP dump quando aplicável.
- `forbidden_shortcuts_until_evidence`: conversão direta de concept, pixels comerciais, `res/` promotion, sprite sheet completa e claims AAA.

## Escopo atual

Direção visual e composição de Vegetable Valley estão travadas conforme os gates desta rodada. O model sheet v01 é `model_sheet_challenger_v01`, `visual_gate=needs_rework`, `promotable=false`, `translation_authorized=false`; o v02 permanece apenas referência de volume; o v03-B é `comparison_only`. O v03-A é a fonte visual canônica por SHA. A pose `native_idle_key_pose_elite_v01`, SHA `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29`, foi aprovada para uma única pose idle nativa 32×32 e prova visual isolada de runtime; não substitui o herói do first playable.

## Cenas de Front-End

Branding, título/menu, primeira fase, playtest, boss arena e game over/continue existem como cenas runtime documentadas em `doc/13-spec-cenas.md`. A direção visual de produção ainda não foi promovida para essas cenas.

## Vibe Playable Birth Route

Projetos novos nascem com rota Vibe Playable preparada, mas bloqueada.

Pedido natural de jogo/fase/personagem/FX deve acionar roteador visual antes de runtime definitivo.

Este projeto não é um template vazio: possui runtime/evidência baseline. A ELITE tem autorização limitada para uma cena de review isolada via recurso real `SPRITE`; a integração e a prova BlastEm continuam pendentes. Não há promoção final para `res/`, sheet completa, animação final, substituição de gameplay ou claim AAA.
