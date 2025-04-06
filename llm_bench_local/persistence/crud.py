"""
Módulo para operações CRUD usando SQLAlchemy.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from llm_bench_local.persistence.database import BenchmarkRecord, HardwareMetricsRecord
from llm_bench_local.schemas.benchmark import BenchmarkResult

class BenchmarkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_benchmark(self, job_id: str, model_id: str, task: str, 
                        config: Dict, hardware_options: Dict) -> None:
        """Cria um novo benchmark no banco de dados."""
        benchmark = BenchmarkRecord(
            job_id=job_id,
            model_id=model_id,
            task=task,
            status="PENDING",
            config=config,
            hardware_options=hardware_options,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(benchmark)
        self.session.commit()

    def update_benchmark_status(self, job_id: str, status: str) -> None:
        """Atualiza o status de um benchmark."""
        stmt = (
            update(BenchmarkRecord)
            .where(BenchmarkRecord.job_id == job_id)
            .values(
                status=status,
                updated_at=datetime.utcnow()
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def save_benchmark_results(self, job_id: str, results: Dict) -> None:
        """Salva os resultados de um benchmark."""
        stmt = (
            update(BenchmarkRecord)
            .where(BenchmarkRecord.job_id == job_id)
            .values(
                results=results,
                updated_at=datetime.utcnow()
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def get_benchmark(self, job_id: str) -> Optional[BenchmarkRecord]:
        """Recupera um benchmark pelo ID do job."""
        stmt = select(BenchmarkRecord).where(BenchmarkRecord.job_id == job_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        return result

    def list_benchmarks(
        self,
        model_id: Optional[str] = None,
        task: Optional[str] = None,
        limit: int = 100
    ) -> List[BenchmarkRecord]:
        """Lista benchmarks com filtros opcionais."""
        query = select(BenchmarkRecord)
        
        if model_id:
            query = query.where(BenchmarkRecord.model_id == model_id)
        if task:
            query = query.where(BenchmarkRecord.task == task)
            
        query = query.order_by(BenchmarkRecord.created_at.desc()).limit(limit)
        result = self.session.execute(query).scalars().all()
        return list(result)

    def delete_benchmark(self, job_id: str) -> None:
        """Remove um benchmark do banco de dados."""
        stmt = delete(BenchmarkRecord).where(BenchmarkRecord.job_id == job_id)
        self.session.execute(stmt)
        self.session.commit()


class HardwareMetricsRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_metrics(self, job_id: str, metrics: Dict[str, float]) -> None:
        """Salva métricas de hardware para um job."""
        hardware_metrics = HardwareMetricsRecord(
            job_id=job_id,
            cpu_usage_percent=metrics.get('cpu_usage_percent'),
            ram_usage_gb=metrics.get('ram_usage_gb'),
            gpu_usage_percent=metrics.get('gpu_usage_percent'),
            vram_usage_gb=metrics.get('vram_usage_gb'),
            timestamp=datetime.utcnow()
        )
        self.session.add(hardware_metrics)
        self.session.commit()

    def get_metrics(self, job_id: str) -> List[HardwareMetricsRecord]:
        """Recupera todas as métricas de hardware para um job."""
        stmt = (
            select(HardwareMetricsRecord)
            .where(HardwareMetricsRecord.job_id == job_id)
            .order_by(HardwareMetricsRecord.timestamp)
        )
        result = self.session.execute(stmt).scalars().all()
        return list(result) 