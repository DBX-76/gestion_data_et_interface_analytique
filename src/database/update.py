# src/database/update.py
"""
Fonctions pour mettre à jour les opérations et journaliser les changements.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

def update_operation(operation_id: int, updates: dict, changed_by: str = "operator"):
    """
    Met à jour une opération et logue l'action.
    
    Args:
        operation_id: ID de l'opération à modifier
        updates: dict {colonne: nouvelle_valeur}
        changed_by: utilisateur ayant fait la modification
    
    Returns:
        bool: True si succès, False sinon
    """
    if not updates:
        return True  # rien à faire

    # Construire la clause SET dynamiquement
    reserved_keywords = {"cross"}
    set_clause = ", ".join([
        f'"{key}" = :{key}' if key in reserved_keywords else f"{key} = :{key}" 
        for key in updates.keys()
    ])
    updates["operation_id"] = operation_id

    update_query = text(f"""
        UPDATE operations
        SET {set_clause}
        WHERE operation_id = :operation_id
    """)

    log_query = text("""
        INSERT INTO audit_log (table_name, operation, changed_by, operation_id)
        VALUES ('operations', 'UPDATE', :changed_by, :operation_id)
    """)

    try:
        with engine.connect() as conn:
            with conn.begin():
                # 1. Mettre à jour l'opération
                result = conn.execute(update_query, updates)
                if result.rowcount == 0:
                    raise ValueError(f"Aucune opération trouvée avec operation_id = {operation_id}")

                # 2. Journaliser
                conn.execute(log_query, {
                    "changed_by": changed_by,
                    "operation_id": operation_id
                })
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")
        return False