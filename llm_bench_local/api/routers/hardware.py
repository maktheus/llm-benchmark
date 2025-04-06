"""
Router para endpoints de hardware.
"""

from fastapi import APIRouter
from llm_bench_local.hardware.monitor import HardwareMonitor

router = APIRouter()


@router.get("/hardware/info")
async def get_hardware_info():
    """Obtém informações sobre o hardware disponível.
    
    Returns:
        Informações sobre CPU, GPU e memória
    """
    monitor = HardwareMonitor(use_gpu=True)
    return monitor.get_metrics()


@router.get("/hardware/gpu")
async def get_gpu_info():
    """Obtém informações específicas sobre GPUs disponíveis.
    
    Returns:
        Lista de informações sobre cada GPU
    """
    monitor = HardwareMonitor(use_gpu=True)
    return monitor.get_gpu_metrics() 