from typing import Optional, Dict, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_bench_local.config.settings import settings

class ModelRunner:
    def __init__(self, model_id: str):
        """Inicializa o executor do modelo."""
        self.model_id = model_id
        self.model_config = settings.get_model_config(model_id)
        if not self.model_config:
            raise ValueError(f"Modelo {model_id} não encontrado na configuração")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

    def _load_model(self):
        """Carrega o modelo e o tokenizer."""
        if self.model is None:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_config["model_id"],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            self.model.eval()
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_config["model_id"]
            )

    def generate(self, prompt: str, max_tokens: Optional[int] = None,
                temperature: float = 0.7, top_p: float = 0.9,
                use_gpu: bool = True) -> str:
        """Gera texto usando o modelo."""
        if not use_gpu and self.device == "cuda":
            self.device = "cpu"
            self.model = None  # Força recarregar o modelo na CPU
        
        self._load_model()
        
        # Configura parâmetros de geração
        max_tokens = max_tokens or self.model_config.get("max_tokens", 1024)
        
        # Tokeniza o prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Gera o texto
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decodifica e retorna o texto gerado
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):]  # Retorna apenas o texto gerado

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo."""
        return {
            "model_id": self.model_id,
            "provider": self.model_config.get("provider", "unknown"),
            "device": self.device,
            "max_tokens": self.model_config.get("max_tokens", 1024),
            "parameters": self.model_config.get("parameters", "unknown")
        } 