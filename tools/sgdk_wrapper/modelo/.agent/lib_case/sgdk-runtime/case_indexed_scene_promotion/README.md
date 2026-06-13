# Case: Indexed Scene Promotion

Caso minimo para lembrar que uma cena correta em review humano ainda pode falhar na promocao para ROM se o recurso SGDK e o custo estrutural nao forem auditados junto com a triagem de representacao indexada.

Estado reconciliado da evidencia:

- este caso fixa com seguranca a necessidade de auditar a politica de `IMAGE` na promocao de cenas grandes para ROM
- este caso usa a transparencia indexada como etapa obrigatoria de triagem quando houver alpha estrutural esperado, mas nao a promove sozinho a causa raiz final
- qualquer aprendizado sobre `resources.d` deve ficar em trilha de pipeline separada ate existir evidência auditavel propria
