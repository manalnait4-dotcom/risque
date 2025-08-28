import streamlit as st
import bcrypt

# ----------------------------------------------------
# CONFIG + STYLE (masquer sidebar, header, footer, badge)
# ----------------------------------------------------
st.set_page_config(
    page_title="SafeWork – HSE",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Masquer le menu hamburger, header, footer */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Masquer toute la sidebar Streamlit */
[data-testid="stSidebar"] {display: none !important;}

/* Optionnel: badge "Hosted with Streamlit" */
.stApp [data-testid="stDecoration"] {display: none !important;}
.stApp a[href*="streamlit.io"] {display: none !important;}

/* Petite carte centrale */
.login-card {
  max-width: 520px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid #e8edf2;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(11,57,84,0.08);
  padding: 18px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# ÉTAT DE SESSION
# ----------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.email = None

# ----------------------------------------------------
# FONCTIONS
# ----------------------------------------------------
def get_users() -> dict:
    """
    Récupère le bloc [users] depuis secrets.
    En local: .streamlit/secrets.toml
    Sur Streamlit Cloud: Settings -> Secrets (même contenu TOML)
    """
    try:
        return dict(st.secrets["users"])
    except Exception:
        return {}

def login(email: str, pwd: str) -> bool:
    users = get_users()
    if email in users:
        stored_hash = users[email].encode()            # hash en bytes
        return bcrypt.checkpw(pwd.encode(), stored_hash)
    return False

def go_hse_page():
    """Basculer vers la page HSE (selon la version de Streamlit)."""
    try:
        st.switch_page("pages/00_Espace_HSE.py")
    except Exception:
        # Si st.switch_page indisponible, proposer un lien
        st.page_link("pages/00_Espace_HSE.py", label=" Accéder à l’espace HSE", icon="🔐")

def logout():
    st.session_state.auth = False
    st.session_state.email = None
    st.experimental_rerun()

# ----------------------------------------------------
# UI
# ----------------------------------------------------
st.title("SafeWork – Sécurité & Prévention")
st.caption("Digitalisation HSE · Suivi des risques · Pilotage · Conformité")
st.write("")

if not st.session_state.auth:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader(" Connexion Responsable HSE")

    with st.form("login_form"):
        email = st.text_input("Adresse e-mail", placeholder="prenom.nom@entreprise.com")
        pwd = st.text_input("Mot de passe", type="password")
        ok = st.form_submit_button("Se connecter")

    if ok:
        if login(email, pwd):
            st.session_state.auth = True
            st.session_state.email = email
            st.success("Connexion réussie ")
            go_hse_page()
        else:
            st.error("E-mail ou mot de passe invalide ")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.success(f"Connecté : **{st.session_state.email}**")
    go_hse_page()
    if st.button("Se déconnecter"):
        logout()
