import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

from llm_bench_local.persistence.crud import BenchmarkRepository
from llm_bench_local.persistence.database import DatabaseConnection

@pytest.fixture
def mock_db():
    """Fixture para o DatabaseConnection mockado."""
    with patch("llm_bench_local.persistence.crud.DatabaseConnection") as mock:
        instance = mock.return_value
        yield instance

@pytest.fixture
def repository(mock_db):
    """Fixture para o BenchmarkRepository."""
    return BenchmarkRepository("test.db", ensure_tables=False)

def test_create_benchmark(repository, mock_db):
    """Testa a criação de um benchmark."""
    job_id = "test-job"
    model_id = "gpt2"
    task = "text-generation"
    config = {
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9
    }
    hardware_options = {
        "use_gpu": True,
        "monitor_interval": 1.0
    }
    
    repository.create_benchmark(job_id, model_id, task, config, hardware_options)
    
    mock_db.execute_query.assert_called_once()
    call_args = mock_db.execute_query.call_args[0]
    assert "INSERT INTO benchmarks" in call_args[0]
    assert call_args[1][0] == job_id
    assert call_args[1][1] == model_id
    assert call_args[1][2] == task
    assert call_args[1][3] == "PENDING"
    assert json.loads(call_args[1][4]) == config
    assert json.loads(call_args[1][5]) == hardware_options

def test_update_benchmark_status(repository, mock_db):
    """Testa a atualização do status de um benchmark."""
    job_id = "test-job"
    status = "COMPLETED"
    results = {
        "duration": 1.5,
        "tokens_generated": 100
    }
    
    repository.update_benchmark_status(job_id, status, results)
    
    mock_db.execute_query.assert_called_once()
    call_args = mock_db.execute_query.call_args[0]
    assert "UPDATE benchmarks" in call_args[0]
    assert call_args[1][0] == status
    assert json.loads(call_args[1][1]) == results
    assert call_args[1][2] == job_id

def test_get_benchmark(repository, mock_db):
    """Testa a obtenção de um benchmark."""
    job_id = "test-job"
    mock_db.execute_query.return_value = [{
        "job_id": job_id,
        "model_id": "gpt2",
        "task": "text-generation",
        "status": "COMPLETED",
        "config": json.dumps({"max_tokens": 100}),
        "hardware_options": json.dumps({"use_gpu": True}),
        "results": json.dumps({"duration": 1.5}),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }]
    
    benchmark = repository.get_benchmark(job_id)
    
    assert benchmark["job_id"] == job_id
    assert benchmark["model_id"] == "gpt2"
    assert benchmark["task"] == "text-generation"
    assert benchmark["status"] == "COMPLETED"
    assert isinstance(benchmark["config"], dict)
    assert isinstance(benchmark["hardware_options"], dict)
    assert isinstance(benchmark["results"], dict)

def test_list_benchmarks(repository, mock_db):
    """Testa a listagem de benchmarks."""
    mock_db.execute_query.return_value = [
        {
            "job_id": "test-job-1",
            "model_id": "gpt2",
            "task": "text-generation",
            "status": "COMPLETED",
            "config": json.dumps({"max_tokens": 100}),
            "hardware_options": json.dumps({"use_gpu": True}),
            "results": json.dumps({"duration": 1.5}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "job_id": "test-job-2",
            "model_id": "gpt2",
            "task": "text-generation",
            "status": "PENDING",
            "config": json.dumps({"max_tokens": 100}),
            "hardware_options": json.dumps({"use_gpu": True}),
            "results": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    benchmarks = repository.list_benchmarks(limit=10, offset=0, status="COMPLETED")
    
    assert len(benchmarks) == 1
    assert benchmarks[0]["job_id"] == "test-job-1"
    assert benchmarks[0]["status"] == "COMPLETED"
    assert isinstance(benchmarks[0]["config"], dict)
    assert isinstance(benchmarks[0]["hardware_options"], dict)
    assert isinstance(benchmarks[0]["results"], dict)

def test_save_hardware_metrics(repository, mock_db):
    """Testa o salvamento de métricas de hardware."""
    job_id = "test-job"
    metrics = {
        "cpu_usage_percent": 50.0,
        "ram_usage_gb": 4.0,
        "gpu_usage_percent": 80.0,
        "vram_usage_gb": 2.0
    }
    
    repository.save_hardware_metrics(job_id, metrics)
    
    mock_db.execute_query.assert_called_once()
    call_args = mock_db.execute_query.call_args[0]
    assert "INSERT INTO hardware_metrics" in call_args[0]
    assert call_args[1][0] == job_id
    assert call_args[1][1] == metrics["cpu_usage_percent"]
    assert call_args[1][2] == metrics["ram_usage_gb"]
    assert call_args[1][3] == metrics["gpu_usage_percent"]
    assert call_args[1][4] == metrics["vram_usage_gb"]

def test_get_hardware_metrics(repository, mock_db):
    """Testa a obtenção de métricas de hardware."""
    job_id = "test-job"
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "job_id": job_id,
            "cpu_usage_percent": 50.0,
            "ram_usage_gb": 4.0,
            "gpu_usage_percent": 80.0,
            "vram_usage_gb": 2.0,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    metrics = repository.get_hardware_metrics(job_id)
    
    assert len(metrics) == 1
    assert metrics[0]["job_id"] == job_id
    assert metrics[0]["cpu_usage_percent"] == 50.0
    assert metrics[0]["ram_usage_gb"] == 4.0
    assert metrics[0]["gpu_usage_percent"] == 80.0
    assert metrics[0]["vram_usage_gb"] == 2.0 