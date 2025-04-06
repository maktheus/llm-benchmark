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