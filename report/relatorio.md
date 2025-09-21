# Relatório de Performance e Custos

Os dados abaixo são referentes são referentes à avaliação do agente de parsing criado.

## Métricas de Qualidade

| Métrica | Batch size 1 | Batch size 16 |
| --- | --- | --- |
| Acurácia (`target_type`) | 77,45% | 20,59% |
| Precisão (`target_type`) | 85,30% | 20.54% |
| Recall (`target_type`) | 77,79% | 20.50% |
| F1 (`target_type`) | 78,88% | 20.35% |
| `timeframe` (exact match) | 87,25% | 57.84% |
| `extracted_value` (exact match) | 76,47% | 7.84% |
| Spearman (`bear_bull`) | 0,91 | 0,11 |
| Sucesso | 100% | 100,0% |


### Matrizes de Confusão (`target_type`)

![Matriz de confusão — batch 1](confusion_matrix/batch-size-1.png)

![Matriz de confusão — batch 16](confusion_matrix/batch-size-16.png)


### Observações

- As métricas de exact match de `timeframe` e `extracted_value` medem a quantidade de vezes em que **todos** os campos dessas extrações são iguais às referências. Por exemplo, para o `timeframe` contar como um acerto, é preciso que `explicit`, `start` e `end` estejam corretos ao mesmo tempo.
- Se o modelo errar a classe, não é possível acertar o `extracted_value`
- O agente com batch_size=16 se saiu consideravelmente pior do que o com batch_size=1, o que era esperado. É muito mais difícil classificar 16 amostras ao mesmo tempo do que 1.
- Sucesso 100% quer dizer que o modelo não errou nenhuma vez o modelo (tipagem) de saída.

## Relatório de Custos

Valores de custo consideram o preço atual do modelo utilizado, o **gemini-2.5-flash** (USD 0,30/M tokens de entrada e USD 2,50/M tokens de saída).

| Métrica | Batch size 1 | Batch size 16 |
| --- | --- | --- |
| Lat. média (s) | 8,48 | 33,79 |
| Lat. p50 (s) | 3,61 | 31,99 |
| Lat. p95 (s) | 49,50 | 43,10 |
| Tokens entrada (média) | 4657,1 | 5784,7 |
| Tokens saída (média) | 495,2 | 5389,5 |
| Custo entrada média (USD) | 0,0014 | 0,0017 |
| Custo entrada p50 (USD) | 0,0014 | 0,0017 |
| Custo entrada p95 (USD) | 0,0014 | 0,0018 |
| Custo saída média (USD) | 0,0012 | 0,0135 |
| Custo saída p50 (USD) | 0,0013 | 0,0137 |
| Custo saída p95 (USD) | 0,0016 | 0,0140 |

### Observações

- A latência média alta pode ser explicada pelo rate limiting da API do Gemini. Eu estou usando uma chave gratuita, o que implica em limites maiores. Cada vez que eu era limitado, esperava 45 segundos para tentar de novo. Considere o p50 como uma métrica mais realista.
