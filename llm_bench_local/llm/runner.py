"""
Módulo para execução de modelos LLM.
"""

import time
from typing import Dict, Optional, Union
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from llama_cpp import Llama
from ctransformers import AutoModelForCausalLM as CTModelForCausalLM

from llm_bench_local.schemas.benchmark import BenchmarkConfig, HardwareOptions


class LLMRunner:
    """Executor de modelos LLM para benchmarks."""
    
    def __init__(
        self,
        model_id: str,
        hardware_options: Optional[HardwareOptions] = None
    ):
        """Inicializa o executor de LLM.
        
        Args:
            model_id: ID do modelo a ser carregado
            hardware_options: Opções de hardware para execução
        """
        self.model_id = model_id
        self.hardware_options = hardware_options or HardwareOptions()
        self.model = None
        self.tokenizer = None
        self.model_type = self._detect_model_type()
    
    def _detect_model_type(self) -> str:
        """Detecta o tipo do modelo baseado no ID.
        
        Returns:
            Tipo do modelo ('transformers', 'llama.cpp', 'ctransformers')
        """
        if self.model_id.endswith('.gguf'):
            return 'llama.cpp'
        elif self.model_id.endswith('.bin'):
            return 'ctransformers'
        else:
            return 'transformers'
    
    def load_model(self):
        """Carrega o modelo e tokenizer."""
        if self.model_type == 'transformers':
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map='auto' if self.hardware_options.use_gpu else 'cpu',
                torch_dtype=torch.float16 if self.hardware_options.use_gpu else torch.float32
            )
        elif self.model_type == 'llama.cpp':
            self.model = Llama(
                model_path=self.model_id,
                n_ctx=2048,
                n_threads=self.hardware_options.cpu_threads,
                n_gpu_layers=-1 if self.hardware_options.use_gpu else 0
            )
        elif self.model_type == 'ctransformers':
            self.model = CTModelForCausalLM.from_pretrained(
                self.model_id,
                gpu_layers=-1 if self.hardware_options.use_gpu else 0,
                threads=self.hardware_options.cpu_threads
            )
    
    def generate(
        self,
        config: BenchmarkConfig
    ) -> Dict[str, Union[str, float]]:
        """Executa a geração de texto.
        
        Args:
            config: Configuração do benchmark
            
        Returns:
            Dict com resultado e métricas
        """
        start_time = time.time()
        
        if self.model_type == 'transformers':
            inputs = self.tokenizer(config.prompt, return_tensors="pt")
            if self.hardware_options.use_gpu:
                inputs = inputs.to('cuda')
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=config.max_new_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                do_sample=True
            )
            
            output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        elif self.model_type == 'llama.cpp':
            output = self.model(
                config.prompt,
                max_tokens=config.max_new_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                stop=["</s>", "Human:", "Assistant:"]
            )['choices'][0]['text']
            
        elif self.model_type == 'ctransformers':
            output = self.model(
                config.prompt,
                max_new_tokens=config.max_new_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                stop=["</s>", "Human:", "Assistant:"]
            )
        
        duration = time.time() - start_time
        
        return {
            "output": output,
            "duration": duration,
            "tokens_generated": len(output.split())  # Aproximação
        }
    
    def __del__(self):
        """Limpa recursos ao destruir o objeto."""
        if self.model_type == 'transformers':
            del self.model
            del self.tokenizer
            if self.hardware_options.use_gpu:
                torch.cuda.empty_cache()
        else:
            del self.model 