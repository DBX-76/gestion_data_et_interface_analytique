# src/database/test_update.py
"""
Test manuel de la fonction update_operation.
"""

from update import update_operation

if __name__ == "__main__":
    # ID d'une opération existante (prends-en une dans ton jeu de données)
    operation_id =-135614  # ⚠️ Remplace par un ID réel présent dans ta base !

    # Nouvelles valeurs à appliquer
    updates = {
        "type_operation": "SAR",  # doit être dans la liste autorisée
        "pourquoi_alerte": "Événement reconnu"
    }

    print(f"🔧 Tentative de mise à jour de l'opération {operation_id}...")
    
    success = update_operation(
        operation_id=operation_id,
        updates=updates,
        changed_by="test_user"
    )

    if success:
        print("✅ Mise à jour réussie !")
        print(f"   - Vérifie dans pgAdmin que les colonnes ont été modifiées.")
        print(f"   - Vérifie aussi la table audit_log.")
    else:
        print("❌ Échec de la mise à jour. Vérifie les logs.")