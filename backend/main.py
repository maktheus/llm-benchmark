"""Aplicação FastAPI do Backend."""

from fastapi import FastAPI

app = FastAPI(title="LLM Bench Backend")


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    """Endpoint de verificação de saúde."""
    return {"status": "ok"}


@app.post("/api/v1/benchmarks")
async def create_benchmark() -> dict[str, str]:
    """Endpoint placeholder para criação de benchmarks."""
    return {"message": "benchmark criado"}
