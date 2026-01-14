# Choix d’architecture – Modèle relationnel

## Pourquoi pas un modèle en étoile (fait/dimensions) ?
Le projet vise à fournir un **outil opérationnel de mise à jour des données** (CRUD), utilisé par des métiers non techniques.  
Un modèle relationnel normalisé (`operations`, `flotteurs`, `resultats_humain`) est donc privilégié :
- Il reflète fidèlement la structure des données sources
- Il permet des mises à jour ligne par ligne (via l’interface CRUD)
- Il évite la complexité inutile d’un data warehouse (non requis pour le MVP)

## Pourquoi pas Bronze / Argent / Or ?
L’architecture en couches (bronze = brut, argent = propre, or = agrégé) est pertinente pour les pipelines analytiques à grande échelle.  
Ici, le besoin est **opérationnel et immédiat** :
- **Bronze** = les fichiers CSV bruts (`data/raw/`)
- **Argent** = les DataFrames propres générés par `prepare_tables.py`
- **Or** = non implémenté (le dashboard Streamlit consomme directement les tables "argent")

> ℹ️ Ces approches restent des pistes d’amélioration pour une phase 2.


# Diagramme Entité-Relation (simplifié)


operations
──────────────
• operation_id (PK)
• date_heure_reception_alerte
• type_operation
• ...

     ↑ (FK)
     │ operation_id
     ↓

flotteurs
──────────────
• operation_id (FK)
• numero_ordre
• pavillon
• ...

     ↑ (FK)
     │ operation_id
     ↓

resultats_humain
──────────────
• operation_id (FK)
• categorie_personne
• nombre
• ...

