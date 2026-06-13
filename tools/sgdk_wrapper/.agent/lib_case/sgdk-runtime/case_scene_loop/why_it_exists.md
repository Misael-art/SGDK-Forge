# Why It Exists

Este caso existe para travar dois fatos:

- `SYS_doVBlankProcess()` fecha o frame no loop principal
- inverter a ordem do loop gera lag, OAM inconsistente ou contrato quebrado
