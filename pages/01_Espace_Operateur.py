import streamlit as st
from auth import require_login, logout

st.set_page_config(page_title="Espace Opérateur", layout="wide")
require_login()

st.title("Espace Opérateur / Chef d’atelier")
st.write("Contenus réservés aux opérateurs.")
if st.button("Se déconnecter"):
    logout()