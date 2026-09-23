# AAA Pipeline Guardian Workflow

Status: `workflow_candidate`

Use este workflow quando o prompt ou entrega alegar AAA, release, tecnica
avancada de Mega Drive, port/conversao complexa ou `ready_for_aaa`.

## 1. Extrair claims

Antes de criar assets, codigo ou relatorio final, liste claims do pedido:

- qualidade visual final;
- sprite sheet, animacao, personagem ou boss;
- stage com camera/parallax;
- colisao avancada;
- streaming/VRAM/DMA;
- Shadow/Highlight, H-Int, scroll FX ou palette cycling;
- catalogo de entidades;
- transicao de estado;
- audio/Z80/PCM;
- port ou conversao high-colour.

## 2. Chamar `aaa-pipeline-guardian`

Produza `aaa_pipeline_gate_report` com:

- `claims`;
- `required_skill_invocations`;
- `claim_to_gate_matrix`;
- `missing_artifacts`;
- `blocked_claims`;
- `ready_for_aaa_decision`.

Se o relatorio bloquear um claim, o agente pode continuar trabalhando, mas nao
pode declarar `ready_for_aaa`, `elite_ready`, `release` ou sucesso final daquele
claim.

## 3. Invocar skills especialistas

Use a matriz do guardiao:

- `collision-system-architect` para colisao multi-ponto/semi-solida;
- `vram-streaming-dma-queue` para streaming, dirty tiles e tile animation;
- `shadow-highlight-scroll-fx` para H-Int, Shadow/Highlight e scroll FX;
- `entity-polymorphism-architect` para catalogo de entidades;
- `game-state-transition-architect` para fade/flush/teardown;
- skills de arte, budget, audio e runtime ja existentes conforme o claim.

## 4. Produzir artefatos antes do status final

Cada skill acionada precisa produzir seu contrato ou report. Ausencia de
artefato e blocker, nao detalhe de documentacao.

Exemplos minimos ficam em:

`tools/sgdk_wrapper/doc/05_technical/examples/`

## 5. Fechar com evidencia

O status final deve ser o menor status comprovado:

- sem contrato: `conceptual_reference`;
- contrato sem execucao: `pipeline_update_candidate`;
- estudo sem prova runtime: `lab_candidate`;
- patch sem runner/teste: `candidate_applied_not_verified`;
- runtime sem prova visual completa: `runtime_candidate`;
- todos os gates frescos: `ready_for_aaa`.

## 6. Validar

Antes de commit da curadoria:

```powershell
tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Antes de fechar projeto real, rode tambem os validadores especificos do projeto
e do wrapper.
