# Successor Asset Directive — Template

Contrato machine-readable: `tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json`
Regra-mae: `SGDK_GLOBAL.md` secao 38 (capacidade declarada com prova).
Skill dona: `image-generation-routing`, Ramo C.

## Quando emitir

Somente depois de sondar de verdade (regra secao 38 — sem sonda nao ha Ramo C):

1. Sonda nativa: a sessao atual tem ferramenta callable/inline de imagem? NAO.
2. Sonda de host: `imagegen_tool.py --json status` + healthcheck do perfil. Falhou por
   estrutura (sem GPU, runtime ausente) ou install foi medida e recusada.
3. Entao: nem agente nem host geram -> **Ramo C**. Emita esta diretriz como ENTREGA,
   registre `generation_channel_decision.json` com `outcome_branch=C_successor_directive`,
   `successor_directive_emitted=true`, e comunique ao usuario em estado honesto:
   `nao_capaz_neste_host`.

## O que a diretriz precisa conter

Preencha o JSON conforme o schema. Resumo dos blocos obrigatorios:

| Bloco | Pergunta que responde |
|---|---|
| `probe_evidence` | Que sondas rodaram e por que cada canal caiu |
| `capability_state` | Estado final no vocabulario de 3 estados |
| `project_context` | O que o sucessor DEVE reler antes de gerar (memory bank, biblica artistica, spec de assets) |
| `successor_role` | Missao do sucessor + skills canonica a carregar ao chegar |
| `assets` | Lista de assets: papel, spec/ponteiro, source_kind exigido, dimensoes, paleta |
| `successor_quality_protocol` | Como o sucessor se obriga a iterar ate barra AAA (prompt magico abaixo) |
| `arrival_gates` | Gates que a arte enfrentara ao chegar (proveniencia, pixel strict, visual excellence, BlastEm) |
| `persistence_contract` | Onde salvar (`data/source_art/<role>/`) e que lineage registrar |

## Prompt magico canônico (embutir na diretriz)

Texto literal para injetar no contexto do modelo gerador junto com a diretriz:

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
>   final (`final_judgment`: visual-excellence-standards + crítico cego >=
>   blind_critic_floor + aprovacao humana) aprovar. Sua auto-satisfacao nunca
>   e anchor de aceitacao.
> - Se um piso nao passa apos `max_rounds_before_honest_gap`, declare a lacuna
>   honestamente conforme SGDK_GLOBAL.md §38 — rebaixar o piso e proibido."

Pisos default canonico do workspace (endureça por projeto, nunca amoleca):

| Piso | Valor default | Medicao |
|---|---|---|
| contraste luma elemento/fundo | >= 34 (1 degrau) | `audit_luma_floor.py` |
| paleta | canais 9-bit exatos {0,34,68,102,136,170,204,238} | pixel strict rules |
| silhueta | legivel em preto-e-branco no tamanho alvo | inspecao + crítico cego |
| grid / transparencia | multiplos de 8px; index 0 transparente | validacao de recursos |
| nota do crítico cego | >= 8.5/10 | painel cego |

## Frase de abertura sugerida para o sucessor

> "Voce esta assumindo o papel de criador de assets visuais deste projeto porque o agente
> anterior provou, com sonda registrada, que nao tinha canal de geracao neste host. Leia os
> docs canonicos em `project_context.canonical_docs_to_read` ANTES de gerar qualquer pixel,
> carregue as skills listadas em `required_skills_to_load` e saiba que sua entrega passara
> pelos gates em `arrival_gates` — arte procedural primitiva nunca satisfaz entrega final."

## Anti-padroes

- Emitir diretriz sem sonda real registrada (`probe_evidence` vazio ou genérico).
- Diretriz Ramo C sem `successor_quality_protocol` populado — insatisfacao sem
  piso numerico vira humor do modelo, nao protocolo.
- Usar a diretriz como desculpa para prometer "depois eu gero" sem preparo medido.
- Diretriz sem ponteiros concretos de contexto (o sucessor tem que adivinhar onde ler).
- Esconder do usuario o estado `nao_capaz_neste_host`.
- Aceitar round antes de `min_rounds` por sensacao de qualidade.
- Rebaixar `blind_critic_floor` para fechar entrega sem aprovacao humana registrada.
