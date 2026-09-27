# Curadoria operacional MUGEN — 2026-09-25

Autorizacao: pedido humano explicito de curadoria e coordenacao nesta sessao.
Esta referencia complementa a de 2026-09-24. Em divergencias descritas abaixo,
vale a qualificacao de 2026-09-25. Promove instrucoes; nao certifica jogo, asset,
API nova, desempenho ou implementacao pendente. Parecer por ID e evidencias:
`doc/curation/2026_09_25_mugen_coordination/lesson_adjudication.json`.

## Fonte, capacidade e autoria

Abrir fonte real antes do brief. Nomes de pacotes nao comprovam elementos,
paletas, tamanho ou animacoes. Separar capacidade de gerar imagem, editar
canvas nativo, indexar, integrar e revisar movimento/audio. Um conceito
1254x1254 com muitas cores nao cumpre contrato32x32 por parecer pixel art.
Correcoes de conversao e remaps lossless podem ser feitos pelo agente tecnico;
reautoria deliberada exige capacidade grafica e direcao aprovada. Nao impor
uma divisao universal de pessoas/modelos nem usar reputacao como prova.

Uma pose aprovada vale para o SHA e escopo registrados. O caso750,1, com cinco
pixels removidos e decomposicao aprovada, nao autoriza corte nos demais frames.
Preservar tempos AIR, vazios intencionais e pivots; prova de movimento precisa
sequencia temporal observada. Referencias de oficio nao sao automaticamente
fontes de pixels. Gitignore e uso local nao concedem direito de redistribuicao.

## Paleta, retrato e transparencia

Indices so tem significado dentro de sua paleta-fonte. Um retrato SFF pode ter
paleta propria, diferente do corpo. Traduzir sua cor e mascara explicitamente;
nao usar indice desconhecido como transparencia. Preto opaco continua opaco.
O teste de mascara exata vale para conversao que promete preserva-la, nao para
redesenho de silhueta deliberadamente aprovado.

Separar contagem exata (indices/classes entre variantes) de distancia perceptiva.
O contrato PAL0 cenario, PAL1/PAL2 lutadores+FX, PAL3 HUD e local. Medir uniao
BG_A/B quando compartilham PAL0. Reservas8+6+1 nao sao lei do Mega Drive;
FX em slots de roupa mudam com variantes e exigem decisao explicita, proibida
pelo contrato atual. Numero23/15 nao e minimo artistico teorico do personagem.

Representacao digital do medidor e PLTE de autoria podem usar convencoes
diferentes. Nesta rota `vdp_rgb` usa niveis ate252; PNG para rescomp usa o
oraculo de autoria0x22 em `forge_art/vdp_color.py`. Converter palavras VDP
explicitamente, testar niveis conhecidos, indice0/tRNS e palavras compiladas.
Nao ensinar que qualquer um desses RGB representa universalmente o CRT.

Reconversao preserva anotacoes humanas fora do manifesto gerado; aprovacoes
valem para o hash atual, historico permanece. A regra e obrigatoria; confirmar
a implementacao da PR21 na branch antes de reconverter producao.

## HUD e recursos logicos

Contrato espacial de UI inclui desenho, limpeza, prioridades e animacoes.
Estrela e combo podem ter desenhos separados e limpezas sobrepostas. Testar
dois digitos, dano, reset, SUPER e ambos jogadores ao mesmo tempo. Retangulo
disjunto nao garante ausencia de oclusao por sprite: verificar a cena.

Energia real e apresentacao sao estados distintos. Descarga visual gradual
nao atrasa gasto, nao cria recurso e nao altera regra de golpe. Teste curvas
e recarga separadamente de traces de gameplay. Igualdade de trace prova apenas
os cenarios executados, nunca equivalencia universal.

## Hardware, custo e transicoes

Medidor precisa de oraculo independente/contraexemplo antes de orientar corte
artistico. Leitura de recursos compilados e mapa temporal de residencia
fundamentam VRAM; PNG sozinho nao mede ocupacao. Reserva considera maior
recurso elegivel e guard real; constantes do Ken nao servem a todo personagem.
Leitura estatica nao comprova DMA, CPU ou pressao de scanline em execucao.

Empréstimo de VRAM/CRAM requer dono, exclusao temporal, entrada, restauracao,
RAM temporaria e pico de transferencia medidos. Cobrir a tela nao torna os
bytes subjacentes livres automaticamente. Medir sprites E pixels por linha;
17 sprites ainda podem ultrapassar o budget de pixels em H40.

Rip de arcade pode exceder residencia; medir tiles unicos, flips, modularidade,
streaming e perda visual antes de decidir. Nao dizer que toda conversao de
cenario e inviavel. Limiares de impacto sao escolhas de design informadas por
dados, nao constantes universais extraidas de um Ken.

Para um stage rolavel, derivar largura por plano de viewport + curso da camera
vezes delta, arredondada ao grid. Medir tambem a pior uniao simultaneamente
visivel e a largura do tilemap VDP, nao somente a uniao completa. No Suzaku,
usar 512 px para ambos os planos ocultou 130 tiles e a borda direita; 520/624
px elevaram o candidato a 1366 tiles, com ate 845 visiveis. Uma imagem 4bpp
valida nao implica que caiba na VRAM, e uma composicao com delta aproximado
nao implementa o parallax da fonte. Prova local em
`Mugenesis_Demo/.../doc/mugen/stage_suzaku_route_2026_09_25.md`.

