from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm_bench_local.datasets import DatasetManager

router = APIRouter()
manager = DatasetManager()


class DatasetRegistration(BaseModel):
    name: str
    hf_id: str


@router.post("/datasets")
async def register_dataset(payload: DatasetRegistration):
    """Registra um novo dataset."""
    try:
        manager.register_dataset(payload.name, payload.hf_id)
        return {"message": "registered"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/datasets")
async def list_datasets():
    """Lista datasets registrados."""
    return manager.list_datasets()
