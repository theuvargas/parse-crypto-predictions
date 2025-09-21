# Decisões tomadas

## Assumptions

Precisei presumir algumas coisas para poder executar esse trabalho:

1. Não foi dado nenhum dataset anotado. Supus que teria que anotar o dataset manualmente, e utilizei o gemini-2.5-pro para fazer isso, e depois revisei tudo e alterei o que julguei necessário.
2. São pedidos batch sizes diferentes. Considerei que um batch size de 16, por exemplo, seria a concatenação de 16 posts em um único prompt. Dessa forma, o modelo teria que classificar todos esses posts 'ao mesmo tempo'.

## Melhorias possíveis

1. Não validei as criptomoedas extraídas pelo modelo, basta ser uma string. Pelo que pesquisei, não há uma padronização existente. Uma melhoria seria guardar localmente uma lista com as moedas mais populares, e validar contra essa lista. Se não estiver na lista, talvez utilizar alguma API para verificar.
2. Uma boa tool para o agente seria a de preço de moeda. Com isso, seria mais fácil realizar a análise de sentimento, já que assim o modelo saberia se um preço previsto é muito otimista ou não. Isso não foi implementado pois envolveria a utilização de mais uma API.
