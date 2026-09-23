# Curadoria - Showdown Camera e Paleta

Data: 2026-06-13  
Status: `rework_required`  
Contexto: `exercise` / `controlled_training_area`  
Entrega AAA: bloqueada

## Decisao

O estudo prova que o stage aparece no BlastEm, mas nao prova qualidade visual.
O resultado atual nao pode ser tratado como sucesso de composicao, camera,
paleta ou traducao artistica para Mega Drive.

O erro principal nao e somente tecnico. O agente aceitou uma cena visivel como
se fosse uma cena bem composta. Para um palco de luta com camera horizontal e
vertical, isso e insuficiente.

## Evidencias observadas

- Fonte/reconstrucao correta: `work/reconstructed_viewports/frame_0000_mugen_start.png`
- Export bin esperado: `work/diagnostics/exported_bin_viewport_default.png`
- Captura/recorte problematica: `work/diagnostics/blastem_final_view_320.png`
- Evidencia BlastEm: `evidence/blastem_showdown_screenshot.png`
- Definicao MUGEN: `rascunho/inputs/showdown.def`
- Relatorio de export: `work/sgdk_bins/showdown_export_meta.json`
- Relatorio de paleta: `analysis/palette_violations.json`
- Relatorio de memoria do estudo: `doc/10-memory-bank.md`

## Falhas encontradas

### 1. Composicao achatada

O `showdown.def` declara quatro camadas com papeis e deltas distintos:

- BG0: `delta = 0.43,0.285`
- BG1: `delta = 0.71,0.635`
- BG2 animado: `delta = 0.71,0.635`
- BG3 foreground: `delta = 1,1`

O viewer atual converte a cena para um mundo tileado unico em `BG_A`. Isso
remove o modelo de parallax do stage e transforma uma cena de luta em uma
imagem plana percorrida por camera.

Blocker: `flattened_mugen_parallax`

### 2. Camera sem contrato de luta

O stage declara:

- `zoffset = 215`
- `boundleft = -224`
- `boundright = 224`
- `boundhigh = -240`
- `boundlow = 0`
- `verticalfollow = .5`

O runtime usa `CAMERA_DEFAULT_X=224` e `CAMERA_DEFAULT_Y=256`, com D-pad e
autopan livre. Isso serve como explorador de laboratorio, mas nao como camera
de palco de luta. A camera deveria preservar chao, zoffset, foco dos
personagens e leitura do espaco jogavel.

Blocker: `fighting_stage_camera_contract_missing`

### 3. Paleta tecnicamente encaixada, mas visualmente degradada

O export atual usa:

- `banded_palette_v1_world`
- quatro sub-paletas por banda vertical
- `187569` remapeamentos por cor mais proxima
- `pass_with_degradation`

Isso remove vitalidade cromatica. A fonte tem agua azul intensa, rochas
quentes e vegetacao com verdes vivos. A captura em BlastEm fica mais cinza,
oliva e opaca, com planos menos separados.

Medicao comparativa:

- viewport fonte: 76 cores uteis, saturacao media 0.3805
- viewport exportado: 26 cores uteis, saturacao media 0.4097
- diferenca source/export: distancia RGB media 30.58; 21.65% dos pixels acima
  de distancia 40
- diferenca source/blastem_final_320: distancia RGB media 152.4; 96.84% dos
  pixels acima de distancia 40

Blocker: `palette_vibrancy_lost`

### 4. Gate visual estreito demais

O gate atual aprova ausencia de matte/magenta e conflitos por tile. Isso e
necessario, mas nao mede:

- vitalidade cromatica;
- separacao entre planos;
- fidelidade perceptiva contra o viewport original;
- coerencia da camera com `zoffset` e `verticalfollow`;
- preservacao do modelo multi-delta do stage.

Blocker: `visual_gate_too_narrow`

### 5. Diagnostico de arte nao enxerga estudo aninhado

`art_diagnostic.py` retorna `3_no_art` no root do estudo, apesar de existirem
reconstrucoes, bins, evidencias e viewer SGDK. O diagnostico esta correto para
projetos SGDK convencionais, mas insuficiente para laboratorios com arte em
`work/`, `analysis/`, `evidence/` e viewer aninhado.

Blocker: `nested_lab_art_not_detected`

## Oportunidades de correcao

1. Criar `camera_motion_contract` antes do runtime.
   - Deve mapear `zoffset`, `boundleft/right/high/low`, `verticalfollow`,
     camera inicial, chao visivel, foco dos lutadores e limites de scroll.

2. Criar `parallax_layer_contract`.
   - BG_B: predios/ceu/atmosfera distante.
   - BG_A: agua, ponte e estrutura principal.
   - Foreground: pedras/chao com prioridade ou sprite graft quando necessario.
   - BG2 animado deve ter politica propria de update, nao full-window reload
     que cause tearing.

3. Substituir `banded_palette_v1_world` por paleta curada por plano/material.
   - Uma paleta para ceu/predios frios.
   - Uma paleta para vegetacao viva.
   - Uma paleta para agua/reflexo.
   - Uma paleta para rochas/chao/personagens conforme prioridade.

4. Adicionar `palette_vitality_check`.
   - Comparar source viewport, export bin e BlastEm.
   - Bloquear quando nearest-color remap for massivo ou quando a cena perder
     contraste de material mesmo sem violacao tecnica.

5. Exigir `compare_flat` honesto se o agente escolher achatar.
   - Se a rota multi-plano nao couber, o resultado deve ser declarado
     `lab_flattened_reference`, nao `elite_ready`.

## Proxima ordem segura para rework

1. Reabrir `showdown.def` como contrato de camera e camadas.
2. Gerar `camera_motion_contract_v001.json`.
3. Gerar `parallax_layer_contract_v001.json`.
4. Gerar `palette_vitality_report_v001.json`.
5. Produzir duas rotas de comparacao:
   - `route_a_multi_plane`
   - `route_b_compare_flat_degraded`
6. Validar lado a lado:
   - source viewport;
   - export preview;
   - BlastEm screenshot;
   - dump VDP quando houver promocao.

## Conclusao

O estudo e valido como laboratorio porque revelou uma falha real do agente:
ele confundiu "aparece no emulador" com "preserva a cena". A licao canonica e
que palco de luta importado de MUGEN precisa de contrato de camera, contrato de
camadas e gate de vitalidade de paleta antes de qualquer claim visual.
