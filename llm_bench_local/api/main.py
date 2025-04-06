"""
API principal do LLM Bench Local.
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from llm_bench_local.persistence.database import Database
from llm_bench_local.persistence.crud import BenchmarkRepository, HardwareMetricsRepository
from llm_bench_local.schemas.benchmark import BenchmarkResult, BenchmarkCreate
from llm_bench_local.core.benchmark import BenchmarkRunner

app = FastAPI(title="LLM Bench Local API")
db = Database()

def get_db():
    """Dependency para obter uma sessão do banco de dados."""
    with db.session_scope() as session:
        yield session

@app.post("/benchmarks/", response_model=BenchmarkResult)
async def create_benchmark(
    benchmark: BenchmarkCreate,
    session: Session = Depends(get_db)
):
    """Cria um novo benchmark."""
    repo = BenchmarkRepository(session)
    runner = BenchmarkRunner()
    
    # Cria o benchmark no banco
    repo.create_benchmark(
        job_id=benchmark.job_id,
        model_id=benchmark.model_id,
        task=benchmark.task,
        config=benchmark.config.dict(),
        hardware_options=benchmark.hardware_options.dict()
    )
    
    # Executa o benchmark
    result = await runner.run(benchmark)
    
    # Atualiza o resultado
    repo.save_benchmark_results(benchmark.job_id, result.metrics)
    
    return result

@app.get("/benchmarks/{job_id}", response_model=BenchmarkResult)
async def get_benchmark(
    job_id: str,
    session: Session = Depends(get_db)
):
    """Recupera um benchmark pelo ID."""
    repo = BenchmarkRepository(session)
    benchmark = repo.get_benchmark(job_id)
    
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark não encontrado")
    
    return BenchmarkResult(
        job_id=benchmark.job_id,
        model_id=benchmark.model_id,
        task=benchmark.task,
        config=benchmark.config,
        hardware_options=benchmark.hardware_options,
        metrics=benchmark.results,
        status=benchmark.status,
        timestamp=benchmark.updated_at.isoformat()
    )

@app.get("/benchmarks/", response_model=List[BenchmarkResult])
async def list_benchmarks(
    model_id: Optional[str] = None,
    task: Optional[str] = None,
    limit: int = 100,
    session: Session = Depends(get_db)
):
    """Lista benchmarks com filtros opcionais."""
    repo = BenchmarkRepository(session)
    benchmarks = repo.list_benchmarks(
        model_id=model_id,
        task=task,
        limit=limit
    )
    
    return [
        BenchmarkResult(
            job_id=b.job_id,
            model_id=b.model_id,
            task=b.task,
            config=b.config,
            hardware_options=b.hardware_options,
            metrics=b.results,
            status=b.status,
            timestamp=b.updated_at.isoformat()
        )
        for b in benchmarks
    ]

@app.get("/benchmarks/{job_id}/metrics")
async def get_benchmark_metrics(
    job_id: str,
    session: Session = Depends(get_db)
):
    """Recupera as métricas de hardware de um benchmark."""
    repo = HardwareMetricsRepository(session)
    metrics = repo.get_metrics(job_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Métricas não encontradas")
    
    return [
        {
            "timestamp": m.timestamp.isoformat(),
            "cpu_usage_percent": m.cpu_usage_percent,
            "ram_usage_gb": m.ram_usage_gb,
            "gpu_usage_percent": m.gpu_usage_percent,
            "vram_usage_gb": m.vram_usage_gb
        }
        for m in metrics
    ] 