from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm_bench_local.rag import SimpleRAGPipeline

router = APIRouter()

# Pipeline global simples para demonstração
type_pipeline = SimpleRAGPipeline | None
pipeline: type_pipeline = None


class BuildRequest(BaseModel):
    model_id: str
    dataset: str
    field: str = "text"


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    max_new_tokens: int = 64


@router.post("/rag/build")
async def build_index(req: BuildRequest):
    """Constrói o índice do pipeline RAG."""
    global pipeline
    try:
        pipeline = SimpleRAGPipeline(req.model_id)
        pipeline.build_index(req.dataset, field=req.field)
        return {"message": "index built"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/rag/query")
async def query(req: QueryRequest):
    """Executa uma consulta no pipeline RAG."""
    if pipeline is None:
        raise HTTPException(status_code=400, detail="Index not built")
    try:
        output = pipeline.query(
            req.question, top_k=req.top_k, max_new_tokens=req.max_new_tokens
        )
        return {"output": output}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
