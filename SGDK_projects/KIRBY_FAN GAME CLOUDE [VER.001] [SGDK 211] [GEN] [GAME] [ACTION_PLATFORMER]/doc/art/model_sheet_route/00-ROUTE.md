# Rota do model sheet — a metade dianteira que o P1 pulou

**Aberta em:** 2026-08-10
**Estado:** etapa 0 concluída, etapa 1 aguardando aprovação humana
**Por que existe:** quatro rotas de arte (P1–P4) foram reprovadas visualmente no mesmo
dia. Todas produziam **asset final** diretamente. Nenhuma produziu model sheet antes.

---

## 1. O diagnóstico que justifica a rota

Medições feitas em 2026-08-08 e 2026-08-10, não opiniões:

| Fato medido | Onde |
|---|---|
| O P1 passa no gate de solidez em 8/8 frames, `center_idx0 = 0,0%` | `out/logs/solidity_p1_vs_archive.json` |
| O P1 tinha **9 tons de corpo** — mais que o dobro da referência NES (4) | `01-reference-study.md` §1 |
| A referência lê melhor a 24×24 com 4 cores do que o P1 a 32×32 com 9 | `out/evidence/model_sheet_route/ref_vs_ours.png` |
| O defeito do P1 é **silhueta**, não paleta nem conversão | `01-reference-study.md` §3 |

**Conclusão:** nenhum gate adicional teria salvado o P1. O erro estava antes do pixel —
na forma. É por isso que a rota começa em desenho, não em conversão.

## 2. A ordem, e o que trava cada passo

Derivada da rota `mare_brava`, a única do workspace que chegou ao runtime com direção
visual aprovada. Cada passo tem uma saída obrigatória; sem ela o passo seguinte não
tem permissão para se declarar concluído.

| # | Etapa | Saída obrigatória | Trava |
|---|---|---|---|
| **0** | **Estudo de referência** | `01-reference-study.md` com números | ✅ **feito** |
| **0b** | **DNA visual** | `visual_dna_manifest.json` conforme schema | ✅ **feito** (`approval_status: draft`) |
| **1** | **Desbloqueio do estudo** | operador autorizou seguir; DNA recalibrado no tier SNES (v02) | ✅ **feito** |
| **2** | **Model sheet + turnaround** | `data/source_art/model_sheet_v01/`, 5 vistas, contrato PASS | ✅ **feito** |
| **3** | **Aprovação humana do model sheet** | `art_gameplay_direction_gate` com decisão registrada | ⛔ **BLOQUEIO ATUAL** |
| 4 | Lineart por estado | contorno fechado, 1 px, um por estado de animação | requer etapa 3 |
| 5 | Key poses | poses extremas, não frames intermediários | requer etapa 4 |
| 6 | Strip | derivado das key poses por **edição de cluster**, nunca gerando cada frame | requer etapa 5 |
| 7 | Conversão + gates | `sprite_solidity` + `validate_assets` + captura BlastEm | requer etapa 6 |

### Por que a etapa 6 é "edição de cluster" e não geração

Lição L12 do MARE_BRAVA (`doc/agent_learning/failure_patterns.md` daquele projeto,
2026-07-29): gerar todos os frames por IA produz **morphing**, não animação — deriva
medida de 7 px horizontal e 3 px de altura, com cabeça, corpo e eixo de apoio
redesenhados a cada frame. A contra-regra promovida é L13: pose-mestre aprovada +
edição de clusters preserva autoria.

## 3. O que a referência pode e não pode fazer

