# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.


## L01 prompt pack para geracao humana assincrona

- Data: 2026-07-03
- Contexto: rota local de geracao IA bloqueada no host (Bonsai/ComfyUI), mas arte de concept necessaria para o CAIS_01; a partir de 2026-07-09, canal nativo callable/inline deve vencer esse bloqueio quando existir
- Padrao observado: prompt pack com prompts especificos (paleta hex, poses numeradas, negative prompt, criterios de aceite, caminho de salvamento) rendeu 15 concepts utilizaveis na primeira geracao feita pelo humano em modelo externo
- Causa provavel: especificidade tecnica do prompt transfere a direcao de arte para qualquer canal disponivel sem perder o contrato visual
- Mitigacao: formalizar prompt_pack como insumo padrao da art-creation-sourcing para qualquer canal; se `generation_channel_decision` selecionar nativo, gerar pela ferramenta da sessao em vez de instalar Bonsai/ComfyUI
- Evidencia: doc/art/prompt_pack/00_leia_primeiro.md e data/source_art/premium_source_manifest.json
- Classificacao: candidato_canonico
- Candidato: art/art-creation-sourcing adotar prompt_pack como artefato padrao

## L04 contact sheet vdp como prova barata

- Data: 2026-07-03
- Contexto: direcao de arte pendente de ratificacao humana; necessidade de provar sobrevivencia da linguagem no VDP antes de converter
- Padrao observado: downscale 320x224 + quantizacao 15 cores + snap 9-bit (passo 36 por canal) separou objetivamente o que sobrevive (cenarios, BG loop, logo) do que nao sobrevive (personagem realista em 44-56px)
- Causa provavel: a prova reproduz as restricoes reais do alvo com custo quase zero
- Mitigacao: incorporar o contact sheet VDP como gate padrao do art-translation-to-vdp via script canonico no wrapper
- Evidencia: data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png
- Classificacao: candidato_canonico
- Candidato: script canonico de contact sheet VDP no tools/sgdk_wrapper

## L12 staging Linux sem LTO recupera build sem contaminar o SDK

- Data: 2026-07-29
- Contexto: build SGDK 2.11 de MARE_BRAVA em Manjaro Linux após mismatch LTO comprovado no link direto
- Padrao observado: copiar o SDK para staging controlado, encapsular os executáveis Windows com a bridge Wine, reconstruir `libmd.a` sem LTO usando o GCC 13 empacotado e compilar o projeto com `LTO=0` produziu ROM válida sem modificar a biblioteca canônica
- Causa provavel: objetos fat preservam código linkável sem exigir que o plugin LTO 13 consuma bytecode LTO 16, e o staging separa a adaptação de host da fonte canônica
- Mitigacao: reutilizar somente no host Linux por meio de `build_sgdk_wine_bridge.sh`, sempre precedido por `select_sgdk_build_route.py`; no Windows exigir coerência nativa do SDK em vez de usar esta bridge
- Evidencia: out/logs/linux_wine_build_report.json com exit_code=0 e ROM SHA-256 8ed8f28bde41cc4987718079f7584c6d90cbe1cad22a73f1b953857b367a434d
- Classificacao: candidato_canonico
- Candidato: rota Linux isolada no sgdk-build-wrapper-operator e production-diagnostic-triage

## L13 pose-mestre aprovada e edicao de clusters preservam autoria na animacao

- Data: 2026-07-29
- Contexto: segunda versão da `idle_guard` da TAÍNA, após a v01 perder identidade e o primeiro strip v02 gerado como seis imagens independentes produzir morphing
- Padrao observado: limpar e aprovar um unico quadro 48x64, congelar contorno, pivot, pes, maos e guarda, e derivar os outros cinco quadros movendo apenas clusters internos de torso, cabelo e faixa produziu um ciclo sem drift e reconhecivel no BlastEm
- Causa provavel: todos os quadros compartilham a mesma topologia pixel e a mesma pose estrutural; a animação descreve mudança temporal localizada em vez de redesenhar a personagem
- Mitigacao: para novos estados, começar por uma pose-mestre humana aprovada; declarar clusters imutáveis e móveis; derivar quadros por edição pixel; medir bbox, massa, pivot, contato e delta; somente depois compilar e revisar no emulador
- Evidencia: `res/sprites/characters/taina/taina_idle_guard_48x64_v02.png` SHA-256 `5d17c164815eecf821cdd83dd45125fa0c57601facc7566307bc3c1cf6a58cde`; `doc/art/characters/taina/animation/taina_idle_guard_frame_delta_report_v02.json`; `doc/art/characters/taina/animation/taina_idle_guard_runtime_visual_review_v02.json`; sessão BlastEm `out/blastem_env_taina_idle_guard_v02/blastem-linux-20260729T094431Z-325801/`
- Classificacao: candidato_canonico
- Candidato: sprite-animation deve exigir pose-mestre compartilhada e prova de topologia para ciclos de personagem

## L14 acao principal deve ter entrada equivalente em pads de tres e seis botoes

