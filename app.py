import streamlit as st
from auth import set_role, login_hse

# ------------------------------------------------------------
# Config de la page
# ------------------------------------------------------------
st.set_page_config(page_title="SafeWork – Sécurité & Prévention", layout="wide")

# ------------------------------------------------------------
# Style minimal pro
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu{visibility:hidden;} header{visibility:hidden;} footer{visibility:hidden;}
    .wrapper{max-width:960px;margin:0 auto;padding:2.2rem 1.2rem;}
    .hero{text-align:center;margin:0 0 1.2rem;}
    .hero .quote{color:#888;font-size:16px;font-style:italic;margin:0 0 6px;}
    .hero .title{font-size:60px;line-height:1.05;font-family:Roboto,system-ui,Segoe UI,Arial,sans-serif;color:#0B3954;margin:0;}
    .hero .subtitle{font-size:18px;color:#5b6b7a;margin:6px 0 0;}
    .card{max-width:520px;margin:22px auto;background:#fff;border:1px solid #e8edf2;border-radius:14px;
          box-shadow:0 10px 24px rgba(11,57,84,0.08);padding:18px 18px;}
    .card h3{margin:0 0 12px;font-size:20px;color:#0B3954;}
    .notice{max-width:960px;margin:0.8rem auto 0;color:#6b7280;font-size:14px;text-align:center;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# En-tête
# ------------------------------------------------------------
st.markdown('<div class="wrapper">', unsafe_allow_html=True)
st.markdown(
    """
      <div class="hero">
        <p class="quote">"Impliquer chacun pour sécuriser tous les postes."</p>
        <h1 class="title">SafeWork –  Sécurité & Prévention</h1>
        <p class="subtitle">Digitalisation HSE · Suivi des risques · Pilotage · Conformité</p>
      </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Carte de connexion (seule chose visible au départ)
# ------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("<h3>Connexion</h3>", unsafe_allow_html=True)

# Options + valeur par défaut
options_roles = ["—", "Opérateur / Chef d'atelier", "Responsable HSE"]
role_choice = st.selectbox("Je suis", options_roles, index=0, key="role_choice")

# Init des états session (si pas déjà présents)
st.session_state.setdefault("go_op", False)
st.session_state.setdefault("go_hse", False)
st.session_state.setdefault("mdp_try", 0)

# ------------------------------------------------------------
# Fonction de redirection multipage
# ------------------------------------------------------------
def safe_switch(page_path: str):
    """
    Redirige vers une page multipage.
    - Si st.switch_page existe (Streamlit récent) => redirection directe
    - Sinon, on affiche un lien cliquable vers la page
    """
    try:
        # Streamlit >= 1.25 (approx.)
        st.switch_page(page_path)
    except Exception:
        st.info("Redirection automatique indisponible dans votre version de Streamlit.")
        # IMPORTANT : label obligatoire
        st.page_link(page_path, label="➡️ Ouvrir la page")

# ------------------------------------------------------------
# Logique des rôles
# ------------------------------------------------------------

# Redirection auto vers l'espace Opérateur
if role_choice == "Opérateur / Chef d'atelier":
    set_role("operateur")
    # éviter boucles/recharges : on redirige une seule fois
    if not st.session_state["go_op"]:
        st.session_state["go_op"] = True
        safe_switch("pages/01_Espace_Operateur.py")

# Redirection auto vers l'espace HSE si mot de passe valide
elif role_choice == "Responsable HSE":
    pwd = st.text_input("Mot de passe", type="password", key="pwd_hse")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        valider = st.button("Se connecter", key="btn_login_hse", type="primary")
    with col_b:
        reinit = st.button("Réinitialiser", key="btn_reset")

    if valider:
        if login_hse(pwd):
            st.session_state["go_hse"] = True
            st.session_state["mdp_try"] = 0  # reset compteur essais
            safe_switch("pages/00_Espace_HSE.py")
        else:
            st.session_state["mdp_try"] += 1
            essais_restants = max(0, 3 - st.session_state["mdp_try"])
            if essais_restants > 0:
                st.error(f"Mot de passe incorrect. Il reste {essais_restants} essai(s).")
            else:
                st.error("Accès bloqué après 3 essais. Relancez l’application.")
                st.stop()

    if reinit:
        for k in ["go_op", "go_hse", "mdp_try", "pwd_hse", "role_choice"]:
            if k in st.session_state:
                del st.session_state[k]
        # Remplace st.experimental_rerun() (déprécié)
        st.rerun()

# ------------------------------------------------------------
# Fermeture des conteneurs
# ------------------------------------------------------------
st.markdown("</div>", unsafe_allow_html=True)  # fin .card
st.markdown("</div>", unsafe_allow_html=True)  # fin .wrapper
