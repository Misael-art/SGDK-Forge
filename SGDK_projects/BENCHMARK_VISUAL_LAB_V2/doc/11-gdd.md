# 11 - GDD

## project_brief

`BENCHMARK_VISUAL_LAB_V2` e um framework vivo de benchmark visual para SGDK 2.11 no Mega Drive.

Ele nao existe apenas para exibir cenas bonitas. Ele existe para fechar, de forma repetivel, o ciclo:

- direcao visual
- traducao para VDP
- budget real
- runtime SGDK
- evidencia em BlastEm
- regressao deterministica
- curadoria do agente

Sua funcao e servir ao mesmo tempo como:

- showroom premium de solucoes visuais avancadas
- laboratorio tecnico de validacao em ROM
- base de treinamento e disciplina para agentes
- referencia reprodutivel para futuras cenas AAA do workspace

Pilares do projeto:

- toda solucao visual precisa existir em ROM real
- toda cena precisa ter leitura humana e leitura tecnica
- evidencias tem que ser frescas e vinculadas a ROM vigente
- curadoria nao sobe por retorica; sobe por entrega validada

## core_loop_statement

`selecionar uma cena benchmark -> observar a solucao visual em ROM -> conferir evidencia e budget -> detectar falha ou acerto -> iterar a cena e o processo`

## feature_scope_map

### entra_no_slice

- front-end inicial com identidade de showroom tecnico premium
- menu navegavel com 3 cenas canonicas iniciais
- contrato de evidencia BlastEm como eixo obrigatorio
- regressao deterministica por cena como eixo obrigatorio
- budget por cena como eixo obrigatorio
- camada de observacao de curadoria do agente, ainda sem promocao automatica para canon

### entra_depois

- expansao para demais labs visuais ate cobrir o conjunto desejado de solucoes avancadas
- title/front-end mais ambicioso com maior carga dramatica
- cena de audio senior e integracao XGM2 como trilha formal do laboratorio
- relatorios comparativos entre rotas visuais ou entre abordagens `basic` e `elite`
- painis de leitura perceptiva mais ricos e matriz de qualidade AAA por cena

### fora_de_escopo

- gameplay de jogo completo como prioridade primaria
- historia, campanha ou progressao longa
- prometer curadoria canonica automatica sem validacao humana
- abrir um conjunto grande de cenas antes de fechar o primeiro slice em ROM

## front_end_profile

- profile_kind: `front_end_profile`
- tom: `hibrido_curado`
- papel: comunicar que o laboratorio e ao mesmo tempo ferramenta de prova tecnica e showcase premium
- fantasia prometida no primeiro contato: "isto e um showroom vivo de excelencia visual SGDK, nao um menu generico"
- vida em idle esperada:
  - pelo menos um sinal de profundidade ou movimento perceptivel
  - resposta visual clara de selecao
  - hierarquia forte entre titulo, lista de cenas e estado do laboratorio
- feedback de selecao esperado:
  - cursor ou item ativo com animacao observavel
  - indicacao clara de cena selecionada
  - leitura imediata do que e showroom e do que e modo tecnico
- proibido por default:
  - fundo morto com texto cru
  - frente tecnicamente utilitaria sem assinatura visual
  - front-end que esconda ou enfraqueça a identidade do laboratorio
- criterio de sucesso:
  - o menu inicial ja precisa parecer parte do produto final
  - a leitura tecnica nao pode matar o impacto visual
  - o impacto visual nao pode comprometer navegacao, legibilidade ou futura automacao
