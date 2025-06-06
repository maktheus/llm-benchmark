import pytest
from unittest.mock import Mock, patch
import torch

from llm_bench_local.core.model import ModelRunner

@pytest.fixture
def mock_settings():
    """Fixture para as configurações mockadas."""
    with patch("llm_bench_local.core.model.settings") as mock:
        mock.get_model_config.return_value = {
            "name": "GPT-2",
            "provider": "Hugging Face",
            "model_id": "gpt2",
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }
        yield mock

@pytest.fixture
def mock_transformers():
    """Fixture para os módulos do transformers mockados."""
    with patch("llm_bench_local.core.model.AutoModelForCausalLM") as mock_model, \
         patch("llm_bench_local.core.model.AutoTokenizer") as mock_tokenizer:
        
        # Mock para o modelo
        model_instance = Mock()
        model_instance.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
        mock_model.from_pretrained.return_value = model_instance
        
        # Mock para o tokenizer
        tokenizer_instance = Mock()
        tokenizer_instance.eos_token_id = 50256
        tokenizer_instance.decode.return_value = "Generated text"
        mock_tokenizer.from_pretrained.return_value = tokenizer_instance
        
        yield mock_model, mock_tokenizer

@pytest.fixture
def mock_torch():
    """Fixture para o módulo torch mockado."""
    with patch("llm_bench_local.core.model.torch") as mock:
        mock.cuda.is_available.return_value = True
        yield mock

def test_model_runner_initialization(mock_settings, mock_torch):
    """Testa a inicialização do ModelRunner."""
    runner = ModelRunner("gpt2")
    
    assert runner.model_id == "gpt2"
    assert runner.model_config == mock_settings.get_model_config.return_value
    assert runner.device == "cuda"
    assert runner.model is None
    assert runner.tokenizer is None

def test_load_model(mock_settings, mock_transformers, mock_torch):
    """Testa o carregamento do modelo."""
    mock_model, mock_tokenizer = mock_transformers
    runner = ModelRunner("gpt2")
    
    runner._load_model()
    
    mock_model.from_pretrained.assert_called_once_with(
        "gpt2",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    mock_tokenizer.from_pretrained.assert_called_once_with("gpt2")

def test_generate_text(mock_settings, mock_transformers, mock_torch):
    """Testa a geração de texto."""
    mock_model, mock_tokenizer = mock_transformers
    runner = ModelRunner("gpt2")
    
    output = runner.generate(
        prompt="Hello, world!",
        max_tokens=10,
        temperature=0.7,
        top_p=0.9,
        use_gpu=True
    )
    
    assert output == "Generated text"
    mock_model.from_pretrained.return_value.generate.assert_called_once()
    mock_tokenizer.from_pretrained.return_value.decode.assert_called_once()

def test_generate_text_cpu(mock_settings, mock_transformers, mock_torch):
    """Testa a geração de texto na CPU."""
    mock_model, mock_tokenizer = mock_transformers
    mock_torch.cuda.is_available.return_value = False
    
    runner = ModelRunner("gpt2")
    runner.device = "cuda"  # Simula que estava na GPU
    runner.model = None  # Força recarregar o modelo
    
    output = runner.generate(
        prompt="Hello, world!",
        max_tokens=10,
        temperature=0.7,
        top_p=0.9,
        use_gpu=False
    )
    
    assert output == "Generated text"
    mock_model.from_pretrained.assert_called_once_with(
        "gpt2",
        torch_dtype=torch.float32,
        device_map=None
    )

def test_get_model_info(mock_settings, mock_torch):
    """Testa a obtenção de informações do modelo."""
    runner = ModelRunner("gpt2")
    info = runner.get_model_info()
    
    assert info["model_id"] == "gpt2"
    assert info["provider"] == "Hugging Face"
    assert info["device"] == "cuda"
    assert info["max_tokens"] == 1024
    assert info["parameters"] == "unknown"

def test_model_not_found(mock_settings):
    """Testa o comportamento quando o modelo não é encontrado."""
    mock_settings.get_model_config.return_value = None
    
    with pytest.raises(ValueError, match="Modelo gpt2 não encontrado na configuração"):
        ModelRunner("gpt2") 