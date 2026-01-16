import streamlit as st
import pandas as pd
from datetime import datetime
from database.read import get_operations, get_operation_by_id, get_operations_count, get_operations_by_id_range
from database.update import update_operation, delete_operation, insert_operation
from ingestion.data_ingestion import ingest_operations_data

def main():
    # Informations générales
    total_operations = get_operations_count()
    st.info(f"📊 Base de données : {total_operations} opérations")

    # Section Upload de données
    st.header("📤 Importer des données (avec validation)")

    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV ou Excel",
        type=['csv', 'xlsx', 'xls'],
        help="Le fichier sera validé avec Pandera avant insertion"
    )

    if uploaded_file is not None:
        try:
            # Lire le fichier
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)

            st.success(f"✅ Fichier chargé : {len(df_upload)} lignes")

            # Aperçu des données
            st.subheader("👀 Aperçu des données")
            st.dataframe(df_upload.head(), use_container_width=True)

            # Option de validation
            skip_validation = st.checkbox("⚠️ Ignorer la validation (pour données existantes)", value=False,
                                        help="Cochez cette case si vous importez des données déjà validées")

            # Validation et ingestion
            if st.button("🔍 Valider et importer", key="validate_import"):
                with st.spinner("Traitement des données en cours..."):
                    if skip_validation:
                        # Insertion directe sans validation
                        inserted_count = 0
                        errors = []
                        for _, row in df_upload.iterrows():
                            try:
                                operation_data = row.to_dict()
                                # Remove NaN values
                                operation_data = {k: v for k, v in operation_data.items() if pd.notna(v)}
                                success = insert_operation(operation_data, changed_by=f"system_upload_{uploaded_file.name}")
                                if success:
                                    inserted_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {row.name}: {str(e)}")

                        ingestion_report = {
                            "status": "success" if inserted_count > 0 else "partial",
                            "total_rows": len(df_upload),
                            "valid_rows": len(df_upload),  # Assume all valid if skipping validation
                            "invalid_rows": 0,
                            "inserted_rows": inserted_count,
                            "quarantine_file": None,
                            "validation_report": {"status": "skipped", "message": "Validation ignorée"},
                            "errors": errors
                        }
                    else:
                        # Validation normale
                        ingestion_report = ingest_operations_data(df_upload, source=f"upload_{uploaded_file.name}")

                # Afficher le rapport
                st.subheader("📊 Rapport d'ingestion")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total lignes", ingestion_report["total_rows"])
                with col2:
                    st.metric("Valides", ingestion_report["valid_rows"])
                with col3:
                    st.metric("Invalides", ingestion_report["invalid_rows"])
                with col4:
                    st.metric("Insérées", ingestion_report["inserted_rows"])

                if ingestion_report["status"] == "success":
                    if ingestion_report["valid_rows"] > 0:
                        st.success(f"✅ {ingestion_report['inserted_rows']} opérations insérées avec succès")

                    if ingestion_report["invalid_rows"] > 0:
                        st.warning(f"⚠️ {ingestion_report['invalid_rows']} lignes invalides mises en quarantaine")
                        st.info(f"📁 Fichier de quarantaine : {ingestion_report['quarantine_file']}")

                        # Afficher les erreurs de validation
                        if "validation_report" in ingestion_report and ingestion_report["validation_report"]["total_errors"] > 0:
                            with st.expander("📋 Détails des erreurs de validation"):
                                for error in ingestion_report["validation_report"]["schema_errors"]:
                                    st.error(f"**{error['column']}**: {error['error_message']}")
                                for error in ingestion_report["validation_report"]["dataframe_errors"]:
                                    st.error(f"**{error['check']}**: {error['error_message']}")
                else:
                    st.error("❌ Erreur lors de l'ingestion")
                    for error in ingestion_report["errors"]:
                        st.error(error)

        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier : {str(e)}")

    st.divider()

    # Option d'affichage de tous les enregistrements
    st.header("📋 Vue d'ensemble")
    if st.button("🔍 Afficher toutes les opérations", key="show_all"):
        st.warning(f"⚠️ Chargement de {total_operations} opérations - cela peut prendre du temps...")
        df_all = get_operations(limit=None)  # Pas de limite
        st.success(f"✅ {len(df_all)} opérations affichées")
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.info("💡 Utilisez la section ci-dessous pour filtrer par intervalle d'IDs")

    # === Section Affichage par intervalle ===
    st.header("📊 Afficher des opérations (intervalle ID)")

    col1, col2 = st.columns(2)
    with col1:
        min_display_id = st.number_input("ID minimum", step=1, value=0, key="min_display")
    with col2:
        max_display_id = st.number_input("ID maximum", step=1, value=0, key="max_display")

    display_btn = st.button("🔍 Afficher", key="display_ok")

    if display_btn and min_display_id <= max_display_id:
        df_range = get_operations_by_id_range(min_display_id, max_display_id)
        if df_range.empty:
            st.warning("Aucune opération trouvée dans cet intervalle")
        else:
            st.success(f"✅ {len(df_range)} opérations trouvées")
            st.dataframe(df_range, use_container_width=True, hide_index=True)

    # === Section Mise à jour ===
    st.header("✏️ Mettre à jour une opération")

    update_id = st.number_input(
        "ID de l'opération à modifier",
        step=1,
        value=0,
        format="%d",
        key="update_id"
    )
    update_btn = st.button("🔍 OK", key="update_ok")

    if update_btn and update_id != 0:
        current_row = get_operation_by_id(update_id)

        if current_row is None or current_row.empty:
            st.error(f"❌ ID {update_id} non trouvé dans la base")
        else:
            st.success(f"✅ Opération {update_id} trouvée")

            # Afficher l'opération actuelle
            st.subheader(f"📋 Opération #{update_id}")
            st.dataframe(current_row, use_container_width=True, hide_index=True)

            # Formulaire de modification
            with st.form("update_form"):
                st.write("### Modifier les champs")

                # Champs modifiables (simplifié pour l'exemple)
                current_type = current_row["type_operation"].iloc[0] if pd.notna(current_row["type_operation"].iloc[0]) else "SAR"
                current_pourquoi = current_row["pourquoi_alerte"].iloc[0] if "pourquoi_alerte" in current_row.columns and pd.notna(current_row["pourquoi_alerte"].iloc[0]) else "Événement reconnu"

                type_options = ["SAR", "MAS", "DIV", "SUR"]
                new_type = st.selectbox(
                    "Type d'opération",
                    options=type_options,
                    index=type_options.index(current_type) if current_type in type_options else 0
                )

                pourquoi_options = [
                    "Événement reconnu", "Inquiétude", "Balise 406",
                    "Signal pyrotechnique", "Autre", "Balise 121,5 - 243",
                    "Signal radio-électrique", "IMMARSAT C", "IMMARSAT",
                    "Autre signal réglementaire"
                ]
                new_pourquoi = st.selectbox(
                    "Motif d'alerte",
                    options=pourquoi_options,
                    index=pourquoi_options.index(current_pourquoi) if current_pourquoi in pourquoi_options else 0
                )

                changed_by = st.text_input("Modifié par", value="utilisateur_streamlit")

                # Confirmation
                confirm_update = st.checkbox("Confirmer la mise à jour")

                submitted = st.form_submit_button("💾 Mettre à jour")

                if submitted:
                    if not confirm_update:
                        st.warning("⚠️ Veuillez confirmer la mise à jour")
                    else:
                        updates = {}
                        if new_type != current_type:
                            updates["type_operation"] = new_type
                        if new_pourquoi != current_pourquoi:
                            updates["pourquoi_alerte"] = new_pourquoi

                        if not updates:
                            st.info("ℹ️ Aucune modification détectée")
                        else:
                            success = update_operation(
                                operation_id=int(update_id),
                                updates=updates,
                                changed_by=changed_by
                            )

                            if success:
                                st.success("✅ Opération mise à jour avec succès !")
                                st.balloons()
                                # Clear the form after a short delay to show the message
                                import time
                                time.sleep(2)
                                st.session_state.update_id = 0
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la mise à jour")

    # === Section Suppression ===
    st.header("🗑️ Supprimer une opération")

    delete_id = st.number_input(
        "ID de l'opération à supprimer",
        step=1,
        value=0,
        format="%d",
        key="delete_id"
    )
    delete_btn = st.button("🗑️ OK", key="delete_ok")

    if delete_btn and delete_id != 0:
        current_row = get_operation_by_id(delete_id)

        if current_row is None or current_row.empty:
            st.error(f"❌ ID {delete_id} non trouvé dans la base")
        else:
            st.warning(f"⚠️ Voulez-vous vraiment supprimer l'opération {delete_id} ?")
            st.dataframe(current_row, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirmer suppression", key="confirm_delete"):
                    st.write(f"🔍 Tentative de suppression de l'ID: {delete_id}")
                    success = delete_operation(
                        operation_id=int(delete_id),
                        changed_by="utilisateur_streamlit"
                    )
                    if success:
                        st.success("✅ Opération supprimée avec succès !")
                        st.info(f"ℹ️ L'opération #{delete_id} a été définitivement supprimée de la base de données.")
                        st.session_state.delete_id = 0
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la suppression")
            with col2:
                if st.button("❌ Annuler", key="cancel_delete"):
                    st.info("Suppression annulée")
                    st.session_state.delete_id = 0

    # === Section Ajout ===
    st.header("➕ Ajouter une nouvelle opération")

    if st.button("🆕 Créer nouvelle opération", key="add_new"):
        # Générer un ID basé sur la date/heure actuelle
        now = datetime.now()
        new_id = int(now.strftime("%Y%m%d%H%M%S"))  # Format YYYYMMDDHHMMSS

        st.info(f"🆔 ID généré automatiquement : {new_id} (format YYYYMMDDHHMMSS basé sur la date/heure actuelle)")
        st.info("ℹ️ Remplissez tous les champs souhaités. Les champs non remplis prendront des valeurs par défaut.")

        # Formulaire d'ajout avec tous les champs disponibles
        with st.form("add_form"):
            st.write("### Remplir les informations de l'opération")

            col1, col2 = st.columns(2)

            with col1:
                # Champs temporels
                date_reception = st.date_input("Date de réception", value=now.date())
                heure_reception = st.time_input("Heure de réception", value=now.time())
                date_fin = st.date_input("Date de fin (optionnel)", value=None)
                heure_fin = st.time_input("Heure de fin (optionnel)", value=None)

                # Champs principaux
                type_op = st.selectbox("Type d'opération", ["SAR", "MAS", "DIV", "SUR"], index=0)
                type_saisi = st.checkbox("Type saisi manuellement", value=True)
                evenement = st.text_input("Événement")
                categorie_evenement = st.text_input("Catégorie d'événement (optionnel)")

                # Alerte
                pourquoi_alerte = st.selectbox("Motif d'alerte", [
                    "Événement reconnu", "Inquiétude", "Balise 406",
                    "Signal pyrotechnique", "Autre", "Balise 121,5 - 243",
                    "Signal radio-électrique", "IMMARSAT C", "IMMARSAT",
                    "Autre signal réglementaire"
                ], index=0)
                pourquoi_saisi = st.checkbox("Motif saisi manuellement", value=True)
                moyen_alerte = st.text_input("Moyen d'alerte (optionnel)")
                qui_alerte = st.text_input("Qui a alerté (optionnel)")
                categorie_qui_alerte = st.text_input("Catégorie de l'alertant (optionnel)")

            with col2:
                # Localisation
                cross = st.text_input("CROSS", value="CROSS_NAME")
                departement = st.text_input("Département")
                prefecture = st.text_input("Préfecture maritime (optionnel)")
                zone_resp = st.text_input("Zone de responsabilité (optionnel)")
                fuseau = st.selectbox("Fuseau horaire", ["Europe/Paris", "Pacific/Noumea"], index=0)
                est_metropolitain = st.checkbox("Métropole", value=True)

                # Météo
                vent_force = st.number_input("Force du vent (Beaufort)", min_value=-1, value=-1)
                mer_force = st.number_input("État de la mer", min_value=-1, value=-1)
                vent_direction = st.number_input("Direction du vent (°)", min_value=-1, max_value=360, value=-1)
                longitude = st.number_input("Longitude", value=-1.0, format="%.6f")
                latitude = st.number_input("Latitude", value=-1.0, format="%.6f")

                # Autres
                autorite = st.text_input("Autorité (optionnel)")
                numero_sitrep = st.text_input("Numéro SITREP (optionnel)")
                cross_sitrep = st.text_input("Référence SITREP complète (optionnel)")
                systeme = st.text_input("Système source", value="streamlit")

                # Flotteurs
                sans_flotteur = st.checkbox("Sans flotteur impliqué", value=True)
                total_flotteurs = st.number_input("Nombre total de flotteurs", min_value=0, value=0)

                # Marée
                maree_categorie = st.text_input("Catégorie de marée (optionnel)")
                maree_port = st.text_input("Port de référence marée (optionnel)")
                maree_coeff = st.number_input("Coefficient de marée", min_value=-1, value=-1)

                # Distances
                distance_metres = st.number_input("Distance côte (mètres)", min_value=-1, value=-1)
                distance_milles = st.number_input("Distance côte (milles nautiques)", min_value=-1, value=-1)

                # Divers
                est_vacances = st.checkbox("Pendant vacances scolaires", value=False)
                meteo_imputee = st.checkbox("Données météo imputées", value=False)

            changed_by = st.text_input("Créé par", value="utilisateur_streamlit")

            submitted_add = st.form_submit_button("💾 Créer l'opération")

            if submitted_add:
                # Combiner date et heure
                date_heure = datetime.combine(date_reception, heure_reception)
                date_heure_fin = None
                if date_fin and heure_fin:
                    date_heure_fin = datetime.combine(date_fin, heure_fin)

                operation_data = {
                    "operation_id": new_id,
                    "date_heure_reception_alerte": date_heure,
                    "date_heure_fin_operation": date_heure_fin,
                    "type_operation": type_op,
                    "type_operation_saisi": type_saisi,
                    "evenement": evenement,
                    "categorie_evenement": categorie_evenement or None,
                    "zone_responsabilite": zone_resp or None,
                    "fuseau_horaire": fuseau,
                    "pourquoi_alerte": pourquoi_alerte,
                    "pourquoi_alerte_saisi": pourquoi_saisi,
                    "moyen_alerte": moyen_alerte or None,
                    "qui_alerte": qui_alerte or None,
                    "categorie_qui_alerte": categorie_qui_alerte or None,
                    "cross_name": cross,
                    "departement": departement,
                    "prefecture_maritime": prefecture or None,
                    "est_metropolitain": est_metropolitain,
                    "vent_force": vent_force,
                    "mer_force": mer_force,
                    "vent_direction": vent_direction,
                    "longitude": longitude,
                    "latitude": latitude,
                    "autorite": autorite or None,
                    "numero_sitrep": numero_sitrep or None,
                    "cross_sitrep": cross_sitrep or None,
                    "systeme_source": systeme,
                    "sans_flotteur_implique": sans_flotteur,
                    "total_flotteurs_impliques": total_flotteurs,
                    "maree_categorie": maree_categorie or None,
                    "maree_port": maree_port or None,
                    "maree_coefficient": maree_coeff,
                    "distance_cote_metres": distance_metres,
                    "distance_cote_milles_nautiques": distance_milles,
                    "est_vacances_scolaires": est_vacances,
                    "donnees_meteo_imputees": meteo_imputee
                }

                # Supprimer les clés avec valeur None pour éviter les erreurs SQL
                operation_data = {k: v for k, v in operation_data.items() if v is not None}

                success = insert_operation(operation_data, changed_by)
                if success:
                    st.success(f"✅ Nouvelle opération créée avec ID {new_id} !")
                    st.info(f"ℹ️ L'opération #{new_id} a été ajoutée à la base de données avec succès.")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création")

    # Bouton retour
    st.divider()
    if st.button("🏠 Retour à l'accueil", key="back_home"):
        st.session_state.page = "home"
        st.rerun()