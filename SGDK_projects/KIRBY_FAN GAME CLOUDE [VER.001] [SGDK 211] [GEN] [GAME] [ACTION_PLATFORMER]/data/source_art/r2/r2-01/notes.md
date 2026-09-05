# R2-01 — correcao localizada da pose floating

- Assinatura: Codex
- Parent: `data/source_art/r1/r1-01/concept.png` (sha256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`).
- Escopo: somente a pose floating no retangulo `x=360..663`, `y=374..549` foi reeditada; o restante recebeu apenas a troca deterministica da rampa salmao pela rampa rosa aprovada.
- Edicao visual: `floating_pose_generated.png` e o registro bruto da edicao localizada com o gerador. `floating_pose_r2_crop.png` e a derivacao 304x176 normalizada e a fonte que foi composta em `concept.png`.
- Rampa final: `#ffdbff` highlight, `#ffb6db` claro, `#ff92b6` meio-tom/base, `#db4992` sombra, `#92246d` profundo; contorno `#6d2449`.
- Aceite medido: 12 cores na prancha; 0 pixels fora da grade RGB333 do projeto; o meio-tom `#ff92b6` ocupa 1539 de 15387 pixels visiveis da pose (10.001950%).
- Decisao: as bochechas laterais e o volume central foram separados em clusters hard-edge para que a silhueta continue legivel na traducao para 28px.
- Limitacao: esta continua sendo uma prancha conceitual. Nao e sprite final, nao entra em `res/` e ainda exige redraw 8x8, pivots e prova no BlastEm.
