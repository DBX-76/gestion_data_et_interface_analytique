# Retours techniques & erreurs résolues

## 🔢 1. Erreurs de type numérique (`DataError: entier en dehors des limites`)

### Contexte
- Chargement des données avec `pandas.to_sql()`
- Valeurs comme `operation_id = 2219860080` dépassent la limite d’un `INTEGER` PostgreSQL (2 147 483 647)

### Cause
- Colonne définie comme `INTEGER` dans le schéma SQL, mais contient des valeurs > 2,1 milliards

### Solution
- Changer le type en `BIGINT` dans toutes les tables concernées :
  - `operations.operation_id`
  - `flotteurs.operation_id`
  - `resultats_humain.operation_id`

### Fichiers impactés
- `init_db.py`
- Schéma Mermaid
- Dictionnaire des données

---

## 🗝️ 2. Mots réservés SQL (`ProgrammingError: erreur de syntaxe sur ou près de « cross »`)

### Contexte
- Création de la table `operations`
- `cross` est un mot-clé SQL (`CROSS JOIN`)

### Cause
- PostgreSQL refuse d’utiliser un mot réservé comme nom de colonne sans échappement

### Solution
- **Renommer la colonne** pour éviter tout risque :
  - Ancien nom : `cross`
  - Nouveau nom : `cross_name`
- Mettre à jour partout : `prepare_tables.py`, `load_data.py`, schéma, doc

### Avantages
- Plus de problème d’échappement
- Compatibilité avec tous les outils (pandas, BI, ORM)
- Code plus lisible

---

## 🧩 3. Incohérence DataFrame ↔ Base de données

### Contexte
- Colonnes présentes dans le DataFrame mais absentes du schéma SQL
- Exemples : `categorie_evenement`, `zone_responsabilite`, `fuseau_horaire`

### Cause
- Le dictionnaire des données initial n’incluait pas ces colonnes métier utiles

### Solution
- Ajouter les colonnes manquantes dans le `CREATE TABLE`
- Mettre à jour la liste des colonnes attendues dans `load_data.py`
- Documenter dans le dictionnaire

### Colonnes ajoutées
- `categorie_evenement TEXT`
- `zone_responsabilite TEXT`
- `fuseau_horaire TEXT`

---

## 🐍 4. Problèmes de compatibilité pandas / SQLAlchemy

### Contexte
- `UserWarning: pandas only supports SQLAlchemy connectable...`
- `AttributeError: 'Engine' object has no attribute 'cursor'`

### Cause
- Versions anciennes de pandas (< 1.4) ne supportent pas directement `sqlalchemy.Engine`
- Utilisation incorrecte de la connexion (`psycopg2` brute au lieu de `sqlalchemy.Connection`)

### Solution
- Utiliser **directement l’`Engine`** dans `to_sql()` (si pandas ≥ 1.4)
- OU utiliser une **connexion SQLAlchemy** via `engine.connect()` dans un context manager
- Éviter les connexions `psycopg2` pures

### Bonne pratique
```python
engine = create_engine(DB_URL)
df.to_sql("table", engine, if_exists="append", index=False)