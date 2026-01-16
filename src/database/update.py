# src/database/update.py
"""
Fonctions pour mettre à jour les opérations et journaliser les changements.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL, pool_pre_ping=True)

def update_operation(operation_id: int, updates: dict, changed_by: str = "operator"):
    """
    Met à jour une opération et logue chaque changement détaillé.

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

    select_query = text("SELECT * FROM operations WHERE operation_id = :operation_id")
    log_query = text("""
        INSERT INTO audit_log (table_name, operation, changed_by, operation_id, column_name, old_value, new_value)
        VALUES ('operations', 'UPDATE', :changed_by, :operation_id, :column_name, :old_value, :new_value)
    """)

    try:
        print(f"Début de mise à jour pour operation_id={operation_id}, updates={updates}")
        with engine.connect() as conn:
            with conn.begin():
                # 1. Récupérer les anciennes valeurs
                result = conn.execute(select_query, {"operation_id": operation_id}).fetchone()
                if result is None:
                    print(f"Aucune opération trouvée avec operation_id = {operation_id}")
                    raise ValueError(f"Aucune opération trouvée avec operation_id = {operation_id}")
                old_values = dict(result._mapping)
                print(f"Anciennes valeurs récupérées: {old_values}")

                # 2. Mettre à jour l'opération
                print(f"Exécution de la requête UPDATE: {update_query}")
                result = conn.execute(update_query, updates)
                print(f"Résultat UPDATE: rowcount={result.rowcount}")
                if result.rowcount == 0:
                    raise ValueError(f"Aucune opération trouvée avec operation_id = {operation_id}")

                # 3. Journaliser chaque changement
                for column, new_value in updates.items():
                    if column != "operation_id":  # Ne pas logger operation_id
                        old_value = old_values.get(column)
                        # Convertir en string pour le stockage
                        old_str = str(old_value) if old_value is not None else None
                        new_str = str(new_value) if new_value is not None else None

                        print(f"Logging changement: {column} de '{old_str}' à '{new_str}'")
                        conn.execute(log_query, {
                            "changed_by": changed_by,
                            "operation_id": operation_id,
                            "column_name": column,
                            "old_value": old_str,
                            "new_value": new_str
                        })
        print("Mise à jour réussie")
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_operation(operation_id: int, changed_by: str = "operator"):
    """
    Supprime une opération et logue l'action.

    Args:
        operation_id: ID de l'opération à supprimer
        changed_by: utilisateur ayant fait la suppression

    Returns:
        bool: True si succès, False sinon
    """
    delete_query = text("DELETE FROM operations WHERE operation_id = :operation_id")

    log_query = text("""
        INSERT INTO audit_log (table_name, operation, changed_by, operation_id)
        VALUES ('operations', 'DELETE', :changed_by, :operation_id)
    """)

    try:
        with engine.connect() as conn:
            with conn.begin():
                # 1. Supprimer l'opération
                result = conn.execute(delete_query, {"operation_id": operation_id})
                if result.rowcount == 0:
                    raise ValueError(f"Aucune opération trouvée avec operation_id = {operation_id}")

                # 2. Journaliser
                conn.execute(log_query, {
                    "changed_by": changed_by,
                    "operation_id": operation_id
                })
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return False

def insert_operation(operation_data: dict, changed_by: str = "operator"):
    """
    Insère une nouvelle opération et logue l'action.

    Args:
        operation_data: dict des données de l'opération
        changed_by: utilisateur ayant fait l'insertion

    Returns:
        bool: True si succès, False sinon
    """
    if 'operation_id' not in operation_data:
        raise ValueError("operation_id est requis pour l'insertion")

    operation_id = operation_data['operation_id']

    # Construire la clause INSERT dynamiquement
    columns = list(operation_data.keys())
    values_placeholders = [f":{col}" for col in columns]

    insert_query = text(f"""
        INSERT INTO operations ({', '.join(columns)})
        VALUES ({', '.join(values_placeholders)})
    """)

    log_query = text("""
        INSERT INTO audit_log (table_name, operation, changed_by, operation_id)
        VALUES ('operations', 'INSERT', :changed_by, :operation_id)
    """)

    try:
        with engine.connect() as conn:
            with conn.begin():
                # 1. Insérer l'opération
                conn.execute(insert_query, operation_data)

                # 2. Journaliser
                conn.execute(log_query, {
                    "changed_by": changed_by,
                    "operation_id": operation_id
                })
        return True
    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")
        return False