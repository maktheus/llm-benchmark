"""
Módulo para persistência de dados usando SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Float, JSON, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from contextlib import contextmanager

from llm_bench_local.config.settings import settings
from llm_bench_local.schemas.benchmark import BenchmarkResult

# Cria a base para os modelos SQLAlchemy
Base = declarative_base()


class BenchmarkRecord(Base):
    """Modelo SQLAlchemy para armazenar resultados de benchmark."""
    
    __tablename__ = "benchmarks"
    
    job_id = Column(String, primary_key=True)
    model_id = Column(String, nullable=False)
    task = Column(String, nullable=False)
    status = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    hardware_options = Column(JSON, nullable=False)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class HardwareMetricsRecord(Base):
    """Modelo SQLAlchemy para armazenar métricas de hardware."""
    
    __tablename__ = "hardware_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey('benchmarks.job_id'), nullable=False)
    cpu_usage_percent = Column(Float, nullable=True)
    ram_usage_gb = Column(Float, nullable=True)
    gpu_usage_percent = Column(Float, nullable=True)
    vram_usage_gb = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class Database:
    def __init__(self):
        """Inicializa a conexão com o banco de dados."""
        self.db_path = settings.DB_PATH
        self._ensure_db_exists()
        
        # Cria o engine do SQLAlchemy
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # Cria as tabelas
        Base.metadata.create_all(self.engine)
        
        # Cria a sessão
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_db_exists(self) -> None:
        """Garante que o diretório do banco de dados existe."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def get_session(self) -> Session:
        """Retorna uma nova sessão do SQLAlchemy."""
        return self.Session()

    @contextmanager
    def session_scope(self):
        """Context manager para gerenciar sessões do SQLAlchemy."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_benchmark(self, result: BenchmarkResult):
        """Salva um resultado de benchmark.
        
        Args:
            result: Resultado do benchmark a ser salvo
        """
        session = self.get_session()
        try:
            record = BenchmarkRecord(
                job_id=result.job_id,
                model_id=result.model_id,
                task=result.task,
                config=result.config.dict(),
                hardware_options=result.hardware_options.dict(),
                results=result.metrics,
                status=result.status,
                updated_at=datetime.fromisoformat(result.timestamp)
            )
            session.add(record)
        finally:
            session.close()
    
    def get_benchmark(self, job_id: str) -> Optional[BenchmarkResult]:
        """Recupera um resultado de benchmark pelo ID.
        
        Args:
            job_id: ID do benchmark
            
        Returns:
            BenchmarkResult se encontrado, None caso contrário
        """
        session = self.get_session()
        try:
            record = session.query(BenchmarkRecord).filter_by(job_id=job_id).first()
            if not record:
                return None
            
            return BenchmarkResult(
                job_id=record.job_id,
                model_id=record.model_id,
                task=record.task,
                config=record.config,
                hardware_options=record.hardware_options,
                metrics=record.results,
                status=record.status,
                timestamp=record.updated_at.isoformat()
            )
        finally:
            session.close()
    
    def list_benchmarks(
        self,
        model_id: Optional[str] = None,
        task: Optional[str] = None,
        limit: int = 100
    ) -> List[BenchmarkResult]:
        """Lista resultados de benchmarks com filtros opcionais.
        
        Args:
            model_id: Filtrar por ID do modelo
            task: Filtrar por tarefa
            limit: Limite de resultados
            
        Returns:
            Lista de BenchmarkResult
        """
        session = self.get_session()
        try:
            query = session.query(BenchmarkRecord)
            
            if model_id:
                query = query.filter_by(model_id=model_id)
            if task:
                query = query.filter_by(task=task)
            
            records = query.order_by(BenchmarkRecord.updated_at.desc()).limit(limit).all()
            
            return [
                BenchmarkResult(
                    job_id=record.job_id,
                    model_id=record.model_id,
                    task=record.task,
                    config=record.config,
                    hardware_options=record.hardware_options,
                    metrics=record.results,
                    status=record.status,
                    timestamp=record.updated_at.isoformat()
                )
                for record in records
            ]
        finally:
            session.close() 