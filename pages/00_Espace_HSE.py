import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Espace HSE", layout="wide")
st.title(" Espace HSE")

# Définir les sections et pages associées
pages_hse = {
    "Pilotage": {
        " Tableau de bord": "20_Tableau_de_bord_KPI",
        " Actions correctives": "41_Pilotage_Actions_correctives",
        " Plans d'actions": "42_Pilotage_Plans_d_actions",
        " Réunions": "43_Pilotage_Reunions"
    },
    "Personnel": {
        " Menu Personnel": "30_Personnel_Menu",
        " Fiches de poste": "31_Personnel_Fiches_de_poste",
        " Formation": "32_Personnel_Formation",
        " Check List": "33_Personnel__Check_List"
    },
    "Documents": {
        " Menu Documents": "50_Documents_Menu",
        " Plans d'évacuation": "51_Documents_Plans_evacuation",
        " Consignes de sécurité": "52_Documents_Consignes"
    }
}

# Choix de la section
choix_section = st.sidebar.selectbox("Choisir une section :", list(pages_hse.keys()))

# Afficher les boutons correspondant aux pages de la section choisie
st.subheader(f"Section : {choix_section}")

for label, page in pages_hse[choix_section].items():
    if st.button(label):
        switch_page(page)

