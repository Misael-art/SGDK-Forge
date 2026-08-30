# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.


## L01 prompt pack para geracao humana assincrona

- Data: 2026-07-03
- Contexto: canal de geracao IA bloqueado no host (sem callable, sem API, Bonsai exige NVIDIA); arte de concept necessaria para o CAIS_01
- Padrao observado: prompt pack com prompts especificos (paleta hex, poses numeradas, negative prompt, criterios de aceite, caminho de salvamento) rendeu 15 concepts utilizaveis na primeira geracao feita pelo humano em modelo externo
- Causa provavel: especificidade tecnica do prompt transfere a direcao de arte para qualquer canal disponivel sem perder o contrato visual
- Mitigacao: formalizar prompt_pack como saida padrao da art-creation-sourcing quando generation_channel_decision=blocked
- Evidencia: doc/art/prompt_pack/00_leia_primeiro.md e data/source_art/premium_source_manifest.json
- Classificacao: candidato_canonico
- Candidato: art/art-creation-sourcing adotar prompt_pack como artefato padrao

## L04 contact sheet vdp como prova barata

- Data: 2026-07-03
- Contexto: direcao de arte pendente de ratificacao humana; necessidade de provar sobrevivencia da linguagem no VDP antes de converter
- Padrao observado: downscale 320x224 + quantizacao 15 cores + snap 9-bit (passo 36 por canal) separou objetivamente o que sobrevive (cenarios, BG loop, logo) do que nao sobrevive (personagem realista em 44-56px)
- Causa provavel: a prova reproduz as restricoes reais do alvo com custo quase zero
- Mitigacao: incorporar o contact sheet VDP como gate padrao do art-translation-to-vdp via script canonico no wrapper
- Evidencia: data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png
- Classificacao: candidato_canonico
- Candidato: script canonico de contact sheet VDP no tools/sgdk_wrapper
