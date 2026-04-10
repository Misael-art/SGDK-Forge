---
name: art-asset-diagnostic
description: Diagnostica o estado dos assets visuais de um projeto SGDK. Detecta automaticamente o cenario (data existe, res inadequado, sem arte) e gera relatorio estruturado com issues criticos, avisos e comandos de correcao.
---

# Art Asset Diagnostic

Use esta skill ANTES de qualquer acao de conversao ou criacao de arte. Ela determina o cenario atual do projeto e direciona o agente para o workflow correto.

---

## Cenarios detectados

| Cenario | Condicao | Proxima acao |
|---------|----------|-------------|
| `1_data_needs_conversion` | `/data` existe com PNGs, sem `/res` adequado | Converter assets de /data |
| `2_res_exists_check` | `/res` existe com PNGs referenciados em .res | Diagnosticar qualidade dos assets em /res |
| `3_no_art` | Nenhum asset encontrado em /data ou /res | Decidir rota A (IA) ou B (web) |

---

## Ferramenta principal

```powershell
# Diagnostico completo do projeto
python tools/sgdk_wrapper/art_diagnostic.py --project "<caminho_do_projeto>"

# Com output JSON para relatorio persistente
python tools/sgdk_wrapper/art_diagnostic.py --project "<caminho>" --output doc/art_diagnostic_report.json

# Analisar .res especifico
python tools/sgdk_wrapper/art_diagnostic.py --project "<caminho>" --res-file res/sprite.res
```

Exit codes:
- `0` = todos os assets ok
- `1` = issues criticos ou assets inadequados
- `2` = nenhuma arte encontrada (cenario 3)

---

## O que o diagnostico verifica

### Issues Criticos (bloqueantes para build)

| Codigo | Problema | Impacto |
|--------|----------|---------|
| `NOT_INDEXED` | Imagem nao e PNG modo P (indexado) | ResComp rejeita |
| `DIM_NOT_MULTIPLE_8` | Dimensoes nao sao multiplos de 8 | ResComp rejeita |
| `TOO_MANY_COLORS` | Mais de 15 cores visiveis | Paleta extrapola hardware |
| `OPEN_FAILED` | Arquivo corrompido ou formato invalido | Build falha |
| `FILE_NOT_FOUND` | Arquivo referenciado no .res nao existe | Linker error |

### Avisos (degradam qualidade)

| Codigo | Problema | Impacto |
|--------|----------|---------|
| `COLORS_NOT_9BIT` | Cores fora do grid 9-bits MD | VDP trunca bits — cores imprecisas |
| `NO_MAGENTA_TRANSPARENT` | Index 0 nao e #FF00FF | Transparencia pode falhar |
| `SPRITE_TOO_LARGE` | Sprite > 32x32 px sem metasprite | Requer multiplas entradas OAM |
| `RGBA_NOT_INDEXED` | Canal alpha presente mas nao indexado | Alpha perdido na conversao |

---

## Analise manual complementar (ImageMagick)

```bash
# Verificar modo e dimensoes
magick identify -verbose "<arquivo>.png" | grep -E "Type:|Geometry:|Colors:"

# Contar cores unicas
magick identify -format "%k cores unicas\n" "<arquivo>.png"

# Verificar se e indexado (mode Palette)
magick identify -format "%[type]\n" "<arquivo>.png"
# Esperado: Palette (indexado) ou Grayscale
# Problematico: TrueColor, TrueColorAlpha

# Converter para ver paleta
magick "<arquivo>.png" -unique-colors txt:-
```

---

## Checklist de qualidade por asset

Execute mentalmente para cada asset antes de aceitar:

- [ ] Formato: PNG indexado modo P (4-bit ou 8-bit)
- [ ] Index 0 = transparente (#FF00FF)
- [ ] Max 15 cores visiveis na paleta
- [ ] Todas as cores no grid 9-bits (R, G, B em multiplos de 0x22)
- [ ] Dimensoes multiplas de 8 (largura E altura)
- [ ] Bounding box sem bordas vazias desnecessarias
- [ ] Tiles duplicados/espelhaveis identificados
- [ ] Sem tecnicas proibidas (AA, alpha parcial, baked light, sombra assada)

---

## Saida esperada do diagnostico

Para cada asset reportar:

```json
{
  "path": "res/sprite/player.png",
  "asset_type": "sprite",
  "scenario": "inadequado",
  "mode": "RGBA",
  "width": 28,
  "height": 30,
  "color_count": 24,
  "issues": [
    {
      "code": "NOT_INDEXED",
      "severity": "critico",
      "message": "Modo RGBA — nao e PNG indexado.",
      "suggestion": "Converter para PNG indexado 4-bit."
    },
    {
      "code": "DIM_NOT_MULTIPLE_8",
      "severity": "critico",
      "message": "Dimensoes 28x30 nao sao multiplos de 8.",
      "suggestion": "Redimensionar para 32x32 px."
    }
  ],
  "res_suggestion": "SPRITE player \"sprite/player.png\" 4 4 FAST 5"
}
```

---

## Decisao apos diagnostico

| Resultado | Acao |
|-----------|------|
| Cenario 1 (data existe) | Ir para `art-conversion-pipeline` |
| Cenario 2 (res inadequado) | Apresentar relatorio ao usuario para decisao de rota |
| Cenario 3 (sem arte) | Ir para `art-creation-sourcing` — decidir rota A ou B |
| Issues criticos em /res | Bloquear build, corrigir antes de prosseguir |
| Apenas avisos em /res | Informar usuario, prosseguir com ressalvas documentadas |
