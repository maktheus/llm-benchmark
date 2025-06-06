#!/usr/bin/env python3
"""
Script CLI para executar benchmarks.
"""

import argparse
import json
import sys
from typing import Dict, Optional
import requests

from llm_bench_local.config.settings import settings


def run_benchmark(
    model_id: str,
    prompt: str,
    task: str = "text-generation",
    max_tokens: int = 100,
    temperature: float = 0.7,
    top_p: float = 0.95,
    use_gpu: bool = True,
    api_url: str = "http://localhost:8000"
) -> Dict:
    """Executa um benchmark via API.
    
    Args:
        model_id: ID do modelo a ser testado
        prompt: Prompt para o modelo
        task: Tarefa a ser executada
        max_tokens: Número máximo de tokens a serem gerados
        temperature: Temperatura para sampling
        top_p: Top-p para sampling
        use_gpu: Se deve usar GPU
        api_url: URL da API
        
    Returns:
        Resultado do benchmark
    """
    # Prepara a requisição
    data = {
        "model_id": model_id,
        "task": task,
        "config": {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        },
        "hardware_options": {
            "use_gpu": use_gpu
        }
    }
    
    # Envia a requisição
    try:
        response = requests.post(
            f"{api_url}/api/v1/benchmarks/",
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao executar benchmark: {e}")
        sys.exit(1)


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Executa benchmarks de LLMs via CLI"
    )
    
    parser.add_argument(
        "--model",
        required=True,
        help="ID do modelo a ser testado"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt para o modelo"
    )
    parser.add_argument(
        "--task",
        default="text-generation",
        help="Tarefa a ser executada"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=100,
        help="Número máximo de tokens a serem gerados"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperatura para sampling"
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p para sampling"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Não usar GPU"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="URL da API"
    )
    
    args = parser.parse_args()
    
    # Executa o benchmark
    result = run_benchmark(
        model_id=args.model,
        prompt=args.prompt,
        task=args.task,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        use_gpu=not args.no_gpu,
        api_url=args.api_url
    )
    
    # Imprime o resultado
    print("\nResultado do Benchmark:")
    print("=" * 50)
    print(f"Modelo: {result['model_id']}")
    print(f"Tarefa: {result['task']}")
    print(f"Duração: {result['duration']:.2f}s")
    print(f"Tokens Gerados: {result['metrics']['tokens_generated']}")
    print("\nSaída:")
    print("-" * 50)
    print(result['output'])
    print("\nMétricas de Hardware:")
    print("-" * 50)
    for metric in result['hardware_metrics']:
        print(f"CPU: {metric['cpu_usage']:.1f}%")
        print(f"Memória: {metric['memory_usage']:.1f}%")
        if metric['gpu_usage'] is not None:
            print(f"GPU: {metric['gpu_usage']:.1f}%")
            print(f"Memória GPU: {metric['gpu_memory_usage']:.1f}%")
            print(f"Temperatura GPU: {metric['gpu_temperature']:.1f}°C")


if __name__ == "__main__":
    main() 