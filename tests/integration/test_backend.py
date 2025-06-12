import pytest
from fastapi.testclient import TestClient
import backend.main as backend

class DummyRepo:
    def __init__(self):
        self.data = {
            "job_id": "job1",
            "model_id": "gpt2",
            "task": "text-generation",
            "status": "COMPLETED",
            "config": {},
            "hardware_options": {},
            "results": None,
            "created_at": "now",
            "updated_at": "now",
        }

    def get_benchmark(self, job_id: str):
        if job_id == self.data["job_id"]:
            return self.data
        return None

    def list_benchmarks(self):
        return [self.data]

    def get_hardware_metrics(self, job_id: str):
        if job_id == self.data["job_id"]:
            return [{"cpu_usage_percent": 10.0}]
        return None

class DummyDatasets:
    def list_datasets(self):
        return ["ds1"]

@pytest.fixture
def client(monkeypatch):
    repo = DummyRepo()
    monkeypatch.setattr(backend, "repo", repo)
    monkeypatch.setattr(backend, "datasets", DummyDatasets())
    monkeypatch.setattr(backend.settings, "get_available_models", lambda: ["gpt2"])
    return TestClient(backend.app)

def test_get_benchmark(client):
    response = client.get("/api/v1/benchmarks/job1")
    assert response.status_code == 200
    assert response.json()["job_id"] == "job1"

def test_get_benchmark_not_found(client):
    response = client.get("/api/v1/benchmarks/unknown")
    assert response.status_code == 404

def test_list_benchmarks(client):
    response = client.get("/api/v1/benchmarks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["job_id"] == "job1"

def test_get_hardware_metrics(client):
    response = client.get("/api/v1/benchmarks/job1/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_hardware_metrics_not_found(client):
    response = client.get("/api/v1/benchmarks/unknown/metrics")
    assert response.status_code == 404

def test_get_models(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert response.json() == ["gpt2"]

def test_get_datasets(client):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert response.json() == ["ds1"]
