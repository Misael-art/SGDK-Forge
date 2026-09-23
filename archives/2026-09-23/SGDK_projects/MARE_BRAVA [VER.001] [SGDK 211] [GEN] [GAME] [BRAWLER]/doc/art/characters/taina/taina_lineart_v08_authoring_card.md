# TAÍNA v08 — Cartão de Autoria de Lineart 1px

Status: `production_brief_ready_not_asset`
Alvo: uma prancha de turnaround de lineart 1px; não é strip, sprite final ou recurso SGDK.

## Fonte permitida

- Direção escolhida: imagem 04 da linha do tempo, `authorial_style_validation_contact_sheet_v01.png`.
- Fonte individual: `taina_identity_turnaround_authorial_v01.png`.
- Contratos: `visual_dna_manifest.json`, `art_gameplay_direction_gate.json`,
  `authorial_line_style_contract.json`, `iteration_control_protocol.md` e
  `taina_v08_visual_breakdown.md`.

Não usar v05, v06, v07 nem as comparações 05/06 como entrada visual. São
apenas evidência de falha.

## Entregável único

`taina_lineart_blocking_1px_candidate_v08.png`

- quatro vistas: frente, 3/4, perfil e costas;
- célula de 48x64 por vista, altura visível alvo 48px;
- pivot `bottom_center`, pés em y=58–60;
- uma cor escura temporária; sem AA, blur, cor, textura ou sombreamento;
- fundo de index 0 planejado, mas o PNG não será promovido sem revisão visual.

## Eixo único desta iteração

Corrigir somente **proporção e escala** sem alterar a assinatura visual.
Se cabelo, face, guarda, assimetria ou roupa exigirem mudança, interromper e
abrir uma nova decisão de direção em vez de alterá-los silenciosamente.

## Marcadores que têm de sobreviver

1. Massa cacheada curta, presa e irregular; nunca capacete ou nuvem lisa.
2. Sobrancelha forte, nariz em cunha, mandíbula compacta e olhar no oponente.
3. Guarda alta diagonal de muay thai; punhos e pés comunicam combate.
4. Top laranja queimado, calça roxo-escura larga, bandagens verdes e faixa
   lateral no lado coerente.
5. Peso de corpo legível: ombro/quadril em diagonal e pés com contato claro.

## Reprovação imediata

- corpo chibi ou anatomia realista alta;
- rosto genérico/liso ou perda da massa de cabelo;
- faixa, bandagens ou guarda trocando de lado/função;
- massa simbólica sem ombros, braços e mecânica de guarda;
- melhoria de escala que reduza a identidade.

## Evidência necessária antes do próximo estado

- comparação `fonte autoral | v08 | v05/v06 como negativo` em escala nativa e 8x;
- tabela `must_preserve` com passou/parcial/reprovado;
- `model_sheet_to_sprite_fidelity_report_v08.json` com `visual_pass` separado
  de conformidade técnica;
- aprovação humana explícita para seguir para color blocking.

Enquanto esses itens não existirem, v08 permanece `candidate_for_human_review`.
