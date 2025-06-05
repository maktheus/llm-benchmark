"""Implementação simplificada de um pipeline RAG."""

from __future__ import annotations

from typing import List

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from llm_bench_local.datasets import DatasetManager


class SimpleRAGPipeline:
    """Pipeline básico de Retrieval-Augmented Generation."""

    def __init__(
        self,
        model_id: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.embedder = SentenceTransformer(embedding_model)
        self.index = None
        self.documents: List[str] = []

    def build_index(self, dataset_name: str, field: str = "text") -> None:
        """Carrega um dataset e constrói um índice FAISS simples."""
        manager = DatasetManager()
        ds = manager.load(dataset_name)
        texts = ds["train"][field]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings).astype("float32"))
        self.documents = list(texts)

    def query(self, question: str, top_k: int = 3, max_new_tokens: int = 64) -> str:
        """Executa a geração baseada em recuperação."""
        if self.index is None:
            raise RuntimeError("Índice não construído")
        q_emb = self.embedder.encode([question])
        dists, idx = self.index.search(np.array(q_emb).astype("float32"), top_k)
        context = "\n".join(self.documents[i] for i in idx[0])
        prompt = f"{context}\n\nQuestion: {question}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
