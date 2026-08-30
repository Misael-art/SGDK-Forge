# Handoff — bissecte o ato 3 antes de corrigir

Cena: `branding_sequence_v2`, `src/scenes/scene_branding_v2.c`.
Atos 1 e 2 renderizam. **O ato 3 (F300-520) nao entrega.**

---

## Por que este documento comeca mandando bissectar

Nesta mesma cena eu gastei **dois builds inteiros** chutando a causa de um crash. Atribui a
esgotamento de pool de sprites, reescrevi a gestao de VRAM, o crash continuou identico. Depois
troquei `PAL_setColor` por escrita direta no CRAM, o crash voltou.

Quem bissectou desligando uma linha achou em minutos: o handler de H-Int era `void`, o GCC
emitia `RTS` em vez de `RTE`, e o SR empilhado virava a word alta do endereco de retorno —
`0x23080000`, exatamente o endereco que o log mostrava desde o inicio.

**O endereco estava dizendo a resposta e eu preferi teorizar.** Nao repita isso.

---

## Sintomas, medidos

Captura em `out/evidence/re4/`, quadro F331, dentro do ato 3:

1. **as bordas voltaram a magenta** — o backdrop era preto nos atos 1 e 2;
2. **nenhum wordmark aparece** — nem autor (F300-430) nem projeto (F430+);
3. **a bigorna sumiu** e nada entrou no lugar dela.

A tela e a parede da forja com o piso de brasa, e mais nada.

O que **funciona** e nao pode regredir: ato 1 (queda da brasa, luz, antecipacao) e ato 2
(impacto, enxame de 56 estilhacos, logo, varredura). `over_budget_frames: 0`,
`max_cpu_load` ate 96, bundle `sealed`.

---

## Metodo: bissecte por desligamento, um por vez

`brandUpdateSignature` tem quatro blocos independentes. Desligue **um** por build e capture:

```c
1. cortina por coluna        if (t <= 60) { ... VDP_setVerticalScrollTile ... }
2. wordmark do projeto       if (f == 430) { VDP_drawImageEx(BG_A, ...) }
3. presents no WINDOW        if (f == BRAND_V2_PRESENTS_IN) { ... }
4. fade de entrega           if (f >= BRAND_V2_END - 10) { PAL_fadeOutAll(...) }
```

E em `brandEnterSignature`, dois candidatos separaveis:

```c
5. SPR_reset()
6. o reuso de VRAM: sVramAuthor = sVramBgA
```

Ciclo por hipotese, cerca de dois minutos cada:

```bash
rm -f out/rom.bin && bash ../build.sh "$PWD"
cd "<raiz do workspace>"
bash tools/sgdk_wrapper/capture_blastem_evidence_linux.sh \
  --project-root "tools/sgdk_wrapper/modelo" \
  --rom "tools/sgdk_wrapper/modelo/out/rom.bin" \
  --output-base "tools/sgdk_wrapper/modelo/out/evidence/bis_<n>" \
  --warmup-seconds 6 --target-scene 0 --burst-count 3 --burst-delay 0 --burst-interval 0.4
```

Warmup 6s cai em F451, dentro do ato 3. Abra `animation_frames/frame_*.png` e olhe: **os tres
sintomas sao independentes** e podem ter causas diferentes. Anote qual sintoma cada
desligamento muda.

---

## Hipoteses ranqueadas — sao PALPITES, nao diagnostico

Nao implemente correcao a partir desta lista. Use-a so para escolher a ordem da bisseccao.

### H1 — o reuso de VRAM apaga os tiles da bigorna (explica o sintoma 3)

`brandEnterSignature` faz `sVramAuthor = sVramBgA` e carrega o wordmark **por cima dos tiles
do `img_forge_bg_a_props`**. Mas o tilemap de BG_A ainda aponta para aqueles tiles desde o ato
1 e ninguem o limpou. Sobrescrever tile sob um tilemap vivo troca o desenho no lugar.

