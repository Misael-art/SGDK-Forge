# 13 - Especificacao Tecnica por Cena — METAL_SLUG_URBAN_SUNSET

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: METAL_SLUG_URBAN_SUNSET

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | 1536 tiles de background como teto seguro de curadoria | 1354 BG + 171 FG semantico = 1525 tiles unicos na analise elite |
| DMA por frame | sem streaming pesado; line scroll pode usar fila DMA de HScroll sem upload de tiles por frame | line scroll em 224 linhas para BG_A e BG_B, sem streaming de tiles no loop |
| Sprites SAT | reservado apenas para estudo de foreground, preferencialmente ate 8 links visiveis na faixa frontal | 0 |
| Paletas | 4 paletas maximas, com meta operacional de 3 ativas e 1 reserva | 2 paletas ativas no runtime atual |
| Efeito dominante | line scroll horizontal por zonas no BG_B | line scroll horizontal buildado; validacao em emulador pendente |

### Observacoes

- O runtime atual continua em 2 planos reais: BG_B para atmosfera e skyline, BG_A para cidade consolidada e WINDOW apenas como overlay textual.
- O build atual ja aplica duas leituras de scroll no BG_B: ceu mais lento e skyline menos lento, sem criar terceiro plano falso.
- O foreground C deve permanecer isolado no pipeline de curadoria ate existir medicao em ROM aprovando sprite strip ou exigindo fusao controlada no BG_A.
- `allow_sprite_grafts` continua falso no spec do caso; qualquer excecao precisa ser deliberada por evidencia, nao por intuicao.
- Se a particao padrao da sprite engine consumir VRAM demais, medir `SPR_initEx(u16 vramSize)` como ajuste operacional e registrar o resultado na memoria.

---

## Cena: PRE-GATE VISUAL

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| Transparencia indice 0 | obrigatoria em todo asset com alpha | implementada na curadoria, precisa ser rechecada na retomada |
| Resolucao alvo | 320x224 ou bbox validada | 320x224 nas camadas de runtime atuais |
| Evidencia BlastEm | screenshot + save.sram + visual_vdp_dump.bin | nao rastreada na arvore revisada nesta sessao |
| Status QA | 7 eixos completos | parcial |
