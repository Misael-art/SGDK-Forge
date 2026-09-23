# V014 Recovery Audit

Data: 2026-06-18

## Resumo

Uma continuacao paralela criou modulos, assets e uma ROM buildada, mas promoveu
o estado acima da evidencia. A ROM `v014` foi auditada no BlastEm e mostrou
corrupcao visual no title e na corrida, seguida de `ADDRESS ERROR` antes do
fechamento do fluxo.

## Licoes

1. Contagem de arquivos nao prova integracao. Cada modulo precisa de um teste
   comportamental e de uma evidencia ligada ao hash atual da ROM.
2. Capturas de ROM anterior nao validam um rebuild. O hash deve ser congelado
   antes da captura e conferido no closeout.
3. Build com warnings de logica impossivel nao pode ser tratado como limpo.
   Os warnings em `race_scene.c:207` antecipavam o defeito da animacao de salto.
4. `VDP_drawImageEx` exige planejamento explicito de tile index e paleta.
   Carregar duas imagens em tile zero destruiu title, font e estrada.
5. Asset gerado por Pillow e geometria simples continua `placeholder`, mesmo
   quando passa ResComp e recebe score automatico alto.
6. Um relatorio de closeout nao substitui `scene_closeout_gate.ps1`; escrever
   `status=implemented` antes da prova cria falso verde.
7. Ferramenta de evidencia nao pode inferir gameplay, performance ou audio
   apenas porque screenshot e SRAM existem. O escopo observado deve ser escrito.
8. Trabalho paralelo precisa de um owner de integracao. Separar runtime e visual
   sem um gate compartilhado permitiu colisao de VRAM, assets mortos e claims
   incompatíveis.
9. Features de fantasia precisam ser verificadas na tela. O perseguidor tinha
   asset e enum, mas era descartado pela camada de entidades e nunca aparecia.
10. A proxima fase nao e Sector 02. E recuperar o Sector 01 ate completar a rota
    sem crash, com visual legivel e contratos basicos funcionando.

## Evidencia

- `doc/code_review_report.json`
- `out/evidence/blastem_audit_v014/screenshot.png`
- `out/evidence/blastem_audit_v014_route2/race_current.png`
- `out/evidence/blastem_audit_v014_route2/result_current.png`
- ROM sha256 `167d4f6937099b542e84f0d64dc6ddf258ba32091c9e874988e01c45a760eafd`

Nenhuma promocao canonica foi aplicada. As licoes permanecem locais ate
reproducao, teste e aprovacao humana.
