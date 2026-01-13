# src/ingestion/prepare_tables.py
"""
Préparation des tables finales à partir des CSV bruts.
Objectif : charger proprement dans PostgreSQL sans nettoyage excessif.
"""

import pandas as pd
from pathlib import Path

# Chemin relatif depuis ce fichier
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def prepare_operations() -> pd.DataFrame:
    """Prépare la table 'operations' enrichie avec des agrégats utiles de operations_stats."""
    # Charger les données
    ops = pd.read_csv(DATA_DIR / "operations.csv", low_memory=False) # enlever le warning
    stats = pd.read_csv(DATA_DIR / "operations_stats.csv", low_memory=False)

    # Convertir les dates
    date_cols = ["date_heure_reception_alerte", "date_heure_fin_operation"]
    for col in date_cols:
        if col in ops.columns:
            ops[col] = pd.to_datetime(ops[col], errors="coerce")

    # Supprimer les colonnes inutiles de operations
    cols_to_drop_ops = ["seconde_autorite"]
    ops = ops.drop(columns=[c for c in cols_to_drop_ops if c in ops.columns], errors='ignore')

    # Supprimer les colonnes inutiles de operations_stats
    cols_to_drop_stats = ["nom_dst", "nom_stm"]
    stats = stats.drop(columns=[c for c in cols_to_drop_stats if c in stats.columns], errors='ignore')

    # Calculer le total des flotteurs impliqués
    flotteur_cols = [col for col in stats.columns if col.startswith("nombre_flotteurs_")]
    stats["total_flotteurs_impliques"] = stats[flotteur_cols].sum(axis=1)

    # Garder seulement les colonnes utiles de stats
    stats_cols_to_keep = [
        "operation_id",
        "sans_flotteur_implique",
        "total_flotteurs_impliques"
    ]
    stats_minimal = stats[stats_cols_to_keep]

    # Fusionner
    df = ops.merge(stats_minimal, on="operation_id", how="left")

    return df

def prepare_flotteurs() -> pd.DataFrame:
    """Prépare la table 'flotteurs'."""
    df = pd.read_csv(DATA_DIR / "flotteurs.csv")
    # Vérifie que la clé existe
    assert "operation_id" in df.columns, "flotteurs.csv doit contenir 'operation_id'"
    return df


def prepare_resultats_humain() -> pd.DataFrame:
    """Prépare la table 'resultats_humain'."""
    df = pd.read_csv(DATA_DIR / "resultats_humain.csv")
    assert "operation_id" in df.columns, "resultats_humain.csv doit contenir 'operation_id'"
    return df


if __name__ == "__main__":
    # Test rapide en local
    print("Chargement operations...")
    ops = prepare_operations()
    print(f"   → {len(ops)} lignes")

    print("Chargement flotteurs...")
    fl = prepare_flotteurs()
    print(f"   → {len(fl)} lignes")

    print("Chargement résultats humains...")
    rh = prepare_resultats_humain()
    print(f"   → {len(rh)} lignes")

    print("\n🟢 Toutes les tables sont prêtes pour PostgreSQL.")