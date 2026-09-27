# Curadoria aplicada: conversao MUGEN e efeitos SGDK

Data: 2026-09-24. Autorizacao: pedido humano de curadoria do agente canonico.
Escopo: instrucoes de conversao, testes e handoff; nao certificacao audiovisual.
Caso observado: Mugenesis_Demo, checkout `7cf00ed8`; PR21 ainda aberta em
`f3b92bb919ab2fd5a01f7a656d0893d1a0e7a2f9`. Nao presumir que uma branch
contenha a outra. HAMOOPIG e outro projeto; nao transportar hashes entre eles.

## 1. Oraculo antes do medidor

Uma ferramenta que valida o proprio resultado pode conservar o mesmo erro.
Validar decodificacao com palavras VDP conhecidas, oito niveis distintos por
canal e round-trip das 512 cores. Testar contraexemplos e a reintroducao do bug.
No conversor MUGEN, `vdp_rgb` representa os niveis por multiplos de 36: branco
252, nao 109. Essa convencao digital nao e uma curva universal de monitor/CRT
e nao substitui o oraculo `forge_art/vdp_color.py` de outra rota de conversao.
Delta E exige convencao de cor, metodo e referencia registrados; e estimativa
de diferenca, nao aprovacao artistica.

Separar indices reservados, indices usados, classes exatas em TODAS as variantes
e aproximacao perceptiva. Waiver registra excecao; nao converte falha em sucesso.
Evidencia: `tools/mugen2sgdk_forge/tests/test_palette_contract.py`.

## 2. Recuperar slots sem sacrificar arte

Fundir indices apenas quando equivalentes em todas as variantes relevantes.
Comparar dimensoes, mascara e cores pixel a pixel, incluindo retratos. Registrar
slots livres explicitamente: preto `0x000` nao significa slot vazio. Auditar
consumidores secundarios, como escolha da cor da sombra. Identidade de pixels
nao prova identidade de packing, DMA, residencia ou tempo de frame.
Evidencia: `tools/mugen2sgdk_forge/tests/test_palette_merge.py`.

## 3. Contrato realizavel para o artista

O contrato local de Ken reserva 8 slots estaveis + 6 de roupa + 1 de FX;
indice 0 transparente. E uma decisao deste projeto, nao lei para todo jogo.
O slot de FX deve atender o catalogo completo, nao apenas a primeira familia.
Catalogar por identidade semantica MUGEN, inclusive familias em varias sheets.
Comparar fonte original e conversao atual; uma conversao defeituosa nao vira
referencia artistica. Manter preto visivel opaco e mascara derivada do indice
transparente da fonte, nunca de uma cor RGB presumida.

Brief e contrato devem derivar dos mesmos numeros. Separar teto autoral,
estimativa offline e custo compilado/medido. O piloto hadouken tem 8 elementos
AIR, incluindo 3 vazios intencionais, teto de 26 tiles e 2 sprites de hardware
por frame. Preservar tempos, pivots e vazios; nao generalizar esse flicker como
solucao para overflow. Geracao de imagem produz candidato; indexacao valida
nao comprova qualidade, movimento ou integracao em ROM.

FX podem ser sprites separados e compartilhar a linha do lutador quando o
contrato assim determinar. Separacao de asset nao exige outra linha de CRAM.
Trocar uma linha afeta todos os consumidores dos indices alterados, inclusive
projeteis: isolamento precisa ser projetado e testado apos a migracao.
Evidencia: testes do piloto em `tests/test_palette_merge.py` e pacote
`doc/mugen/fx_pilot_hadouken/` do projeto.

## 4. Fonte de DMA enfileirado tem vida util

Para `DMA_QUEUE`, manter buffer valido e com conteudo correto ate o consumo no
VBlank. Nao enfileirar ponteiro para variavel local que sai de escopo. Buffer
persistente tambem falha se for sobrescrito antes do consumo. Verificar API no
header; `DMA_QUEUE_COPY` tem semantica e custo diferentes, nao e troca gratuita.
Testes host devem atrasar o consumo, conferir cores exatas e exercitar hitstop,
hits consecutivos, superpause, KO, reset e limites das linhas de paleta.
Mutantes devem demonstrar sensibilidade ao bug; host nao mede custo no 68000.
Evidencia: `sdk/sgdk-2.11/inc/dma.h`, `tests/host/genesis.h` e
`tests/test_host_runtime.py` em `tools/mugen2sgdk_forge/`.

## 5. Reconversao preserva decisoes humanas

Separar dados regeneraveis de anotacoes humanas persistentes. Preservar notas,
restricoes e historico de recursos removidos. Vincular aprovacao ao SHA-256 do
asset; mudanca invalida sua aplicabilidade atual, sem apagar a decisao antiga.
Testar reconversao em copia, migracao de notas antigas e segunda execucao
identica byte a byte. Nao editar apenas derivado que sera sobrescrito.

Essa regra preventiva esta incorporada ao canon. Sua implementacao na PR21 foi
inspecionada separadamente; nao esta integrada ao checkout da etapa 3 e nao foi
executada nesta curadoria. Antes de reconverter, verificar integracao e executar
seus quatro testes em `tests/test_provenance_preserve.py`.

## 6. Evidencia proporcional e continuidade

Comparar ROMs sobre mesmos inputs, estado, janela, warmup, regiao e configuracao
de audio/captura. Registrar hash completo e contagem numerador/denominador.
70/1200 frames acima do budget nao sustenta 60 fps constantes; tampouco mede,
sozinho, a taxa de apresentacao do video. Dois frames de diferenca isolados nao
provam causalidade nem equivalencia de desempenho.

Sob pressao de memoria, executar uma captura por vez apos preflight; nao adotar
1 GiB como limiar universal, matar aplicativos do usuario ou repetir batches
que ja falharam. Preservar falhas e checkpoint, continuar trabalho independente.
Capturas curtas podem provar um evento, nao estabilidade prolongada ou audio.
PR22 permanece sem validacao de budget/visual ate completar a matriz de ROMs.

## Limites desta promocao

Foram promovidas instrucoes de processo com evidencia de codigo/testes. Nao
foram aprovados o piloto artistico, Suzaku, migracao completa de paleta,
isolamento de projetil, Stage 3 em emulador, 60 fps constantes ou qualidade AAA.
Ver parecer e verificacoes em `doc/curation/2026_09_24_canonical/`.
