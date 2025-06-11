import pytest
from fastapi.testclient import TestClient
from llm_bench_local.api.main import app

client = TestClient(app)

def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "1.0.0"
    }

def test_run_benchmark():
    """Testa o endpoint de execução de benchmark."""
    data = {
        "model_id": "gpt2",
        "prompt": "Hello, world!",
        "task": "text-generation",
        "max_tokens": 10,
        "temperature": 0.7,
        "top_p": 0.9,
        "use_gpu": True
    }
    
    response = client.post("/api/v1/benchmarks/run", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "job_id" in result
    assert result["model"] == "gpt2"
    assert result["task"] == "text-generation"
    assert "duration" in result
    assert "tokens_generated" in result
    assert "output" in result
    assert "hardware_metrics" in result

def test_get_benchmark():
    """Testa o endpoint de obtenção de benchmark."""
    # Primeiro executa um benchmark
    data = {
        "model_id": "gpt2",
        "prompt": "Test prompt",
        "task": "text-generation"
    }
    response = client.post("/api/v1/benchmarks/run", json=data)
    job_id = response.json()["job_id"]
    
    # Depois tenta obter o benchmark
    response = client.get(f"/api/v1/benchmarks/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_list_benchmarks():
    """Testa o endpoint de listagem de benchmarks."""
    response = client.get("/api/v1/benchmarks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_models():
    """Testa o endpoint de obtenção de modelos."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_hardware_metrics():
    """Testa o endpoint de obtenção de métricas de hardware."""
    # Primeiro executa um benchmark
    data = {
        "model_id": "gpt2",
        "prompt": "Test prompt",
        "task": "text-generation"
    }
    response = client.post("/api/v1/benchmarks/run", json=data)
    job_id = response.json()["job_id"]
    
    # Depois tenta obter as métricas
    response = client.get(f"/api/v1/hardware/metrics/{job_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dataset_registration_and_listing(monkeypatch):
    """Testa registro e listagem de datasets."""
    from llm_bench_local.api.routers import datasets as datasets_router

    class DummyManager:
        def __init__(self):
            self.data = {}

        def register_dataset(self, name: str, hf_id: str) -> None:
            self.data[name] = hf_id

        def list_datasets(self):
            return list(self.data.keys())

    dummy = DummyManager()
    monkeypatch.setattr(datasets_router, "manager", dummy)

    response = client.post(
        "/api/v1/datasets",
        json={"name": "test_ds", "hf_id": "dataset/id"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "registered"}

    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert response.json() == ["test_ds"]


def test_rag_pipeline(monkeypatch):
    """Testa construção e consulta do pipeline RAG."""
    import sys
    import types
    import importlib
    from fastapi.testclient import TestClient

    st_stub = types.ModuleType("sentence_transformers")
    st_stub.SentenceTransformer = object
    sys.modules["sentence_transformers"] = st_stub
    faiss_stub = types.ModuleType("faiss")
    faiss_stub.IndexFlatL2 = object
    sys.modules["faiss"] = faiss_stub

    rag_stub = types.ModuleType("llm_bench_local.rag")
    class SimpleRAGPipeline:
        def __init__(self, model_id: str):
            self.model_id = model_id
            self.built = False
            self.args = None
        def build_index(self, dataset_name: str, field: str = "text"):
            self.built = True
            self.args = (dataset_name, field)
        def query(self, question: str, top_k: int = 3, max_new_tokens: int = 64):
            return f"answer:{question}"
    rag_stub.SimpleRAGPipeline = SimpleRAGPipeline
    sys.modules["llm_bench_local.rag"] = rag_stub

    import llm_bench_local.api.main as main
    importlib.reload(main)
    local_client = TestClient(main.app)

    response = local_client.post(
        "/api/v1/rag/build",
        json={"model_id": "t5", "dataset": "test_ds"},
    )
    assert response.status_code == 200
    assert main.rag.pipeline.built is True
    assert main.rag.pipeline.args == ("test_ds", "text")

    response = local_client.post(
        "/api/v1/rag/query",
        json={"question": "hello"},
    )
    assert response.status_code == 200
    assert response.json()["output"] == "answer:hello"
