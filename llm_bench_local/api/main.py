"""API simplificada usada nos testes."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List

from llm_bench_local.core.benchmark import Benchmark
from llm_bench_local.persistence.crud import BenchmarkRepository
from llm_bench_local.config.settings import settings

app = FastAPI(title="LLM Bench Local API")
repo = BenchmarkRepository(settings.db_path)

class RunRequest(BaseModel):
    model_id: str
    prompt: str
    task: str = "text-generation"
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    use_gpu: bool = True

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/v1/benchmarks/run")
async def run_benchmark(req: RunRequest):
    bench = Benchmark(
        model_id=req.model_id,
        prompt=req.prompt,
        task=req.task,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        use_gpu=req.use_gpu,
    )
    result = bench.execute()
    repo.update_benchmark_status(bench.job_id, "COMPLETED", result)
    return {"job_id": bench.job_id, **result}

@app.get("/api/v1/benchmarks/{job_id}")
async def get_benchmark(job_id: str):
    bench = repo.get_benchmark(job_id)
    if not bench:
        raise HTTPException(status_code=404, detail="Benchmark não encontrado")
    return bench

@app.get("/api/v1/benchmarks")
async def list_benchmarks():
    return repo.list_benchmarks()

@app.get("/api/v1/models")
async def get_models() -> List[str]:
    return settings.get_available_models()

@app.get("/api/v1/hardware/metrics/{job_id}")
async def get_hw_metrics(job_id: str):
    metrics = repo.get_hardware_metrics(job_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Métricas não encontradas")
    return metrics
