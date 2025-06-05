# PRD - LLM Benchmark Suite

Este documento descreve os requisitos para um sistema completo de benchmark de Modelos de Linguagem Grandes (LLMs) com suporte a pipelines de Retrieval-Augmented Generation (RAG).

## Objetivo
- Fornecer uma plataforma para testar modelos de linguagem e pipelines RAG.
- Permitir registro de datasets e modelos.
- Gerar métricas de performance e armazenar resultados para análise.

## Visão Geral do Projeto
O sistema será dividido em três projetos interligados:

1. **LLM Core Benchmark** – Biblioteca com a lógica de machine learning, execução de benchmarks e pipelines RAG.
2. **Backend** – API REST responsável por orquestrar execuções e persistir resultados.
3. **Frontend** – Interface Web para configurar testes e visualizar métricas.

## Funcionalidades Requeridas
### Core Benchmark
- Registro e carregamento de datasets (Hugging Face ou locais).
- Execução de modelos LLM em várias tarefas.
- Pipeline RAG para experimentos de recuperação de contexto.
- Coleta de métricas de hardware (CPU, GPU, memória).
- Armazenamento de resultados em SQLite (ou banco configurável).

### Backend
- Endpoints para benchmarks, modelos e datasets.
- Fila de execução/agenda de jobs.
- Autenticação opcional para ambientes multiusuário.
- Exportação de métricas para Prometheus.

### Frontend
- Dashboard para criação e acompanhamento de benchmarks.
- Edição e reutilização de prompts e configurações.
- Visualização gráfica de resultados e métricas.
- Upload de datasets locais e seleção de modelos.

## Integração entre Projetos
- O Frontend comunica-se com o Backend via HTTP usando JSON.
- O Backend importa o Core Benchmark como dependência para executar testes.
- Resultados e logs são persistidos pelo Backend e disponibilizados ao Frontend.

## Armazenamento de Dados
- Banco de dados SQLite (opcionalmente Postgres em produção).
- Diretório `data/datasets/` para datasets locais.
- Logs de execução gravados em arquivos ou no banco.

## Tecnologias Indicadas
- **Python** para Core e Backend.
- **FastAPI** para a API.
- **Vue.js** ou **React** para o Frontend.
- **SQLAlchemy** para persistência.
- **Docker** e **Docker Compose** para orquestração.

## Roadmap Inicial
1. Definir modelos e esquemas do Core.
2. Implementar `DatasetManager` e pipeline RAG.
3. Criar endpoints básicos do Backend.
4. Desenvolver interface inicial do Frontend.
5. Adicionar autenticação e métricas avançadas.
6. Documentar e preparar scripts de deploy.

## Referências
- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [Building LLM Applications](https://www.promptingguide.ai/)

