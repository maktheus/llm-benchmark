# LLM Bench Local

**Ferramenta local para realizar benchmark de performance de Modelos de Linguagem Grandes (LLMs) em diferentes hardwares.**

## Visão Geral

`llm-bench-local` é um microserviço local projetado para executar, monitorar e comparar a performance de inferência de LLMs em sua própria máquina. O objetivo é fornecer métricas consistentes sobre como diferentes modelos se comportam em hardwares variados, desde dispositivos de baixa potência como Raspberry Pi até PCs desktop e servidores com GPUs dedicadas.

A ferramenta é construída como um serviço local com uma API REST, permitindo integração fácil com frontends, scripts ou outras ferramentas de automação. Ela é projetada para ser empacotada com Docker para facilitar a instalação e garantir a reprodutibilidade dos ambientes.

## Divisão em Projetos

O repositório é organizado em módulos independentes. Aqui está a biblioteca **LLM Core Benchmark**, responsável por executar os testes e pipelines de machine learning. Além deste núcleo existem dois serviços que completam a solução:
* **Backend** – API REST que orquestra os benchmarks e mantém os resultados.
* **Frontend** – aplicação web que permite configurar experimentos e visualizar métricas.

Para detalhes completos de requisitos, consulte [docs/prd.md](docs/prd.md).

## Funcionalidades Principais

Esta ferramenta foi pensada para uso local e oferece:

* **Benchmarking de LLMs** diretamente no seu hardware.
* **Monitoramento de hardware** (CPU, GPU, RAM, temperatura e VRAM) durante a execução.
* **Suporte a diversos modelos e backends**, como Hugging Face Transformers ou llama.cpp.
* **Gerenciamento de datasets** e pipeline RAG simples.
* **API REST** para iniciar e consultar benchmarks a partir de scripts ou frontends.
* **Persistência local** de resultados em formatos simples, como SQLite ou JSON.
* **Configuração flexível** de modelos, tarefas e coleta de métricas.
* **Distribuição via Docker** para manter o ambiente reproduzível em qualquer sistema.

## Arquitetura

A aplicação segue uma arquitetura de microserviço (mesmo que implantada inicialmente como um único contêiner) para modularidade e separação de responsabilidades.

```ascii
+-----------------------------------------------------------------------------+
|  Usuário / Frontend                                                         |
+-----------------------------------------------------------------------------+
       | ▲
       | Requisições HTTP (Iniciar Benchmark, Ver Resultados)
       ▼ |
+---------------------+      +------------------------------------------------+
|                     |----->|          Microserviço de Benchmark             |
|   [ Frontend ]      |      |                                                |
|   (Web App / CLI)   |      |  +------------------------------------------+  |
|                     |<-----|  |            API Layer (FastAPI/Flask)     |  |
+---------------------+      |  |  (Endpoints: /benchmarks, /models, etc.) |  |
                             |  +-------------------|----------------------+  |
                             |                      | ▲                      |
                             |                      ▼ |                      |
                             |  +-------------------|----------------------+  |
                             |  |        Orchestration Engine              |  |
                             |  |  (Gerencia Jobs, Coordena Módulos)       |  |
                             |  +-------------------|----------------------+  |
                             |          /|\         |           /|\         |
                             |           |          |            |          |
                             | Controla  |          | Controla   | Controla |
                             |           |          |            |          |
                             |          \|/         |           \|/         |
                             |  +----------------+  |  +-------------------+ |
                             |  |   LLM Runner   |  |  | Hardware Monitor  | |
                             |  | (Transformers, |  |  | (psutil, pynvml)  | |
                             |  | llama.cpp, ...) |  |  |                   | |
                             |  +-------|--------+  |  +--------|----------+ |
                             |          |           |           |            |
                             |          | Lê        |           | Lê         |
                             |          ▼           |           ▼            |
+---------------------+      | +-----------------+  | +-------------------+  |
| Modelos LLM         |<-------| Arquivos/Modelos|  | | Hardware (CPU/GPU)|  |
| (Arquivos .gguf,    |      | |  Locais/Remotos |  | | (RAM/VRAM, Temp)  |<--+
|  Diretórios HF)     |      | +-----------------+  | +-------------------+  |
+---------------------+      |                      |                      |
                             |                      |                      |
                             |  +-------------------|----------------------+  |
                             |  | Results Storage / Persistência           |  |
                             |  | (SQLite / JSON / CSV)                    |  |
                             |  +-------------------|----------------------+  |
                             |                      | ▲                      |
                             |                      | Armazena/Lê Resultados |
                             |                      ▼                        |
                             |          +-----------------------+           |
                             |          | Banco de Dados/Arquivo|           |
                             |          | (ex: benchmark.db)    |           |
                             |          +-----------------------+           |
                             |                                                |
                             |  +------------------------------------------+  |
                             |  |      Configuration Management            |  |
                             |  |      (Arquivos YAML/JSON, Env Vars)      |  |
                             |  +------------------------------------------+  |
                             |      ▲                                         |
                             |      | (Lido por vários módulos)               |
                             +------------------------------------------------+
```

