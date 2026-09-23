# R1 — VEREDITO MEDIDO + PACOTE R2

> **Julgado em:** 2026-07-29
> **Entregas:** 7 pedidos, 11 PNGs normalizados + 11 originais de gerador
> **Metodo:** medicao programatica, nao inspecao visual. Todo numero abaixo saiu
> de script sobre o PNG entregue.

---

## 0. Primeiro: o que o Codex fez certo, e que nao era obvio

Registro isso porque define o padrao das proximas rodadas.

1. **Separou origem de derivacao.** `concept_generated.png` guarda a saida crua do
   gerador (104k a 463k cores, 99-100% dos pixels fora da grade do VDP) e
   `concept.png` e a normalizacao. Auditabilidade preservada sem contaminar o
   entregavel. Eu nao pedi isso explicitamente. Foi decisao correta.
2. **Quantizacao real, nao alegada.** Medido: **0.00% de pixels ilegais em todos
   os 11 entregaveis.** Zero. Nao houve "quase legal".
3. **Autocritica que acertou o defeito antes de mim.** A nota do R1-01 diz que as
   poses de bochecha inflada e boca aberta "comprimem detalhes faciais demais".
   Meu teste de 28 px encontrou exatamente isso. A nota do R1-06 admite que o
   comparativo nao usa geometria modular identica. Isso e o oposto de inventar
   conformidade e vale mais que arte bonita.

---

## 1. Tabela de veredito

| ID | Cores | Ilegais | Veredito |
|---|---|---|---|
| R1-01 personagem | 10 / 15 | 0.00% | **APROVADO COM CORRECAO** |
| R1-02 camadas | 41 / 45 | 0.00% | **APROVADO COM CORRECAO** |
| R1-03 Whispy | 15 / 15 | 0.00% | **REPROVADO** — chave de transparencia |
| R1-04 chapeus | 15 / 15 | 0.00% | **APROVADO COM CORRECAO** |
| R1-05 terreno | 15 / 15 | 0.00% | **APROVADO** |
| R1-06 lago | 41/39/37 / 45 | 0.00% | **APROVADO COM RESSALVA** |
| R1-07 titulo | 30 / 45 | 0.00% | **APROVADO** |

Gate de legalidade de cor: **7/7 passa.** Gate de teto de cores: **7/7 passa.**

---

## 2. R1-03 — REPROVADO. Causa unica, mecanica, nao artistica

**O conteudo esta certo.** Os 7 segmentos existem, numerados; as tres curvaturas
(reto, curl up, whip down) foram entregues com numeracao de segmento; tronco,
rosto desmontado, maca e rajada estao separados. Isso era o pedido difícil e foi
cumprido.

**O defeito e a chave de transparencia.** Medido:

```
(255,   0, 219)   56.38%   <- fundo dominante
(255,   0, 255)    4.61%   <- a chave que eu especifiquei
(219,   0, 219)    2.02%   <- terceira magenta
```

O fundo virou `255,0,219`, nao `255,0,255`. As tres magentas coexistem. Qualquer
passo de keying vai fazer uma de tres coisas erradas: deixar 56% do fundo opaco,
recortar buracos no meio do sprite, ou deixar franja roxa na borda.

**Correcao R2-03:** refazer **apenas o keying**, nao a arte. Forcar todo pixel de
fundo para exatamente `255,0,255` e garantir que nenhuma cor da arte caia em
`{(255,0,219), (219,0,219), (255,0,255)}`. Se a arte precisar de roxo, use
`(182,73,182)` ou `(146,36,146)`.

**Segundo item, menor:** 15 de 15 cores nao deixa folga. O boss vai precisar de
ao menos 1 indice livre para o flash de dano (ARCHITECTURE.md §7 exige flash por
troca de paleta, nao sprite branco). Entregue R2-03 com **13 cores**, liberando 2.

---

## 3. R1-02 — o defeito de valor, medido

**O que passou:**

