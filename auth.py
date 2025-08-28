import streamlit as st
import bcrypt

def check_credentials(email: str, password: str) -> bool:
    """Retourne True si l'email est autorisé et le mot de passe est bon (bcrypt)."""
    allowed = set(st.secrets["auth"]["allowed_emails"])
    if email not in allowed:
        return False

    hashed = st.secrets["auth"]["passwords"].get(email)
    if not hashed:
        return False

    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def login_form():
    """Affiche le formulaire et retourne (ok, email)."""
    with st.form("login"):
        email = st.text_input("E-mail", key="login_email")
        pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
        ok = st.form_submit_button("Se connecter")
    if ok and check_credentials(email, pwd):
        return True, email
    elif ok:
        st.error("Identifiants invalides")
    return False, None
