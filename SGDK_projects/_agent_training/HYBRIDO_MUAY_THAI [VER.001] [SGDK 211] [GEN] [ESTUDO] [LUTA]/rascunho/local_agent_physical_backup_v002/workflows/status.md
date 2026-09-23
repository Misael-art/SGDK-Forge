# Workflow: Status

Use este fluxo para relatar o estado real de um projeto sem ambiguidades.

1. Leia manifesto, docs canonicos e sinais de artefato.
2. Preencha os campos: `documentado`, `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`, `placeholder`, `parcial`, `futuro_arquitetural`, `agent_bootstrapped`.
3. Para cada campo, declare explicitamente:
   - evidencia positiva (o que prova)
   - ausencia de evidencia (nao prova nada)
   - evidencia negativa (prova que esta falhando)
4. Aponte conflitos entre documento e codigo (com a fonte de maior autoridade vencendo).
5. Use `out/logs/validation_report.json` como fonte primaria do painel de status quando existir.
6. Quando `out/logs/runtime_metrics.json` existir, ele deixa de ser "anexo" e passa a alimentar o `validation_report.json` e os campos de runtime do painel.
7. Use heuristica por presenca de arquivo apenas como fallback honesto quando os artefatos estruturados nao existirem.

## Evidencias recomendadas por campo

| Campo | Evidencia positiva minima (exemplos) | Nao aceito como evidencia |
|------|--------------------------------------|---------------------------|
| `documentado` | docs canonicos existentes em `doc/` (ex.: GDD, spec de cenas) | README isolado como prova de estado real |
| `implementado` | codigo em `src/` + integracao de `res/` coerente com o manifesto | "tem pasta src" sem compilar ou sem integracao verificavel |
| `buildado` | `out/rom.bin` existe (ideal: hash/tamanho) | "passou no meu PC" sem artefato |
| `testado_em_emulador` | evidência rastreável de BlastEm no gate de entrega; BizHawk só complementa telemetria e debug. Quando houver dump visual em SRAM, `screenshot + save.sram + visual_vdp_dump.bin` fecham o gate sem exigir quicksave nativo | "builda" ou "abre no emulador" sem rodar de fato; Gens KMod como pseudo-evidência |
| `validado_budget` | auditoria de VRAM/DMA/sprites por cena com conclusao objetiva ou `runtime_metrics.json` absorvido no `validation_report.json` sem status critico | "parece caber" sem numeros |
| `placeholder` | asset/logica explicitamente marcada como provisoria | tratar placeholder como final |
| `parcial` | feature funciona em um recorte claro mas falta completar (com criterios) | "quase pronto" sem delimitar o que falta |
| `futuro_arquitetural` | item fora do escopo atual, registrado como futuro | misturar futuro com estado atual |
| `agent_bootstrapped` | `.agent/ARCHITECTURE.md` existe no projeto | confundir `.agent` central com `.agent` local |

## Gates semanticos (recomendado)

Quando o projeto tiver um viewer/laboratorio visual, ele **nao** deve ser confundido com ROM jogavel.

Use os gates abaixo (quando presentes no `validation_report.json`):

- `visual_lab_aprovado`: prova visual rastreavel (gate visual + BlastEm + ROM vigente), mas sem exigir performance/audio/hardware_real.
- `gameplay_rom_aprovada`: prova de ROM jogavel (gameplay + performance + audio + hardware_real) sobre a mesma base de evidencia.
- `ready_for_aaa`: so pode ser verdadeiro quando `gameplay_rom_aprovada` e `validado_budget` estiverem verdadeiros, sem blockers de fechamento.
