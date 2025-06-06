"""Camada simples de persistencia usando SQLite."""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional, Dict

from llm_bench_local.persistence.database import DatabaseConnection


class BenchmarkRepository:
    """Operacoes CRUD para benchmarks."""

    def __init__(self, db_path: str, ensure_tables: bool = True):
        self.db = DatabaseConnection(db_path)
        if ensure_tables:
            self._ensure_tables()

    def _ensure_tables(self) -> None:
        self.db.execute_query(
            """
            CREATE TABLE IF NOT EXISTS benchmarks (
                job_id TEXT PRIMARY KEY,
                model_id TEXT NOT NULL,
                task TEXT NOT NULL,
                status TEXT NOT NULL,
                config TEXT NOT NULL,
                hardware_options TEXT NOT NULL,
                results TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.db.execute_query(
            """
            CREATE TABLE IF NOT EXISTS hardware_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                cpu_usage_percent REAL,
                ram_usage_gb REAL,
                gpu_usage_percent REAL,
                vram_usage_gb REAL,
                timestamp TEXT NOT NULL
            )
            """
        )

    def create_benchmark(
        self,
        job_id: str,
        model_id: str,
        task: str,
        config: Dict,
        hardware_options: Dict,
    ) -> None:
        now = datetime.utcnow().isoformat()
        self.db.execute_query(
            """
            INSERT INTO benchmarks (
                job_id, model_id, task, status, config, hardware_options,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                job_id,
                model_id,
                task,
                "PENDING",
                json.dumps(config),
                json.dumps(hardware_options),
                now,
                now,
            ],
        )

    def update_benchmark_status(
        self, job_id: str, status: str, results: Optional[Dict] = None
    ) -> None:
        self.db.execute_query(
            """
            UPDATE benchmarks
            SET status = ?, results = ?
            WHERE job_id = ?
            """,
            [status, json.dumps(results) if results is not None else None, job_id],
        )

    def get_benchmark(self, job_id: str) -> Optional[Dict]:
        rows = self.db.execute_query(
            "SELECT * FROM benchmarks WHERE job_id = ?", [job_id]
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "job_id": row["job_id"],
            "model_id": row["model_id"],
            "task": row["task"],
            "status": row["status"],
            "config": json.loads(row["config"]),
            "hardware_options": json.loads(row["hardware_options"]),
            "results": json.loads(row["results"]) if row["results"] else None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def list_benchmarks(
        self, limit: int = 10, offset: int = 0, status: Optional[str] = None
    ) -> List[Dict]:
        query = "SELECT * FROM benchmarks"
        params: List = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.db.execute_query(query, params)
        results = []
        for row in rows:
            results.append(
                {
                    "job_id": row["job_id"],
                    "model_id": row["model_id"],
                    "task": row["task"],
                    "status": row["status"],
                    "config": json.loads(row["config"]),
                    "hardware_options": json.loads(row["hardware_options"]),
                    "results": json.loads(row["results"]) if row["results"] else None,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        if status:
            results = [r for r in results if r["status"] == status]
        return results

    def save_hardware_metrics(self, job_id: str, metrics: Dict[str, float]) -> None:
        self.db.execute_query(
            """
            INSERT INTO hardware_metrics (
                job_id, cpu_usage_percent, ram_usage_gb,
                gpu_usage_percent, vram_usage_gb, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                job_id,
                metrics.get("cpu_usage_percent"),
                metrics.get("ram_usage_gb"),
                metrics.get("gpu_usage_percent"),
                metrics.get("vram_usage_gb"),
                datetime.utcnow().isoformat(),
            ],
        )

    def get_hardware_metrics(self, job_id: str) -> List[Dict]:
        rows = self.db.execute_query(
            "SELECT * FROM hardware_metrics WHERE job_id = ? ORDER BY timestamp",
            [job_id],
        )
        return [dict(row) for row in rows]
