# Handoff — Kirby V11 visual production

## Retomar daqui

- Branch: `codex/kirby-full-visual-production-v11`
- Base preservada: `codex/kirby-visual-review-runtime-v10`
- Último commit funcional: `05cecc83 feat(kirby): open v11 native visual production review`
- Escopo: candidatos visuais completos autorizados nesta branch; promoção
  mainline e aceitação final humana continuam proibidas.

## Entrega concluída

O primeiro pacote causal é `kirby_run_contact_v11`:

- fonte de identidade exclusiva: `data/source_art/r1/r1-01/concept.png`
- SHA da fonte: `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`
- bridge: `forge-art native-edit`
- ações: `data/staging/v11_native_edit/run_contact_actions.json`
- candidato: `out/v11_native_edit/run_contact_v2/`
- runtime review: `APP_SCENE_NATIVE_ART_REVIEW`, recurso `spr_native_run_contact_v11`
- estado: `native_candidate`, não é arte final

Comandos de rechecagem:

```text
cd tools/sgdk_wrapper
PROJECT_ROOT="../../SGDK_projects/KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]"
python3 -m forge_art self-check
python3 -m forge_art validate "$PROJECT_ROOT/out/v11_native_edit/run_contact_v2/candidate.png" --index0-role transparent0
```

## Evidência real

Bundle BlastEm selado:
`out/evidence/v11_run_contact/blastem-linux-20260904T084548Z-2942661/`

- ROM SHA: `55b5759a27e18e0064653a285b80dcef378397c777f63704ed05025faa2e3b8c`
- cena 11 correta; 600 frames; 60,2 fps; CPU p99 21%; hard gates pass
- screenshot, SRAM, VDP dump e métricas estão vinculados ao mesmo ROM SHA

## Auditoria de continuidade — 2026-09-04

- Técnico: `candidate.png` e `candidate_8x.png` conferem com os hashes do
  relatório; o contrato P/4bpp/index-0 transparente passou sem blockers.
- 1×: a leitura do personagem é baixa fora de zoom; o sprite ocupa pouco do
  quadro e exige inspeção ampliada para distinguir pose e detalhes faciais.
- 8×: a silhueta é legível e a paleta é consistente, mas corpo e os dois pés
  aparecem como componentes separados; confirmar com a referência R1 se essa
  separação é intencional para o contato ou um artefato de pose.
- Runtime: BlastEm provou consumo no review scene 11 e passou os hard gates,
  mas a captura não prova qualidade visual, coesão de animação ou aceitação
  humana; não há burst de animação neste bundle.
- Resultado: nenhum defeito técnico do pacote exige correção nesta rodada. O
  próximo passo continua dependente da revisão humana em 1×/8×.

## Próxima ação obrigatória

1. Fazer revisão humana do candidato em 1× e 8×, comparando-o com R1 sem
   substituir a autoridade.
2. Se aprovado, produzir a próxima pose nativa (`run_passing`) pelo mesmo bridge,
   com action file independente e captura de comparação.
3. Só depois de um roster mínimo coerente começar `stage_1 + HUD`.

Não reutilizar pixels v04–v10 como fonte. Não transformar este candidato em
`visual_pass`, `final_acceptance` ou `ready_for_aaa` sem decisão humana,
recaptura da ROM e gates completos.

## Bloqueios conhecidos fora deste pacote

Os validadores metodológicos continuam bloqueados por dívida preexistente:
`critical_motion` sem pacote perceptivo/humano completo, `modular_boss` sem
contrato FK válido e higiene do projeto com nome/template e referência Windows
legados. Não mascarar esses blockers para fechar o handoff.
