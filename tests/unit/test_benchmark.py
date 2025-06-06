import pytest
from unittest.mock import Mock, patch

from llm_bench_local.core.benchmark import Benchmark
from llm_bench_local.core.model import ModelRunner
from llm_bench_local.hardware.monitor import HardwareMonitor
from llm_bench_local.persistence.crud import BenchmarkRepository

@pytest.fixture
def mock_model_runner():
    """Fixture para o ModelRunner mockado."""
    with patch("llm_bench_local.core.benchmark.ModelRunner") as mock:
        instance = mock.return_value
        instance.generate.return_value = "Generated text"
        yield instance

@pytest.fixture
def mock_hardware_monitor():
    """Fixture para o HardwareMonitor mockado."""
    with patch("llm_bench_local.core.benchmark.HardwareMonitor") as mock:
        instance = mock.return_value
        instance.start_monitoring.return_value = None
        instance.stop_monitoring.return_value = {
            "cpu_usage_percent": 50.0,
            "ram_usage_gb": 4.0,
            "gpu_usage_percent": 80.0,
            "vram_usage_gb": 2.0
        }
        yield instance

@pytest.fixture
def mock_repository():
    """Fixture para o BenchmarkRepository mockado."""
    with patch("llm_bench_local.core.benchmark.BenchmarkRepository") as mock:
        instance = mock.return_value
        yield instance

def test_benchmark_initialization(mock_model_runner, mock_hardware_monitor, mock_repository):
    """Testa a inicialização do benchmark."""
    benchmark = Benchmark(
        model_id="gpt2",
        prompt="Test prompt",
        task="text-generation",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
        use_gpu=True
    )
    
    assert benchmark.model_id == "gpt2"
    assert benchmark.prompt == "Test prompt"
    assert benchmark.task == "text-generation"
    assert benchmark.max_tokens == 100
    assert benchmark.temperature == 0.7
    assert benchmark.top_p == 0.9
    assert benchmark.use_gpu == True

def test_benchmark_execution(mock_model_runner, mock_hardware_monitor, mock_repository):
    """Testa a execução do benchmark."""
    benchmark = Benchmark(
        model_id="gpt2",
        prompt="Test prompt",
        task="text-generation"
    )
    
    results = benchmark.execute()
    
    assert "model" in results
    assert "task" in results
    assert "duration" in results
    assert "tokens_generated" in results
    assert "output" in results
    assert "hardware_metrics" in results
    
    # Verifica se os métodos foram chamados
    mock_model_runner.generate.assert_called_once()
    mock_hardware_monitor.start_monitoring.assert_called_once()
    mock_hardware_monitor.stop_monitoring.assert_called_once()
    mock_repository.create_benchmark.assert_called_once()
    mock_repository.update_benchmark_status.assert_called_once()

def test_benchmark_error_handling(mock_model_runner, mock_hardware_monitor, mock_repository):
    """Testa o tratamento de erros durante a execução do benchmark."""
    mock_model_runner.generate.side_effect = Exception("Test error")
    
    benchmark = Benchmark(
        model_id="gpt2",
        prompt="Test prompt",
        task="text-generation"
    )
    
    with pytest.raises(Exception):
        benchmark.execute()
    
    # Verifica se o status foi atualizado para FAILED
    mock_repository.update_benchmark_status.assert_called_with(
        benchmark.job_id,
        "FAILED",
        {"error": "Test error"}
    )

def test_get_benchmark_status(mock_repository):
    """Testa a obtenção do status do benchmark."""
    mock_repository.get_benchmark.return_value = {
        "job_id": "test-id",
        "status": "COMPLETED"
    }
    
    benchmark = Benchmark(
        model_id="gpt2",
        prompt="Test prompt",
        task="text-generation"
    )
    
    status = benchmark.get_status()
    assert status["job_id"] == "test-id"
    assert status["status"] == "COMPLETED"
    mock_repository.get_benchmark.assert_called_once_with(benchmark.job_id)

def test_get_hardware_metrics(mock_repository):
    """Testa a obtenção das métricas de hardware."""
    mock_repository.get_hardware_metrics.return_value = [
        {
            "cpu_usage_percent": 50.0,
            "ram_usage_gb": 4.0,
            "gpu_usage_percent": 80.0,
            "vram_usage_gb": 2.0
        }
    ]
    
    benchmark = Benchmark(
        model_id="gpt2",
        prompt="Test prompt",
        task="text-generation"
    )
    
    metrics = benchmark.get_hardware_metrics()
    assert len(metrics) == 1
    assert metrics[0]["cpu_usage_percent"] == 50.0
    mock_repository.get_hardware_metrics.assert_called_once_with(benchmark.job_id) 