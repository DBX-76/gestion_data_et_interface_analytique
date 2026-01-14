# src/database/init_db.py
"""
Crée les tables dans PostgreSQL selon le dictionnaire des données final.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def init_tables():
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        with conn.begin():  # garantit un rollback en cas d'erreur
            # === TABLE operations ===
            conn.execute(text("""
                DROP TABLE IF EXISTS operations CASCADE;
                CREATE TABLE operations (
                    operation_id INTEGER PRIMARY KEY,
                    date_heure_reception_alerte TIMESTAMPTZ,
                    date_heure_fin_operation TIMESTAMPTZ,
                    type_operation TEXT,
                    type_operation_saisi BOOLEAN,
                    evenement TEXT,
                    pourquoi_alerte TEXT,
                    pourquoi_alerte_saisi BOOLEAN,
                    moyen_alerte TEXT,
                    qui_alerte TEXT,
                    categorie_qui_alerte TEXT,
                    "cross" TEXT,
                    departement TEXT,
                    prefecture_maritime TEXT,
                    est_metropolitain BOOLEAN,
                    vent_force FLOAT,
                    mer_force FLOAT,
                    vent_direction FLOAT,
                    vent_direction_categorie TEXT,
                    longitude FLOAT,
                    latitude FLOAT,
                    autorite TEXT,
                    numero_sitrep INTEGER,
                    cross_sitrep TEXT,
                    systeme_source TEXT,
                    phase_journee TEXT,
                    sans_flotteur_implique BOOLEAN,
                    total_flotteurs_impliques INTEGER,
                    maree_categorie TEXT,
                    maree_port TEXT,
                    maree_coefficient FLOAT,
                    distance_cote_metres FLOAT,
                    distance_cote_milles_nautiques FLOAT,
                    est_vacances_scolaires BOOLEAN,
                    donnees_meteo_imputees BOOLEAN
                );
            """))

            # === TABLE flotteurs ===
            conn.execute(text("""
                DROP TABLE IF EXISTS flotteurs;
                CREATE TABLE flotteurs (
                    operation_id INTEGER REFERENCES operations(operation_id) ON DELETE CASCADE,
                    numero_ordre FLOAT,
                    pavillon TEXT,
                    resultat_flotteur TEXT,
                    type_flotteur TEXT,
                    categorie_flotteur TEXT,
                    numero_immatriculation TEXT
                );
            """))

            # === TABLE resultats_humain ===
            conn.execute(text("""
                DROP TABLE IF EXISTS resultats_humain;
                CREATE TABLE resultats_humain (
                    operation_id INTEGER REFERENCES operations(operation_id) ON DELETE CASCADE,
                    categorie_personne TEXT,
                    resultat_humain TEXT,
                    nombre INTEGER,
                    dont_nombre_blesse INTEGER
                );
            """))

            # === TABLE audit_log ===
            conn.execute(text("""
                DROP TABLE IF EXISTS audit_log;
                CREATE TABLE audit_log (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    operation_date TIMESTAMPTZ DEFAULT NOW(),
                    changed_by TEXT DEFAULT 'operator',
                    operation_id INTEGER
                );
            """))

    print("Tables créées selon le dictionnaire des données final.")

if __name__ == "__main__":
    init_tables()