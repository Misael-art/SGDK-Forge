# Changelog Canonico - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## 2026-09-24 - Q3: indice de intake MUGEN -> owners

- `python3 -m mugen2sgdk_forge intake-index` gera `doc/curation/mugen_intake_index.{json,md}` a partir do registro de licoes + parecer mais recente.
- Cada linha: licao, fonte@commit, blob sha1, owner resolvido contra o repo, status, proxima acao. O indice nao guarda status proprio nem promove nada.
- `--check` reprova indice desatualizado, owner inexistente e promocao sem `canonized_in`. Estado atual: 12 licoes, 0 problemas. Suite: 43 testes.

## 2026-09-24 - Q2: regressao focal do SuperPause

- Personagem sintetico (sem terceiros), com valores distintos por parametro, compilado e executado no host.
- Verifica o espelhamento do X com facing -1, os ticks exatos de pausa e movetime, o dono, o power e qual som tocou.
- Mutacao de indice ou do espelho reprova o teste. Suite: 41 testes.

## 2026-09-24 - Q1: proveniencia no schema canonico + falso positivo do neg1_masks

- O conversor gravava enums fora do schema, e o manifesto inteiro invalido gerava 125 "sem proveniencia" falsos.
- Agora: procedural_composed_from_authored + placeholder + hash do pacote + licenca NAO verificada, por simbolo.
- O auditor segue o array ate o destino (chamada VDP/DMA, tipo grafico SGDK, campo de struct -> usos).
  - Tabela logica: informativa.
  - Pixel renomeado ou nao resolvido: continua bloqueando.
- Auditoria do projeto: rc=0, sem bloqueios. As outras 17 arvores nao tem arrays desse tipo (sem mudanca).

## 2026-09-24 - Etapa 1: desempenho com audio real (29,3% -> 8,5%)

- Captura com audio real (disk). O denominador pos-warmup agora e exportado; o quociente bruto antigo subestimava.
- Sonda: px por linha (limite de 320 em H40) e varredura so nas fronteiras; o laco antigo custava ~10% do quadro.
- VM: frente leve para constantes e var(n); pilha por ponteiro. O trace do host e identico (md5 b47cfeef...).
- Maximos: 10 sprites e 288 px por linha. PCM real custa ~4 pontos. Nenhum efeito visivel removido.

## 2026-09-23 - P6: catalogo de 180 efeitos registrado (consultivo)

- Aderencia avaliada: 10+ ja em uso com ROM citada, 7 candidatos priorizados, eixos fora de escopo justificados. Nada implementado.

## 2026-09-23 - P3: memo de multiplexacao dos aneis (NO-GO)

- Medido: pior quadro de anel 107 tiles / 3,4 KB DMA; simulador 16 sprites/linha (ok).
- Multiplex 16x16 estoura (21/linha); 32x32 fica perto do limite (18) e perde fidelidade. Nada implementado.

## 2026-09-23 - P5: sombra pontilhada sob o lutador (memo comparativo)

- Memo: doc/hud/p5_shadow_memo.md (dither x flicker x blinking x Shadow/Highlight, com custos medidos).
- Vencedora: dither em sprite 32x8 (+1 sprite/lutador, 0 paleta, 4 tiles, 0 DMA/quadro); estouro residual
  0,20% tratado por prioridade (sombra descartada primeiro), nao por flicker.
- Forma DERIVADA da silhueta 0,0 do Ken (technical_candidate, aprovacao visual pendente).
- ROM 46a9cd65...: 27,0% acima do orcamento (faixa 23-27% entre capturas).

## 2026-09-23 - P4/P4.1: HUD de luta (arte SFA2 Lifebars convertida)

- Vida amarela drenando com fantasma vermelho (estilo SF), especial azul (mesma arte, cor por paleta),
  tempo, retratos 9000,0, vitorias, "N HITS" junto de quem comba (ancora de evento do P1), ROUND n /
  FIGHT! / K.O. / TIME OVER / DRAW. HUD some durante o fundo de super (nobardisplay).
- Contrato, medicoes e decisoes: doc/hud/p4_hud_contract.md. `convert-hud` no mugen2sgdk_forge.
- ROM b138fb35...: 23,1-26,2% dos quadros acima do orcamento (baseline 22,6%); HUD ~3% do quadro.

## 2026-09-23 - P2: rampas de roupa mais vivas (medidas antes de ajustar)

- Achado: saturacao ja era maxima; defeito real = brilho baixo + degrau colapsado + pouco contraste.
- Alvos T1-T4 e metodo em doc/mugen/p2_palette_calibration.md; `convert-char --vivid-clothing`.
- Turquesa (P1): V 0,85/0,56 -> 0,99/0,71, deltaE 50 -> 63. Vermelho (P2): degraus 5 -> 6, deltaE 90 -> 97.
- Evidencia BlastEm: ROM 5690eafe... (antes 38a67c94...). Desempenho inalterado.

## 2026-09-23 - P1: faiscas ancoradas no ponto de contato + variacao em combo

- Faisca nasce no centro da intersecao Clsn1 x Clsn2 que registrou o acerto (antes: borda frontal do
  defensor + sparkxy, regra MUGEN). Divergencia deliberada, declarada.
- Combo na mesma regiao (relativa ao corpo do defensor, <=16 px, <=90 ticks) percorre 4 variacoes
  sutis (0,0) (+3,-2) (-3,+2) (+2,+3).
- Teste: tests/test_host_runtime.py::test_hit_sparks_anchor_on_contact_and_vary_in_combo
  (alto y~-78 vs baixo y~-6; variacoes 0,1,2,3,0).
- Evidencia BlastEm: ROM de teste f1f4df6a... (-DMG_TEST_SCRIPT -DMG_TEST_COMBO), sessao
  out/mugenesis_evidence/p1_sparks/blastem-linux-20260923T184801Z-674202.
- Desempenho (ROM normal 38a67c94..., CPU x CPU): 860/3811 quadros acima do orcamento = 22,6%
  (antes 23%), pico 159%. Sem regressao.

## 2026-09-23 - Efeitos de super completos (anel, bola de fogo super, fundo de vitoria)

- Quadros grandes divididos em ate 4 sprites; fundo de super em BG_B com animacao de paleta; Helper reduzido.
- Corrigido deslocamento de indice de parametros (SuperPause/PlaySnd).
- ROM ce783a61...; desempenho: 23% dos quadros acima do orcamento (E3b pendente).

## 2026-09-23 - E3: Ken convertido do MUGEN rodando no BlastEm

- Cena de luta hospeda o runtime generico mugen2sgdk_forge; boot direto na luta (MG_DIRECT_FIGHT).
- Ken Masters ADV convertido: 81 sheets, 12 paletas, 33 sons (214 KB), 796 controladores
  (702 diretos, 72 aproximados, 22 sem suporte, todos com motivo no relatorio).
- CPU ativa comandos do .cmd (como a IA do MUGEN); P1 vira CPU apos 5 s ocioso (demonstracao).
- Evidencia BlastEm selada para a ROM da354830...; desempenho ainda acima do orcamento em 16% dos quadros.


## 2026-09-23T01:30:22.2602857Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia
