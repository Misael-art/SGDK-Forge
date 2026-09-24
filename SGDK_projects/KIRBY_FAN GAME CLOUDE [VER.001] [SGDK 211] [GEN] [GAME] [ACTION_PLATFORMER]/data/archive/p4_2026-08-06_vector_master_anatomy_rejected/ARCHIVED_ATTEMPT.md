# P4 — tentativa arquivada por falha anatômica

Status: `archived_visual_rejected`
Data: `2026-08-06`

## Sintoma observado

O master vetorial estava tecnicamente limpo, mas os braços e pés não se
integravam de maneira convincente ao volume corporal. A revisão v2 melhorou a
compactação, porém continuou abaixo da anatomia e do carisma exigidos pelo
conceito aprovado.

## Diagnóstico técnico-artístico

- a validação inicial mediu SVG, fills, gradientes e filtros, mas não fechou o
  gate de topologia e proporção;
- membros foram tratados como formas anexadas, não como extensões coerentes da
  massa e da pose;
- limpeza vetorial foi confundida com aprovação visual;
- não existia comparação formal `model sheet + master + silhouette overlay`.

## Heurística preventiva

Um master vetorial de personagem só pode seguir para redução quando passar,
nesta ordem: topologia, proporção, integração dos membros, contato/base,
silhueta, expressão e, por último, limpeza técnica do vetor. Validação de
gradientes, filtros e cores nunca substitui anatomia.

## Uso permitido

Os arquivos em `source_art/p4/` são `negative_evidence` e
`comparison_only`. Não podem ser usados como `generation_source`, baseline,
entrada de quantização ou conteúdo de `res/`.
