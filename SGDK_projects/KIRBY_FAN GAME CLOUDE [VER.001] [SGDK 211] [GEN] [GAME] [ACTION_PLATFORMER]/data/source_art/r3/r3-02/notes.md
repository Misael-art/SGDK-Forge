# R3-02 — colapso de ruido de paleta da camada 5

- Assinatura: Codex
- Parent: `data/source_art/r2/r2-02/layers.png` (sha256 `93710b6d70231a2e6235c041987b3d09c4742ebf681423c1da20174206c91c85`).
- Escopo: somente os cinco RGBs declarados no pacote R3 foram remapeados. Todos ocorriam em `y>=730`; camadas 1-4 permanecem byte a byte iguais.
- Regra: menor distancia RGB euclidiana ao vizinho que ja existia na paleta R2; desempate lexicografico documentado no relatorio. Nao houve resampling, crop, dither adicional ou cor nova.
- Mapa: `#244949 -> #246d49`; `#494924 -> #496d24`; `#496d6d -> #49496d`; `#926d6d -> #926d49`; `#92926d -> #92b649`.
- Aceite medido: 47 -> 42 cores; luminancia sRGB ponderada da camada 5 = 0.270037; diff de pixel nas camadas 1-4 = 0; 0 pixels fora da grade RGB333 do projeto.
- Limitacao: continua sendo estudo de composicao fonte. Nao entra em `res/` e ainda exige decomposicao semantica e gates VDP/BlastEm normais.
