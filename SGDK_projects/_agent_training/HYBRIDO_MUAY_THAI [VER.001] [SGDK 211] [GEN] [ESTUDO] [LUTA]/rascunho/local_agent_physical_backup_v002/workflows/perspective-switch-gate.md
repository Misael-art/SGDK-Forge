# Perspective Switch Gate

Status: `canonical_workflow`

## Objetivo

Permitir que o agente alterne a lente operacional sem abandonar a tarefa,
inventar persona paralela ou trocar de modo sem consentimento.

Perspectiva e uma lente de trabalho. Nao e agente novo.

## Perspectivas

| Perspectiva | Foco | Quando ativar |
|---|---|---|
| `director` | promessa, escopo, assinatura, GDD | projeto novo, reseed, gap de personalidade |
| `architect` | TDD, FSM, ownership, cenas | mudanca estrutural ou arquitetura incerta |
| `artist` | arte, UI, animacao, VDP translation | assets, direcao visual ou sprites |
| `hardware` | VRAM, DMA, sprites, CRAM, budget | tecnica avancada ou risco de hardware |
| `coder` | C/SGDK, runtime, build | implementacao de codigo |
| `audio` | XGM2, SFX, PCM, estados musicais | musica, SFX ou drivers |
| `qa` | validacao, BlastEm, closeout | entrega, auditoria ou regressao |
| `learner` | aprendizado local seguro | captura/auditoria de licoes de projeto |
| `curator` | patch canonico, drift, docs | alteracao em canone ou registry |
| `lab_operator` | experimento isolado | tecnica nao validada ou prova controlada |

## Gatilhos

Considere troca quando:

- o trabalho atual depende de outro dominio para nao errar;
- ha risco de seguir com perspectiva inadequada;
- um artefato exige owner diferente;
- uma tecnica avancada entra em cena;
- a proxima etapa do pipeline canonico pede outro tipo de validacao.

Nao troque quando:

- a tarefa atual ainda nao foi estabilizada;
- a troca so adicionaria comentario sem acao;
- o usuario pediu explicitamente foco unico;
- a etapa atual ja tem owner adequado.

## Protocolo

Antes de trocar, informe de forma curta:

1. perspectiva atual;
2. perspectiva sugerida;
3. motivo tecnico;
4. artefatos esperados;
5. impacto na rota atual.

Peça confirmacao humana. Se confirmada, registre a transicao em
`doc/agent_session_state.json` ou declare no chat quando a escrita do estado nao
for apropriada.

## Forma Recomendada

```text
Proponho alternar de `artist` para `hardware`.
Motivo: a composicao visual depende de VRAM/DMA/sprite budget antes do runtime.
Artefatos esperados: budget por cena, tags tecnicas e fallback.
Posso seguir assim?
```

## Restrições

- Nao altere modo sem consentimento.
- Nao use perspectiva para driblar GDD, TDD ou gates.
- Nao aplique patch canonico durante uma perspectiva de projeto.
- Nao marque tecnica como `MESTRE_*` por parecer, texto externo ou laboratorio.
- Nao declare pronto sem evidencia de build, validacao e BlastEm quando o
  escopo for entrega de ROM.

