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
| `arrival_gates` | Gates que a arte enfrentara ao chegar (proveniencia, pixel strict, visual excellence, BlastEm) |
| `persistence_contract` | Onde salvar (`data/source_art/<role>/`) e que lineage registrar |

## Frase de abertura sugerida para o sucessor

> "Voce esta assumindo o papel de criador de assets visuais deste projeto porque o agente
> anterior provou, com sonda registrada, que nao tinha canal de geracao neste host. Leia os
> docs canonicos em `project_context.canonical_docs_to_read` ANTES de gerar qualquer pixel,
> carregue as skills listadas em `required_skills_to_load` e saiba que sua entrega passara
> pelos gates em `arrival_gates` — arte procedural primitiva nunca satisfaz entrega final."

## Anti-padroes

- Emitir diretriz sem sonda real registrada (`probe_evidence` vazio ou genérico).
- Usar a diretriz como desculpa para prometer "depois eu gero" sem preparo medido.
- Diretriz sem ponteiros concretos de contexto (o sucessor tem que adivinhar onde ler).
- Esconder do usuario o estado `nao_capaz_neste_host`.
