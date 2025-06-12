"""Aplicação FastAPI do Backend."""

from fastapi import FastAPI, HTTPException

from llm_bench_local.config.settings import settings
from llm_bench_local.persistence.crud import BenchmarkRepository
from llm_bench_local.datasets import DatasetManager

repo = BenchmarkRepository(settings.db_path)
datasets = DatasetManager()

app = FastAPI(title="LLM Bench Backend")


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    """Endpoint de verificação de saúde."""
    return {"status": "ok"}


@app.post("/api/v1/benchmarks")
async def create_benchmark() -> dict[str, str]:
    """Endpoint placeholder para criação de benchmarks."""
    return {"message": "benchmark criado"}


@app.get("/api/v1/benchmarks/{job_id}")
async def get_benchmark(job_id: str):
    """Retorna informações de um benchmark específico."""
    bench = repo.get_benchmark(job_id)
    if bench is None:
        raise HTTPException(status_code=404, detail="Benchmark não encontrado")
    return bench


@app.get("/api/v1/benchmarks")
async def list_benchmarks() -> list:
    """Lista benchmarks registrados."""
    return repo.list_benchmarks()


@app.get("/api/v1/benchmarks/{job_id}/metrics")
async def get_hardware_metrics(job_id: str):
    """Retorna métricas de hardware de um benchmark."""
    metrics = repo.get_hardware_metrics(job_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Métricas não encontradas")
    return metrics


@app.get("/api/v1/models")
async def get_models() -> list[str]:
    """Lista modelos disponíveis."""
    return settings.get_available_models()


@app.get("/api/v1/datasets")
async def get_datasets() -> list[str]:
    """Lista datasets registrados."""
    return datasets.list_datasets()
