# Changelog de aprendizado - 2026-08-25

Status: `doctrine_canonized_and_drift_cured`

## Secao 38 — Capacidade declarada com prova (doutrina anti-autoengano)

- criada secao `SGDK_GLOBAL.md` §38: sonda real obrigatoria antes de qualquer
  promessa de capacidade; vocabulario de tres estados
  (`capaz_com_prova_agora`, `capaz_apos_preparo_medido`, `nao_capaz_neste_host`);
  proibido claim por memoria, fama do modelo ou suposicao;
- motivacao: modelos anteriores prometiam geracao visual sem canal nenhum e
  skills canonicas citavam artefatos inexistentes em disco.

## Arvore de 3 ramos no roteamento visual

- `image-generation-routing` agora abre com a arvore obrigatoria:
  **Ramo A** nativo com prova -> gerar; **Ramo B** host preparado -> circuito
  local; **Ramo C** nem agente nem host -> emitir diretriz de sucessor;
- campos novos na decisao: `agent_native_probe_attempted`,
  `host_readiness_probed`, `capability_state`, `outcome_branch`,
  `successor_directive_emitted`;
- bloqueio morto sem diretriz virou anti-padrao.

## Diretriz para Modelo Sucessor (Ramo C como entrega)

- schema canonico: `tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json`;
- template operacional:
  `tools/sgdk_wrapper/.agent/references/successor_asset_directive_template.md`.

## Drift curado (5 achados reais do validador novo)

- `validate_skill_framework.py` ganhou `check_skill_path_references`: so marca
  referencias ancoradas (`tools/...`, `.agent/...`) sem wildcard/placeholder;
  calibrado contra a arvore inteira antes de publicar (licao da secao 37);
- criados os schemas que a skill declarava canonicos e nao existiam:
  `capability_report.schema.json`,
  `generation_channel_decision.schema.json`,
  `asset_lineage_record.schema.json`,
  `prompt_pack_manifest.schema.json`,
  `bonsai_license_ack.schema.json`,
  `bonsai_session.schema.json`,
  `master_style_manifest_lookup.schema.json`
  (em `tools/ai_imagegen/reports/schema/`);
- corrigido path errado no tdd-authoring
  (`.agent/architecture/...` -> `.agent/skills/architecture/...`);
- `imagegen_tool.py` ganhou subcomando `self-check` (secao 34): valida manifest,
  profiles, schemas e skill dona; PASS confirmado.

## Prova viva da arvore neste host (2026-08-25)

- sondas reais executadas: nativo ausente; host AMD VanGogh sem VRAM dedicada,
  2.8GB RAM livres (<4GB minimo cpu_fallback), ComfyUI e modelos ausentes ->
  `selected_source: blocked`;
- desfecho honesto: `nao_capaz_neste_host`, Ramo C;
- artefatos emitidos e schema-validos:
  - `out/logs/generation_channel_decision.json` (`outcome_branch=C_successor_directive`);
  - `out/logs/successor_asset_directive_2026-08-25.json` apontando para a spec
    real do GOTHAM_OVERDRIVE (`doc/spec_assets_dark_deco.md`, 11 assets);
  - `out/logs/tooling_capability_report.json`.
- nenhum claim de imagem gerada; nenhuma tecnica promovida a MESTRE.

## Protocolo de insatisfacao mensuravel (prompt magico do Ramo C)

- novo bloco opcional `successor_quality_protocol` no schema
  `successor_asset_directive.schema.json`: o modelo sucessor NAO aceita
  primeira versao e NAO julga por sensacao;
- `iteration_policy`: min_rounds=3 mesmo se "pareceu bom"; apos max rounds sem
  passar, lacuna declarada honestamente (§38) — rebaixar piso e proibido;
- `numeric_floors` com ferramenta de medicao por piso: luma >=34
  (`audit_luma_floor.py`), paleta 9-bit exata, silhueta B/N no tamanho alvo,
  grid 8px/index 0, dithering funcional;
- `rejection_triggers`: reprova automatica (gradiente continuo, canal fora dos
  8 valores, downscale detectado, contorno <1px, fundo brigando com silhueta);
- `blind_critic_floor` default **8.5/10** (Kirby tirou 5.8 sem este protocolo);
  endurecer por projeto e livre, amolecer exige aprovacao humana registrada;
- `final_judgment` ancorado em gates imparciais — auto-satisfacao do gerador
  nunca e anchor de aceitacao (§36: adjetivo sem piso e defeito; §38: sensacao
  nao decide);
- prompt magico canonico literal adicionado ao template markdown;
- Ramo C na skill passa a exigir o protocolo; diretriz ja emitida hoje foi
  regenerada com o protocolo populado para os assets dark deco (schema valido).
