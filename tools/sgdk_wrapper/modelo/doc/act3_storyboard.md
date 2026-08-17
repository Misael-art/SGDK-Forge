# Storyboard do ato 3 — planta baixa

Aplicacao retroativa de `tools/sgdk_wrapper/.agent/workflows/scene-direction-first.md` sobre o
ato 3, que foi produzido sem passar pelos passos 1 e 2.

O workflow manda, para arte ja produzida: rodar os passos 3, 4 e 5 sobre o que existe e ver o
que eles invalidam. **Invalidaram a composicao inteira.**

---

## O que a planta baixa revelou

Coordenadas lidas do codigo, convertidas de tile para pixel:

| Elemento | Plano | Tile | Pixel x | Pixel y |
|---|---|---|---|---|
| `img_logo_author_v2` (MISAEL) | BG_A | (8,12) | 64-256 | **96-128** |
| `img_logo_project_v2` (MASTER) | BG_A | (6,10) | 48-272 | **80-128** |
| `img_presents_text_v2` | WINDOW | (14,23) | 112-208 | 184-200 |

**O projeto contem o autor por inteiro.** Mesma faixa vertical, e o MASTER e mais largo e mais
alto que o MISAEL em todas as direcoes.

E ha **56 px de vao morto** entre o fim do projeto (y=128) e o inicio do presents (y=184).

## O que a captura revelou, e e pior

Busca por remocao de elemento no ato 3: **nenhuma**. Cada elemento e desenhado **por cima** do
anterior e nada sai de cena.

Vivos simultaneamente em F451:

```
BG_B     forja, com a cortina levantando colunas
BG_A     bigorna (ato 1) + FORGE (ato 2) + MISAEL (F300) + MASTER (F430)
WINDOW   PRESENTS (F480)
```

Quatro coisas empilhadas na faixa `y=80..128`. Na captura da para ler o **FORGE azul por tras
do MASTER**, os dois ocupando o mesmo espaco.

## A causa e uma regra minha, mal escrita

O contrato dizia:

> *"Zero cortes a preto. A transicao entre atos e feita por luz, scroll e paleta, nunca por
> `VDP_clearPlane`."*

Escrevi a proibicao e **nao escrevi a alternativa**. "Nunca limpe o plano" foi implementado
como "nunca remova nada", e o resultado e acumulo.

Continuidade nao e ausencia de remocao. **Continuidade e ter uma saida desenhada para cada
elemento.** O storyboard e onde essa saida se declara — e ele nao existia.

---

## A planta baixa corrigida

Tela de 320x224, quatro zonas com papel fixo:

```
y   0..56    COIFA        topo da forja; e o que a cortina levanta
y  56..144   PALCO        a faixa dos wordmarks; UM por vez, nunca dois
y 144..200   FORJA        bigorna e piso de brasa; permanece a cena toda
y 200..224   ASSINATURA   plano WINDOW; so o PRESENTS vive aqui
```

O PALCO e a regra que faltava: **um elemento por vez**. Quem entra, entra porque o anterior
saiu.

### Sucessao, com entrada e saida declaradas

| Quadros | Elemento | Entra por | Sai por |
|---|---|---|---|
| ate F300 | **FORGE** (ato 2) | pouso dos estilhacos | **scroll vertical para cima**, sob a cortina, F300-330 |
| F300-360 | cortina de coluna | — | levanta a COIFA e revela o PALCO vazio |
| F330-430 | **MISAEL** | scroll de baixo para o PALCO, F330-360 | **scroll para cima**, F420-440 |
| F430-500 | **MASTER** | scroll de baixo, F430-460 | fade de paleta na entrega |
| F480-520 | **PRESENTS** | fade de paleta no WINDOW | fade de paleta na entrega |

O FORGE sair para cima **por baixo da cortina** e o que liga o ato 2 ao 3 sem corte: a cortina
sobe, o logo sobe junto e desaparece atras da coifa. Continuidade por movimento, nao por
sobreposicao.

### O vao morto

Os 56 px entre o fim do PALCO e o inicio da ASSINATURA nao sao desperdicio se a **FORJA** os
ocupa. A bigorna e o piso de brasa vivem exatamente ali. O erro nao era o vao: era o PALCO
estar alto demais (y=80) e deixar a bigorna sem relacao com os wordmarks.

Com o PALCO em `y=56..144`, os wordmarks pousam **sobre** a forja e nao flutuando acima dela.

### Tipografia e sucessao de nomes

| Elemento | Papel | Peso |
|---|---|---|
| FORGE | a engine, forjada no ato 2 | maximo: metal, chanfro, rampa completa em PAL1 |
| MISAEL | o autor, humano | medio: mesma gramatica, PAL2, sem competir com FORGE |
| MASTER | o projeto | alto, mas depois do autor — e o ultimo nome forte |
| PRESENTS | conectivo | minimo em tamanho, **nunca em contraste** (piso de luma 100) |

A ordem importa: engine, autor, projeto, conectivo. Cada um cede o palco ao seguinte.

---

## Medicao do ato 3 como ele esta hoje (passo 4)

| | |
|---|---|
| sprites | 0 — o ato 3 nao usa o SAT |
| residencia de tiles | 865 de 1740, 50% de margem |
| DMA por quadro | tabela de scroll por coluna, F300-360 |
| `over_budget_frames` | 0 |
| `max_cpu_load` | 96 — o pico da cena inteira |

**Nao ha problema de orcamento no ato 3.** Ha folga de sobra: 50% de VRAM e zero sprites. Os
defeitos sao 100% de composicao, e por isso nenhum gate os pegou — todos medem hardware.

Isso e um achado sobre os gates: **eles nao veem composicao.** Empilhar quatro wordmarks na
mesma faixa passa em residencia, em scanline, em provenance e no gate de compreensao de marca.

---

## O que isto invalida

1. **A regra de continuidade do contrato** precisa dizer que cada elemento tem saida declarada,
   nao apenas que `VDP_clearPlane` e proibido.
2. **As posicoes de desenho no runtime** — as tres coordenadas mudam com o PALCO em `y=56..144`.
3. **O beat "o do autor sai por scroll vertical"** existia na concepcao de cena e **nunca foi
   implementado**. Isso ja era divergencia entre contrato e ROM antes desta analise.
4. **`img_logo_project_v2` a 224x48** contra `img_logo_author_v2` a 192x32: se os dois ocupam o
   mesmo palco em momentos diferentes, a diferenca de massa e escolha de direcao e nao acidente.
   Hoje ela e acidente.

Nenhum asset precisa ser redesenhado. **A correcao e de runtime e de contrato**, exceto o
PRESENTS, que ja tem passe de arte aberto por contraste.
