---
name: collision-system-architect
description: Use quando um projeto Mega Drive precisar de colisao multi-ponto, one-way, slopes, lanes, atores grandes ou separacao entre solid, hit, hurt e push boxes.
---

# Collision System Architect

Define topologia e ordem de resolucao antes do runtime.

## Contrato Operacional

### Entrada minima

- tipos de corpos e materiais
- sistema de coordenadas
- tilemap ou geometria colidivel
- regras de movimento, combate e camera

### Saida minima

- `collision_topology_report`
- tabela de probes
- politica one-way/slope/step
- manifestos hit/hurt/push quando houver combate
- fixtures e budget de pior caso

### Passa quando

- visual, solid, hit, hurt e push sao dominios distintos
- atores grandes usam probes suficientes
- one-way consulta posicao anterior e intencao de queda
- ordem X/Y e tolerancias estao declaradas
- fixtures cobrem cantos, teto, parede, queda, slope e knockback

### Handoff para proxima etapa

- entregar materiais e probes a `sgdk-runtime-coder`
- entregar custo por entidade a `megadrive-vdp-budget-analyst`
- entregar boxes de combate a `systems-mechanics-validator`

## Regras

- Resolver em world-space.
- Nao derivar solidez de cor/paleta.
- Pushbox nao reutiliza hurtbox sem justificativa.
- Buffers sao estaticos; sem heap no loop.

## Anti-padroes

- AABB unico para ator grande
- one-way por posicao atual apenas
- casos especiais sem tabela de materiais
- colisao em screen-space
