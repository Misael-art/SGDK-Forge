# FORGE_REFERENCE — Brief

## Objetivo

Ser a fixture técnica neutra do SGDK Forge para provar contratos de gates,
telemetria compatível, playtest observado pela ROM e identidade de evidência.

## Escopo

- uma cena geométrica e textual sem personagem, marca ou universo licenciados;
- movimento e salto determinísticos solicitados por tabela ROM-side;
- bloco SRAM `FREF` versionado;
- regressões host para sete regras de prevenção de falso verde;
- build SGDK 2.11 e prova BlastEm quando o host permitir.

## Fora de escopo

- jogo completo, arte final, narrativa, campanha, boss ou release;
- claim AAA, qualidade criativa ou performance sustentada por inferência;
- promoção automática de aprendizado sem aprovação humana.

## Sucesso proporcional

A fixture é bem-sucedida quando seus contratos passam, a ROM compila, o bloco
`FREF` confirma os estados observados e toda prova operacional aponta para o
mesmo SHA-256. Até haver captura BlastEm rastreável, o status máximo é
`buildado`; depois, apenas `testado_em_emulador` para os escopos efetivamente
observados.
