# src/ingestion/prepare_tables.py
"""
Extract + Transform:
- Charge les CSV bruts
- Nettoie, impute, calcule
- Retourne des DataFrames prêts pour PostgreSQL
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

# Mapping officiel CROSS → départements (d'après ton analyse)
CROSS_TO_DEP = {
    "Adge": ["Aude", "Bouches-du-Rhône", "Gard", "Hérault", "Pyrénées-Orientales"],
    "Antilles-Guyane": ["Collectivité de Saint Barthélémy", "Collectivité de Saint Martin", "Guadeloupe", "Guyane", "Martinique"],
    "Corse": ["Alpes-Maritimes", "Aude", "Bouches-du-Rhône", "Charente-Maritime", "Corse", "Corse-du-Sud", "Haute-Corse", "Hérault", "Pyrénées-Orientales", "Var"],
    "Corsen": ["Charente-Maritime", "Corse-du-Sud", "Côtes-d'Armor", "Finistère", "Gironde", "Hérault", "Ille-et-Vilaine", "Manche", "Morbihan", "Vendée"],
    "Gris-Nez": ["Alpes-Maritimes", "Aude", "Bouches-du-Rhône", "Calvados", "Charente-Maritime", "Corse-du-Sud", "Côtes-d'Armor", "Eure", "Finistère", "Gard", "Gironde", "Guadeloupe", "Guyane", "Haute-Corse", "Hérault", "Ille-et-Vilaine", "Landes", "Loire-Atlantique", "Manche", "Martinique", "Morbihan", "Nord", "Nouvelle-Calédonie", "Pas-de-Calais", "Polynésie", "Pyrénées-Atlantiques", "Pyrénées-Orientales", "Saint-Pierre-et-Miquelon", "Seine-Maritime", "Somme", "Var", "Vendée"],
    "Guadeloupe": ["Guadeloupe"],
    "Guyane": ["Guyane"],
    "Jobourg": ["Alpes-Maritimes", "Calvados", "Côtes-d'Armor", "Eure", "Finistère", "Gironde", "Ille-et-Vilaine", "Manche", "Morbihan", "Pas-de-Calais", "Seine-Maritime", "Somme"],
    "La Garde": ["Alpes-Maritimes", "Aude", "Bouches-du-Rhône", "Corse", "Corse-du-Sud", "Gard", "Haute-Corse", "Hérault", "Pyrénées-Orientales", "Var"],
    "La Réunion": ["Mayotte", "Réunion"],
    "Martinique": ["Guadeloupe", "Martinique"],
    "Mayotte": ["Mayotte"],
    "Nouvelle-Calédonie": ["Nouvelle-Calédonie"],
    "Polynésie": ["Polynésie"],
    "Soulac": ["Charente-Maritime", "Gironde", "Landes", "Pyrénées-Atlantiques", "Vendée"],
    "Sud océan Indien": ["La Réunion", "Mayotte"],
    "Étel": ["Charente-Maritime", "Finistère", "Gironde", "Landes", "Loire-Atlantique", "Morbihan", "Pyrénées-Atlantiques", "Vendée"],
}

def get_phase_journee(dt):
    """Calcule la phase de la journée selon les conventions métier."""
    if pd.isna(dt):
        return None
    h = dt.hour
    if 6 <= h < 12:
        return "matinée"
    elif 12 <= h < 14:
        return "déjeuner"
    elif 14 <= h < 19:
        return "après-midi"
    else:
        return "nuit"

def impute_departement(row):
    """Impute departement depuis cross si possible."""
    if pd.notna(row["departement"]):
        return row["departement"]
    cross_val = row["cross"]
    if pd.isna(cross_val) or cross_val not in CROSS_TO_DEP:
        return "Non renseigné"
    # Prendre le premier département comme convention
    return CROSS_TO_DEP[cross_val][0]

def prepare_operations() -> pd.DataFrame:
    # === EXTRACT ===
    ops = pd.read_csv(DATA_DIR / "operations.csv",low_memory=False)
    stats = pd.read_csv(DATA_DIR / "operations_stats.csv",low_memory=False)

    # === TRANSFORM: dates ===
    date_cols = ["date_heure_reception_alerte", "date_heure_fin_operation"]
    for col in date_cols:
        if col in ops.columns:
            ops[col] = pd.to_datetime(ops[col], errors="coerce")

    # === TRANSFORM: suppression colonnes inutiles ===
    cols_to_drop_ops = ["seconde_autorite"]
    for col in cols_to_drop_ops:
        if col in ops.columns:
            ops = ops.drop(columns=[col])

    cols_to_drop_stats = ["nom_dst", "nom_stm", "distance_cote_metres", "distance_cote_milles_nautiques", "est_vacances_scolaires"]
    for col in cols_to_drop_stats:
        if col in stats.columns:
            stats = stats.drop(columns=[col])

    # === TRANSFORM: imputations operations ===
    # Météo
    median_vent = ops["vent_force"].median()
    median_mer = ops["mer_force"].median()
    ops["vent_force"] = ops["vent_force"].fillna(median_vent)
    ops["mer_force"] = ops["mer_force"].fillna(median_mer)
    ops["vent_direction"] = ops["vent_direction"].fillna(-1)
    ops["vent_direction_categorie"] = ops["vent_direction_categorie"].fillna("VARIABLE")
    ops["donnees_meteo_imputees"] = (
        ops["vent_force"].isna().astype(bool) | ops["mer_force"].isna().astype(bool)
    )

    # Autorité & autres
    ops["autorite"] = ops["autorite"].fillna("Non renseigné")
    ops["longitude"] = ops["longitude"].fillna(-1)
    ops["latitude"] = ops["latitude"].fillna(-1)

    # Département (avec ton mapping complet)
    ops["departement"] = ops.apply(impute_departement, axis=1)

    # === TRANSFORM: colonnes calculées ===
    ops["phase_journee"] = ops["date_heure_reception_alerte"].apply(get_phase_journee)

    # === TRANSFORM: enrichissement depuis stats ===
    flotteur_cols = [col for col in stats.columns if col.startswith("nombre_flotteurs_")]
    stats["total_flotteurs_impliques"] = stats[flotteur_cols].sum(axis=1)

    stats_minimal = stats[[
        "operation_id",
        "sans_flotteur_implique",
        "total_flotteurs_impliques",
        "prefecture_maritime",
        "maree_categorie",
        "maree_port",
        "maree_coefficient"
    ]].copy()

    # Imputer maree_* et prefecture_maritime
    stats_minimal["prefecture_maritime"] = stats_minimal["prefecture_maritime"].fillna("Non renseigné")
    stats_minimal["maree_categorie"] = stats_minimal["maree_categorie"].fillna("Non renseigné")
    stats_minimal["maree_port"] = stats_minimal["maree_port"].fillna("Non renseigné")
    stats_minimal["maree_coefficient"] = stats_minimal["maree_coefficient"].fillna(-1)

    # Fusion
    df = ops.merge(stats_minimal, on="operation_id", how="left")

    return df


def prepare_flotteurs() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "flotteurs.csv")
    df["numero_immatriculation"] = df["numero_immatriculation"].fillna("Non renseigné")
    df["numero_ordre"] = df["numero_ordre"].fillna(-1)
    df["pavillon"] = df["pavillon"].fillna("Non renseigné")
    df["resultat_flotteur"] = df["resultat_flotteur"].fillna("Non renseigné")
    df["type_flotteur"] = df["type_flotteur"].fillna("Non renseigné")
    df["categorie_flotteur"] = df["categorie_flotteur"].fillna("Non renseigné")
    return df


def prepare_resultats_humain() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "resultats_humain.csv")
    df["categorie_personne"] = df["categorie_personne"].fillna("Non renseigné")
    df["resultat_humain"] = df["resultat_humain"].fillna("Non renseigné")
    df["nombre"] = df["nombre"].fillna(0).astype(int)
    df["dont_nombre_blesse"] = df["dont_nombre_blesse"].fillna(0).astype(int)
    return df


if __name__ == "__main__":
    print("Chargement et transformation...")
    ops = prepare_operations()
    fl = prepare_flotteurs()
    rh = prepare_resultats_humain()
    
    print(f"→ operations: {len(ops)} lignes")
    print(f"→ flotteurs: {len(fl)} lignes")
    print(f"→ resultats_humain: {len(rh)} lignes")
    print("\nPrêt pour le chargement dans PostgreSQL.")