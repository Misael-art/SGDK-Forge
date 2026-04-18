# 09 - Multi-Plane Composition Standards — Mega Drive AAA (v1 DRAFT)

Status: `DRAFT_APROVADO` — Incorporado operacionalmente na skill `multi-plane-composition`; prova runtime continua pendente

---

## Objetivo

Definir regras rigidas para composicao multi-plano no Mega Drive, protegendo profundidade, papel funcional de cada plano e honestidade de budget quando a cena sair do laboratorio e entrar em ROM.

---

## 1. Hierarquia canonica de planos

| Plano | Papel | Regra |
|------|------|-------|
| `BG_B` | atmosfera, massa distante, respiracao do cenario | deve competir menos que o plano jogavel |
| `BG_A` | estrutura principal, arquitetura, solo legivel | deve sustentar a cena sem repetir o fundo inteiro |
| `midground_layer` | massa estrutural intermediaria fora do papel puro de BG_A/BG_B | usar quando a source desmontada nao cabe na taxonomia simples |
| `foreground_layer` | destrocos, ornamentacao de frente, massa frontal composicional | nunca classificar como actor sprite por default |
| `sprite_graft` | profundidade adicional via sprite | so com budget declarado |

### Regras absolutas

- so existem `BG_A`, `BG_B` e `WINDOW` como planos fixos de VDP; qualquer sensacao de terceiro plano deve ser resolvida por composicao, sprite graft ou compare flat
- `BG_B` nunca deve exigir mais atencao do olho que `BG_A`
- foreground real deve abraçar o gameplay ou o enquadramento; decoracao solta sem funcao deve ser cortada

---

## 2. Composicao correta

### Pipeline obrigatorio

1. interpretar semanticamente a source
2. definir papel de profundidade
3. extrair layers com base espacial comum
4. recompor por alpha compositing
5. so entao quantizar

### Regras de montagem

- `A` estabelece a base atmosferica
- `B` entra sobre `A` por matte/alpha controlado
- `C` entra por cima preservando massa, sombra e pertencimento espacial
- layers transparentes de review podem parecer vazias fora da area util; isso precisa ser declarado no laudo

### Proibicoes

- somar PNGs por sobreposicao cega
- quantizar antes da recomposicao semantica
- recortar cada plano em tamanhos espaciais incompatíveis

---

## 3. Budget e promocao para ROM

### Regra de honestidade

Uma curadoria multi-plano pode vencer offline e ainda assim falhar como prova direta de ROM.

Nesses casos, o agente deve escolher explicitamente entre:

- manter multi-plano real
- usar `compare_flat`
- usar `sprite_graft`
- fundir parte do foreground no plano principal

### Sinais de alerta

- `BG_A + BG_B` excedem o teto pratico de tiles unicos
- foreground pede paleta propria e implode o budget
- a cena fica melhor offline, mas perde viabilidade de runtime

### Resposta obrigatoria

- emitir `hardware_budget_review`
- registrar a tecnica escolhida
- nao vender prova offline como prova de ROM

---

## 4. Metricas obrigatorias

| Metrica | Threshold | Metodo |
|--------|-----------|--------|
| `depth_separation` | BG_A e BG_B possuem papeis visuais distintos | inspeção visual e alternancia isolada dos planos |
| `plane_role_clarity` | foreground/midground nao sao julgados como sprite errado | laudo semantico e painel humano |
| `scene_readability` | a cena continua compreensivel em 320x224 | screenshot nativo |
| `budget_fit` | a estrategia declarada cabe no VDP escolhido | auditoria de tiles, paletas e runtime |
| `rom_strategy_declared` | existe escolha honesta para promocao | manifesto do caso |

---

## 5. Checklist de validacao

- [ ] BG_B tem menos densidade e menos competicao visual que BG_A?
- [ ] BG_A sustenta solo, arquitetura ou estrutura jogavel?
- [ ] foreground foi classificado como composicional e nao como sprite por default?
- [ ] todas as layers compartilham `shared_canvas`?
- [ ] a recomposicao foi feita por alpha compositing?
- [ ] a promocao para ROM tem estrategia declarada?
- [ ] existe `hardware_budget_review`?
- [ ] a cena foi julgada em 320x224, nao apenas em painel ampliado?

---

## 6. Anti-padroes

| Anti-padrao | Diagnostico | Consequencia |
|------------|-------------|--------------|
| BG_A e BG_B quase iguais | profundidade falsa | reprovar e redistribuir papeis |
| foreground tratado como sprite compacto | massa frontal podada | reprovar classificacao |
| paired_bg usado como premio automatico | score inflado | rebaixar o laudo |
| imagem inteira convertida como um unico fundo | explosao de tiles | exigir modularizacao ou compare flat |
| promocao direta de curadoria offline para ROM sem budget | risco de fraude tecnica | bloquear promocao |

---

## 7. Integracao com skills

| Skill | Relacao |
|------|---------|
| `art-translation-to-vdp` | parsing semantico e traducao base |
| `visual-excellence-standards` | julgamento estetico de profundidade |
| `megadrive-vdp-budget-analyst` | budget real antes de runtime |
| `megadrive-elite` | implementacao de scroll, IMAGE/MAP, sprite graft e prova em ROM |
