from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm_bench_local.core.benchmark import Benchmark
from llm_bench_local.config.settings import settings
from llm_bench_local.persistence.crud import BenchmarkRepository

router = APIRouter()
repository = BenchmarkRepository(settings.db_path)

class BenchmarkRequest(BaseModel):
    model_id: str
    prompt: str
    task: str = "text-generation"
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    use_gpu: bool = True

class BenchmarkResponse(BaseModel):
    job_id: str
    model: str
    task: str
    duration: float
    tokens_generated: int
    output: str
    hardware_metrics: Dict

@router.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@router.post("/benchmarks/run", response_model=BenchmarkResponse)
async def run_benchmark(request: BenchmarkRequest):
    """Executa um novo benchmark."""
    try:
        benchmark = Benchmark(
            model_id=request.model_id,
            prompt=request.prompt,
            task=request.task,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            use_gpu=request.use_gpu
        )
        
        results = benchmark.execute()
        return BenchmarkResponse(
            job_id=benchmark.job_id,
            **results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/benchmarks/{job_id}")
async def get_benchmark(job_id: str):
    """Retorna os resultados de um benchmark específico."""
    benchmark = repository.get_benchmark(job_id)
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark não encontrado")
    return benchmark

@router.get("/benchmarks")
async def list_benchmarks(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """Lista benchmarks com paginação e filtro opcional por status."""
    return repository.list_benchmarks(limit, offset, status)

@router.get("/models")
async def get_models():
    """Retorna a lista de modelos disponíveis."""
    return settings.get_available_models()

@router.get("/hardware/metrics/{job_id}")
async def get_hardware_metrics(job_id: str):
    """Retorna as métricas de hardware de um benchmark."""
    metrics = repository.get_hardware_metrics(job_id)
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="Métricas de hardware não encontradas"
        )
    return metrics 