# Continuacao de QA — 2026-09-13

Resultado: P2 vencedor, START e combate PAL exercitados; empate e vencedor
por tempo observados; audio isolado com sinal. Nenhum C, recurso ou ROM
alterado nesta rodada. Mudancas limitadas ao capturador, configuracao local,
regressoes, ferramentas de evidencia e documentacao.

ROM preservada: `out/rom.bin`, 2490368 bytes, SHA256
`532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`.
Build continua sendo o de `out/logs/visual_ko_verified_build.log`.

## Provas revisadas

Todos os diretorios abaixo vivem em `out/emulator_evidence/`.

| Sessao | Observacao | Evidencia |
|---|---|---|
| `visual_ko_20260913T114321Z` | NTSC, Musgo x Musgo: P2 vence dois KOs; P1 deitado e barra vazia; START retorna ao seletor | `zero_2_result.png`, `return_select_or_pause.png`, video e manifest |
| `visual_ko_20260913T114702Z` | PAL europeu, Ryo x Musgo: P2 vence, P1 deitado e barra vazia; START retorna ao seletor | mesmos nomes; titulo amostrado proximo de 50 fps; audio desta sessao rejeitado por silencio |
| `visual_ko_20260913T114914Z` | NTSC, vida igual: DRAW no fim do relogio e round seguinte restaurado | `combat_058.png`, `combat_063.png`, video; audio roteado manualmente durante a sessao, nao usado como prova principal |
| `visual_ko_20260913T115242Z` | Outra prova de DRAW, nao de vencedor por tempo: o golpe solicitado nao acertou | `combat_058.png`; audio isolado com rota verificada e sinal real |
| `visual_ko_20260913T193905Z` | Dano nao letal observado em P1; relogio zero concede PLAYER 2 WINS; round seguinte restaura barras | `timeover_damage_setup.png`, `combat_010.png`, `combat_015.png`, video e manifest |

Input enviado nao foi promovido a resultado: a classificacao acima vem das
imagens revisadas. Poses de derrota/vitoria ja implementadas funcionaram
com o vencedor no lado P2. Revanche A em NTSC permanece provada nas sessoes
de 2026-09-12 da mesma ROM.

## Audio: sinal comprovado, qualidade ainda nao aprovada

Prova principal: `visual_ko_20260913T115242Z/emulator_audio.wav` e
`audio_signal_report.json`. PCM 48 kHz, stereo, 111,85 s; pico 5734/32768,
RMS aproximadamente -28,12 dBFS, zero amostras saturadas. Metadados identificam
exatamente um fluxo `blastem.bin` no sink isolado.

`audit_captured_audio_signal.py --self-check` passou (silencio, RMS conhecido,
clipping e rejeicao de arquivo vazio). WAV silencioso retorna exit 2 e
`not_validated`; arquivo com sinal/rota verificada nao e aprovacao de mix,
musicalidade ou escuta. Ainda falta audicao critica e prova dedicada de SFX
sob combate pesado.

Captura adicional completa na sessao de vencedor por tempo
`visual_ko_20260913T193905Z`: 201,8 s, pico 6182/32768, RMS -28,22 dBFS,
zero amostras saturadas, rota isolada verificada. A duracao e maior por
lentidao do host; nao indica duracao do round nem FPS da ROM.

O silencio inicial nao demonstrava defeito na ROM: o fluxo real estava no
sink do processador de audio do host. Corrigido no capturador por identidade
do novo fluxo, movimento explicito e espera pela confirmacao do roteamento.
Nao houve mudanca de dispositivo padrao nem de fluxos de outros aplicativos.

## Regressoes e integridade

- `test_health_contract.py`: PASS, funcoes C reais, 192 transicoes letais,
  clamps, dois lados, zero completo e ausencia de relancamento duplicado.
- `test_stage_palette.py`: PASS, indices opacos 1..14, paleta 9-bit,
  vinculo dos hashes e relatorio de 768 tiles.
- `test_timeover_contract.py`: PASS, trecho real de `src/fsm.c`, 9.216
  combinacoes de vida positiva; empate nao concede ponto, vencedor correto,
  relogio nao zerado ignorado e 120 repeticoes sem pontuar novamente.
- Regressoes host nao substituem emulador nem medem VBlank/SAT.
- `seal_continuation_evidence.py` prepara paths de arquivos reais e verifica
  ROM atual, copia por sessao e hash no manifest antes do finalizador canonico.
- Relatorios: `out/logs/continuation_session_20260913.json`,
  `out/logs/evidence_closeout_report.json`,
  `out/logs/screenshot_semantic_gate_report.json`.
- Finalizador canonico: `seal_status=sealed`, gate semantico `passed`,
  incluindo as cinco sessoes acima e seus artefatos reais. Prova
  identidade/integridade, nao selo VLAB/VDP/runtime completo.
- Grafo de recursos atualizado: quatro informativos sobre `ALIGN` nao
  interpretado e um aviso `code_loaded_tiles_unmeasured`; nao e overflow
  demonstrado. Auditoria estatica nao substitui dump/telemetria.
- Frescor global ainda tem limites: compilacao de contratos de cena ausente
  e validation_report antigo. O compilador de cenas sobrescreve o contrato
  estrutural; nao foi executado apenas para apagar esse aviso nesta rodada
  de provas, que preserva C/recursos/ROM.

## Melhorias no teste e licoes

- Configuracao local completa derivada do pacote instalado, com segundo
  controle no teclado, sem substituir a configuracao global do usuario.
- `XDG_CONFIG_HOME` definido dentro do sandbox; o pacote usa o diretorio
  diretamente para `blastem.cfg`. Conferido no
  [patch do pacote Flatpak](https://raw.githubusercontent.com/flathub/com.retrodev.blastem/master/0001-Add-support-for-Flatpak-config-data-dir-variables.patch).
- `XDG_DATA_HOME` por sessao impede que todas as copias `rom.bin` reutilizem
  o mesmo SRAM global. SRAM capturada nao e declarada probe decodificada.
- Entrada na luta exige HUD visivel antes de amostrar zeros. Coordenadas
  NTSC do nome no seletor nao foram generalizadas para PAL.
- Preparacao de vencedor por tempo exige reducao visivel e nao letal de vida;
  uma tentativa de golpe nao basta.
- Sink isolado temporario e removido ao final; falhas de host/captura sao
  separadas da ROM. Tentativas sem HUD ou com audio silencioso nao aprovam QA.
- Licoes locais em `test_harness_lessons.json`; nenhuma promocao canonica.

## Limites e proxima prioridade

Teto continua `prototype`, nao `ready_for_aaa` nem `validado_budget`.
FPS do titulo amostrado e cadencia do arquivo de video nao medem FPS do loop.
Na retomada da tarde, o host apresentou carga alta; nao usar essa sessao para
certificar performance.

Proximos ramos: especial/projetil apos reset nos dois lados; pior DMA,
SAT/scanline e fragmentacao do pool; audicao e SFX; provas PAL adicionais
(empate, revanche, especiais); bundle VLAB/VDP/runtime. Polimento de sombra,
corpo cortado na borda e perdas locais do cenario permanece separado.
