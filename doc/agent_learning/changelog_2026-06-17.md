# Changelog de Curadoria Canonica - 2026-06-17

## Enforcement de progresso e evidencia

- Historico de loop passou a usar `build_meta.json`.
- Dois ciclos sem progresso exigem intencao explicita; tres exigem decisao
  estrategica.
- Evidencia de emulador agora e selada contra o hash da ROM e dos artefatos.
- Rebuild posterior ou artefato ausente invalida o selo.
- Learning candidates conhecidos sao deduplicados contra owners existentes.

Validacao: regressões operacionais passed; learning loop `33/33`; ambiente do
agente `ready`. Nenhuma ROM, asset ou claim AAA foi promovido.
