# Prompt Modelo — Direcionamento de Projeto Completo

**versao:** 1.0.0
**ultima_incrementacao:** 2026-08-25
**fontes canonicas:** `AGENTS.md` (raiz) · `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` (§29, §30, §34–38) · `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md` · `tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json` · `doc/PADRAO_NOMENCLATURA.md`

---

## Proposito e protocolo de uso

Este arquivo e o **contrato-base** que todo agente carrega quando o projeto
recebe um direcionamento externo (mega-prompt de jogo completo, brief de
cliente, ideia de escopo grande).

Regra unica: **reconciliar, nunca adotar verbatim.**

1. Leia o direcionamento recebido inteiro.
2. Aplique as 8 correcoes do Bloco 2 — cada uma tem gate correspondente;
   correcao sem gate aplicado nao conta como feita.
3. Embuta o Bloco 3 (prompt magico) na diretriz resultante.
4. Preencha os placeholders do Bloco 4 com o escopo REAL do direcionamento,
   cortando para vertical slice primeiro.
5. Declare capacidade (Bloco 1) antes de prometer qualquer coisa ao usuario.
6. Registre no REGISTRO DE INCREMENTOS (Bloco 5) qualquer licao medida nova
   surgida durante a reconciliacao.

O output da reconciliacao e a **diretriz do projeto incrementada** — documento
unico, deduplicado, com budget fechado e gates canonicos mapeados.

---

## Bloco 1 — Preambulo de capacidade (copiar literal no topo da diretriz)

> Antes de aceitar qualquer tarefa deste contrato, declare capacidade com
> prova (SGDK_GLOBAL.md §38): execute a sonda real e escolha UM estado —
>
> - `capaz_com_prova_agora` — sonda passou nesta sessao;
> - `capaz_apos_preparo_medido` — preparo ausente, custo medido e declarado;
> - `nao_capaz_neste_host` — limite estrutural declarado sem promessa futura.
>
> Para geracao visual vale a arvore obrigatoria: Ramo A (nativo com prova ->
> gerar), Ramo B (host preparado -> circuito local ai_imagegen), Ramo C (nem
> agente nem host -> successor_asset_directive com quality protocol).
> "Acho que consigo" nao existe como estado.

---

## Bloco 2 — Protocolo de reconciliacao (8 correcoes obrigatorias)

| # | Correcao | Gate/ferramenta que prova |
|---|---|---|
| 1 | Herdar prior art em vez de criar projeto orfao; se novo nome for inevitavel, formalizar sucessao | `adopt_project_methodology.ps1`; inventario de projetos irmaos em `SGDK_projects/` |
| 2 | Path e nomenclatura validos antes de qualquer arquivo | `validate_project_name.ps1`; `doc/PADRAO_NOMENCLATURA.md`; sem subdiretorio aninhado extra |
| 3 | So gates canonicos do wrapper; proibido criar `gates.py`/harness proprio dentro do projeto | `vdp_scanline_simulator.py`, `capture_blastem_evidence`, `screenshot_semantic_gate.py`, `audit_luma_floor.py`, evidence ladder |
| 4 | Toda arte IA atravessa a cadeia completa de proveniencia | `doc/asset_provenance_manifest.json` (`ai_generated` + hash), authoriality gate, clone risk report, `art-translation-to-vdp` |
| 5 | Primeiro alvo = vertical slice completo fechando os 7 eixos do gate de entrega; expansao por degrau medido | doutrina de audacia §30: medir o proximo degrau, nao sentir |
| 6 | Fatos de hardware corretos: XGM2 (nao XGM), convencao RGB unica {0,34,68,102,136,170,204,238}, H40=320px / H32=256px, flicker documentado onde o visual vive (nao em SOUNDMAP) | tabela anti-alucinacao do `AGENTS.md`; headers `sdk/sgdk-2.11/inc/` |
| 7 | Diretriz deduplicada: secao repetida, bloco colado duas vezes ou instrucao contraditoria = defeito bloqueante de Fase 0 | revisao humana do contrato F0 |
| 8 | Budget de tokens/tempo definido ANTES de iniciar; checkpoint humano periodico; parada final sempre humana | campo `{{BUDGET}}` preenchido; MILESTONES |

---

## Bloco 3 — Nucleo do prompt magico (protocolo de insatisfacao)

Fonte estruturada: `successor_quality_protocol` em
`tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json`.
Texto literal para embutir na diretriz:

