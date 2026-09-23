# Changelog Canonico - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

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
