# mugen2sgdk_forge — Plano e Roadmap

> Documento de continuidade. Um agente que retomar este trabalho deve ler, nesta ordem:
> `AGENTS.md` (raiz) → este arquivo → `doc/BASELINE_E0.md` → `reports/`.
> Atualize a secao **Estado atual** ao fim de cada sessao.

## Missao

Construir um conversor **offline, modular, deterministico e reutilizavel** de conteudo MUGEN
(personagens, stages, sons, demais recursos) para SGDK 2.11, usando o HAMOOPIG como runtime
base de luta e um projeto de demonstracao separado como consumidor.

"Completo" e objetivo arquitetural. Nada e declarado pronto sem: entrada real, testes, build pelo
wrapper canonico e ROM rodando no BlastEm com evidencia vinculada ao SHA-256 do binario.

## Onde fica cada coisa

| Papel | Caminho | Observacao |
|---|---|---|
| Motor (ferramenta) | `tools/mugen2sgdk_forge/` | Python, sem dependencia do HAMOOPIG |
| Runtime base | `SGDK_projects/HAMOOPIG [VER.001] …/` | preservado; integracao so via adaptador |
| Jogo de demonstracao | `SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/` | criar na E3 |
| Ferramenta legada | `tools/mugen2sgdk/interface.dist/` | exe PyInstaller de terceiros, sem fonte, gitignored; so referencia |
| Acervo (fora do repo) | `/mnt/sdcard/Projects/Mugenesis/Base de Estudo/` | **somente leitura**; nunca copiar para o Git |
| Referencia historica | release `hamoopig-original-v001-recovered-20260922` | intocavel |

Branch/worktree: `feat/mugen2sgdk-forge` em `/mnt/sdcard/Projects/Sgdk Forge.wt-mugen2sgdk`
(base `dee2356e`). O worktree principal tem trabalho nao commitado do usuario — nao mexer nele.

## Arquitetura (pacote `mugen2sgdk_forge`)

```
inventory   → descoberta de arquivos, formatos, dependencias, candidatos a licenca   [E1 ✅ v1]
parsers/    → def, air, sff(v1 PCX / v2 PNG-RLE8-LZ5), act, cmd, cns/st, snd         [E2/E3]
ir/         → modelo canonico (Character, Stage, Anim, Frame, Clsn, Palette, Sound,
              State, Command) — dataclasses + JSON schema, sem nada de SGDK           [E2]
analysis/   → compatibilidade e orcamento: cores/paleta, tiles, VRAM, sprites/linha,
              DMA por frame, RAM, audio; classifica cada elemento em
              direct | approximate | manual | unsupported                             [E2+]
converters/ → sprite/paleta (quantizacao 15 cores + index0), anim, clsn→hitbox tables,
              states→tabela de estados C, snd→WAV 8-bit/XGM2, stage→BG A/B + parallax [E3/E4]
generators/ → .res, .h/.c de dados (const, sem float/malloc), manifest de saida       [E3]
validate/   → schema, referencias, orcamento; falha com mensagem acionavel           [E2+]
report/     → manifest entrada/saida com hashes, relatorio de fidelidade e licenca    [E1+]
```

Regras: IR nao conhece SGDK; generators nao leem MUGEN; toda saida de arte nasce
`technical_candidate` (aprovacao visual e humana); nenhum caminho absoluto do host em saida.

## Etapas

| Etapa | Entrega | Criterio de aceite | Estado |
|---|---|---|---|
| E0 Baseline | `doc/BASELINE_E0.md`, worktree | hashes da release conferidos; riscos listados | ✅ 2026-09-22 |
| E1 Inventario | `inventory.py`, `reports/e1_inventory.json`, testes | 119 zips lidos, 0 erros, deterministico | ✅ v1 2026-09-22 |
| E1b Licencas | `reports/e1_licenses.csv` (humano confirma) | cada item candidato com status; nenhum "confirmed" sem evidencia | ⏳ depende do usuario |
| E2 IR + parsers | parsers def/air/sff/act + schema IR + testes de contrato | parse de 100% dos .def/.air/.sff do acervo sem crash; erros com arquivo:linha | ⏳ |
| E3 Personagem vertical | 1 personagem → sprites, anim, clsn, cmd, estados, sons → MUGEN_DEMO | build wrapper + BlastEm + relatorio de fidelidade | ⏳ |
| E4 Stage vertical | 1 stage → BG/parallax/chao/limites/musica | idem + orcamento VDP | ⏳ |
| E5 Generalizacao | ≥2 chars, ≥2 stages, casos hostis | relatorio por recurso; codigo HAMOOPIG-especifico em adaptador | ⏳ |
| E6 Fechamento | ROM + evidencia + memory bank/changelog + revisao independente | evidencia ligada ao hash; revisao registrada | ⏳ |

## Achados da E1 (resumo de `reports/e1_inventory.json`)

- 119 zips (fullgames ignorado), 0 erros de leitura; 38 com arquivo candidato a licenca/readme.
- SFF: 301 × v1.0.1.0 (PCX), 2 × v2 → **parser v1 e prioridade**; v2 vem depois.
- .def: 22 personagens, 252 stages, 42 sistema/desconhecidos. 31 .snd, 30 .st, 163 .png.
- Nenhuma licenca confirmada. Autores dos personagens registrados no inventario.
- Personagem da E3: `ken_masters_adv.zip` (1,3 MB) ou `robert98.zip` (3,8 MB), escolhidos pelo usuario.
- Formatos sem classificacao ainda: .ai .bat .css .db .exe .gif .htm .html .jpg .js .rar
  (maioria lixo de distribuicao; .rar aninhado precisa de decisao).

## Politica de licenca

- `license_status` so vira `confirmed` com evidencia registrada pelo usuario (texto de permissao,
  autoria propria, CC). Arquivo readme encontrado = apenas `candidate`.
- Sem confirmacao: conteudo convertido fica em pasta gitignored (`out/local_study/`), nunca em
  commit/release. Testes e fixtures do Git sao sinteticos.

## Decisoes do usuario (2026-09-22)

1. Pastas vazias de split de caminho no HAMOOPIG: **removidas**. `[ENGINE]/` e `src/` na raiz
   (nao vazias, nao rastreadas) continuam intocadas — sem decisao.
2. Personagens **autorizados pelo usuario para uso** no projeto:
   `chars/street-fighter/ken_masters_adv.zip` (Chok) ou `chars/kof/robert98.zip` (Scal).
   Autorizacao de uso != permissao de redistribuicao dos autores: arte/dados convertidos
   continuam fora do Git e de releases ate confirmacao de redistribuicao.
3. Jogo de demonstracao: `Mugenesis_Demo`.

## Comandos

```bash
cd tools/mugen2sgdk_forge
python3 -m pytest -q tests
python3 -m mugen2sgdk_forge.inventory "/mnt/sdcard/Projects/Mugenesis/Base de Estudo" \
        --out reports/e1_inventory.json
```
Build de ROM no Linux: so a ponte Wine funciona (build.sh sofre PATH shadowing).

## Estado atual

- 2026-09-22: E0 e E1 v1 concluidas. Pastas vazias removidas; personagens da E3 definidos. Proximo passo: **E2 — parser SFF v1 + AIR + DEF e schema do IR**,
  testados contra fixtures sinteticas e depois contra todo o acervo (somente leitura).
- E0/E1 commitados na branch; HAMOOPIG memory bank/changelog nao tocados (nenhuma mudanca de runtime).