> "Voce nao entrega primeira versao. Para cada asset deste contrato:
> **gere → audite cada piso numerico → rejeite qualquer saida que falhe UM
> piso → regenere registrando o que mudou.**
>
> - Minimo de 3 rounds mesmo quando o round anterior pareceu bom — 'pareceu
>   bom' NAO e criterio; piso numerico e.
> - Audite cada piso com a ferramenta declarada (`numeric_floors[].measurement_tool`),
>   nunca por impressao.
> - Qualquer padrao listado em `rejection_triggers` reprova a saida
>   automaticamente antes do proximo round.
> - Cada round registra score por piso + correcao feita no log de critica
>   propria (`self_critique_log_required`).
> - So declare a arte pronta quando TODOS os pisos passarem E o julgamento
>   final aprovar: visual-excellence-standards + crítico cego >=
>   blind_critic_floor (default canonico **8.5/10**) + aprovacao humana. Sua
>   auto-satisfacao nunca e anchor de aceitacao.
> - Se um piso nao passa apos `max_rounds_before_honest_gap`, declare a lacuna
>   honestamente conforme SGDK_GLOBAL.md §38 — rebaixar o piso e proibido."

Pisos default canonico (endurecer por projeto livre; amolecer exige aprovacao humana):

| Piso | Valor default | Medicao |
|---|---|---|
| contraste luma elemento/fundo | >= 34 (1 degrau) | `audit_luma_floor.py` |
| paleta | canais 9-bit exatos {0,34,…,238} | pixel strict rules |
| silhueta | legivel em preto-e-branco no tamanho alvo | inspecao + crítico cego |
| grid/transparencia | multiplos de 8px; index 0 transparente | validacao de recursos |
| nota do crítico cego | >= 8.5/10 | painel cego embaralhado com referencias |

Complemento obrigatoria ao crítico cego: identificacao cega sozinha nao fecha
gate (critico ruim ≠ arte boa). Passa quem soma pisos numericOS verdes E nota
>= piso E sem rejection trigger ativo.

---

## Bloco 4 — Esqueleto de fases (preencher placeholders)

```
{{PROJETO}}       — nome conforme PADRAO_NOMENCLATURA
{{ESCOPO_SLICE}}  — o vertical slice do primeiro fechamento
{{BUDGET}}        — tokens/tempo definidos pelo usuario ANTES do inicio

FASE 0 — CONTRATO (docs do modelo/, criterios mensuraveis, deduplicado)
FASE 1 — VERTICAL SLICE {{ESCOPO_SLICE}} com arte provisoria DENTRO dos
         gates; TODOS os 7 eixos verdes; evidencia BlastEm por build
FASE 2 — GAUNTLET de subsistemas/assets: Construtor produz, protocolo do
         Bloco 3 itera, crítico cego + pisos julgam, GATES.md registra
FASE 3 — expansao por degrau medido (novas fases/habilidades/trilhas),
         cada degrau medido antes de entrar (§30)
```

Cada fase herda o esqueleto documental real de
`tools/sgdk_wrapper/modelo/doc/` — memory bank, GDD, spec-cenas, changelog
versionado por build. Documento paralelo inventado = orfao.

---

## Bloco 5 — REGISTRO DE INCREMENTOS

### Regras de incremento automatico

1. O agente PODE incrementar este arquivo sozinho quando existir **licao
   medida** com fonte citada: changelog de `doc/agent_learning/`, JSON de
   curadoria, report de gate, ou secao numerada da SGDK_GLOBAL.
2. Cada linha: data · fonte · incremento · evidencia. Sem fonte, sem linha.
3. Incremento que ALTERNA doutrina existente (nao apenas acrescenta) exige
   aprovacao humana registrada antes do merge — politica de curadoria.
4. Bump de versao: +0.0.1 para linhas novas, +0.1.0 para regra nova,
   +1.0.0 para reescrita aprovada por humano.

### Registro

| Data | Fonte | Incremento | Evidencia |
|---|---|---|---|
| 2026-08-25 | avaliacao do mega-prompt Kirby AX ALPHA (sessao ox-alpha) | criacao do arquivo: 8 correcoes de reconciliacao + protocolo de insatisfacao (min_rounds=3, blind_critic_floor 8.5, lacuna honesta §38) | `doc/agent_learning/changelog_2026-08-25.md`; predecessor GROK BUILD com crítico cego 5.8/10 e fases ausentes; registry sem tecnica MESTRE_* |

---

## Anti-padroes

- adotar direcionamento externo verbatim sem reconciliacao
- reconciliar sem aplicar as 8 correcoes com gate provado
- adjetivo de qualidade sem piso numerico (§36)
- tool de medicao inventada dentro do projeto (duplica wrapper)
- escopo total antes do vertical slice fechado
- budget "[definir depois]"
- documento com secao duplicada seguindo para producao
- crítico cego como unico juiz de pass/fail
- prompt magico sem pisos numericos ("nao se satisfaca" sem numero)
