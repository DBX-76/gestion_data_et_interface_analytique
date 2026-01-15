# src/database/read.py
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def get_operations(limit=100):
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DB_URL)
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