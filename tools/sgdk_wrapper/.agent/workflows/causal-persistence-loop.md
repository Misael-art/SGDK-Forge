# Workflow: Causal Persistence Loop

Use quando o usuario exigir continuidade ate a entrega, quando um blocker se
repetir ou quando uma unica ferramenta falhar e o agente estiver prestes a
parar. Este workflow coordena rotas; as skills continuam donas da execucao.

## Regra central

Trabalhe sobre o blocker folha que mais limita o claim ativo. Execute uma
hipotese verificavel por vez, meca o resultado e registre o delta. Falha de uma
ferramenta nao e blocker do projeto enquanto existir rota segura equivalente.

## Ciclo

1. Selecione um blocker folha dentro do escopo autorizado.
2. Registre `rota`, `hipotese`, `evidencia_antes` e resultado esperado.
3. Execute uma acao reversivel e proporcional ao risco.
4. Meça com a ferramenta dona do gate; intencao e texto nao contam como delta.
5. Se passou, sincronize memoria/changelog aplicaveis e avance.
6. Se falhou, classifique a causa e mude algo causal antes de tentar novamente.

Classificacoes minimas:

- `implementation_failure`
- `tool_capability_failure`
- `interaction_channel_mismatch`
- `representation_mismatch`
- `scale_density_mismatch`
- `environment_failure`
- `contract_or_spec_conflict`
- `human_decision_required`

## Limites de repeticao

- Duas tentativas equivalentes sem evidencia nova encerram a rota, nao o
  projeto.
- Nova tentativa precisa mudar ferramenta, representacao, hipotese ou entrada
  de forma registrada.
- Build, screenshot, refresh de report ou documento novo com
  `blockers_removed=0` nao e progresso causal.
- Nunca reduza teste, budget, schema, gate visual ou claim para fabricar verde.

## Roteamento de imagem CLI-first

Quando uma operacao deterministica estiver sendo feita por screenshots,
ponteiro ou GUI, classifique `interaction_channel_mismatch` e interrompa essa
rota.

Ordem:

1. `forge-art` para cor VDP, indexacao e contrato pixel;
2. Pillow/ImageMagick para crop, resize NEAREST e composicao mecanica;
3. GIMP batch somente para operacao GIMP/GEGL registrada, depois de
   `forge-art gimp-batch-preflight`;
4. produtor visual capaz ou gate humano quando a decisao for semantica.

GIMP GUI e ferramenta humana opcional. Automacao de ponteiro nao e rota de
producao. GIMP batch nao vira oraculo de cor, nao aceita script gerado
arbitrariamente e escreve somente no staging da operacao curada.

## Escala e densidade de sprite

Quando o PNG passa tecnicamente, mas rosto, maos, pes, guarda ou feature
assinatura nao sobrevivem em 1x, classifique `scale_density_mismatch`.

- escala `locked`: reautorizar clusters no grid travado; probe maior e apenas
  evidencia nao promovivel
- escala `provisional`: comparar no maximo tres caixas com a mesma pose e medir
  camera, hitbox, workload, metasprite, tiles e pior scanline
- troca que altera FOV, gameplay ou budget: abrir gate humano somente depois da
  comparacao medida

Quantizar novamente a mesma fonte, operar GUI por ponteiro ou promover a probe
maior nao sao mudancas causais validas.

## Gate humano sem paralisar o projeto

Registre a decisao exata, as opcoes e o artefato que depende dela. Continue
apenas ramos cuja validade nao possa ser alterada pela resposta. Nao anime um
personagem antes da aprovacao de sua silhueta; pode continuar uma fixture de
ferramenta ou outro ramo realmente independente.

Quando o usuario pedir explicitamente producao continua/forward-test sem gates
intermediarios, aplique
`skills/art/sprite-animation/references/uninterrupted-forward-production-policy.md`.
Nesse modo, a revisao humana continua pendente e nao e simulada, mas candidatos,
rework e prototipos downstream reversiveis podem continuar em staging como
`agent_curated_diagnostic_review`/`speculative_downstream`. Isso nunca autoriza
`res/`, runtime ou elevacao de claim.

## Persistencia entre sessoes

Ao encerrar um ciclo relevante, registre no `doc/10-memory-bank.md`:

- claim ativo e blocker folha;
- ultima rota e evidencia;
- delta obtido ou causa da falha;
- rotas encerradas e motivo;
- proxima acao causal;
- gate humano pendente e ramos independentes, quando houver.

Resultado de ciclo pode ser espelhado em `doc/active_iteration.json` (estado
auxiliar machine-readable ancorado no hash do memory bank). Valide com
`validate_active_iteration.ps1`; hash divergente vira `stale_anchor` e e
report (nao bloqueante). O espelho nunca substitui o memory bank, contratos,
validators ou evidencia de emulador.

## Parada legitima

Pare e reporte somente quando ocorrer um destes casos:

- acao destrutiva, externa, cara ou expansao material sem autorizacao;
- credencial, licenca ou fonte obrigatoria ausente;
- contradicao entre autoridades que muda materialmente o resultado;
- decisao humana irredutivel sem ramo independente seguro;
- impossibilidade de hardware medida cujo fallback muda o produto;
- todas as rotas seguras foram esgotadas com evidencia.

O reporte deve nomear blocker, tentativas distintas, evidencias, limite de
claim e menor proxima acao que realmente desbloqueia o trabalho.
