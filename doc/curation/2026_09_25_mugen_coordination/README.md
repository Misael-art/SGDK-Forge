# Curadoria e coordenacao MUGEN — 25/09/2026

Pedido humano: curar aprendizados pendentes, orientar conclusao do projeto
SGDK com cenario/musica/refinos e preparar iniciativa equivalente no SMSForge
ate demo de combate sem cenario final. Autorizacao explicita permite esta
atualizacao canonica; nao representa aprovacao de novos assets ou releases.

## Resultado da curadoria

O indice tinha38 IDs: cinco promovidos anteriormente e33 pendentes.
Todos os33 receberam parecer individual. Foram incorporadas24 instrucoes
com escopo qualificado; nove formulacoes ficaram nao promovidas, com correcao
explicita e necessidade de prova adicional. Foram acrescentadas sete licoes
do HUD/continuidade. Total atual:45 IDs,36 instrucoes promovidas e nove nao
promovidas. Nenhum desses numeros significa jogos/assets aprovados.

Artefatos:

- `lesson_adjudication.json`: decisao, formulacao curada, evidencia e proxima
  acao para cada um dos40 IDs desta rodada; cinco anteriores preservados.
- `source_snapshot.json`: hashes das fontes consultadas, sem inventar nova
  execucao de ROM.
- `validation_report.json`: verificacoes executadas nesta rodada.
- `../../prompts_modelo/prompt_mugen_sgdk_completion_2026_09_25.md`:
  direcionador de producao SGDK.
- `../../prompts_modelo/prompt_mugen_sms_port_2026_09_25.md`:
  direcionador do backend SMS.

Referencia operacional canonica:
`tools/sgdk_wrapper/.agent/references/mugen_curation_operational_2026_09_25.md`.
Quatro skills existentes apontam para ela: conversao, excelencia visual,
runtime SGDK e budget VDP. O indice e regenerado pelo conversor; agora exibe
redacao curada e preserva `source_lesson` original. Isso impede que um agente
reaprenda a generalizacao rejeitada somente por ler o indice compacto.

## O que se tornou instrucao aproveitavel

- Conferir fonte real e capacidades do executor antes do brief.
- Preservar paleta propria/mask do retrato e distinguir RGB autoral do medidor.
- Tratar escrita e limpeza como parte do layout HUD; separar energia real
  da curva de apresentacao.
- Medir recursos compilados e residencia temporal, duas restricoes por
  scanline, transicoes e custo do medidor.
- Aplicar harness semantico, oraculos independentes e restauracao segura;
  limitar conclusoes ao caso/janela efetivamente testados.
- Preservar proveniencia/aprovacoes por hash e delimitar sonda forcada,
  ROM normal, screenshot, movimento e audio.

## Formulacoes nao promovidas

`ai_activates_commands`, `md_68000_loop_cost`, `measure_on_hardware_not_host`,
`mugen_engine_rules_outside_cns`, `screenshot_gate_without_scene`,
`mugen_mask_compositing`, `source_resolution_scale_evaluation`,
`template_probe_self_cost`, `window_plane_top_or_bottom`.

Os principios seguros relacionados aparecem qualificados na referencia, mas
as afirmacoes originais nao viraram doutrina: fator fixo de custo, escala5/6,
geometria WINDOW simplificada, transparencia generalizada, suporte sem fixture
e cenario criado apenas para satisfazer edge density foram rejeitados como
regras universais. Caso/API especifico precisa prova propria para nova promocao.

## Aprendizado herdado e estado do jogo

Audit local retornou48 licoes/30 candidatos e `learning_context_present`.
Inspecao encontrou conteudo de The Forge herdado do template. Esses dados
foram preservados; a revisao local de promocao recebeu aviso de origem e
escopo vigente. Nenhuma promocao automatica em lote foi aplicada ao ledger.
O indice curado por IDs e a referencia acima sao a entrada desta rodada.

Aprovar piloto750,1 nao aprova demais poses. Conceito de retrato1254x1254 nao
e moldura nativa32x32. Resultado conhecido do HUD continua vinculado a ROM
f5eb26a3…b62d1d e sonda24183495…5ba871; esta curadoria nao produziu nova ROM.
14 erros globais de validacao, paleta global, cenario, audio e desempenho
continuam itens do executor, nao foram resolvidos por documentacao.

## Coordenacao dos dois executores

1. SGDK: reconciliar trabalhos isolados/proveniencia, fechar paleta/FX/HUD,
   medir base, produzir Suzaku com camera/profundidade/vida ambiental, integrar
   musica e fechar regressao audiovisual no mesmo SHA.
2. SMS: inventariar destino, criar backend/projeto isolado quando ausente,
   portar frontend/IR com rastreio, congelar subconjunto obrigatorio, provar
   dois lutadores, movimento, combate, HUD/FX e PSG sem cenario final.
3. Ambos mantem backlog, checkpoint reproduzivel e caso minimo para o
   coordenador quando falham duas tentativas sem progresso. Podem trabalhar
   em codigo/arte independente; builds e capturas pesadas compartilham o host
   e devem ser serializadas quando houver pressao de memoria.
4. Nao editar os mesmos arquivos, copiar status entre plataformas, aprovar o
   proprio visual apenas por contagem de cores ou declarar AAA por persistencia.
   Geracao de imagem e uma capacidade; escuta, revisao temporal e codigo exigem
   suas proprias provas. Se nao houver capacidade de revisar, esse eixo fica aberto.

Os prompts exigem continuar depois de cada marco, com criterio de fim e
escalonamento concreto. Nenhum prompt garante sozinho qualidade absoluta,
conclusao autonoma ilimitada ou ausencia de regressao. A garantia operacional
e nao permitir que falta de prova se torne aprovacao.
