import streamlit as st
HSE_PASSWORD = "filmod" 

def set_role(role: str):
    """Mémorise le rôle courant ('operateur' ou 'hse')."""
    st.session_state["role"] = role

def login_hse(pwd: str) -> bool:
    """Vérifie le mot de passe HSE et mémorise l'état de connexion."""
    if "mdp_try" not in st.session_state:
        st.session_state["mdp_try"] = 0
    if pwd == HSE_PASSWORD:
        st.session_state["mdp_ok"] = True
        st.session_state["role"] = "hse"
        return True
    st.session_state["mdp_try"] += 1
    return False

def require_hse():
    """À placer en haut de chaque page réservée HSE."""
    if st.session_state.get("role") != "hse" or not st.session_state.get("mdp_ok"):
        st.error(" Accès réservé au Responsable HSE.")
        st.page_link("app.py", label="↩ Retour à l'accueil")
        st.stop()
