"""
Schemas Pydantic para os benchmarks.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HardwareOptions(BaseModel):
    """Opções de hardware para o benchmark."""
    use_gpu: bool = Field(default=True, description="Se deve usar GPU")
    gpu_device_ids: List[int] = Field(default=[0], description="IDs das GPUs a serem usadas")
    cpu_threads: int = Field(default=4, description="Número de threads CPU")


class BenchmarkConfig(BaseModel):
    """Configuração do benchmark."""
    prompt: str = Field(..., description="Prompt para o modelo")
    max_new_tokens: int = Field(default=100, description="Número máximo de tokens a serem gerados")
    temperature: float = Field(default=0.7, description="Temperatura para sampling")
    top_p: float = Field(default=0.95, description="Top-p para sampling")


class BenchmarkRequest(BaseModel):
    """Requisição para iniciar um benchmark."""
    model_id: str = Field(..., description="ID do modelo a ser testado")
    task: str = Field(..., description="Tarefa a ser executada (ex: text-generation)")
    config: BenchmarkConfig = Field(..., description="Configuração do benchmark")
    hardware_options: Optional[HardwareOptions] = Field(
        default=None,
        description="Opções de hardware para o benchmark"
    )


class BenchmarkCreate(BenchmarkRequest):
    """Compatibilidade com versões antigas."""
    job_id: Optional[str] = None


class HardwareMetrics(BaseModel):
    """Métricas de hardware coletadas durante o benchmark."""
    cpu_usage: float = Field(..., description="Uso de CPU em porcentagem")
    memory_usage: float = Field(..., description="Uso de memória em porcentagem")
    gpu_usage: Optional[float] = Field(None, description="Uso de GPU em porcentagem")
    gpu_memory_usage: Optional[float] = Field(None, description="Uso de memória GPU em porcentagem")
    gpu_temperature: Optional[float] = Field(None, description="Temperatura da GPU em Celsius")


class BenchmarkResult(BaseModel):
    """Resultado do benchmark."""
    job_id: str = Field(..., description="ID único do job")
    model_id: str = Field(..., description="ID do modelo testado")
    task: str = Field(..., description="Tarefa executada")
    config: BenchmarkConfig = Field(..., description="Configuração usada")
    hardware_options: HardwareOptions = Field(..., description="Opções de hardware usadas")
    metrics: Dict[str, float] = Field(..., description="Métricas de performance do modelo")
    hardware_metrics: List[HardwareMetrics] = Field(..., description="Métricas de hardware coletadas")
    output: str = Field(..., description="Saída do modelo")
    duration: float = Field(..., description="Duração total em segundos")
    timestamp: str = Field(..., description="Timestamp do benchmark") 