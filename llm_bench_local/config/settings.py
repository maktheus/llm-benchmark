"""
Configurações da aplicação usando Pydantic Settings.
"""

from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import json
import os


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    API_RELOAD: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Database
    DATABASE_URL: str = "sqlite:///./data/db/benchmarks.db"

    # Models
    MODEL_CACHE_DIR: str = "./data/models"
    DEFAULT_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"

    # Hardware
    USE_GPU: bool = True
    GPU_DEVICE_IDS: List[int] = [0]
    CPU_THREADS: int = 4

    # Benchmark
    DEFAULT_MAX_TOKENS: int = 100
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.95

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    def __init__(self, **data):
        super().__init__(**data)
        object.__setattr__(self, "base_dir", Path(__file__).parent.parent.parent)
        object.__setattr__(self, "data_dir", self.base_dir / "data")
        object.__setattr__(self, "models_dir", self.data_dir / "models")
        object.__setattr__(self, "db_dir", self.data_dir / "db")
        object.__setattr__(self, "datasets_dir", self.data_dir / "datasets")

        # Carrega configurações dos modelos
        self.models_config = self._load_models_config()

        # Configurações do banco de dados
        self.db_path = str(self.db_dir / "benchmarks.db")

        # Configurações de hardware
        self.default_hardware_options = {
            "use_gpu": True,
            "monitor_interval": 1.0,  # segundos
            "max_memory_usage": 0.9,  # 90% da memória disponível
            "max_gpu_memory_usage": 0.9,  # 90% da VRAM disponível
        }

        # Configurações de logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Configurações de cache
        self.cache_dir = self.data_dir / "cache"
        self.cache_ttl = 3600  # 1 hora em segundos

    def _load_models_config(self) -> Dict[str, Any]:
        """Carrega a configuração dos modelos do arquivo JSON."""
        config_path = self.models_dir / "config.json"
        if not config_path.exists():
            return {}

        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def get_model_config(self, model_id: str) -> Dict[str, Any]:
        """Retorna a configuração de um modelo específico."""
        return self.models_config.get(model_id, {})

    def get_available_models(self) -> list:
        """Retorna a lista de modelos disponíveis."""
        return list(self.models_config.keys())

    def update_model_config(self, model_id: str, config: Dict[str, Any]) -> None:
        """Atualiza a configuração de um modelo."""
        self.models_config[model_id] = config
        self._save_models_config()

    def _save_models_config(self) -> None:
        """Salva a configuração dos modelos no arquivo JSON."""
        config_path = self.models_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(self.models_config, f, indent=4)


# Instância global das configurações
settings = Settings()
