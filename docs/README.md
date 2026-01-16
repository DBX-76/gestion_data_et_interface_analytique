# 🚢 Rescue Operations Data Platform

Interface analytique polyvalente pour la gestion et l'analyse des opérations de sauvetage maritime (SEC MAR).

## 📋 Vue d'ensemble

Cette plateforme centralise les données opérationnelles des CROSS (Centres Régionaux Opérationnels de Surveillance et de Sauvetage) pour :
- **Gérer** les opérations de sauvetage (CRUD complet)
- **Analyser** les données pour optimiser les interventions
- **Traquer** toutes les modifications manuelles avec audit complet
- **Valider** automatiquement les données à l'ingestion

## 🏗️ Architecture

### Structure du projet
```
rescue-ops-data/
├── data/                    # Données (brutes et quarantaine)
│   └── quarantine/         # Données invalides mises en quarantaine
├── docs/                   # Documentation
├── src/                    # Code source
│   ├── app/               # Interface utilisateur Streamlit
│   ├── database/          # Scripts base de données PostgreSQL
│   ├── ingestion/         # Pipeline ETL
│   └── validation/        # Validation des données avec Pandera
├── .env                    # Variables d'environnement
├── requirements.txt        # Dépendances Python
└── README.md              # Cette documentation
```

### Technologies utilisées
- **Backend** : Python 3.8+, PostgreSQL
- **Interface** : Streamlit
- **Validation** : Pandera (schéma strict avec lazy validation)
- **ORM** : SQLAlchemy

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL 13+
- Git

### Configuration

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd rescue-ops-data
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   ```bash
   # Créer un fichier .env avec vos variables
   cp .env.example .env
   # Éditer .env avec vos paramètres PostgreSQL
   ```

5. **Initialiser la base de données**
   ```bash
   python -m src.database.init_db
   ```

## 📊 Utilisation

### 1. Ingestion des données

**Via l'interface Streamlit** (recommandé) :
```bash
streamlit run src/app/streamlit_app.py
```
- Aller dans "🚢 Opérations" > "📤 Importer des données"
- Sélectionner un fichier CSV/Excel
- Validation automatique avec quarantaine des données invalides

**Via script** :
```bash
python -m src.ingestion.data_ingestion
```

### 2. Gestion des opérations

L'interface Streamlit permet :
- **📋 Vue d'ensemble** : Consulter toutes les opérations
- **🔍 Recherche** : Filtrer par ID ou intervalle
- **✏️ Modification** : Mettre à jour les opérations avec audit automatique
- **🗑️ Suppression** : Supprimer avec traçabilité
- **➕ Ajout** : Créer de nouvelles opérations

### 3. Historique d'audit

- **📋 Historique** : Consulter toutes les modifications
- Chaque changement est tracé avec :
  - Utilisateur ayant fait la modification
  - Ancienne et nouvelle valeur
  - Timestamp précis
  - Référence à l'opération concernée

## 🔧 Validation des données

### Schéma strict avec Pandera
- **Types de données** : Validation automatique des types (int, float, str, datetime)
- **Colonnes requises** : Vérification de la présence des colonnes essentielles
- **Contraintes métier** : Validation des plages de valeurs (ex: Beaufort 0-12)
- **Quarantaine** : Les données invalides sont automatiquement mises de côté

### Gestion des erreurs
- **Lazy validation** : Collecte de toutes les erreurs avant échec
- **Rapports détaillés** : Description précise des problèmes
- **Récupération** : Interface pour examiner et corriger les données en quarantaine

## 📈 Tables de données

### Operations
Données principales des interventions :
- Informations temporelles et géographiques
- Types d'événements et d'opérations
- Conditions météorologiques
- Ressources mobilisées

### Flotteurs
Informations sur les navires impliqués :
- Données d'identification
- Résultats des interventions
- Pavillons et types de navires

### Résultats Humains
Impacts sur les personnes :
- Statistiques de secours
- Catégories de personnes
- Résultats des interventions

### Audit Log
Traçabilité complète :
- Historique des modifications manuelles
- Utilisateurs et timestamps
- Valeurs avant/après modification

## 🔒 Sécurité et audit

### Traçabilité
- **Journal d'audit** non falsifiable
- **Transactions atomiques** pour la cohérence
- **Horodatage** précis de toutes les modifications

### Validation
- **Schéma strict** empêchant les données corrompues
- **Quarantaine automatique** des données invalides
- **Interface de correction** pour les données problématiques

## 📚 Documentation

- `docs/README.md` : Vue d'ensemble
- `docs/methodologie.md` : Méthodologie de développement
- `docs/data_dictionary.md` : Dictionnaire des données
- `docs/choix_architecture.md` : Choix techniques
- `docs/troubleshooting.md` : Dépannage
