# Modèle relationnel

## operations
- operation_id (PK)
- date_heure_reception_alerte
- date_heure_fin_operation
- type_operation
- evenement
- cross
- ... (autres colonnes utiles de operations.csv + operations_stats.csv)

## flotteurs
- operation_id (FK → operations)
- numero_ordre
- pavillon
- resultat_flotteur
- ...

## resultats_humain
- operation_id (FK → operations)
- categorie_personne
- resultat_humain
- nombre
- dont_nombre_blesse