# Changelog — FORGE_REFERENCE

## 2026-08-05 — criação e promoção cirúrgica

- criado projeto neutro via bootstrap canônico;
- classificado como `technical_demo`, sem claim AAA;
- implementado bloco SRAM versionado `FREF`;
- implementado playtest determinístico com estados marcados pela ROM;
- implementada prova de elisão de trabalho byte-idêntico;
- adicionadas regressões canônicas para os sete contratos;
- reforçado loop de aprendizado: E4 exige bundle selado e gate aprovado com o
  mesmo SHA-256 da ROM;
- validação host inicial: 10/10 e 36/36; build/BlastEm ainda não registrados
  neste ponto do changelog.

## 2026-08-06 — prova em ROM

- removidos os diretórios herdados `res/branding` e `res/audio/branding`; são
  reproduzíveis pelo template, mas não pertencem à fixture neutra;
- rebuild Linux/Wine concluído sem warnings e sem recursos externos;
- primeira captura executável rejeitada por densidade visual baixa e VLAB
  ausente; o gate permaneceu inalterado;
- cena enriquecida com grid geométrico neutro e exportador `VLAB` real
  (24 métricas + 64 palavras de CRAM);
- bundle BlastEm `blastem-linux-20260806T023359Z-197827` selado sem blocker;
- gate `FREF` final: 7 contratos, status `passed`, 229 amostras, 0 violações,
  cobertura observada `0x0007`, frame 270;
- ROM e todos os relatórios: SHA-256
  `1167b7597491cf02f264c5031771925149eaba86c48d3d0747c8f18114b82dc3`;
- `ready_for_aaa=false`: a fixture prova contratos técnicos, não produto AAA.
- revisão formal detectou colisão de SRAM entre o runtime probe (`0x0000`) e o
  bloco `VLAB`; o probe foi movido para `0x0200` antes do fechamento;
- a evidência anterior foi invalidada após essa mudança de ROM e substituída
  pela sessão `blastem-linux-20260806T024237Z-253942`;
- ROM e gate finais recapturados: SHA-256
  `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`,
  bundle selado, sete contratos aprovados e nenhum blocker.
