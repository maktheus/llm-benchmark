# LLM Bench Backend

Este diretório contém o código inicial do serviço Backend responsável por orquestrar os benchmarks do projeto **LLM Bench**.

O Backend será construído em **FastAPI** e terá as seguintes responsabilidades principais:

- Expor uma API REST para disparar e consultar benchmarks.
- Registrar modelos, datasets e resultados no banco de dados.
- Disponibilizar métricas de hardware coletadas durante a execução.
- Servir como camada de comunicação com o Frontend.

## Rotas Iniciais

A API seguirá o prefixo `/api/v1` e incluirá os endpoints abaixo:

| Método | Rota                           | Descrição                                               |
|-------|--------------------------------|---------------------------------------------------------|
| `GET` | `/api/v1/health`               | Verifica se o serviço está ativo.                       |
| `POST`| `/api/v1/benchmarks`           | Inicia um benchmark com os parâmetros enviados.         |
| `GET` | `/api/v1/benchmarks/{job_id}`  | Consulta o resultado de um benchmark específico.        |
| `GET` | `/api/v1/benchmarks`           | Lista benchmarks cadastrados (filtros opcionais).       |
| `GET` | `/api/v1/benchmarks/{job_id}/metrics` | Retorna métricas de hardware do benchmark.      |
| `GET` | `/api/v1/models`               | Lista modelos disponíveis para teste.                   |
| `GET` | `/api/v1/datasets`             | Lista datasets registrados.                             |

### Parâmetros de Entrada (exemplo `/benchmarks`)

```json
{
  "model_id": "gpt2",
  "prompt": "Seu prompt aqui",
  "task": "text-generation",
  "max_tokens": 50,
  "temperature": 0.7,
  "top_p": 0.9,
  "use_gpu": true
}
```

### Resposta Esperada

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "model": "gpt2",
  "task": "text-generation",
  "duration": 1.23,
  "tokens_generated": 50,
  "output": "texto gerado",
  "hardware_metrics": {
    "cpu_usage_percent": 40.5,
    "ram_usage_gb": 3.2,
    "gpu_usage_percent": 70.1,
    "vram_usage_gb": 2.0
  }
}
```

## Estrutura Prevista

```
backend/
├── README.md        # Visão geral e documentação da API
├── main.py          # Aplicação FastAPI
└── __init__.py      # Torna o diretório um pacote Python
```

Este é apenas o início do Backend. Novas rotas e módulos serão adicionados conforme o desenvolvimento do projeto.

## Como executar

1. Instale as dependências do projeto:

   ```bash
   pip install -r requirements.txt
   ```

2. Inicie o servidor localmente:

   ```bash
   uvicorn backend.main:app --port 8000 --reload
   ```

3. Acesse `http://localhost:8000/api/v1/health` para verificar se o serviço está ativo.
4. Utilize as demais rotas listadas acima para criar e consultar benchmarks, modelos e datasets.
