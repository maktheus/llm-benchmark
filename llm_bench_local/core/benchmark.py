import time
import uuid
from typing import Dict, Optional, List
from datetime import datetime

from llm_bench_local.config.settings import settings
from llm_bench_local.hardware.monitor import HardwareMonitor
from llm_bench_local.persistence.crud import BenchmarkRepository
from llm_bench_local.core.model import ModelRunner

class Benchmark:
    def __init__(self, model_id: str, prompt: str, task: str = "text-generation",
                 max_tokens: Optional[int] = None, temperature: float = 0.7,
                 top_p: float = 0.9, use_gpu: bool = True):
        """Inicializa um novo benchmark."""
        self.job_id = str(uuid.uuid4())
        self.model_id = model_id
        self.prompt = prompt
        self.task = task
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.use_gpu = use_gpu
        
        # Inicializa componentes
        self.model_runner = ModelRunner(model_id)
        self.hardware_monitor = HardwareMonitor()
        self.repository = BenchmarkRepository(settings.db_path)
        
        # Configurações do modelo
        self.model_config = settings.get_model_config(model_id)
        if not self.model_config:
            raise ValueError(f"Modelo {model_id} não encontrado na configuração")
        
        # Configurações de hardware
        self.hardware_options = settings.default_hardware_options.copy()
        self.hardware_options["use_gpu"] = use_gpu

    def execute(self) -> Dict:
        """Executa o benchmark e retorna os resultados."""
        try:
            # Salva o benchmark no banco de dados
            self.repository.create_benchmark(
                self.job_id,
                self.model_id,
                self.task,
                {
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p
                },
                self.hardware_options
            )
            
            # Inicia o monitoramento de hardware
            self.hardware_monitor.start_monitoring()
            
            # Executa o modelo
            start_time = time.time()
            output = self.model_runner.generate(
                self.prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                use_gpu=self.use_gpu
            )
            end_time = time.time()
            
            # Para o monitoramento e obtém métricas
            hardware_metrics = self.hardware_monitor.stop_monitoring()
            
            # Calcula resultados
            duration = end_time - start_time
            tokens_generated = len(output.split())
            
            results = {
                "model": self.model_id,
                "task": self.task,
                "duration": duration,
                "tokens_generated": tokens_generated,
                "output": output,
                "hardware_metrics": hardware_metrics
            }
            
            # Atualiza o benchmark no banco de dados
            self.repository.update_benchmark_status(
                self.job_id,
                "COMPLETED",
                results
            )
            
            return results
            
        except Exception as e:
            # Em caso de erro, atualiza o status do benchmark
            self.repository.update_benchmark_status(
                self.job_id,
                "FAILED",
                {"error": str(e)}
            )
            raise

    def get_status(self) -> Dict:
        """Retorna o status atual do benchmark."""
        return self.repository.get_benchmark(self.job_id)

    def get_hardware_metrics(self) -> List[Dict]:
        """Retorna as métricas de hardware do benchmark."""
        return self.repository.get_hardware_metrics(self.job_id) 