# P3 / A1 — tradução de frames individuais

Estado: `partial_source_candidate_not_promoted`

## Decisão de fluxo

A imagem HD é arte-fonte. O gradiente do gerador não foi tratado como motivo
para reprovar a geometria; a etapa de pós-processamento fez recorte por chroma,
redução nearest-neighbor, quantização e reserva da chave magenta no índice 0.

## Frames disponíveis

| Frame | Arquivo processado | Papel |
|---|---|---|
| 0 | `frame_00_idle.png` | idle |
| 1 | `frame_01_run_contact.png` | contato da corrida |
| 2 | `frame_02_run_passing.png` | passagem da corrida |
| 3 | `frame_03_run_contact_opposite.png` | contato oposto |
| 6 | `frame_06_float.png` | float com silhueta expandida |

Cada arquivo é PNG indexado de 32×32, 4-bit e tem a chave magenta reservada.

## Não inventado

Os frames 4 (passagem oposta), 5 (salto) e 7 (inalação) ainda não existem como
fonte aprovada nesta rodada. Portanto não existe `ph_kirby.png` de 256×32 nem
promoção para `res/`: montar uma folha com duplicatas ou lacunas seria falsificar
a animação.

## Linhagem

- fontes HD: `data/raw_ai/p3_frame_concepts/A1/`
- quantizador: `data/builders/quantize_p3_frame.py`
- candidatos processados: `data/processed/p3_frame_concepts/A1/`