**Componentes Principais:**

1.  **API Layer:** Interface HTTP (FastAPI/Flask) para interagir com o serviço.
2.  **Orchestration Engine:** Coordena o fluxo de execução dos benchmarks.
3.  **LLM Runner:** Carrega e executa a inferência dos modelos LLM usando diferentes backends.
4.  **Hardware Monitor:** Coleta métricas de utilização de hardware (CPU, GPU, RAM) em tempo real.
5.  **Results Storage / Persistence:** Armazena os resultados e métricas dos benchmarks (ex: usando SQLite).
6.  **Configuration Management:** Gerencia as configurações da aplicação.

## Tecnologia Stack (Proposta Inicial)

*   **Linguagem:** Python 3.9+
*   **API Framework:** FastAPI (recomendado) ou Flask
*   **Monitoramento de Hardware:** `psutil`, `pynvml` (para Nvidia GPUs)
*   **LLM Backends:** Hugging Face `transformers`, `llama-cpp-python`, `ctransformers`
*   **Validação de Dados:** Pydantic
*   **Persistência:** SQLite (via SQLAlchemy ou `sqlite3`), JSON/CSV
*   **Containerização:** Docker, Docker Compose
*   **Gerenciamento de Dependências:** Poetry ou PDM (`pyproject.toml`)
*   **Testes:** Pytest
*   **Linting/Formatação:** Ruff, Black
*   **Type Checking:** MyPy

## Estrutura do Projeto

Cada diretório desempenha um papel específico na aplicação. A visão geral é a seguinte:

```
llm-bench-local/
├── docker-compose.yml         # Orquestração com Docker
├── Dockerfile                 # Construção da imagem
├── data/                      # Dados locais (não versionados)
│   ├── models/
│   └── db/
├── docs/                      # Documentação e diagramas
├── scripts/                   # Utilidades de linha de comando
├── llm_bench_local/           # Código principal
│   ├── api/                   # Rotas e modelos
│   ├── core/                  # Execução do benchmark
│   ├── hardware/              # Métricas de CPU/GPU
│   ├── datasets/              # Registro e carregamento
│   └── persistence/           # Resultados em disco
└── tests/                     # Testes unitários e de integração
```

## Começando (Getting Started)

Você pode executar o LLM Bench Local em um contêiner Docker ou configurá-lo diretamente no seu ambiente. Os passos a seguir mostram as duas abordagens.

### Pré-requisitos

*   Docker e Docker Compose instalados.
*   Git
*   (Opcional, para desenvolvimento local sem Docker) Python 3.9+ e Poetry/PDM.

### Instalação e Execução (Usando Docker - Recomendado)

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd llm-bench-local
    ```

2.  **Configure o Ambiente:**
    Copie o arquivo de exemplo de variáveis de ambiente e ajuste conforme necessário (ex: caminhos para modelos, configurações de GPU).
    ```bash
    cp .env.example .env
    # Edite o arquivo .env com suas configurações
    ```

3.  **Construa e Execute o Contêiner:**
    ```bash
    docker-compose up --build -d
    ```
    Isso construirá a imagem Docker (se ainda não existir) e iniciará o serviço em background.

4.  **Verifique se o serviço está rodando:**
    Acesse `http://localhost:8000/docs` (ou a porta que você configurar) no seu navegador para ver a documentação interativa da API (Swagger UI se estiver usando FastAPI).

### Desenvolvimento Local (Sem Docker)

1.  **Clone o repositório:** (Como acima)
2.  **Instale as dependências:** (Usando Poetry como exemplo)
    ```bash
    poetry install
    ```
3.  **Configure o Ambiente:** Crie e edite o arquivo `.env`.
4.  **Execute a Aplicação:** (Exemplo com Uvicorn para FastAPI)
    ```bash
    poetry run uvicorn llm_bench_local.api.main:app --reload
    ```

## Configuração

As configurações principais são gerenciadas através de variáveis de ambiente definidas no arquivo `.env`. Consulte `.env.example` para ver as variáveis disponíveis, que podem incluir:

