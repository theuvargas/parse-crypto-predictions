# parse-crypto-predictions

Coleta, armazena e avalia predições estruturadas geradas por um agente LLM sobre posts de criptomoedas.

## Visão Geral

- **API FastAPI** (`src/main.py`) expõe dois endpoints (`/parse_prediction` e `/parse_prediction_batch`) que recebem texto natural e retornam um objeto estruturado (`ParsedPredictionResponse`).
- **Pipeline de parsing** (`src/agent.py`) orquestra chamadas ao modelo Gemini 2.5 Flash via `pydantic-ai`, aplicando prompts e `thinking_budget` customizados para requisições unitárias e em lote.
- **Banco DuckDB** (`crypto_predictions.db`) guarda o histórico de respostas do modelo (tabela `prediction_results`) e estatísticas de uso (tabela `token_usage`). A inicialização e logging ficam em `src/database.py`.
- **Dataset anotado** (`data/annotated-dataset.json`) oferece ground truth para avaliação; cada entrada possui `id`, `target_type`, `extracted_value`, `timeframe`, `bear_bull`, notas e metadados do post.
- **Scripts utilitários** em `scripts/` permitem gerar execuções, calcular métricas e emitir relatórios de custo.

## Pré-requisitos

1. Instale dependências com [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```
2. Crie um arquivo `.env` e adicione uma chave de API do Gemini (`GOOGLE_API_KEY`). É possível gerar uma chave em https://aistudio.google.com/

## Executando a API

```bash
uv run python -m src.main
```

Endpoints disponíveis:
- `POST /parse_prediction` — processa um único post.
- `POST /parse_prediction_batch` — aceita um corpo `{ "items": [...] }` com até 16 posts.

Exemplo de chamada:

```bash
curl -X POST http://localhost:8000/parse_prediction \
  -H "Content-Type: application/json" \
  -d '{
        "post_text": "BTC breaking $80k before end of year!",
        "post_created_at": "2025-08-25T12:00:00Z"
      }'

Alternativamente, visite http://localhost:8000/docs para testar os endpoints.
```

As respostas são instâncias JSON de `ParsedPredictionResponse` contendo `target_type`, `extracted_value`, `timeframe`, `bear_bull` e `notes`.

## Geração de Predições

Para preencher o banco com novos resultados do modelo, use o script de batching:

```bash
uv run python -m scripts.generate_predictions --batch-sizes 1 16
```

O script percorre o dataset anotado em lotes, chama a API configurada (local ou remota) e insere cada resposta em `prediction_results` junto com metadados (`run_id`, `example_id`, tamanho do lote). O progresso é retomável via `--run-id`.

## Avaliação

### Métricas de Qualidade

Recalcule métricas de acurácia, precisão, recall, F1, exact match (`timeframe` / `extracted_value`) e correlação de sentimento (`bear_bull`) — além das matrizes de confusão por `target_type` — executando:

```bash
uv run python -m scripts.calculate_metrics
```

### Relatório de Custos

Para obter médias e percentis (p50/p95) de latência e custos:

```bash
uv run python -m scripts.cost_report
```

## Relatórios

- **Performance e Custos:** `report/relatorio.md` resume métricas atuais e inclui as imagens das matrizes de confusão.
- **Matrizes de Confusão:** `report/confusion_matrix/batch-size-1.png` e `.../batch-size-16.png`.

## Estrutura Principal

```
.
├── data/annotated-dataset.json      # dataset anotado usado como ground truth
├── report/
│   ├── decisoes.md                  # justificativas para algumas decisões tomadas
│   ├── relatorio.md                 # resumo de métricas e custos
│   ├── tricky_cases.md              # casos difícies de parsing
│   └── confusion_matrix/            # figuras das matrizes de confusão
├── scripts/
│   ├── calculate_metrics.py         # cálculo de métricas de qualidade
│   ├── cost_report.py               # agregação de custos e latência
│   └── generate_predictions.py      # coleta de predições via API
└── src/
    ├── agent.py                     # pipeline de interação com o LLM
    ├── config.py                    # configuração de modelo e caminhos
    ├── database.py                  # inicialização e logging no DuckDB
    ├── main.py                      # entrypoint FastAPI
    └── models.py                    # esquemas Pydantic utilizados
```
