"""
Script para migração do banco de dados.
"""

import sqlite3
from pathlib import Path
import json
from datetime import datetime

from llm_bench_local.config.settings import settings
from llm_bench_local.persistence.database import Base, Database

def migrate_database():
    """Migra o banco de dados antigo para o novo formato."""
    db_path = settings.DB_PATH
    backup_path = f"{db_path}.backup"
    
    # Faz backup do banco atual
    if Path(db_path).exists():
        Path(db_path).rename(backup_path)
    
    # Cria novo banco com SQLAlchemy
    db = Database()
    
    # Migra dados do backup
    if Path(backup_path).exists():
        old_conn = sqlite3.connect(backup_path)
        old_conn.row_factory = sqlite3.Row
        
        # Migra benchmarks
        with db.session_scope() as session:
            cursor = old_conn.cursor()
            cursor.execute("SELECT * FROM benchmarks")
            
            for row in cursor.fetchall():
                benchmark = {
                    "job_id": row["job_id"],
                    "model_id": row["model_id"],
                    "task": row["task"],
                    "status": row["status"],
                    "config": json.loads(row["config"]),
                    "hardware_options": json.loads(row["hardware_options"]),
                    "results": json.loads(row["results"]) if row["results"] else None,
                    "created_at": datetime.fromisoformat(row["created_at"]),
                    "updated_at": datetime.fromisoformat(row["updated_at"])
                }
                
                session.execute(
                    "INSERT INTO benchmarks VALUES (:job_id, :model_id, :task, :status, :config, :hardware_options, :results, :created_at, :updated_at)",
                    benchmark
                )
            
            # Migra métricas de hardware
            cursor.execute("SELECT * FROM hardware_metrics")
            
            for row in cursor.fetchall():
                metrics = {
                    "job_id": row["job_id"],
                    "cpu_usage_percent": row["cpu_usage_percent"],
                    "ram_usage_gb": row["ram_usage_gb"],
                    "gpu_usage_percent": row["gpu_usage_percent"],
                    "vram_usage_gb": row["vram_usage_gb"],
                    "timestamp": datetime.fromisoformat(row["timestamp"])
                }
                
                session.execute(
                    "INSERT INTO hardware_metrics (job_id, cpu_usage_percent, ram_usage_gb, gpu_usage_percent, vram_usage_gb, timestamp) VALUES (:job_id, :cpu_usage_percent, :ram_usage_gb, :gpu_usage_percent, :vram_usage_gb, :timestamp)",
                    metrics
                )
        
        old_conn.close()
        
        # Remove o backup após migração bem-sucedida
        Path(backup_path).unlink()

if __name__ == "__main__":
    migrate_database() 