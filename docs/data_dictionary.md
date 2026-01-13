# Dictionnaire des données

##  Stratégie de modélisation

| Table source | Action retenue | Raison |
|--------------|----------------|--------|
| `operations.csv` | **Conservée et enrichie** | Base principale du CRUD ; enrichie avec 2 agrégats de `operations_stats` |
| `flotteurs.csv` | **Toutes les colonnes conservées** | Données détaillées utiles pour le suivi des embarcations |
| `resultats_humain.csv` | **Toutes les colonnes conservées** | Informations critiques sur les personnes impliquées |
| `operations_stats.csv` | **Non chargée comme table** | Seulement 2 indicateurs extraits (`sans_flotteur_implique`, `total_flotteurs_impliques`) → évite la redondance et simplifie le modèle |

> Cette approche permet un **CRUD simple** et  un **dashboard efficace**

# Dictionnaire des données

## Table `operations`

| Colonne | Source | Type | Description | À garder ? |
|--------|--------|------|-------------|-----------|
| `operation_id` | operations.csv | entier | Identifiant unique de l'opération 
| `date_heure_reception_alerte` | operations.csv | datetime | Date/heure de réception de l'alerte 
| `date_heure_fin_operation` | operations.csv | datetime | Date/heure de fin de l'opération 
| `type_operation` | operations.csv | texte | Type : MAS, SAR, etc. 
| `evenement` | operations.csv | texte | Nature de l'événement (avarie, baignade, etc.) 
| `moyen_alerte` | operations.csv | texte | VHF, téléphone, balise, etc. 
| `qui_alerte` | operations.csv | texte | Qui a donné l'alerte 
| `categorie_qui_alerte` | operations.csv | texte | Catégorie de l'alertant 
| `cross` | operations.csv | texte | Centre opérationnel (CROSS/MRCC) 
| `departement` | operations.csv | texte | Département ou collectivité concernée 
| `est_metropolitain` | operations.csv | booléen | Opération en métropole 
| `vent_force` | operations.csv | nombre | Force du vent (échelle Beaufort) 
| `mer_force` | operations.csv | nombre | Hauteur de la mer 
| `numero_sitrep` | operations.csv | entier | Numéro du compte-rendu SITREP 
| `cross_sitrep` | operations.csv | texte | Référence complète (ex: "Nouvelle-Calédonie SAR 2025/184") 
| `systeme_source` | operations.csv | texte | Système d'origine (ex: secmarweb) 
| `seconde_autorite` | operations.csv | texte | >96% NaN | ❌ SUPPRIMÉ |

### Colonnes ajoutées depuis `operations_stats.csv`

| Colonne | Description | Calcul |
|--------|-------------|--------|
| `sans_flotteur_implique` | Aucun flotteur impliqué | Booléen direct |
| `total_flotteurs_impliques` | Nombre total de flotteurs impliqués | Somme de toutes les colonnes `nombre_flotteurs_*` |

### Colonnes supprimées de `operations_stats.csv`
- `nom_dst` (98.8% NaN)
- `nom_stm` (93.2% NaN)
- Toutes les colonnes détaillées `nombre_flotteurs_...` (trop fines pour le MVP)
- Colonnes temporelles (`annee`, `mois`, etc.) → calculables depuis la date

## Table `flotteurs`

| Colonne | Description |
|--------|-------------|
| `operation_id` | Lien vers l'opération |
| `numero_ordre` | Ordre du flotteur dans l'opération |
| `pavillon` | Nationalité (Français, Étranger, etc.) |
| `resultat_flotteur` | Issue (Remorqué, Assisté, etc.) |
| `type_flotteur` | Type détaillé (Plaisance à moteur < 8m, etc.) |
| `categorie_flotteur` | Catégorie large (Plaisance, Commerce, Pêche) |
| `numero_immatriculation` | Immatriculation (si connue) |

## Table `resultats_humain`

| Colonne | Description |
|--------|-------------|
| `operation_id` | Lien vers l'opération |
| `categorie_personne` | Type de personne (Plaisancier français, Marin étranger, etc.) |
| `resultat_humain` | Statut (Personne assistée, tirée d'affaire, etc.) |
| `nombre` | Nombre total de personnes dans cette catégorie |
| `dont_nombre_blesse` | Nombre de blessés parmi elles |
