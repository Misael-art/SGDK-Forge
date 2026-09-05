# P3 — tentativa arquivada: geometria preservada, pixelização reprovada

Status: `archived_visual_rejected`
Data: `2026-08-06`

P3 acertou a separação entre a arte-conceito e o pós-processamento técnico: a
silhueta e a intenção de pose partiram de uma fonte HD. Contudo, o recorte de
croma, a redução nearest-neighbor e a quantização automática de 15 cores foram
aplicados sobre uma fonte ainda imperfeita. O resultado 32×32 ficou com ruído,
degraus e transições desajeitadas — uma aparência de arte esmagada por
algoritmo, não pixel art desenhada com intenção.

Este diretório preserva fontes, processados, script e notas apenas para estudo.
Nenhum arquivo dele pode ser promovido a `res/`, usado como sprite final ou
servir de fonte de pixelização para P4.

Lição operacional para P4: antes de qualquer escala ou quantização, aprovar um
master de geometria limpa em cores flat e cel-shading estrito. O primeiro
artefato P4 é somente esse master visual; 32×32, RGB333, PAL2 e indexação ficam
bloqueados até aprovação humana explícita.
