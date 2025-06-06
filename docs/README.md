# LLM Bench Local - Documentação

## Visão Geral
LLM Bench Local é uma ferramenta para benchmarking de modelos de linguagem locais. Ela permite avaliar o desempenho de diferentes modelos em termos de velocidade, uso de recursos e qualidade das respostas.

Para um panorama geral dos requisitos do sistema, consulte o documento [docs/prd.md](prd.md).

## Estrutura do Projeto
```
llm_bench_local/
├── api/                 # API FastAPI
├── core/               # Lógica principal
├── data/               # Dados e configurações
│   ├── db/            # Banco de dados SQLite
│   └── models/        # Configurações dos modelos
├── docs/              # Documentação
├── scripts/           # Scripts utilitários
└── tests/             # Testes
    ├── integration/   # Testes de integração
    └── unit/          # Testes unitários
```

## Configuração
1. Clone o repositório
2. Instale as dependências: `pip install -e .`
3. Configure as variáveis de ambiente (veja `.env.example`)
4. Execute os testes: `pytest`

## Uso
Para executar um benchmark:
```bash
python scripts/run_benchmark_cli.py --model gpt2 --prompt "Seu prompt aqui"
```

## API
A API está disponível em `http://localhost:8000/api/v1` com os seguintes endpoints:
- `/health` - Verificação de saúde
- `/benchmarks` - Execução de benchmarks
- `/models` - Gerenciamento de modelos
- `/hardware` - Métricas de hardware
- `/datasets` - Registro e listagem de datasets
- `/rag` - Endpoints para testes de RAG

## Licença
MIT License - veja o arquivo LICENSE para detalhes. 
