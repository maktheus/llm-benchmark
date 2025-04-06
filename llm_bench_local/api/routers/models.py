"""
Router para endpoints de modelos.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

from llm_bench_local.config.settings import settings

router = APIRouter()


@router.get("/models/")
async def list_models() -> List[str]:
    """Lista os modelos disponíveis.
    
    Returns:
        Lista de IDs dos modelos disponíveis
    """
    try:
        # Lista modelos do Hugging Face
        models = []
        
        # Adiciona modelos locais
        if os.path.exists(settings.MODEL_CACHE_DIR):
            for root, _, files in os.walk(settings.MODEL_CACHE_DIR):
                for file in files:
                    if file.endswith(('.gguf', '.bin')):
                        models.append(os.path.join(root, file))
        
        # Adiciona modelo padrão
        models.append(settings.DEFAULT_MODEL)
        
        return models
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar modelos: {str(e)}"
        )


@router.get("/models/{model_id}/info")
async def get_model_info(model_id: str):
    """Obtém informações sobre um modelo específico.
    
    Args:
        model_id: ID do modelo
        
    Returns:
        Informações do modelo
        
    Raises:
        HTTPException: Se o modelo não for encontrado
    """
    try:
        # Verifica se é um modelo local
        if os.path.exists(model_id):
            return {
                "id": model_id,
                "type": "local",
                "format": model_id.split('.')[-1]
            }
        
        # Tenta carregar informações do Hugging Face
        try:
            config = AutoModelForCausalLM.from_pretrained(
                model_id,
                trust_remote_code=True
            ).config
            
            return {
                "id": model_id,
                "type": "huggingface",
                "architecture": config.architectures[0] if config.architectures else "unknown",
                "model_type": config.model_type,
                "vocab_size": config.vocab_size,
                "hidden_size": config.hidden_size,
                "num_attention_heads": config.num_attention_heads,
                "num_hidden_layers": config.num_hidden_layers
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Modelo {model_id} não encontrado: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter informações do modelo: {str(e)}"
        ) 