- 5 camadas detectadas automaticamente, todas separaveis ✓
- Ceu: **11 faixas contiguas, 10 cores distintas** — pedi 10-14 ✓
- Perspectiva atmosferica **correta e medida**: camada 2 (montanhas) tem
  saturacao media 0.269 contra 0.339 da camada 3 (colinas). A camada distante e
  mesmo mais dessaturada. Isso e exatamente o pedido ✓

**O defeito.** Luminancia media medida por camada:

```
camada 1  ceu         0.726
camada 2  montanhas   0.512     gap -0.214  OK
camada 3  colinas     0.420     gap -0.092  OK
camada 4  terreno     0.340     gap -0.080  OK
camada 5  primeiro    0.370     gap +0.030  <-- FALHA
```

**A camada 5 e MAIS CLARA que a camada 4, por 0.030.** Em escala de cinza elas
colapsam. E a camada 5 e a unica que passa **na frente do Kirby** — ela precisa
ler como a mais proxima da camera, nao empatar com o chao.

**Correcao R2-02:** escurecer a camada 5 para luminancia media alvo **0.24-0.27**,
ou seja **dois degraus abaixo da camada 4**, e aumentar a saturacao dela. Grama de
primeiro plano em sombra, verde profundo. Nao mexa nas camadas 1-4: elas estao
aprovadas e medidas.

---

## 4. R1-01 — 3 de 4 poses passam a 28 px

Teste real: recorte, downscale nearest para 28 px de altura, contagem de cores.

| Pose | Tamanho a 28px | Cores | Leitura |
|---|---|---|---|
| neutral | 33x28 | 9 | ✓ olhos, blush e pes claros |
| running | 48x28 | 9 | ✓ silhueta e linhas de movimento claras |
| **floating** | 36x28 | 9 | **✗ colapsa** — bochechas infladas viram borrao, olhos se perdem |
| inhaling | 42x28 | 9 | ✓ boca aberta le muito bem |

Silhuetas em preto solido: entregues e funcionais ✓. Chave magenta limpa,
uma unica cor ✓.

**Correcao R2-01a — pose floating.** A bochecha inflada precisa **estourar para
fora do circulo do corpo**, criando duas protuberancias na silhueta, e ganhar
contorno proprio em `(109,36,73)`. Hoje a bochecha esta dentro da massa do corpo
e por isso desaparece. Teste de aceite: a silhueta preta da pose floating tem de
ser distinguivel da silhueta de neutral **so pelo contorno**.

**Correcao R2-01b — o meio-tom esta ausente.** Distribuicao medida dos rosas:

```
(255,182,182)  13.77%   <- claro, carrega quase tudo
(219,109,146)   1.64%   <- sombra
(255,146,146)   0.58%   <- MEIO-TOM, praticamente inexistente
```

A forma esferica esta sendo resolvida com dois tons, nao tres. Por isso o corpo
le mais chapado do que macio. Suba o meio-tom para **8-12% da area do corpo**.

---

## 5. Correcao do MEU proprio brief — o rosa estava errado

Regra dura 4 do projeto: medicao contradiz o brief, segue a medicao e documenta.
Aqui o brief era meu e estava errado.

Especifiquei `255,182,182 / 255,146,146 / 219,109,146`. Medido no resultado: isso
e uma rampa **salmao**, puxada para o laranja. O Kirby das referencias e um rosa
**chiclete, puxado para o magenta**. O Codex seguiu minha especificacao
corretamente; a especificacao e que nao servia.

**Rampa corrigida, toda dentro da grade RGB333, para R2 e para todo o projeto:**

```
highlight   (255, 219, 255)
claro       (255, 182, 219)
base        (255, 146, 182)
sombra      (219,  73, 146)
profundo    (146,  36, 109)
contorno    (109,  36,  73)   (mantido)
```

Cinco tons na rampa do corpo em vez de tres. Cabe: R1-01 usou 10 de 15 cores.

Registrado tambem em `doc/agent_learning/failure_patterns.md` — errar a paleta do
protagonista no contrato e um erro barato de corrigir agora e caro depois de
existirem 200 tiles.

---

