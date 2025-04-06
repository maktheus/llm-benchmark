"""
Módulo para monitoramento de hardware.
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

@dataclass
class HardwareMetrics:
    timestamp: datetime
    cpu_usage_percent: float
    ram_usage_gb: float
    gpu_usage_percent: Optional[float] = None
    vram_usage_gb: Optional[float] = None

class HardwareMonitor:
    """Monitor de hardware para coletar métricas durante o benchmark."""
    
    def __init__(self):
        self.metrics: List[HardwareMetrics] = []
        self._monitoring = False
        self._start_time: Optional[float] = None
        
        # Inicializa NVML se disponível
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self._gpu_available = True
            except pynvml.NVMLError:
                self._gpu_available = False
        else:
            self._gpu_available = False

    def start_monitoring(self) -> None:
        """Inicia o monitoramento de hardware."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._start_time = time.time()
        self.metrics.clear()

    def stop_monitoring(self) -> Dict:
        """Para o monitoramento e retorna as métricas agregadas."""
        if not self._monitoring:
            return {}
        
        self._monitoring = False
        
        if not self.metrics:
            return {}
        
        # Calcula médias e picos
        cpu_usage = [m.cpu_usage_percent for m in self.metrics]
        ram_usage = [m.ram_usage_gb for m in self.metrics]
        gpu_usage = [m.gpu_usage_percent for m in self.metrics if m.gpu_usage_percent is not None]
        vram_usage = [m.vram_usage_gb for m in self.metrics if m.vram_usage_gb is not None]
        
        result = {
            "cpu_usage_mean_percent": sum(cpu_usage) / len(cpu_usage),
            "cpu_usage_peak_percent": max(cpu_usage),
            "ram_usage_mean_gb": sum(ram_usage) / len(ram_usage),
            "ram_usage_peak_gb": max(ram_usage),
        }
        
        if gpu_usage:
            result.update({
                "gpu_usage_mean_percent": sum(gpu_usage) / len(gpu_usage),
                "gpu_usage_peak_percent": max(gpu_usage),
            })
        
        if vram_usage:
            result.update({
                "vram_usage_mean_gb": sum(vram_usage) / len(vram_usage),
                "vram_usage_peak_gb": max(vram_usage),
            })
        
        return result

    def get_current_metrics(self) -> HardwareMetrics:
        """Coleta métricas atuais do hardware."""
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_usage_gb = ram.used / (1024 ** 3)
        
        metrics = HardwareMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=cpu_usage,
            ram_usage_gb=ram_usage_gb
        )
        
        if self._gpu_available:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                metrics.gpu_usage_percent = gpu_util.gpu
                metrics.vram_usage_gb = gpu_memory.used / (1024 ** 3)
            except pynvml.NVMLError:
                pass
        
        return metrics

    def update(self) -> None:
        """Atualiza as métricas se o monitoramento estiver ativo."""
        if not self._monitoring:
            return
        
        metrics = self.get_current_metrics()
        self.metrics.append(metrics)

    def get_static_info(self) -> Dict:
        """Retorna informações estáticas sobre o hardware."""
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        ram_info = {
            "total_gb": psutil.virtual_memory().total / (1024 ** 3)
        }
        
        gpu_info = []
        if self._gpu_available:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    name = pynvml.nvmlDeviceGetName(handle)
                    
                    gpu_info.append({
                        "index": i,
                        "name": name.decode('utf-8'),
                        "total_memory_gb": info.total / (1024 ** 3),
                        "compute_capability": pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    })
            except pynvml.NVMLError:
                pass
        
        return {
            "cpu_info": cpu_info,
            "ram_info": ram_info,
            "gpu_info": gpu_info
        }

    def __del__(self):
        """Limpa recursos ao destruir o objeto."""
        if PYNVML_AVAILABLE and self._gpu_available:
            try:
                pynvml.nvmlShutdown()
            except:
                pass 