Nao usar 384->320 para deduzir deformacao ou escala5/6 obrigatoria: aspecto de
pixel, modo de exibicao, enquadramento e intencao artistica precisam ser definidos.
WINDOW tem controles horizontais/verticais; nao descreve apenas uma faixa.
Para o layout atual, duas faixas horizontais independentes de HUD exigem
composicao apropriada, como base em BG_A com scroll protegido. Consultar
headers/documentacao antes de generalizar a geometria do hardware.

## Semantica, testes e claims

Parsers devem preservar a distincao entre identificador de estado, owner e
chave conforme sintaxe suportada. Fixtures locais nao certificam todo MUGEN.
Harness do runtime C real com stubs honestos detecta semantica; ROM verifica
integracao, tempo e arte. Gates extraidos da AST precisam condicoes necessarias
e testes diferenciais positivos/negativos; um trace nao prova equivalencia geral.
Regras de engine externas ao CNS precisam fixtures individuais, nao uma lista
inteira declarada suportada. `mask` de BG nao governa toda transparencia SFF.

Numerador e denominador de overbudget cobrem a mesma janela. Retirar warmup
so do denominador aumenta a taxa. Registrar inputs, estado, eventos cobertos,
regiao, audio e medidor. Janela sem super nao comprova seu custo. Sonda que
forca12hits ou congela um projetil prova o estado forcado; evento natural e
ROM normal exigem evidencia propria. Host nao mede ciclos do68000. Custo
do medidor e do loop deve ser medido na rota atual, sem fatores universais.

SHA igual preserva identidade do binario; reaproveitar apenas observacao cujo
ambiente/inputs/escopo continuam pertinentes. Nao reciclar captura como sessao
nova ou estender screenshot a aprovacao de audio. Rebuild binariamente identico
nao prova determinismo para todas as entradas/configuracoes.

Parametro `target_scene` de um runner e apenas pedido; exigir `scene_id`
observado na telemetria da ROM. A captura com `target_scene=2` em build
`MG_DIRECT_FIGHT=1` foi selada mas mostrou `scene_id=3`; o validador novo
bloqueia o mismatch e a falta de ID. Teste positivo com build de menu separado
observou `scene_id=2`. Arquivo `audio.raw` nao comprova musica, loop ou mix.
Testes: `tools/sgdk_wrapper/tests/test_verify_emulator_target_scene.py`.

Em audio gerado, validar cabecalho/loop contra a especificacao do formato,
mesmo se ResComp compilar. O VGM do menu tinha campos de amostras/loop
deslocados em quatro bytes; o teste corrigido fixa o ponteiro absoluto dentro
do arquivo. Comparar a ROM anterior e posterior em janela igual antes de
atribuir efeito audivel: ambas produziram sinal float32 no menu, entao o
defeito de formato nao foi demonstrado como silencio perceptivel. Presence
de waveform e conformidade de header nao substituem escuta de juncao/mix.

## Continuidade e aprendizado

Isolar variantes e mutantes, backups de arquivos proprios e verificacao por
hash depois de interrupcao. `trap` nao cobre SIGKILL; reset global em workspace
compartilhado e proibido. Restricoes Flatpak sao da rota observada, nao regra
universal de worktree. Verificar mounts e paths do executor atual.

Verificar se `.agents/skills` resolve como link para a arvore canonica; uma
copia rastreada mais antiga deixa agentes em instrucoes divergentes. Preservar
a arvore substituida antes de corrigir a ponte; nao sobrescrever skills
locais silenciosamente. O guard deve confirmar a ponte depois da correcao.

Auditoria de recursos da ROM deve descobrir `.res` apenas na pasta ativa
`res/`; copias em `rascunho/` sao material de estudo e nao podem virar
duplicatas da ROM. No Mugenesis, a busca recursiva anterior trouxe 11 arquivos
e 484 issues falsos; a rota corrigida trouxe 3 `.res`, 161 declaracoes validas
e 1 aviso real de tile carregado por codigo. `-ResPath` continua disponivel
para auditar um rascunho explicitamente. Link relativo de `.agents/skills`
resolve em relacao ao diretorio do link; validador que usa o cwd do projeto
acusa `target_mismatch` falso.

Aprendizado herdado de template fica identificado por origem, sem virar fato
local. Ledger presente e schema valido nao provam que suas licoes pertencem ao
projeto. A curadoria usa IDs/fontes explicitos; nao promove48 entradas em bloco.
Gate semantico de screenshot precisa contexto: nao inventar cenario so para
passar edge density em demo sem palco. Isso nao aprova arte final de jogo.

O frontend MUGEN pode informar outro backend; limites, controles, som e provas
sao da plataforma destino. Nenhuma paleta, DMA, overflow ou evidencia MD
e automaticamente aplicavel ao SMS. Prompts de continuidade ficam em
`doc/prompts_modelo/prompt_mugen_sgdk_completion_2026_09_25.md` e
`doc/prompts_modelo/prompt_mugen_sms_port_2026_09_25.md`.

## Escolha de rota e custo de entrega (2026-09-26)

Aplicar [guia de custo e qualidade](mugen_cost_quality_decisions.md): alternativas
exploradas sao opcionais; diagnosticar recursos atuais e integrar cedo.

## Diagnostico Suzaku (2026-09-27)

[Caso e limites de evidencia](mugen_suzaku_vram_diagnostic_2026_09_27.md).
A curadoria incorporou o metodo nos owners de budget VDP, composicao de
planos, triagem de producao e evidencia de emulador. Capacidade de streaming,
fidelidade do piso, qualidade visual, FPS e entrega do jogo seguem pendentes.
