# Changelog Canonico - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

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
