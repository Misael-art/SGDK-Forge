# TAINA hybrid cleanup — decisão humana

`decision=approve_hybrid_cleanup_shootout`

`scale=56x80`

## Gate

Escolher uma candidata somente se rosto/olho, guarda diagonal, cabelo assimétrico, top/abdômen, wraps, sash, pernas e pés continuarem legíveis em 1×. Comparar perdas de contorno, halos e separação de materiais; não somar score.

Respostas aceitas:

```text
decision=approve_hybrid_cleanup_candidate
asset_id=<id exato>
sha256=<SHA exato>
scale=56x80
```

ou:

```text
decision=reject_hybrid_cleanup_shootout
reason=<motivo observável>
```

Esta decisão não libera `res/`, animação, runtime, ROM, `visual_pass` ou AAA.