Teste: desligue o item 6, aponte `sVramAuthor` para uma regiao livre e veja se a bigorna
sobrevive. O gate de residencia diz que ha folga: `act3_signature` usa 865 de 1740 tiles.

### H2 — a cortina move o plano errado (explica o sintoma 2)

A cortina roda `VDP_setVerticalScrollTile(BG_B, ...)`, ou seja **levanta BG_B**. O wordmark do
autor esta em **BG_A**. Para uma cortina revelar algo, o que e revelado precisa estar **atras**
dela. Se BG_A esta na frente, o wordmark ja deveria estar visivel antes da cortina — e nao
esta, o que sugere que o problema nao e so de ordem de plano.

Teste: desligue o item 1. Se o wordmark aparecer com a cortina desligada, a cortina o esta
cobrindo; se continuar sumido, o problema e do desenho dele.

### H3 — prioridade de plano herdada do ato 1 (pode explicar 2 e 3)

O ato 1 desenha `img_forge_bg_a_props` com `TILE_ATTR_FULL(..., TRUE, ...)`, prioridade alta. O
wordmark do ato 3 e desenhado com prioridade `FALSE`. Prioridade e por tile: os tiles antigos
de prioridade alta podem continuar mandando na composicao.

### H4 — o magenta do backdrop (sintoma 1)

`PAL_setColor(0, 0x0000)` roda **uma vez**, em `brandEnterIgnition`. O indice 0 e o backdrop.
Qualquer carga de paleta posterior que toque o indice 0 devolve o magenta de transparencia dos
PNGs. Procure quem escreve em PAL0[0] depois do ato 1 — inclusive `SPR_reset()` e as trocas de
paleta dos wordmarks.

Este sintoma e provavelmente **independente** dos outros dois. Trate separado.

---

## O que nao pode regredir

Depois de cada correcao, confirme que os atos 1 e 2 continuam de pe:

```bash
python3 tools/sgdk_wrapper/audit_tile_residency.py --project-root tools/sgdk_wrapper/modelo
python3 tools/sgdk_wrapper/validate_brand_comprehension_gate.py \
  --contract tools/sgdk_wrapper/modelo/doc/branding_sequence_contract.json
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \
  --project-root tools/sgdk_wrapper/modelo --shared-builder-root tools/image-tools
```

Os tres precisam sair com exit 0, e o bundle precisa selar com `blockers: []`.

Nao mexa nos parametros de coreografia sem re-medir: `SHARD_COUNT 56`, `SHARD_ROWS 7`,
`SHARD_ROW_STAGGER 6` e `sector = (index * 5) & 15` saem de uma matriz medida no
`vdp_scanline_simulator`. Mudar qualquer um exige refazer a matriz — `56/stagger 4` **reprova**
com 23/20 sprites.

---

## Duas coisas que continuam abertas e nao sao suas, mas voce vai esbarrar nelas

**`brandEnsureShard` falha em silencio.** Se `SPR_addSpriteEx` devolve NULL a funcao apenas
retorna: sem contador, sem blocker. Enquanto isso existir, "56 estilhacos" e claim nominal e
nao visual. Se voce puder acrescentar um contador exportado pela probe, ele resolve tambem a
proxima linha.

**Modelo e hardware discordam.** A varredura em Python preve pico de 16 sprites por scanline; a
probe on-hardware, cobrindo F90-F511 e contando todas as 224 linhas, mede 6. A probe e a
autoridade. A diferenca deixa a matriz conservadora e nao perigosa, mas nao esta explicada — e
o contador acima e a hipotese mais barata para explica-la.

---

## Ao terminar

Registre em `doc/10-memory-bank.md` e no changelog **qual desligamento revelou cada sintoma**,
nao apenas a correcao final. A bisseccao e o artefato mais valioso aqui: ela e o que impede a
proxima pessoa de teorizar por dois builds como eu fiz.
