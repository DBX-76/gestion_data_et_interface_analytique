"""
Système d'ingestion de données avec validation Pandera et quarantaine.

Ce module fournit des fonctions pour ingérer des données avec validation et quarantaine
des enregistrements invalides.
"""

import pandas as pd
from typing import Dict, Any, Tuple
from database.update import insert_operation
from validation.validator import validator

def ingest_operations_data(df: pd.DataFrame, source: str = "upload") -> Dict[str, Any]:
    """
    Ingère les données d'opérations avec validation et quarantaine.

    Args:
        df: DataFrame à ingérer
        source: Identifiant source pour les fichiers de quarantaine

    Returns:
        Rapport d'ingestion avec résultats de validation et quarantaine
    """
    report = {
        "source": source,
        "total_rows": len(df),
        "valid_rows": 0,
        "invalid_rows": 0,
        "inserted_rows": 0,
        "quarantine_file": None,
        "validation_report": {},
        "errors": []
    }

    try:
        # Valider les données avec validation lazy
        valid_data, invalid_data, validation_report = validator.validate_operations(df, lazy=True)

        report["valid_rows"] = len(valid_data)
        report["invalid_rows"] = len(invalid_data)
        report["validation_report"] = validation_report

        # Mettre en quarantaine les données invalides si présentes
        if not invalid_data.empty:
            quarantine_file = validator.quarantine_invalid_data(invalid_data, source, validation_report)
            report["quarantine_file"] = quarantine_file

        # Insérer les données valides
        if not valid_data.empty:
            inserted_count = 0
            for _, row in valid_data.iterrows():
                try:
                    operation_data = row.to_dict()
                    # Supprimer les valeurs NaN
                    operation_data = {k: v for k, v in operation_data.items() if pd.notna(v)}

                    success = insert_operation(operation_data, changed_by=f"system_{source}")
                    if success:
                        inserted_count += 1
                except Exception as e:
                    report["errors"].append(f"Erreur lors de l'insertion de la ligne {row.name}: {str(e)}")

            report["inserted_rows"] = inserted_count

        report["status"] = "success"

    except Exception as e:
        report["status"] = "error"
        report["errors"].append(f"Échec de l'ingestion: {str(e)}")

    return report

def ingest_flotteurs_data(df: pd.DataFrame, source: str = "upload") -> Dict[str, Any]:
    """Ingère les données de flotteurs avec validation."""
    # Placeholder - à implémenter quand le CRUD flotteurs sera prêt
    return {
        "status": "not_implemented",
        "message": "Ingestion des flotteurs pas encore implémentée"
    }

def ingest_resultats_humain_data(df: pd.DataFrame, source: str = "upload") -> Dict[str, Any]:
    """Ingère les données de résultats humain avec validation."""
    # Placeholder - à implémenter quand le CRUD résultats humain sera prêt
    return {
        "status": "not_implemented",
        "message": "Ingestion des résultats humain pas encore implémentée"
    }