- Data: 2026-07-29
- Contexto: primeira integração visual de `combo_hit_1_jab` na cena demo, testada no BlastEm com mapeamento padrão de pad de três botões
- Padrao observado: a animação estava correta e buildada, mas não aparecia na captura porque o primeiro runtime aceitava somente `BUTTON_X`; adicionar `BUTTON_C` como entrada equivalente tornou o golpe acessível no pad de três botões sem remover `X` no pad de seis botões
- Causa provavel: `X` não existe no controle original de três botões e a captura física do BlastEm envia a tecla correspondente a `C`
- Mitigacao: ações essenciais devem declarar uma entrada primária A/B/C e, opcionalmente, um alias X/Y/Z; teste de animação no emulador deve usar o perfil de pad declarado antes de atribuir falha ao asset
- Evidencia: `src/scenes/scene_demo.c`; ROM SHA-256 `0c281347c4d1673855a45a646cd639a395d0ea7279e15cd0b28c49d538db3822`; sessão `out/blastem_env_taina_combo_hit_1_jab_v01/blastem-linux-20260729T111215Z-598254/`
- Classificacao: local_note
- Limite de uso: não define o mapeamento final do jogo; apenas impede que uma ação essencial dependa exclusivamente de um botão ausente no pad de três botões

## L15 burst temporal de emulador nao e spritesheet

- Data: 2026-07-29
- Contexto: revisão humana da prancha 6×8 montada a partir de 48 screenshots consecutivos do BlastEm
- Padrao observado: uma montagem temporal sem rótulo de proveniência foi interpretada como sheet de 48 quadros; as repetições de idle pareciam desperdício de VRAM e o texto BG_B parecia assado no sprite
- Causa provavel: contact sheet de captura e spritesheet físico usaram a mesma gramática visual de grade, sem cabeçalho que diferenciasse amostras temporais de células de recurso
- Mitigacao: toda prancha de runtime deve declarar `runtime_temporal_burst`, ROM, intervalo e contagem de amostras; a prancha de frames únicos deve vir separada e apontar diretamente para o PNG em `/res`
- Evidencia: `doc/art/characters/taina/animation/taina_combo_hit_1_jab_contact_sheet_classification_correction_v01.json` e `doc/art/characters/taina/review/taina_combo_hit_1_jab_runtime_unique_contact_6x_v02.png`
- Classificacao: local_note
- Limite de uso: a prancha temporal continua útil para timing e estabilidade, mas nunca mede sozinha contagem de frames, ROM ou VRAM

## L16 montagem modular nativa preserva leitura e reduz tiles

- Data: 2026-07-29
- Contexto: primeiro recorte jogável do CAIS_01 após o contrato rejeitar panorama pronto como cenário final
- Padrao observado: construir céu, indústria, quatro bandas de mar, piso e props diretamente na grade de 8×8/16×16 preservou a direção quente/fria, manteve o centro livre para combate e resultou em 204 tiles após ResComp
- Causa provavel: módulos com função explícita repetem formas deliberadamente e permitem que o compressor deduplique padrões; a composição nasce para BG_A/B e para a silhueta do jogador em vez de ser achatada depois
- Mitigacao: continuar o cais por salas modulares; declarar papel, plano, paleta, colisão e sinal de gameplay de cada módulo antes da promoção; usar panorama somente como referência direcional
- Evidencia: `doc/art/environments/cais01/cais01_modular_slice_build_v01.json`; `doc/art/environments/cais01/cais01_vdp_budget_report_v01.json`; ROM SHA-256 `e1fc0dd5180ffb09f74087248f1d4d363ace93b5c1a74f0e307c1b8f3e05c1c6`; `out/blastem_env_cais01_slice_v01/blastem-linux-20260729T162222Z-466584/screenshot.png`
- Classificacao: local_note
- Limite de uso: o número de 204 tiles vale apenas para a primeira sala travada 320×224; não prova streaming, parallax ou budget da fase completa

## L17 preflight headless separa capacidade de ferramenta de producao artistica

- Data: 2026-08-30
- Contexto: curadoria do Visual Forge depois de a rota GIMP interativa consumir contexto sem exportar uma candidata segura.
- Padrao observado: um preflight curto em perfil XDG isolado provou GIMP 3.2.4 + `python-fu-eval` sem abrir GUI, enquanto o registro `registered_production_operations=[]` impediu transformar capacidade do host em falso claim de conversao.
- Causa provavel: separar probe, operacao registrada, contrato pixel e gate visual torna cada claim reproduzivel e evita que a ferramenta opcional contamine o core.
- Mitigacao: manter o preflight independente do `convert`; registrar operacoes GIMP somente com script estatico, spec, timeout, staging e fixtures; validar toda saida pelo forge-art.
- Evidencia: `forge-art self-check` 107/107; `test_art_pipeline.py` 116/116; auditor isolado 1/1; preflight local exit 0.
- Classificacao: candidato_canonico
- Candidato: adaptadores GUI/CLI opcionais devem possuir preflight separado e registry vazio por default.
