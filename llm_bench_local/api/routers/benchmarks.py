"""
Router para endpoints de benchmark.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException

from llm_bench_local.schemas.benchmark import (
    BenchmarkRequest,
    BenchmarkResult,
    HardwareOptions
)
from llm_bench_local.llm.runner import LLMRunner
from llm_bench_local.hardware.monitor import HardwareMonitor
from llm_bench_local.persistence.database import Database

router = APIRouter()
db = Database()


@router.post("/benchmarks/", response_model=BenchmarkResult)
async def create_benchmark(request: BenchmarkRequest) -> BenchmarkResult:
    """Cria e executa um novo benchmark.
    
    Args:
        request: Requisição com configuração do benchmark
        
    Returns:
        Resultado do benchmark
    """
    # Inicializa o monitor de hardware
    hardware_options = request.hardware_options or HardwareOptions()
    monitor = HardwareMonitor(use_gpu=hardware_options.use_gpu)
    
    # Inicializa o runner do modelo
    runner = LLMRunner(
        model_id=request.model_id,
        hardware_options=hardware_options
    )
    
    try:
        # Carrega o modelo
        runner.load_model()
        
        # Executa o benchmark
        result = runner.generate(request.config)
        
        # Coleta métricas de hardware
        hardware_metrics = monitor.get_metrics()
        
        # Cria o resultado
        benchmark_result = BenchmarkResult(
            job_id=str(uuid.uuid4()),
            model_id=request.model_id,
            task=request.task,
            config=request.config,
            hardware_options=hardware_options,
            metrics=result,
            hardware_metrics=[hardware_metrics],
            output=result["output"],
            duration=result["duration"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Salva o resultado
        db.save_benchmark(benchmark_result)
        
        return benchmark_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar benchmark: {str(e)}"
        )


@router.get("/benchmarks/{job_id}", response_model=BenchmarkResult)
async def get_benchmark(job_id: str) -> BenchmarkResult:
    """Recupera um resultado de benchmark pelo ID.
    
    Args:
        job_id: ID do benchmark
        
    Returns:
        Resultado do benchmark
        
    Raises:
        HTTPException: Se o benchmark não for encontrado
    """
    result = db.get_benchmark(job_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark {job_id} não encontrado"
        )
    return result


@router.get("/benchmarks/", response_model=List[BenchmarkResult])
async def list_benchmarks(
    model_id: Optional[str] = None,
    task: Optional[str] = None,
    limit: int = 100
) -> List[BenchmarkResult]:
    """Lista resultados de benchmarks com filtros opcionais.
    
    Args:
        model_id: Filtrar por ID do modelo
        task: Filtrar por tarefa
        limit: Limite de resultados
        
    Returns:
        Lista de resultados de benchmark
    """
    return db.list_benchmarks(model_id=model_id, task=task, limit=limit) 