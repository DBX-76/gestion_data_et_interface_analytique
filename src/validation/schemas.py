"""
Schémas de validation des données utilisant Pandera pour la base SEC MAR.

Ce module définit des schémas de validation stricts pour toutes les tables avec validation paresseuse
pour capturer toutes les erreurs d'un coup plutôt que de s'arrêter à la première erreur.
"""

import pandas as pd
import pandera.pandas as pa
from pandera import Column, DataFrameSchema, Check
from datetime import datetime
import re

# Custom check functions
def validate_operation_id(operation_id: int) -> bool:
    """Valide le format operation_id (doit être numérique, peut être négatif)"""
    return isinstance(operation_id, int)

def validate_cross_name(cross: str) -> bool:
    """Valide le format du nom CROSS"""
    if pd.isna(cross):
        return False
    return bool(re.match(r'^[A-Z]{4,}$', str(cross)))

def validate_department(dept: str) -> bool:
    """Valide le nom du département"""
    if pd.isna(dept):
        return False
    return len(str(dept).strip()) > 0

def validate_type_operation(type_op: str) -> bool:
    """Valide le type d'opération"""
    valid_types = ["SAR", "MAS", "DIV", "SUR"]
    return str(type_op).upper() in valid_types

def validate_coordinates(coord: float) -> bool:
    """Valide les coordonnées latitude/longitude"""
    if pd.isna(coord) or coord == -1:
        return True  # -1 est autorisé comme "inconnu"
    return -180 <= coord <= 180

def validate_beaufort_force(force: int) -> bool:
    """Valide l'échelle de force du vent Beaufort"""
    if pd.isna(force) or force == -1:
        return True  # -1 est autorisé comme "inconnu"
    return 0 <= force <= 12

def validate_douglas_scale(scale: int) -> bool:
    """Valide l'échelle d'état de la mer Douglas"""
    if pd.isna(scale) or scale == -1:
        return True  # -1 est autorisé comme "inconnu"
    return 0 <= scale <= 9

