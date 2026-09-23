# Plano de provas QA — BLAZE_ENGINE

1. Rodar `preflight_host.ps1` e selecionar a rota Linux/Windows.
2. Rodar `select_sgdk_build_route.py` antes do primeiro build.
3. Executar metodologia, contexto, higiene e `validate_resources.ps1`.
4. Construir com o wrapper central usando o SDK `sdk/sgdk-2.11` do workspace.
5. Capturar boot e, quando possível, navegação até gameplay no BlastEm.
6. Registrar hash da ROM, `validation_report.json`, `runtime_metrics.json`, `visual_vdp_dump.bin`, `save.sram`, áudio e limitações.

O primeiro fechamento é técnico. `ready_for_aaa`, áudio aprovado, 60 fps sustentados e game feel só podem ser declarados após evidência própria para cada eixo.
