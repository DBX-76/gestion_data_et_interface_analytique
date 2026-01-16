# Dictionnaire des données

##  Stratégie de modélisation

| Table source | Action retenue | Raison |
|--------------|----------------|--------|
| `operations.csv` | **Conservée et enrichie** | Base principale du CRUD ; enrichie avec 2 agrégats de `operations_stats` |
| `flotteurs.csv` | **Toutes les colonnes conservées** | Données détaillées utiles pour le suivi des embarcations |
| `resultats_humain.csv` | **Toutes les colonnes conservées** | Informations critiques sur les personnes impliquées |
| `operations_stats.csv` | **Non chargée comme table** | Seulement 2 indicateurs extraits (`sans_flotteur_implique`, `total_flotteurs_impliques`) → évite la redondance et simplifie le modèle |

> Cette approche permet un **CRUD simple** et  un **dashboard efficace**

## Table `operations`

| Colonne | Description |
|--------|-------------|
| `operation_id` | Identifiant unique de l'opération |
| `date_heure_reception_alerte` | Date/heure de réception de l'alerte |
| `date_heure_fin_operation` | Date/heure de fin de l'opération |
| `type_operation` | Type d’opération : SAR, MAS, DIV, SUR |
| `type_operation_saisi` | `True` si saisi manuellement, `False` si imputé |
| `evenement` | Nature de l'événement (avarie, baignade, etc.) |
| `categorie_evenement` | Catégorie métier regroupant les événements (ex: "Avaries non suivies d'accident navire", "Fausses alertes", ... |
| `zone_responsabilite` | Zone de responsabilité opérationnelle du CROSS (ex: "Eaux territoriales", "Responsabilité française") |
| `fuseau_horaire` | Fuseau horaire de l’opération (ex: "Europe/Paris", "Pacific/Noumea") |
| `pourquoi_alerte` | Motif de l’alerte (Balise 406, signal pyrotechnique, etc.) |
| `pourquoi_alerte_saisi` | `True` si saisi manuellement, `False` si imputé |
| `moyen_alerte` | Canal d’alerte (VHF, téléphone, etc.) |
| `qui_alerte` | Personne ou entité ayant donné l’alerte |
| `categorie_qui_alerte` | Catégorie de l’alertant |
| `cross_name` | Centre opérationnel (CROSS/MRCC) ayant géré l’opération |
| `departement` | Département ou collectivité concernée |
| `prefecture_maritime` | Préfecture maritime responsable |
| `est_metropolitain` | Opération en métropole ? |
| `vent_force` | Force du vent (échelle Beaufort) |
| `mer_force` | Hauteur de la mer |
| `vent_direction` | Direction du vent (degrés, -1 si inconnue) |
| `vent_direction_categorie` | Catégorie de direction (ex: "VARIABLE") |
| `longitude` | Coordonnée géographique (-1 si inconnue) |
| `latitude` | Coordonnée géographique (-1 si inconnue) |
| `autorite` | Autorité en charge |
| `numero_sitrep` | Numéro du compte-rendu SITREP |
| `cross_sitrep` | Référence complète (ex: "Nouvelle-Calédonie SAR 2025/184") |
| `systeme_source` | Système d'origine (ex: secmarweb) |
| `phase_journee` | Période de la journée : matinée, déjeuner, après-midi, nuit |
| `sans_flotteur_implique` | Aucun flotteur impliqué ? |
| `total_flotteurs_impliques` | Nombre total de flotteurs impliqués |
| `maree_categorie` | Catégorie de marée |
| `maree_port` | Port de référence pour la marée |
| `maree_coefficient` | Coefficient de marée (-1 si inconnu) |
| `distance_cote_metres` | Distance à la côte en mètres (-1 si inconnue) |
| `distance_cote_milles_nautiques` | Distance à la côte en milles nautiques (-1 si inconnue) |
| `est_vacances_scolaires` | Opération pendant les vacances scolaires ? |
| `donnees_meteo_imputees` | `True` si vent/mer ont été imputés par la médiane |

> 💡 **Note sur l’imputation contrôlée**  
> Les colonnes `pourquoi_alerte` et `type_operation` ont été imputées automatiquement à partir de leur relation avec `evenement`, puis complétées par le mode global.  
> Deux flags (`pourquoi_alerte_saisi`, `type_operation_saisi`) indiquent si la valeur provient d’une saisie humaine (`True`) ou d’une imputation (`False`).  
> Ces données restent modifiables via l’interface CRUD, conformément à l’objectif du projet.

### Colonnes supprimées de `operations.csv`
- `seconde_autorite` (>96 % de valeurs manquantes)

### Colonnes ajoutées depuis `operations_stats.csv`
| Colonne | Description | Calcul |
|--------|-------------|--------|
| `sans_flotteur_implique` | Aucun flotteur impliqué ? | Booléen direct |
| `total_flotteurs_impliques` | Nombre total de flotteurs impliqués | Somme de toutes les colonnes `nombre_flotteurs_*` |

### Colonnes supprimées de `operations_stats.csv`
- `nom_dst` (98,8 % de NaN)
- `nom_stm` (93,2 % de NaN)
- Toutes les colonnes détaillées `nombre_flotteurs_...` (trop fines pour le MVP)
- Colonnes temporelles (`annee`, `mois`, etc.) → calculables depuis la date

---

## Table `flotteurs`

| Colonne | Description |
|--------|-------------|
| `operation_id` | Lien vers l'opération |
| `numero_ordre` | Ordre du flotteur dans l'opération (-1 si inconnu) |
| `pavillon` | Nationalité (Français, Étranger, etc.) |
| `resultat_flotteur` | Issue (Remorqué, Assisté, etc.) |
| `type_flotteur` | Type détaillé (Plaisance à moteur < 8m, etc.) |
| `categorie_flotteur` | Catégorie large (Plaisance, Commerce, Pêche) |
| `numero_immatriculation` | Immatriculation (si connue) |

---

## Table `resultats_humain`

| Colonne | Description |
|--------|-------------|
| `operation_id` | Lien vers l'opération |
| `categorie_personne` | Type de personne (Plaisancier français, Marin étranger, etc.) |
| `resultat_humain` | Statut (Personne assistée, tirée d'affaire, etc.) |
| `nombre` | Nombre total de personnes dans cette catégorie |
| `dont_nombre_blesse` | Nombre de blessés parmi elles |

## Table `audit_log`

Table de traçabilité des modifications manuelles effectuées via l’application.

| Colonne | Description |
|--------|-------------|
| `id` | Identifiant technique auto-incrémenté de l’entrée d’audit |
| `table_name` | Nom de la table modifiée (ex: `"operations"`) |
| `operation` | Type d’opération (`"UPDATE"`, `"INSERT"`, `"DELETE"`) |
| `changed_by` | Identifiant de l’utilisateur ayant effectué la modification |
| `operation_id` | `operation_id` de l’opération concernée (référence vers `operations`) |
| `column_name` | Nom de la colonne modifiée (ex: `"type_operation"`) |
| `old_value` | Valeur avant modification (sous forme textuelle) |
| `new_value` | Valeur après modification (sous forme textuelle) |
| `timestamp` | Date et heure de la modification (UTC par défaut) |
