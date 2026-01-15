# Méthodologie de traitement des données

## 🔧 Choix techniques
- **Base de données** : PostgreSQL avec encodage UTF-8
- **Pipeline** : Python + pandas + SQLAlchemy
- **Interface** : Streamlit (CRUD)
- **Audit** : table `audit_log 

## 🧹 Règles de nettoyage & imputation
- **`departement`** : imputé depuis `cross_name` via le dictionnaire `CROSS_TO_DEP`
- **Météo (`vent_force`, `mer_force`)** : imputée par médiane
- **`categorie_evenement`** : conservée car agrège utilement les événements métier
- **IDs négatifs** : considérés comme des saisies manuelles valides (source `secmarweb`)

## 🗺️ Mapping des colonnes
| Source (`operations.csv`) | Cible (`operations` SQL) | Transformation |
|--------------------------|--------------------------|----------------|
| `cross`                  | `cross_name`             | Renommage (mot réservé SQL) |
| `operation_id`           | `BIGINT`                 | Pour supporter les grands IDs |

## 🤔 Hypothèses clés
- Les données `seamis_json` sont plus complètes que `secmarweb`
- Les opérations avec `operation_id < 0` sont légitimes et doivent être conservées
- Le champ `cross` ne peut pas rester tel quel à cause du mot-clé SQL `CROSS`

## 📊 Qualité des données
- Taux de remplissage de `longitude`/`latitude` : 92%
- Valeurs aberrantes détectées et corrigées : aucune (valeurs cohérentes avec la mer)