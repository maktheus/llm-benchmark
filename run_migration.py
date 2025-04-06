#!/usr/bin/env python3
"""
Script para executar a migração do banco de dados.
"""

from llm_bench_local.persistence.migrations import migrate_database

if __name__ == "__main__":
    print("Iniciando migração do banco de dados...")
    migrate_database()
    print("Migração concluída com sucesso!") 