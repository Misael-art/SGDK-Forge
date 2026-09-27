# MUGEN para SGDK: custo e qualidade

Curadoria solicitada em 2026-09-26. Guia de diagnostico, nao aprovacao de arte/ROM.
O catalogo oficial do Mega Drive e piso de ambicao, nao teto de engenharia.
Os limites fisicos continuam reais; os defaults do SDK nao sao uma particao
obrigatoria de recursos para toda cena.

## Roteiro curto

1. Confronte fonte e captura atual; descreva a diferenca observavel.
2. Conte recursos COMPILADOS por estado: corpo, FX, HUD, retrato, mapas e pool.
   Nao perpetue uma estimativa antiga contra codigo que ja mudou.
3. Escolha uma hipotese causal, rollback e prova curta. Preserve a fonte antes
   de redesenhar; coordenadas erradas de layers nao se resolvem com panorama novo.
4. Integre cedo stage + jogadores + HUD. Arte isolada nao prova coexistencia.
5. Compile, observe BlastEm e teste o evento que empresta/devolve recursos.
6. Pare a exploracao quando o requisito estiver comprovado. Reabra por defeito
   ou novo requisito; nunca exija repetir todo o historico de experimentos.

Custo inclui tempo do agente, ferramentas, retrabalho, memoria, CPU/DMA,
manutencao e perda visual. Menos tiles com imagem pior nao significa menor custo.
Experimentos sao repertorio OPCIONAL, nao etapas obrigatorias.

## Alternativas condicionais

| Alternativa | Precondicao | Prova e limite |
|---|---|---|
| Mesclar indices iguais | Igualdade em todas as variantes | Mascara/pixels iguais; slot livre explicito, nao RGB preto |
| Frame-fonte integrado | Falta prova de coexistencia | Fidelidade e budget; declarar camera/parallax ausentes |
| Repartir sprite pool | Reserva nominal excessiva | Picos, fragmentacao e falhas em combate pesado |
| Font/gaps de VRAM | Fonte nao usada e mapas fixos | Intervalos disjuntos, remap e reset; layout especifico |
| A/WINDOW compartilhados | Ambos UI fixa compativel | Scroll zero e regioes distintas; nao serve para BG_A de cenario |
| Streaming/loan de super | Residencia excede budget | VBlank, lifetime, restauracao e continuidade visual |
| Redesenhar FX | Remap destrutivo demonstrado | Piloto pequeno: mascara, pivots, timing, variantes e paleta |
| Cores do HUD para FX | Slots imutaveis correlatos | Loan explicito; variantes e flash sem contaminar HUD |
| Sombras/FX alternados | Degradacao aceita e falta medida | Ganho real e legibilidade; nunca alterar colisao/dano ou mascarar overflow |

## Armadilhas

- Definicao de personagem igual NAO permite compartilhar tiles animados P1/P2:
  quadros diferentes sobrescrevem o mesmo destino. Retrato imutavel e outro caso.
- WINDOW substitui BG_A na sua area. Code0 revela BG_B, nao BG_A escondido.
  Nao remover o ceu inteiro pela altura geometrica do HUD.
- Menor maior bloco livre na janela nao e o maior bloco possivel nem garantia
  de contiguidade numa arena menor.
- Compressao de ROM nao reduz tiles residentes. Recolor identico pode mudar
  deduplicacao/DMA; performance continua precisando medicao.
- Screenshot comprova um quadro; titulo60fps nao aprova cadencia, audio ou jogo.

## Handoff

Entregar SHA, ROM, captura, testes, escopo observado e defeitos restantes.
Separar regra comprovada, opcao condicional e experimento rejeitado.
Novo layout integrado do Mugenesis e evidencia local em desenvolvimento;
nao constitui layout universal nem aprovacao de desempenho.
