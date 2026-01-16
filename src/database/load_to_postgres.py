# src/database/load_to_postgres.py
"""
Charge les DataFrames transformés dans PostgreSQL.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add src to path for relative imports when run as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..ingestion.prepare_tables import (
    prepare_operations,
    prepare_flotteurs,
    prepare_resultats_humain
)

load_dotenv()
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def load_data():
    """Charge les données dans PostgreSQL avec gestion transactionnelle."""
    engine = create_engine(DB_URL, pool_pre_ping=True)
    
    print("Chargement des donnees...")
    
    # Utiliser une transaction manuelle
    with engine.begin() as conn:
        try:
            # === Charger operations ===
            df_ops = prepare_operations()
            
            expected_ops_cols = {
                "operation_id", "date_heure_reception_alerte", "date_heure_fin_operation",
                "type_operation", "type_operation_saisi", "evenement", "categorie_evenement", "zone_responsabilite", "fuseau_horaire", "pourquoi_alerte",
                "pourquoi_alerte_saisi", "moyen_alerte", "qui_alerte", "categorie_qui_alerte",
                "cross_name", "departement", "prefecture_maritime", "est_metropolitain",
                "vent_force", "mer_force", "vent_direction", "vent_direction_categorie",
                "longitude", "latitude", "autorite", "numero_sitrep", "cross_sitrep",
                "systeme_source", "phase_journee", "sans_flotteur_implique",
                "total_flotteurs_impliques", "maree_categorie", "maree_port",
                "maree_coefficient", "distance_cote_metres", "distance_cote_milles_nautiques",
                "est_vacances_scolaires", "donnees_meteo_imputees"
            }
            
            missing_cols = expected_ops_cols - set(df_ops.columns)
            if missing_cols:
                raise ValueError(f"Colonnes manquantes dans operations: {missing_cols}")
            
            df_ops.to_sql("operations", conn, if_exists="append", index=False)
            print(f"[OK] operations : {len(df_ops)} lignes chargees")
            
            # === Charger flotteurs ===
            df_fl = prepare_flotteurs()
            df_fl.to_sql("flotteurs", conn, if_exists="append", index=False)
            print(f"[OK] flotteurs : {len(df_fl)} lignes chargees")
            
            # === Charger resultats_humain ===
            df_rh = prepare_resultats_humain()
            df_rh.to_sql("resultats_humain", conn, if_exists="append", index=False)
            print(f"[OK] resultats_humain : {len(df_rh)} lignes chargees")
            
            print("\n[SUCCES] Chargement termine avec succes.")
            
        except Exception as e:
            print(f"\n[ERREUR] {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    load_data()