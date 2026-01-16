"""
Système de validation des données utilisant Pandera avec validation paresseuse et quarantaine.

Ce module implémente :
- Validation paresseuse (collecte toutes les erreurs avant d'échouer)
- Système de quarantaine pour les données invalides
- Routage des données valides/invalides
"""

import pandas as pd
import pandera as pa
from pandera.errors import SchemaErrors
from typing import Tuple, Dict, Any
import os
from datetime import datetime
import json

from .schemas import OPERATIONS_SCHEMA, FLOTTEURS_SCHEMA, RESULTATS_HUMAIN_SCHEMA

class DataValidator:
    """Système de validation des données avec validation paresseuse et quarantaine."""

    def __init__(self, quarantine_dir: str = "data/quarantine"):
        self.quarantine_dir = quarantine_dir
        os.makedirs(quarantine_dir, exist_ok=True)

    def validate_operations(self, df: pd.DataFrame, lazy: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Valide les données d'opérations en utilisant la validation paresseuse.

        Args:
            df: DataFrame à valider
            lazy: Si utiliser la validation paresseuse (collecte toutes les erreurs)

        Returns:
            Tuple de (données_valides, données_invalides, rapport_validation)
        """
        try:
            # Attempt validation
            validated_df = OPERATIONS_SCHEMA.validate(df, lazy=lazy)
            return validated_df, pd.DataFrame(), {"status": "success", "errors": [], "total_errors": 0}

        except SchemaErrors as e:
            # Collect validation errors
            error_report = self._process_schema_errors(e)

            # If no valid rows can be determined, consider all data invalid
            try:
                valid_mask = self._get_valid_rows_mask(df, e)
                valid_data = df[valid_mask].copy() if valid_mask.any() else pd.DataFrame()
                invalid_data = df[~valid_mask].copy() if (~valid_mask).any() else df.copy()
            except Exception:
                # If we can't determine valid rows, all data is invalid
                valid_data = pd.DataFrame()
                invalid_data = df.copy()

            return valid_data, invalid_data, error_report

    def _process_schema_errors(self, schema_errors: SchemaErrors) -> Dict[str, Any]:
        """Traite les SchemaErrors en un rapport structuré."""
        error_summary = {
            "status": "failed",
            "total_errors": len(schema_errors.schema_errors),
            "schema_errors": [],
            "dataframe_errors": [],
            "error_details": {}
        }

        # Process schema-level errors
        for error in schema_errors.schema_errors:
            error_summary["schema_errors"].append({
                "column": error.schema.name if hasattr(error.schema, 'name') else str(error.schema),
                "check": error.check.name if hasattr(error.check, 'name') else str(error.check),
                "error_message": str(error)
            })

        # Note: dataframe_errors might not exist in all Pandera versions
        # We'll handle it gracefully
        if hasattr(schema_errors, 'dataframe_errors'):
            error_summary["total_errors"] += len(schema_errors.dataframe_errors)
            for error in schema_errors.dataframe_errors:
                error_summary["dataframe_errors"].append({
                    "check": error.check.name if hasattr(error.check, 'name') else str(error.check),
                    "error_message": str(error)
                })

        return error_summary

    def _get_valid_rows_mask(self, df: pd.DataFrame, schema_errors: SchemaErrors) -> pd.Series:
        """Détermine quelles lignes sont valides basées sur les erreurs de validation."""
        # Start with all rows as valid
        valid_mask = pd.Series(True, index=df.index)

        # For each error, mark affected rows as invalid
        for error in schema_errors.schema_errors:
            if hasattr(error, 'failure_cases') and error.failure_cases is not None:
                # Mark rows with validation failures as invalid
                failure_indices = error.failure_cases.index
                valid_mask.loc[failure_indices] = False

        return valid_mask

    def quarantine_invalid_data(self, invalid_data: pd.DataFrame, source: str, validation_report: Dict[str, Any]) -> str:
        """
        Sauvegarde les données invalides en quarantaine avec le rapport de validation.

        Args:
            invalid_data: DataFrame avec les lignes invalides
            source: Source des données (ex: 'operations_upload')
            validation_report: Rapport d'erreurs de validation

        Returns:
            Chemin du fichier de quarantaine
        """
        if invalid_data.empty:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quarantine_{source}_{timestamp}.json"

        quarantine_path = os.path.join(self.quarantine_dir, filename)

        quarantine_record = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "total_invalid_rows": len(invalid_data),
            "validation_report": validation_report,
            "invalid_data": invalid_data.to_dict('records')
        }

        with open(quarantine_path, 'w', encoding='utf-8') as f:
            json.dump(quarantine_record, f, indent=2, default=str, ensure_ascii=False)

        return quarantine_path

    def get_quarantine_files(self) -> list:
        """Obtient la liste des fichiers de quarantaine."""
        if not os.path.exists(self.quarantine_dir):
            return []

        return [f for f in os.listdir(self.quarantine_dir) if f.startswith('quarantine_') and f.endswith('.json')]

    def load_quarantine_file(self, filename: str) -> Dict[str, Any]:
        """Charge un fichier de quarantaine."""
        filepath = os.path.join(self.quarantine_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_flotteurs(self, df: pd.DataFrame, lazy: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Valide les données de flotteurs."""
        try:
            validated_df = FLOTTEURS_SCHEMA.validate(df, lazy=lazy)
            return validated_df, pd.DataFrame(), {"status": "success", "errors": []}
        except SchemaErrors as e:
            error_report = self._process_schema_errors(e)
            valid_mask = self._get_valid_rows_mask(df, e)
            valid_data = df[valid_mask].copy() if valid_mask.any() else pd.DataFrame()
            invalid_data = df[~valid_mask].copy() if (~valid_mask).any() else pd.DataFrame()
            return valid_data, invalid_data, error_report

    def validate_resultats_humain(self, df: pd.DataFrame, lazy: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Valide les données de résultats humain."""
        try:
            validated_df = RESULTATS_HUMAIN_SCHEMA.validate(df, lazy=lazy)
            return validated_df, pd.DataFrame(), {"status": "success", "errors": []}
        except SchemaErrors as e:
            error_report = self._process_schema_errors(e)
            valid_mask = self._get_valid_rows_mask(df, e)
            valid_data = df[valid_mask].copy() if valid_mask.any() else pd.DataFrame()
            invalid_data = df[~valid_mask].copy() if (~valid_mask).any() else pd.DataFrame()
            return valid_data, invalid_data, error_report

# Global validator instance
validator = DataValidator()