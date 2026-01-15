import streamlit as st
from database.read import get_operations

st.title("🔍 Opérations SEC MAR")

# Filtre simple
df_all = get_operations(limit=1000)  # charge 1000 lignes max
cross_options = ["Tous"] + sorted(df_all["cross_name"].dropna().unique())
selected_cross = st.sidebar.selectbox("Filtrer par CROSS", cross_options)

if selected_cross != "Tous":
    df = df_all[df_all["cross_name"] == selected_cross]
else:
    df = df_all

# Afficher seulement les colonnes utiles
cols_to_show = [
    "operation_id", "date_heure_reception_alerte", "type_operation",
    "evenement", "cross_name", "departement", "systeme_source"
]
st.dataframe(df[cols_to_show], use_container_width=True)
st.info("💡 Faites défiler vers la droite pour voir plus de colonnes")