# Operations table validation schema
OPERATIONS_SCHEMA = DataFrameSchema({
    "operation_id": Column(
        int,
        checks=[
            Check(validate_operation_id, name="valid_operation_id")
        ],
        nullable=False,
        unique=True,
        description="Identifiant unique d'opération"
    ),

    "date_heure_reception_alerte": Column(
        str,
        nullable=True,  # Allow null for existing data
        required=False,
        description="Date et heure de réception de l'alerte"
    ),

    "date_heure_fin_operation": Column(
        str,
        nullable=True,
        required=False,
        description="Date et heure de fin d'opération"
    ),

    "type_operation": Column(
        str,
        nullable=True,  
        description="Type d'opération (SAR, MAS, DIV, SUR)"
    ),

    "type_operation_saisi": Column(
        bool,
        nullable=True,
        description="Si le type d'opération a été saisi manuellement"
    ),

    "evenement": Column(
        str,
        nullable=True,
        description="Description de l'événement"
    ),

    "categorie_evenement": Column(
        str,
        nullable=True,
        description="Catégorie d'événement"
    ),

    "zone_responsabilite": Column(
        str,
        nullable=True,
        description="Zone de responsabilité"
    ),

    "fuseau_horaire": Column(
        str,
        nullable=True,
        description="Fuseau horaire"
    ),

    "pourquoi_alerte": Column(
        str,
        nullable=True,
        description="Motif d'alerte"
    ),

    "pourquoi_alerte_saisi": Column(
        bool,
        nullable=True,
        description="Si le motif d'alerte a été saisi manuellement"
    ),

    "moyen_alerte": Column(
        str,
        nullable=True,
        description="Moyen d'alerte"
    ),

    "qui_alerte": Column(
        str,
        nullable=True,
        description="Qui a donné l'alerte"
    ),

    "categorie_qui_alerte": Column(
        str,
        nullable=True,
        description="Catégorie de l'alertant"
    ),

    "cross_name": Column(
        str,
        nullable=True,
        description="Nom du centre CROSS"
    ),

    "departement": Column(
        str,
        nullable=True,
        description="Département"
    ),

    "prefecture_maritime": Column(
        str,
        nullable=True,
        description="Préfecture maritime"
    ),

    "est_metropolitain": Column(
        bool,
        nullable=True,
        description="Est en France métropolitaine"
    ),

    "vent_force": Column(
        float,
        nullable=True,
        required=False,
        description="Force du vent (échelle Beaufort)"
    ),

    "mer_force": Column(
        float,
        nullable=True,
        required=False,
        description="État de la mer (échelle Douglas)"
    ),

    "vent_direction": Column(
        float,
        nullable=True,
        required=False,
        description="Direction du vent en degrés"
    ),

    "longitude": Column(
        float,
        nullable=True,
        description="Coordonnée longitude"
    ),

    "latitude": Column(
        float,
        nullable=True,
        description="Coordonnée latitude"
    ),

    "autorite": Column(
        str,
        nullable=True,
        description="Autorité"
    ),

    "numero_sitrep": Column(
        int,
        nullable=True,
        required=False,
        description="Numéro SITREP"
    ),

    "cross_sitrep": Column(
        str,
        nullable=True,
        description="Référence SITREP complète"
    ),

    "systeme_source": Column(
        str,
        nullable=True,
        description="Système source"
    ),

    "sans_flotteur_implique": Column(
        bool,
        nullable=True,
        description="Aucun flotteur impliqué"
    ),

    "total_flotteurs_impliques": Column(
        int,
        nullable=True,
        description="Nombre total de flotteurs impliqués"
    ),

    "maree_categorie": Column(
        str,
        nullable=True,
        description="Catégorie de marée"
    ),

    "maree_port": Column(
        str,
        nullable=True,
        description="Port de référence marée"
    ),

    "maree_coefficient": Column(
        int,
        nullable=True,
        description="Coefficient de marée"
    ),

    "distance_cote_metres": Column(
        int,
        nullable=True,
        description="Distance à la côte en mètres"
    ),

    "distance_cote_milles_nautiques": Column(
        int,
        nullable=True,
        description="Distance à la côte en milles nautiques"
    ),

    "est_vacances_scolaires": Column(
        bool,
        nullable=True,
        description="Pendant les vacances scolaires"
    ),

    "donnees_meteo_imputees": Column(
        bool,
        nullable=True,
        description="Données météo imputées"
    )
})

# Schéma de table Flotteurs (espace réservé - à compléter)
FLOTTEURS_SCHEMA = DataFrameSchema({
    "operation_id": Column(int, nullable=False, description="Référence à l'opération"),
    "numero_ordre": Column(int, nullable=False, description="Numéro d'ordre"),
    "pavillon": Column(str, nullable=False, description="Pavillon/Nationalité"),
    "resultat_flotteur": Column(str, nullable=False, description="Résultat du flotteur"),
    "type_flotteur": Column(str, nullable=False, description="Type de flotteur"),
    "categorie_flotteur": Column(str, nullable=False, description="Catégorie de flotteur"),
    "numero_immatriculation": Column(str, nullable=True, description="Numéro d'immatriculation")
}, strict=True)

# Schéma de table Résultats Humain (espace réservé - à compléter)
RESULTATS_HUMAIN_SCHEMA = DataFrameSchema({
    "operation_id": Column(int, nullable=False, description="Référence à l'opération"),
    "categorie_personne": Column(str, nullable=False, description="Catégorie de personne"),
    "resultat_humain": Column(str, nullable=False, description="Résultat humain"),
    "nombre": Column(int, nullable=False, description="Nombre total"),
    "dont_nombre_blesse": Column(int, nullable=False, description="Nombre de blessés")
}, strict=True)