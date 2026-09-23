# 98 - 16-bit Effects Campaign Semantic Gate

## Status

Canonizado como gate de rejeicao para campanhas multi-ROM, showcases por eixo tecnico e qualquer pacote que alegue dominio AAA de tecnicas 16-bit.

Ferramenta canonica:

```powershell
tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1 -FailOnBlocker
```

## Falha que este gate cura

A campanha anterior produziu ROMs que compilavam e abriam no BlastEm, mas a tela era dominada por texto, ASCII art, padroes procedurais e um fundo generico. O closeout estrutural contou arquivos, ROMs e screenshots, mas nao provou que as tecnicas estavam implementadas como cenas AAA.

Sintomas proibidos:

- painel de texto ou lista de efeitos vendido como fase;
- `VDP_drawText` dominante como substituto de arte, camera, animacao, audio ou gameplay;
- `lab_bg_b`, ASCII art, `safe rhythm lane`, `efeito empurra` ou template repetido como prova visual;
- fallback procedural generico reutilizado para muitos efeitos;
- `ready_for_aaa=true` com `visual_delivery_gate_report`, `freshness_audit_report`, `scene_closeout_gate_report` ou `res_graph_report` ausente/stale;
- aprendizado local que apenas repete a mesma frase para todos os efeitos.

## Invariantes novos

1. `ready_for_aaa=true` exige `blocking_statuses` vazio.
2. Screenshot BlastEm prova execucao, nao prova qualidade AAA sozinha.
3. Fallback so e aceito se preservar a intencao perceptiva e mecanica especifica do efeito.
4. Fallback generico em massa vira `mass_generic_procedural_fallback`.
5. Campanha de 180 tecnicas precisa provar identidade canonica da tabela, nao inflar cobertura com `proposal_only` sem catalogo verificado.
6. ROM procedural/debug deve declarar `lab_not_delivery=true`.

## Blockers emitidos

- `canonical_180_identity_unverified`
- `mass_generic_procedural_fallback`
- `registry_backed_without_lib_cases`
- `generic_debug_text_panel`
- `generic_lab_resource_set`
- `axis_api_signature_missing`
- `ready_for_aaa_with_blockers`
- `ready_for_aaa_with_unproven_report`

## Uso obrigatorio

Rodar apos as 17 ROMs existirem e antes do closeout consolidado:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1 -FailOnBlocker
```

Saidas esperadas:

- `SGDK_projects/data/aaa_effect_lab_campaign/semantic_audit_report.json`
- `SGDK_projects/data/aaa_effect_lab_campaign/semantic_audit_report.md`

Se o status for `failed`, a campanha nao pode ser chamada de AAA, completa, nota 8, validada, finalizada ou pronta.

## Relacao com aprendizado local

O gate pode apontar padroes de falha, mas nao promove skills automaticamente. Qualquer aprendizado local continua passivo ate revisao humana deliberada.

## Resultado da auditoria da campanha ruim

Execucao em 2026-05-24:

- status: `failed`
- projetos checados: `17`
- tecnicas: `180`
- `proposal_only`: `140`
- `registry_backed`: `40`
- blockers: `105`
- warnings: `17`

Principais agrupamentos:

- `ready_for_aaa_with_unproven_report`: `68`
- `generic_debug_text_panel`: `17`
- `generic_lab_resource_set`: `17`
- `repeated_effect_learning_notes`: `17`
- `canonical_180_identity_unverified`: `1`
- `mass_generic_procedural_fallback`: `1`
- `registry_backed_without_lib_cases`: `1`

Conclusao: a campanha deve ser tratada como `rejected_visual_semantic_gate`, nao como entrega AAA.
