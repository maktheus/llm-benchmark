"""Funções utilitárias para gerenciar datasets usados nos benchmarks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from datasets import load_dataset

from llm_bench_local.config.settings import settings


class DatasetManager:
    """Gerencia o registro e carregamento de datasets."""

    def __init__(self) -> None:
        self.datasets_dir = settings.data_dir / "datasets"
        self.config_path = self.datasets_dir / "config.json"
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._save_config({})

    def _load_config(self) -> Dict[str, Dict]:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_config(self, data: Dict[str, Dict]) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def register_dataset(self, name: str, hf_id: str) -> None:
        """Registra um dataset do Hugging Face Hub."""
        config = self._load_config()
        config[name] = {"hf_id": hf_id}
        self._save_config(config)

    def list_datasets(self) -> List[str]:
        """Retorna a lista de datasets registrados."""
        return list(self._load_config().keys())

    def load(self, name: str):
        """Carrega o dataset pelo nome registrado."""
        config = self._load_config()
        if name not in config:
            raise ValueError(f"Dataset {name} não encontrado")
        hf_id = config[name]["hf_id"]
        return load_dataset(hf_id)
