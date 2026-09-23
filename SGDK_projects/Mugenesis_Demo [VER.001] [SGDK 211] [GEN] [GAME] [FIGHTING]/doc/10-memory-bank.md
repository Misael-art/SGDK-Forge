<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: bootstrap de projeto novo
- Ultima sincronizacao: 2026-09-23T01:30:22.2602857Z
- Ultimo build versionado: nenhum
- ROM vigente: inexistente
- Evidencia de emulador: inexistente
- Gate visual: blocked_no_premium_source
- Gate gameplay: nao provado
- Gate AAA: ready_for_aaa=false
<!-- SGDK GENERATED STATUS END -->

# 10 - Memory Bank & Context Tracker - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

**Ultima atualizacao:** 2026-09-23
**Fase atual:** E3 - primeiro personagem vertical (Ken, via mugen2sgdk_forge)
**Proxima fase:** E3b desempenho 60 fps constante; E4 primeiro stage

## 1. Estado operacional

- documentado: sim (tools/mugen2sgdk_forge/doc/ROADMAP.md e doc/mugen/ken_conversion_report.json)
- implementado: cena de luta (src/scenes/scene_demo.c) + runtime generico (src/mg/, copiado da ferramenta)
- buildado: sim, pela ponte Wine canonica; ROM SHA-256 da3548308324606da3f71584a6b48bf441f0d9884e32df33166893ab3534fcfc
- testado_em_emulador: sim, BlastEm; sessao selada out/mugenesis_evidence/e3_ken/blastem-linux-20260923T070143Z-1272238 (arvore principal)
- validado_budget: NAO. 598 de 3631 quadros acima de 100% de CPU (16%), pico 156%; 10 sprites/linha no pico
- audio: sons convertidos tocam via XGM2 (RMS nao nulo em todos os segundos da captura)
- visual: technical_candidate (conversao automatica; aprovacao humana pendente); gate semantico de tela rejeita por baixa densidade de bordas (sem cenario)
- ready_for_aaa: false

### Direcionamento 2026-09-23 (P1..P6)
- P1 faiscas ancoradas no contato: FECHADO (ROM normal 38a67c94..., teste f1f4df6a...; 22,6% acima do orcamento).
- P2 saturacao, P4 HUD, P5 sombra, P3 memo aneis, P6 registro de efeitos: pendentes, nessa ordem.
- Build: ROMs com --output-dir alternativo exigem out/ ja buildado (sega.s inclui out/rom_head.bin).

### Conteudo de terceiros
Ken Masters ADV (autor Chok): uso local autorizado pelo usuario; redistribuicao nao verificada.
Saidas convertidas (res/mugen/, res/mgres_*, src/mg_gen/, inc/mg_gen/, out_prof/) ficam fora do Git.
Regerar: `python3 -m mugen2sgdk_forge convert-char <ken_masters_adv.zip> --id ken --project .`

### Licoes
- No 68000 cada iteracao de laco custa centenas de ciclos: o reconhecimento de comandos e o estado -1
  so cabem guiados por eventos/indices gerados pelo compilador (portoes de comando e de tempo).
- Numero em [State N, ...] e rotulo: controlador pertence ao ultimo Statedef (Ken reaproveita rotulos).
- `B` = direcao tras, `b` = botao; caixa importa no .cmd.

## 2. Bloqueios iniciais

- contexto e metodologia ainda precisam de classificacao humana
- fonte visual premium ainda nao foi aprovada
- nenhuma ROM ou evidencia de BlastEm existe

## 3. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.
