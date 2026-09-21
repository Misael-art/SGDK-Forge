# Passe de arte — `img_presents_text_v2`

Asset: `res/branding/presents_text_96x16.png`, PAL2, plano WINDOW, entra em F480.

O runtime esta correto. `VDP_setWindowVPos(TRUE, 22)` foi corrigido, o wordmark aparece na
faixa de baixo e a prioridade ja esta alta. **O que falta e contraste, e nao codigo.**

---

## O que foi medido

No asset:

| | |
|---|---|
| cobertura de tinta | 23% do canvas (351 de 1536 px) |
| indices usados | 3, 4 e 8 |
| **indice 3 (luma 38)** | **347 px — 99% de toda a tinta** |
| indice 4 (luma 72) | 2 px |
| indice 8 (luma 101) | 2 px |
| caixa util do texto | 70x12 px num canvas 96x16 |

Na tela, faixa onde o PRESENTS vive:

| | |
|---|---|
| luma media do fundo | **46** |
| pixels do fundo acima de luma 60 | 21% |
| **contraste corpo/fundo** | **−8** |

**O texto e mais escuro que o proprio fundo.** Nao e "tenue": ele esta abaixo da linha de
leitura. E nao existe rampa — 99% da tinta e uma cor so.

---

## Parte da culpa e da direcao, nao sua

`branding_v2_art_direction.md` e o brief de producao descreviam o PRESENTS assim:

> *"O oposto dos outros: leve, pequeno, sem chanfro, apenas corpo e contorno. Nao compete com o
> wordmark do projeto — entra, respira, para."*

Voce cumpriu ao pe da letra. **"Leve" sem piso de contraste virou "invisivel"** — e isso e
defeito da direcao, que pediu discricao sem dizer onde fica o chao.

A direcao esta corrigida: discricao e sobre **tamanho e peso tipografico**, nunca sobre luma.
Um elemento discreto continua tendo que ser lido.

---

## O alvo

Mantenha tudo que esta certo:

- **tamanho**: 70x12 px de glifo em 96x16 esta bom, nao aumente;
- **sem chanfro**: continua correto, o PRESENTS nao e metal forjado como os outros;
- **nao competir** com o wordmark do projeto: continua sendo a regra.

Corrija o contraste:

- **piso de luma do corpo: >= 100.** Contra um fundo de luma media 46, isso da +54 de
  separacao. Hoje sao −8;
- **rampa de 3 passos minimos**, nao uma cor so:
  - contorno/sombra em `PAL2[1..2]` — separa o glifo do fundo mesmo onde o fundo clareia;
  - corpo em `PAL2[8..9]` — e a faixa de luz de chanfro do mapa de papel de PAL2, e e onde o
    corpo precisa viver para ler;
  - um toque de acento em `PAL2[12]` na aresta inferior, 1px, coerente com a luz de baixo.
- o fundo tem 21% de pixels acima de luma 60: o contorno escuro e o que garante leitura nessas
  regioes claras. Sem ele, o corpo claro some onde o fundo clareia.

O papel de indice de PAL2 esta em `branding_v2_art_direction.md` secao 5 e nao muda.

---

## Como saber que passou, antes de entregar

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root "<este projeto>" --shared-builder-root tools/image-tools
python3 tools/sgdk_wrapper/art_diagnostic.py
python3 tools/sgdk_wrapper/art_quality_gate.py
python3 tools/sgdk_wrapper/audit_tile_residency.py --project-root "<este projeto>"
```

O asset tem 19 tiles unicos hoje e a residencia do ato 3 esta em 865 de 1740 — ha folga de
sobra, entao nao economize cor por medo de VRAM.

Verificacao propria do contraste, antes de me chamar: a luma media dos pixels de tinta precisa
ficar acima de 100, e nenhum indice deve concentrar mais de ~70% da tinta.

---

## O que nao mudar

Proveniencia, pipeline e paleta seguem como estao: median 3x3 e snap 9-bit antes do remap,
fonte limpa em `raw_png/`, sha256 no lineage, `acceptance_status: placeholder` ate a revisao
humana. Nenhum pixel nasce de primitiva.

E continua valendo: se voce achar que o resultado nao atingiu o nivel, diga. A autocritica das
suas entregas anteriores foi util e correta.
