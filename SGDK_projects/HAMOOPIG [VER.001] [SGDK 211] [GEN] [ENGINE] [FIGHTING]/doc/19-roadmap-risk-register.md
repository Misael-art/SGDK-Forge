# 19 - Roadmap e Registro de Riscos - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

## 1. Milestones

| Milestone | Objetivo | Evidencia de aceite | Status |
|---|---|---|---|
| M0 | Fundação documental classificada | contexto, brief, GDD/TDD proporcionais | concluído — curadoria Discord e plano QA registrados |
| M1 | Primeiro slice jogável ou técnico | ROM/build/report conforme contexto | concluído — ROM vigente `532d4453`, wrapper SGDK 2.11 e provas BlastEm |
| M2 | Polimento dominante | blocker dominante removido | em andamento — HUD/KO/poses/fonte corrigidos; P2 vencedor e START vistos em NTSC e PAL em 2026-09-13; VLAB/VDP/runtime e acabamento do cenário ainda pendentes |

## 2. Riscos

| Risco | Probabilidade | Impacto | Mitigacao | Dono | Status |
|---|---|---|---|---|---|
| Captura canônica sem VLAB/VDP/runtime | alta | alto | manter screenshot semântico + registrar bloqueio; instrumentar probes antes da promoção | QA/engine | aberto |
| KO do Musgo reiniciar frame terminal | média | alto | estado terminal sem reentrada; dano letal unico; arte deitada e espera de pouso | gameplay | mitigado com captura de ambos os lados |
| Showdown quadriculado / VRAM excedida | alta | alto | reautorizar tilemap por camadas e medir residência antes de trocar asset | arte/engine | aberto |
| Mensagens fora da fonte autorada | média | médio | atlas solicitado em PAL1 e painel VBlank; preservar poses visiveis | HUD | mitigado em capturas NTSC/PAL |
| P2 vencedor e revanche não exercitados | média | alto | roteiro de input simetrico e entrada de luta verificada | QA/gameplay | P2/START provados em NTSC/PAL; revanche NTSC provada em 2026-09-12 |
| Captura de audio silenciosa por roteamento do host | alta | medio | verificar sink real do novo fluxo BlastEm, nao apenas PULSE_SINK | QA/audio | causa identificada; nao atribuir silencio a ROM sem rota verificada |
| PAL usa enquadramento diferente do NTSC | alta | medio | nao comparar template de nome em coordenadas NTSC; validar HUD e estado visivel | QA | capturador reforcado; conferir variantes antes de generalizar |

## 3. Cortes Permitidos

Liste cortes que preservam a promessa do projeto.

- Adiar parallax MUGEN e expansão de roster até o orçamento de tiles/scanline ser medido.
- Manter Musgo como `source_candidate` até existir lineart/pixel art autoral aprovado.

## 4. Cortes Proibidos

Liste cortes que destruiriam a identidade ou o objetivo.

- Remover o estado terminal, a queda no piso ou o feedback de KO.
- Declarar vitória/fps/AAA sem captura fresca e sem hash da ROM vinculada.

## 5. Criterio de Parada

- Quando parar de iterar: após build repetível, prova simétrica de round e gates de arte/HUD mínimos passarem.
- Quando bloquear e pedir decisão humana: se a fonte do cenário ou da tipografia exigir nova autoria/licença, ou se VLAB/runtime não puder ser instrumentado.
- Quando capturar aprendizado local: a cada falha causal repetida (VRAM, sprite, captura, KO) em `doc/agent_learning/` e no changelog.