*   `MODEL_CACHE_DIR`: Diretório para armazenar modelos baixados.
*   `DATABASE_URL`: String de conexão para o banco de dados (ex: `sqlite:///./data/db/benchmarks.db`).
*   `LOG_LEVEL`: Nível de logging (DEBUG, INFO, WARNING, ERROR).
*   Configurações específicas de GPU (ex: quais GPUs usar).

## Uso

A principal forma de interagir com o serviço é através da sua API REST.

**Exemplo: Iniciar um novo Benchmark**

```bash
curl -X POST "http://localhost:8000/benchmarks/" -H "Content-Type: application/json" -d '{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
  "task": "text-generation",
  "config": {
    "prompt": "Explique o que é um benchmark de LLM em 3 frases.",
    "max_new_tokens": 100
  },
  "hardware_options": {
    "use_gpu": true
  }
}'
```

**Exemplo: Obter resultados de um Benchmark**

```bash
curl -X GET "http://localhost:8000/benchmarks/{job_id}"
```

*(Substitua `{job_id}` pelo ID retornado ao iniciar o benchmark)*

Você também pode usar scripts (como o exemplo em `scripts/run_benchmark_cli.py`) ou um futuro frontend para interagir com a API.

### Endpoints Principais

| Método | Rota | Descrição |
|-------|--------------------------------|---------------------------------------------|
| `GET` | `/api/v1/health` | Verifica se o serviço está ativo. |
| `POST` | `/api/v1/benchmarks/run` | Inicia um benchmark com os parâmetros enviados. |
| `GET` | `/api/v1/benchmarks/{job_id}` | Consulta o resultado de um benchmark específico. |
| `GET` | `/api/v1/benchmarks` | Lista benchmarks cadastrados. |
| `GET` | `/api/v1/hardware/metrics/{job_id}` | Retorna métricas de hardware do benchmark. |
| `GET` | `/api/v1/models` | Lista modelos disponíveis para teste. |
| `GET` | `/api/v1/datasets` | Lista datasets registrados. |
| `POST` | `/api/v1/datasets` | Registra um novo dataset. |
| `POST` | `/api/v1/rag/build` | Constrói o índice do pipeline RAG. |
| `POST` | `/api/v1/rag/query` | Realiza uma consulta no pipeline RAG. |

## Datasets e Pipeline RAG

O `DatasetManager` permite registrar conjuntos de dados do Hugging Face Hub e recuperá-los quando necessário. Esses datasets são usados pelo pipeline RAG simplificado, que combina recuperação de documentos via FAISS com geração de texto do modelo escolhido.

```ascii
 +---------------+     build_index      +------------+
 | DatasetManager| -------------------> |  FAISS IDX  |
 +---------------+                      +------------+
         |                                   |
         |             consulta               v
         +------------------------------->  [LLM]
```

1. **Registro de Dataset** – envie nome e `hf_id` para `/api/v1/datasets`.
2. **Construção de Índice** – utilize `/api/v1/rag/build` informando o dataset registrado.
3. **Consulta** – realize perguntas para `/api/v1/rag/query` e receba respostas geradas com recuperação de contexto.

## Executando Testes

Para rodar os testes automatizados (assumindo que você está usando Pytest):

**Dentro do Docker (Recomendado para CI/CD):**

```bash
docker-compose exec <nome-do-servico-no-compose> pytest tests/
```
*(Você pode precisar ajustar o comando `docker-compose exec` dependendo de como o serviço é nomeado no `docker-compose.yml`)*

**Localmente (com ambiente configurado):**

```bash
poetry run pytest tests/
```

## Contribuindo

Contribuições são bem-vindas! Se você deseja contribuir, por favor:

1.  Faça um Fork do repositório.
2.  Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3.  Faça commit das suas mudanças (`git commit -am 'Adiciona nova feature'`).
4.  Faça push para a branch (`git push origin feature/nova-feature`).
5.  Abra um Pull Request.

Por favor, certifique-se de adicionar testes para suas funcionalidades e de que todos os testes e linters estão passando.

## Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Roadmap / Trabalho Futuro
*   Implementação completa do `DatasetManager` e APIs de RAG.
*   Separação dos projetos Backend e Frontend.
*   Desenvolvimento de um Frontend Web simples para interagir com a API.
*   Suporte a mais backends de LLM (ex: TensorRT-LLM, ONNX Runtime).
*   Suporte a mais tarefas de benchmark (Sumarização, Q&A, etc.).
*   Coleta de métricas de hardware mais detalhadas (energia, uso de barramento PCIe).
*   Melhor gerenciamento e visualização de resultados históricos.
*   Empacotamento como instalador nativo (opcional).
*   Suporte a benchmarks distribuídos (múltiplas máquinas).

