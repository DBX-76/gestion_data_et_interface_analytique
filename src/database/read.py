# src/database/read.py
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def get_operations(limit=100):
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    if limit is None:
        query = "SELECT * FROM operations"
    else:
        query = f"SELECT * FROM operations LIMIT {limit}"
    return pd.read_sql(query, engine)

# src/database/read.py

def get_operation_by_id(operation_id: int):
    """Récupère une opération par son ID, directement depuis la base."""
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    query = text("SELECT * FROM operations WHERE operation_id = :operation_id")
    df = pd.read_sql(query, engine, params={"operation_id": operation_id})
    return df if not df.empty else None

def get_operation_id_range():
    """Récupère le min et max des operation_id dans la base."""
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    query = text("SELECT MIN(operation_id) as min_id, MAX(operation_id) as max_id FROM operations")
    result = pd.read_sql(query, engine)
    return result.iloc[0]['min_id'], result.iloc[0]['max_id']

def get_operations_count():
    """Récupère le nombre total d'opérations dans la base."""
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    query = text("SELECT COUNT(*) as count FROM operations")
    result = pd.read_sql(query, engine)
    return int(result.iloc[0]['count'])

def get_operations_by_id_range(min_id: int, max_id: int):
    """Récupère les opérations dans un intervalle d'IDs."""
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    query = text("SELECT * FROM operations WHERE operation_id BETWEEN :min_id AND :max_id ORDER BY operation_id")
    return pd.read_sql(query, engine, params={"min_id": min_id, "max_id": max_id})

def get_audit_log(limit=100):
    """Récupère les entrées du journal d'audit."""
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
    if limit is None:
        query = "SELECT * FROM audit_log ORDER BY timestamp DESC"
    else:
        query = f"SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT {limit}"
    return pd.read_sql(query, engine)