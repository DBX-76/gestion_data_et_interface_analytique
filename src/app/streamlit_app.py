import streamlit as st
from validation.validator import validator
import pandas as pd

# Gestion de la navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "operations":
    import operations
    operations.main()
elif st.session_state.page == "flotteurs":
    st.title("⛵ Flotteurs - Bientôt disponible")
    st.info("Fonctionnalité en développement...")
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()
elif st.session_state.page == "resultats_humain":
    st.title("👥 Résultats Humains - Bientôt disponible")
    st.info("Fonctionnalité en développement...")
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()
elif st.session_state.page == "audit_log":
    st.title("📋 Historique des modifications")

    from database.read import get_audit_log

    # Afficher les dernières entrées du journal d'audit
    df_audit = get_audit_log(limit=100)
    if df_audit.empty:
        st.info("Aucun historique disponible")
    else:
        st.success(f"✅ {len(df_audit)} entrées dans l'historique")
        st.dataframe(df_audit, use_container_width=True, hide_index=True)

        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Modifications", len(df_audit))
        with col2:
            st.metric("Utilisateurs actifs", df_audit['changed_by'].nunique())
        with col3:
            st.metric("Tables modifiées", df_audit['table_name'].nunique())

    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()
else:
    # Page d'accueil
    st.title("🏠 Interface Analytique Polyvalente - SEC MAR")

    st.markdown("""
    ## 📊 Gestion des données de secours maritime

    Choisissez la table que vous souhaitez gérer :
    """)

    # Options de navigation
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚢 Opérations", key="nav_operations", use_container_width=True):
            st.session_state.page = "operations"
            st.rerun()

    with col2:
        if st.button("⛵ Flotteurs", key="nav_flotteurs", use_container_width=True):
            st.session_state.page = "flotteurs"
            st.rerun()

    with col3:
        if st.button("👥 Résultats", key="nav_resultats", use_container_width=True):
            st.session_state.page = "resultats_humain"
            st.rerun()

    with col4:
        if st.button("📋 Historique", key="nav_audit", use_container_width=True):
            st.session_state.page = "audit_log"
            st.rerun()

    # Informations générales
    st.divider()
    st.subheader("📈 Statistiques générales")

    from database.read import get_operations_count, get_audit_log

    total_operations = get_operations_count()
    total_audit_entries = len(get_audit_log(limit=None))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Opérations", f"{total_operations:,}")

    with col2:
        st.metric("Flotteurs", "à venir")

    with col3:
        st.metric("Résultats Humains", "à venir")

    with col4:
        st.metric("Historique", f"{total_audit_entries:,}")

    st.info("💡 Cliquez sur une table ci-dessus pour accéder aux opérations CRUD")

    # Section Quarantaine
    st.divider()
    st.subheader("🛡️ Quarantaine des données")

    quarantine_files = validator.get_quarantine_files()
    if quarantine_files:
        st.warning(f"⚠️ {len(quarantine_files)} fichier(s) en quarantaine détecté(s)")

        selected_file = st.selectbox(
            "Sélectionner un fichier de quarantaine",
            quarantine_files,
            key="quarantine_select"
        )

        if selected_file:
            if st.button("📋 Examiner la quarantaine", key="view_quarantine"):
                quarantine_data = validator.load_quarantine_file(selected_file)

                st.subheader(f"📄 Détails de {selected_file}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lignes invalides", quarantine_data["total_invalid_rows"])
                with col2:
                    st.metric("Erreurs de validation", quarantine_data["validation_report"]["total_errors"])
                with col3:
                    st.metric("Source", quarantine_data["source"])

                # Afficher les erreurs
                if quarantine_data["validation_report"]["schema_errors"]:
                    st.subheader("❌ Erreurs de schéma")
                    for error in quarantine_data["validation_report"]["schema_errors"]:
                        st.error(f"**{error['column']}**: {error['error_message']}")

                if quarantine_data["validation_report"]["dataframe_errors"]:
                    st.subheader("❌ Erreurs de dataframe")
                    for error in quarantine_data["validation_report"]["dataframe_errors"]:
                        st.error(f"**{error['check']}**: {error['error_message']}")

                # Afficher les données invalides
                if quarantine_data["invalid_data"]:
                    st.subheader("📊 Données invalides")
                    invalid_df = pd.DataFrame(quarantine_data["invalid_data"])
                    st.dataframe(invalid_df, use_container_width=True)

                    # Option de correction (placeholder)
                    st.info("💡 Fonctionnalité de correction à venir")
    else:
        st.success("✅ Aucune donnée en quarantaine")