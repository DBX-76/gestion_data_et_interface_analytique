import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

def prepare_operations():
    ops = pd.read_csv(DATA_DIR / "operations.csv")
    stats = pd.read_csv(DATA_DIR / "operations_stats.csv")
    # Force les dates
    ops['date_heure_reception_alerte'] = pd.to_datetime(ops['date_heure_reception_alerte'], errors='coerce')
    ops['date_heure_fin_operation'] = pd.to_datetime(ops['date_heure_fin_operation'], errors='coerce')
    # Garde toutes les colonnes utiles → pas de suppression massive
    return ops

def prepare_flotteurs():
    df = pd.read_csv(DATA_DIR / "flotteurs.csv")
    # Vérifie que operation_id existe
    return df

def prepare_resultats_humain():
    df = pd.read_csv(DATA_DIR / "resultats_humain.csv")
    return df