## 6. R1-04 — franja de quantizacao

Chave dominante correta `(255,0,255)` 74.51% ✓. Mas existe halo:

```
(219,  0, 219)   1.58%
(219, 36, 182)   0.60%
```

Sao pixels de transicao entre o sprite e o fundo. Ao aplicar o key, viram borda
roxa. **Correcao R2-04:** eliminar qualquer pixel intermediario — a fronteira
sprite/fundo tem de ser um degrau duro, sem cor de transicao. Conteudo dos 5
chapeus, o corpo de pedra do STONE e os 3 quadros de FX estao aprovados.

---

## 7. R1-05 e R1-07 — aprovados sem correcao

**R1-05:** 15 cores, 0% ilegal, grade de 8 px visivel, provas de ladrilhamento
3x3 presentes, cachoeira com 3 quadros, encostas, quinas, destrutivel e fundo de
caverna entregues. Solido e distinguivel de decoracao. Passa.

**R1-07:** 30 cores, **17 cores distintas no ceu** — pedi 16-20 ✓. Silhueta de
primeiro plano em poucas cores, espaco real reservado no terco superior para o
logo, zero texto na imagem, campo de estrelas em tamanhos discretos. Tem calma.
Passa.

Ressalva tecnica anotada, nao um defeito: na coluna que amostrei o R1-07 tem 57
transicoes contiguas porque estrelas e nuvens cortam a coluna. As 17 cores
distintas sao o que importa para a tabela de faixas do H-int, e estao no alvo.

---

## 8. R1-06 — aprovado com ressalva, e a ressalva e boa

Tres arquivos entregues, todos legais. A regra de derivacao que eles propuseram:

> para cada cor de superficie nao branca, mover G e B um degrau para cima, mover
> R um degrau para baixo, reduzir o valor maximo um degrau; branco permanece
> branco

E uma regra enunciavel, que era o pedido. E eles proprios escreveram que **o
proximo passo precisa materializar uma tabela, nao aplicar operacao cega** — o
que esta certo, porque operacao cega vai achatar materiais diferentes na mesma
cor.

**Nao e correcao de arte. E entrada para o `PALETTES.md`**, que ainda nao existe.
A tabela de 16 -> 16 vai nascer la, e o R1-06 vira a referencia visual dela.

Eles tambem admitiram que o comparativo acima/abaixo nao usa geometria modular
identica. Anotado; nao bloqueia, porque o valor do pedido era o plano de cor.

---

## 9. PACOTE R2 — o que pedir agora

Quatro itens. **Nada de arte nova.** Tudo correcao cirurgica sobre o aprovado.

| ID | Pedido | Criterio de aceite medivel |
|---|---|---|
| **R2-03** | Re-key do R1-03 | fundo 100% em `(255,0,255)`; zero pixel em `(255,0,219)` e `(219,0,219)`; total de cores <= 13 |
| **R2-02** | Escurecer camada 5 do R1-02 | luminancia media da camada 5 entre **0.24 e 0.27**; camadas 1-4 inalteradas (diff de pixel zero fora da camada 5) |
| **R2-01** | Pose floating + meio-tom + rampa nova | silhueta de floating distinguivel de neutral; meio-tom em 8-12% da area do corpo; rampa da secao 5 aplicada; <= 15 cores |
| **R2-04** | Limpar franja do R1-04 | zero pixel em `(219,0,219)` e `(219,36,182)`; fronteira em degrau duro |

Prioridade: **R2-03 e R2-02 primeiro** — sao os dois que bloqueiam trabalho
posterior. R2-01 e R2-04 sao polimento.

Regra que continua valendo: nada disso vai para `res/`. Status maximo segue
`source_candidate`. A promocao exige `PALETTES.md`, traducao para grade nativa e
gate visual no BlastEm.

---

## 10. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | R1 julgada por medicao. 6 aprovados (4 com correcao), 1 reprovado por chave de transparencia. Rampa de rosa do protagonista corrigida no contrato — erro era meu. R2 emitida com 4 correcoes cirurgicas. |
