import pytest
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configura variáveis de ambiente para testes
os.environ["API_HOST"] = "127.0.0.1"
os.environ["API_PORT"] = "8000"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture para o diretório de dados de teste."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def test_db_path(test_data_dir):
    """Fixture para o caminho do banco de dados de teste."""
    return str(test_data_dir / "test.db")

@pytest.fixture(scope="session")
def test_models_dir(test_data_dir):
    """Fixture para o diretório de modelos de teste."""
    models_dir = test_data_dir / "models"
    models_dir.mkdir(exist_ok=True)
    return models_dir

@pytest.fixture(scope="session")
def test_cache_dir(test_data_dir):
    """Fixture para o diretório de cache de teste."""
    cache_dir = test_data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir 