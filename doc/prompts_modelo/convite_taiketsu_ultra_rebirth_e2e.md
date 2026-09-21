# Convite de Ativacao — TAIKETSU ULTRA REBIRTH (fighting game E2E)

**versao:** 1.0.0
**data:** 2026-09-05
**natureza:** instancia concreta da via opcional `doc/prompts_modelo/prompt_modelo_jogo_completo_e2e.md`. Nao cria gate, script, tooling nem modo de sessao novo.
**projeto de origem (engine base):** `SGDK_Engines/TaiketsuUltraHeroGenesis/` (HAMOOPIG, GameDevBoss — creditos obrigatorios)
**projeto alvo (novo):** `SGDK_projects/TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]`

---

## 0. O que o humano decidiu (registrado, nao re-perguntar)

| # | Decisao | Valor |
|---|---|---|
| D1 | Nome/tag do projeto novo | `TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]` |
| D2 | Roster | **convivem**: Jack + Ryo (engine base) + 4 originais = **6 lutadores** |
| D3 | Movimentacao no dialogo | **os tres**: retrato animado (SNK'96/SVC) + sprite de corpo inteiro reagindo + camera/scroll cinematografico |

---

## 1. Requisitos do jogo (contrato de escopo — literal, do humano)

### 1.1 Roster (6 lutadores)

| id | origem | requisito duro |
|---|---|---|
| `jack` | engine base | mantido; serve tambem de **regua de escala** |
| `ryo` | engine base | mantido; regua de escala |
| `C1` | original | **>= +25% de altura de sprite** vs. o maior entre jack/ryo (medido em pixels, nao estimado) |
| `C2` | original | **personagem feminina** |
| `C3` | original | **poderes**: golpes especiais + **golpes aereos** |
| `C4` | original | **chefe final desbloqueavel** (nao selecionavel ate condicao de unlock) |

> R1 nao e opiniao: `altura_C1_px >= ceil(1.25 * max(altura_jack_px, altura_ryo_px))`,
> medida no frame idle do model sheet e reconferida no sprite final em VRAM.

### 1.2 Sistema de especial

- Barra de especial por lutador, **carrega** durante a luta (dano dado/recebido, defesa, whiff penalizado).
- Golpe especial consome a barra; **a barra volta a cheia ao conectar o especial** (regra literal do pedido — registrar no TDD como mecanica intencional, nao bug).
- Golpes aereos como categoria propria de move (C3 obrigatorio; demais opcionais por design).

### 1.3 Cutscenes e apresentacao

| id | gatilho | conteudo |
|---|---|---|
| CS-A | execucao do golpe especial | cutscene de especial (por personagem) |
| CS-B | `life <= 25%` **E** barra de especial cheia | cutscene especial de desespero/clutch (por personagem) |
| CS-C | entrada de stage | intro de stage |
| CS-D | inicio de luta | **intro individual de cada personagem**, no idioma visual **SNK 1996 / SVC Chaos 1-2** |
| CS-E | pre-luta | **dialogo unico por par ordenado** de personagens |

### 1.4 Dialogo (CS-E) — os tres eixos de movimentacao (D3)

1. **Retrato animado**: portrait grande com boca/olhos/respiracao sincronizados com a linha de texto.
2. **Corpo inteiro reagindo**: os dois lutadores em cena com poses/gestos que mudam por linha (apontar, cruzar bracos, recuar).
3. **Camera cinematografica**: pan/zoom por scroll de plano e corte entre falantes conforme quem fala.

**Unicidade:** o dialogo e unico por **par ordenado**. Com 6 lutadores isso e
`6 x 5 = 30` dialogos ordenados. Esse numero e o principal risco de escopo —
ver Bloco 3 (degraus).

---

## 2. Reconciliacao honesta com o contrato-mae

O `prompt_modelo_jogo_completo_e2e.md` trava escopo-alvo em **micro-jogo VER.001**.
Este convite pede algo maior. A reconciliacao (SGDK_GLOBAL §21 producao por
degraus, §30 doutrina de audacia) e:

- O escopo total do Bloco 1 e o **destino**, nao o primeiro fechamento.
- O **degrau 1** e um micro-jogo completo que ja prova cada mecanica exigida
  uma vez (Bloco 3, D1). Nenhum degrau seguinte abre antes do anterior fechar
  com evidencia BlastEm selada por hash.
- Qualquer degrau nao alcancado dentro do orcamento entra no pacote de
  aceitacao como **escopo declarado nao entregue** — nunca como verde.

---

## 3. Degraus de producao (ordem inegociavel)

| degrau | entrega | fecha quando |
|---|---|---|
| **D0** | Fase -1 + Fase 0: host, medicao, projeto criado, GDD/TDD, `capability_coverage_plan.json`, opt-in do genero | Q1 aprovado |
| **D1** | vertical slice: 2 lutadores (jack + C1), 1 stage, barra de especial, 1 CS-A, 1 CS-D, 1 CS-E completo com os 3 eixos | **P1** (laudo `live_scene_bar`) + Q3 |
| **D2** | roster jogavel completo (jack, ryo, C1, C2, C3) com movesets e aereos de C3 | Q3 do roster |
| **D3** | cutscenes completas: CS-A e CS-B por personagem, CS-C por stage, CS-D por personagem | evidencia por cena |
| **D4** | os 30 dialogos CS-E do par ordenado | auditoria de unicidade (nenhum texto repetido entre pares) |
| **D5** | C4 chefe final + condicao de unlock + persistencia do unlock | boot-to-unlock provado no emulador |
| **D6** | audio final integrado + fechamento | **P2** → golden CI → **P3** |

**Regra de corte:** se o orcamento acabar em Dn, o entregavel e Dn fechado e
honesto, com Dn+1..D6 declarados como nao entregues. Nunca um D6 pela metade.

---

## 4. Pre-condicoes especificas deste workspace (nao pular)

Estas sao conhecidas e ja causaram falha antes. Todas viram item da Fase -1:

1. **Tooling de host Linux quebrado** — `build.sh` / `new_project.sh` /
   graphify sofrem de PATH shadowing; a rota que builda de fato e o wine
   bridge. Provar a rota de build **antes** de qualquer arte.
2. **Estado de medicao 17/18** (`validate_measurement_tools.py` — self-check
   ausente em `validate_native_sprite_production.py`). Declarar o gap e o teto
   de claim decorrente; sem `ready_for_aaa` enquanto nao fechar.
3. **Projeto novo herda memory bank sujo** — `new_project.sh` copia o historico
   do template para a autoridade #1 da hierarquia de verdade. **Zerar/rebasear
   o memory bank do projeto novo antes da Fase 1.**
4. **Genero exige manifesto opt-in** — a tag `[FIGHTING]` na pasta **nao** conta.
   Emitir o manifesto de genero e atualizar
   `doc/07_game_design/genre_coverage_state.json` (arquivo unico; nao criar um
   segundo arquivo de cobertura). Report com `manifest_status=absent` e falso
   positivo.
5. **Skills do template defasadas** — materializar `.agent` local a partir da
   fonte canonica `tools/sgdk_wrapper/.agent/`, nao de uma copia de projeto.
6. **Pipeline de imagem contradiz as regras** — `batch_resize_index`
   (Lanczos/RGBA) e `fix_png_transparency` destroem o index 0. Nao usa-los no
   caminho de asset final; conversao automatica nasce `technical_candidate`,
   `visually_approved` exige humano.
7. **Fan-out paralelo pesado estoura a sessao** — orquestracao multi-agente so
   via `harness_orchestration.py probe|plan`, respeitando o `execution_mode`
   retornado; nao disparar 3 produtores pesados em paralelo.
8. **Licenca/creditos HAMOOPIG** — jack/ryo e derivados mantem credito a
   GameDevBoss (Daniel Moura) na tela de creditos e no `README.md` do projeto.

---

## 5. Gates especificos deste jogo (usando so o que ja existe)

Nenhum gate novo. Estes sao **criterios de aceitacao** medidos com ferramentas
existentes:

| criterio | como e medido |
|---|---|
| C1 >= +25% | leitura de altura em px do model sheet e do sprite final; registrado no GDD e reconferido no `audit_tile_residency.py` |
| 2 lutadores grandes + efeitos de especial cabem | `vdp_scanline_simulator.py` (2 limites por scanline) **antes** da arte |
| VRAM do roster de 6 | `audit_tile_residency.py` + plano de streaming por luta (so os 2 ativos residentes) |
| cutscene nao derruba 60fps | evidencia BlastEm por cena, selada por hash da ROM |
| unicidade dos 30 dialogos | auditoria textual no closeout (D4) |
| proveniencia de arte | `doc/asset_provenance_manifest.json` + `audit_procedural_asset_provenance.py` |
| identidade SNK'96/SVC nas intros | protocolo de insatisfacao: >= 3 rounds, critico cego >= 8.5/10, pisos numericos |

---

## 6. MENSAGEM DE ATIVACAO (cole numa sessao nova)

```
[Contexto MD Carregado] Ative a via opcional
doc/prompts_modelo/prompt_modelo_jogo_completo_e2e.md como contrato operacional
desta sessao, integralmente e sem pular etapas, instanciada pelo convite
doc/prompts_modelo/convite_taiketsu_ultra_rebirth_e2e.md (escopo, degraus,
pre-condicoes e criterios de aceitacao vem do convite; o resto vem do contrato-mae).

PRE-AUTORIZACAO (Bloco 0 do contrato, concedida agora):
- Modo create_new_project autorizado; nao renderize o menu de sessao.
- Trocas entre as 10 lentes autorizadas DENTRO deste projeto, sempre via
  perspective-switch-gate com registro em doc/agent_session_state.json.
- Conceito ja definido pelo humano (Bloco 1 do convite): NAO reabra o conceito,
  NAO espere aprovacao de escopo. Voce autora nome dos 4 originais, movesets,
  stages, roteiro das cutscenes e texto dos dialogos.
- Orcamento: loop continuo ate o criterio de conclusao do degrau vigente, commit
  local a cada cena fechada; limite duro de 30 iteracoes sem fechar nenhuma cena
  = parada honesta com handoff.
- Pontos de parada obrigatoria (os UNICOS): P1 laudo live_scene_bar da primeira
  cena jogavel do degrau D1; P2 escuta do audio final; P3 pacote de aceitacao.
  Todo o resto roda em loop sem me perguntar.

PROJETO ALVO: crie
SGDK_projects/TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]
a partir da engine de referencia SGDK_Engines/TaiketsuUltraHeroGenesis (HAMOOPIG,
GameDevBoss/Daniel Moura — creditos obrigatorios no jogo e no README). SGDK 2.11.
Roster de 6: jack + ryo (base) + 4 originais (C1 >= +25% de altura vs o maior de
jack/ryo, medido em px; C2 feminina; C3 com especiais e golpes aereos; C4 chefe
final desbloqueavel). Barra de especial que carrega e volta cheia ao conectar o
especial. Cutscene no especial; cutscene de clutch com life <= 25% E barra cheia;
intro de stage; intro individual por personagem no idioma SNK'96/SVC Chaos;
dialogo unico por par ordenado (30) com retrato animado + corpo inteiro reagindo
+ camera cinematografica, os tres simultaneamente.

FASE -1 OBRIGATORIA antes de tudo (Bloco 4 do convite): provar a rota de build
(wine bridge; build.sh/new_project.sh sofrem PATH shadowing neste host);
validate_measurement_tools.py e declarar o gap 17/18 com o teto de claim;
zerar o memory bank herdado do template no projeto novo; emitir o manifesto
opt-in do genero FIGHTING e atualizar doc/07_game_design/genre_coverage_state.json
(arquivo unico); materializar .agent local da fonte canonica; nao usar
batch_resize_index/fix_png_transparency no caminho de asset final.

EXECUCAO EM DEGRAUS (Bloco 3 do convite): D0 → D1 → D2 → D3 → D4 → D5 → D6.
Degrau nao abre antes do anterior fechar com evidencia BlastEm selada por hash.
Orcamento esgotado em Dn = entregar Dn fechado e declarar Dn+1..D6 como escopo
nao entregue. Pipeline mestre game_production_v1.json; por cena aaa_scene_v1.json
na ordem scene-direction-first (medicao ANTES da arte: vdp_scanline_simulator.py
+ audit_tile_residency.py). Multi-agente so via harness_orchestration.py
probe|plan respeitando o execution_mode; revisores read-only Q1-Q4.

REGRA DE FERRO: se nao foi visto rodando no emulador, nao existe. Cada iteracao
termina com build via wrapper, evidencia BlastEm selada por hash, changelog e
memory bank atualizados. ready_for_aaa nunca e auto-declarado.
```

---

## 7. Anti-padroes especificos deste convite

- reabrir o conceito ou pedir aprovacao de escopo (ja decidido no Bloco 0/D1-D3)
- produzir os 30 dialogos antes do D1 fechar (custo morto se a direcao de cena mudar)
- estimar o "+25%" no olho em vez de medir px no model sheet e no sprite final
- manter os 6 lutadores residentes em VRAM ao mesmo tempo em vez de streaming por luta
- gerar sprite grande (C1) sem rodar `vdp_scanline_simulator.py` antes
- rodar `fix_png_transparency` / `batch_resize_index` em asset de entrega
- tratar a tag `[FIGHTING]` da pasta como atribuicao de genero sem manifesto opt-in
- abrir arte com o memory bank herdado sujo do template
- fan-out de 3+ produtores pesados em paralelo

---

## 8. REGISTRO DE INCREMENTOS

| Data | Fonte | Incremento | Evidencia |
|---|---|---|---|
| 2026-09-05 | pedido humano (fighting game E2E) + decisoes D1/D2/D3 | criacao do convite: instancia do prompt modelo E2E com escopo de fighting, degraus D0-D6, pre-condicoes de host conhecidas e criterios de aceitacao mensuraveis | `doc/prompts_modelo/prompt_modelo_jogo_completo_e2e.md`; `SGDK_Engines/TaiketsuUltraHeroGenesis/README.md`; estado 17/18 de `validate_measurement_tools.py` |
