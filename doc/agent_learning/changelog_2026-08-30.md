# Changelog de curadoria — 2026-08-30

## Lacuna tratada

O agente canônico conseguia gerar fontes visualmente promissoras e converter
PNGs, mas não mantinha uma fronteira operacional entre fonte, probe de escala,
autoria nativa e asset de runtime. Isso permitia regressão estética mesmo com
relatórios técnicos verdes.

## Mudanças canônicas

- nova skill `art/native-sprite-production`
- novo workflow `native-sprite-production-loop.md`
- protocolo de geração, autoria nativa e escala
- schema `native_sprite_production_record.schema.json`
- validador adversarial `validate_native_sprite_production.py`
- evidência visual rederivada do candidato e aprovação humana ancorada no hash
- integração no framework manifest, lifecycle registry, pipeline AAA e meta-gate
- harness de lifecycle portável entre `powershell.exe` e `pwsh`
- nova causa `scale_density_mismatch` no loop de persistência
- remoção da rota documental depreciada baseada em
  `batch_resize_index.py`/`fix_png_transparency_final.py`

## Decisões

- qualidade visual não é inferida de conformidade técnica
- `forge-art convert` não é autor semântico de sprite
- uma saída convertida pode ser adotada como `assisted_native_translation`
  somente após gates independentes; isso preserva a rota prática sem falso verde
- scale probe é sempre não promovível
- escala travada não muda por conveniência do produtor
- operação determinística é CLI/headless; GUI por ponteiro é canal incompatível
- falha estética provoca iteração causal, não pedido para o humano fabricar o PNG

## Evidência esperada

- validador de produção nativa: `12/12`
- loop causal adversarial: `10/10`
- validação estrutural da nova skill: `passed`
- lifecycle registry: `passed`, hashed e reversível
- forge-art: `107/107`
- art pipeline: `116/116`
- auditor isolado da nova ferramenta: `1/1`, `verdict=OK`
- meta-gate global: 14/14 self-checks passam, `verdict=BLOCKED` pelas 18 cópias
  stale preexistentes de `runtime_probe` em nove projetos

## Teto de claim

Esta curadoria pode provar que o processo bloqueia falsos verdes conhecidos.
Ela não prova que uma arte específica é excelente, que uma ROM está correta ou
que qualquer projeto está `ready_for_aaa`.
