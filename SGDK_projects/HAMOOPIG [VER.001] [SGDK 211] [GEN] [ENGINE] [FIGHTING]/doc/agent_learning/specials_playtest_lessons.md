# Lições do teste de especiais — 2026-09-13

1. O estado 700 não é uniforme entre o elenco: para Ryo (`id==1`) ele agenda
   `spr_ryo_701` no frame de animação 12; para Musgo a leitura correta é o golpe
   corporal. O teste precisa classificar o lutador antes de procurar projétil.
2. Cinco amostras de 75 ms eram curtas demais para capturar um evento disparado
   no frame 12. A janela foi ampliada para 24 quadros, mantendo a captura dentro
   da pasta de evidências e vinculada ao hash da ROM.
3. O comando deve ser exercitado antes e depois do reset; presença antes do KO
   não prova que o teardown restaurou sprites/projéteis. A captura de 2026-09-13
   confirmou barras restauradas e nova sequência de especiais após o reset.
4. A tira de screenshots é evidência de evento visual, não de orçamento VDP. Para
   concluir DMA/SAT ainda será necessário um probe ou dump vinculado à mesma ROM.