O material de estudo (Kirby's Adventure NES e irmãos) já está em disco, baixado pelo
projeto irmão GROK BUILD, catalogado com `"ship_allowed": false`.

| Uso | Permitido |
|---|---|
| Medir proporção, razão de sombra, economia de tons | **sim** — é o `benchmark_used_as: scale_density_timing_only` |
| Olhar para decidir o que faz o personagem legível a 32 px | sim |
| Traçar, decalcar, usar como base de img2img ou upscale | **não** |
| Copiar para `res/`, entrar na ROM | **não** |

A segunda coluna não é escrúpulo meu: `SGDK_GLOBAL.md:218` bloqueia promoção de fonte
clone ou benchmark-derived, e a Trava 6 exige `authorial_line_contract` para asset
autoral crítico. Um model sheet decalcado reprova nos dois.

**Precedente registrado:** o projeto irmão instalou rips do TSR direto em `res/` na
sessão 011, com autorização escrita por ele mesmo. O resultado regrediu a qualidade
que suas próprias rodadas R3–R6 haviam conquistado com arte autoral. A regra existe
porque o atalho já foi medido e é pior.

## 3b. Autocrítica do model sheet v01 — defeitos que o contrato não reprova

O gerador passa em todas as travas mecânicas. Isso **não** é aprovação visual, e
registrar os defeitos aqui é o que impede o v01 de virar final por exaustão (§17 e
§22 do `SGDK_GLOBAL`). Defeitos que eu vejo e que nenhum número deste projeto pega:

| # | Defeito | Gravidade |
|---|---|---|
| V1 | **Braços ainda fundem no corpo.** Leem como protuberâncias laterais, não como cotos com entalhe de contorno. A silhueta total é um ovo horizontal, não uma esfera com apêndices | alta — é identidade |
| V2 | **Pés flutuam.** Há vão entre a base do corpo e os lobos do pé | média |
| V3 | **`three_quarter_back` e `back` são idênticas.** O turnaround não gira de fato nas duas últimas vistas | média — turnaround incompleto |
| V4 | **Sem bochecha.** A referência trata blush como feature de identidade; o v01 não tem | baixa |
| V5 | Braços tocam a borda da célula em x=0 e x=31, sem folga de bbox | baixa |

Duas correções já aplicadas nesta rodada, ambas por violarem o DNA sem que o gate
percebesse — o gate foi reforçado junto:

- **rim contornava para o lado escuro**, contradizendo a luz superior-esquerda
  declarada em R1. O gate media área por degrau e nunca **onde** ela caía. Agora
  verifica o centroide do degrau claro contra o vetor de luz.
- **olho lia como fenda** (3,1 px de largura). O gate media a bbox dos dois olhos
  juntos (11×7) e reprovava um par correto. Agora mede um olho por vez.

## 4. Bloqueio atual — decisão do operador

A etapa 1 exige julgamento humano, e ele não pode ser delegado a nenhum gate. O que
está sobre a mesa é o `visual_dna_manifest.json`, em particular:

1. **Economia cromática como regra** — 4 a 6 tons de corpo, contra os 9 do P1.
   Isto contraria a intuição de "mais cor = mais AAA", e é a mudança de direção mais
   forte que a medição sugere.
2. **Contorno escuro fechado** em 100% da silhueta, com slot dedicado (PAL2[6]).
3. **Razão corpo : pé ≥ 3:1** — o pé do P1 dominava o terço inferior.
4. **Olho como feature-assinatura**, oval vertical de ~1/4 da altura do corpo.

Enquanto `approval_status` for `draft`, nenhuma arte final deve ser produzida. Essa é
literalmente a regra que o P1 violou.

## 5. Recuperação de memória

| Quero saber | Leio |
|---|---|
| Por que a rota existe | este arquivo §1 |
| Os números da referência | `01-reference-study.md` |
| O contrato de arte vigente | `visual_dna_manifest.json` |
| Comparação visual ref × atual × P1 | `out/evidence/model_sheet_route/ref_vs_ours.png` |
| Por que o gate de índice não bastou | `doc/agent_learning/failure_patterns.md`, entrada 2026-08-08 |
| O que o gate de índice prova e não prova | `tools/harness/README.md` §`sprite_solidity.py` |
| Onde as rotas mortas estão | `data/source_art/archive/`, `data/archive/`, `rascunho/archive/` — **evidência negativa, proibidas como fonte** |
