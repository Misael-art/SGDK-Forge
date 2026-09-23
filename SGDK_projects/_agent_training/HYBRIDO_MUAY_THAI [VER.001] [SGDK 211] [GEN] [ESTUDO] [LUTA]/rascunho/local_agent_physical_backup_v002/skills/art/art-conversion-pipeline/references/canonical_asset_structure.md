# Canonical Asset Structure

Use esta estrutura para projetos SGDK que produzam assets AAA. Ela separa fonte, trabalho, debug e runtime para impedir que um fallback visual vire entrega final.

## Diretorios canonicos

```text
data/source_art/
  premium_source_manifest.json
  *.png, *.psd, *.aseprite ou fonte visual premium aceita

data/raw_ai/
  saidas brutas de geracao por IA
  nunca entra em res/ diretamente

data/working/
  recortes, limpeza, paleta manual, slicing, previews e ajustes intermediarios

data/processed/
  candidatos convertidos/indexados apos curadoria

data/debug_lab/
  local_author_pixel_rasterization, procedural_renderer, controles e placeholders
  nunca e fonte final AAA

res/
  apenas assets aprovados para runtime e declarados em resources.res

out/
  logs, relatorios, capturas, ROMs, evidencia de emulador e auditorias

doc/
  GDD, specs, memoria, source cases, relatarios de gate e changelog
```

## Regras de promocao

- `data/raw_ai/` vira fonte somente depois de curadoria e persistencia em `data/source_art/`.
- `data/debug_lab/` nunca promove asset critico para `res/`.
- `data/processed/` so promove para `res/` com lineage, spec/builder, paleta/indexacao validada, `source_validity=true`, `authoriality_gate=passed`, `clone_risk_score` dentro do limite declarado quando autoral, gate visual aplicavel e `elite_ready=true`.
- Benchmark tecnico nunca entra em `data/source_art/` nem vira origem visual; `benchmark_similarity_index` acima do limite declarado pelo `benchmark_profile` bloqueia promocao de asset critico.
- `needs_review`, `placeholder`, `debug_lab`, `benchmark-derived`, `rework` ou `perceptual_quality=nao_medido` bloqueiam promocao de asset critico para `res/`.
- Se o arquivo for laboratorio, declarar `lab_not_delivery=true` e manter fora de delivery.
- Sprite heroico com gi branco ou tecido claro precisa de `white_material_palette_contract`; `PALETTE_WASTE` bloqueia promocao visual.
- Sprite animado de personagem precisa de `sprite_artifact_report` por strip ou por lote antes de entrar em `res/`; clipping de celula, matte nao transparente, index 0 incorreto, ilhas soltas de debris, componente desconectado grande, escala inconsistente ou FX embutido bloqueiam promocao.
- Personagem grande precisa de `slicing_cell_contract` por estado: celula derivada de `max_bbox + padding` ou celula fixa justificada com motivo tecnico, dimensoes em tiles, ground line, pivot e margem livre minima. Hardcode opaco no builder nao e contrato.
- `res/` deve conter somente o que a ROM usa de fato.
- `resources.res` deve apontar para os assets aprovados, nao para copias soltas ou controles de laboratorio.

## Scripts locais

Scripts especificos do projeto podem existir apenas quando forem:

- adaptadores finos para chamar o wrapper central
- probes de diagnostico do proprio projeto
- laboratorios em `data/debug_lab/`

Logica de build, captura, validacao, promocao generica de assets, automacao BlastEm ou regras compartilhadas deve morar em `tools/sgdk_wrapper/` ou `tools/image-tools/`.

Se um projeto tiver muitos `.md`, `.png`, `.json` ou scripts soltos na raiz, classifique como `legacy_scattered_artifacts` e nao use esses arquivos como fonte canonica sem reancorar em `doc/`, `data/source_art/`, `data/processed/`, `res/` ou `out/`.
