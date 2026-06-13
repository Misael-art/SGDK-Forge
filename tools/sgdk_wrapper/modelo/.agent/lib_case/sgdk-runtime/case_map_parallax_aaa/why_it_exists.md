# Why It Exists

Agentes estavam prometendo cenarios "monumentais" com parallax, agua, pseudo-3D ou profundidade infinita sem declarar owner, custo e fallback.

Este caso fixa o aprendizado:

- Mega Drive tem BG_A, BG_B e WINDOW. Profundidade extra nasce de composicao e scroll por linha, nao de planos novos.
- Line scroll precisa de owner unico e reset ao sair.
- Parallax monumental precisa de funcao de gameplay ou narrativa; se for so decoracao, o status correto e `decorative_only_blocked`.
- O budget deve separar estimativa, compilado e emulador. Sem BlastEm, a medicao continua pendente.

