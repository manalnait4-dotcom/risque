import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Plans d'actions", layout="wide")
st.title(" Plans d'actions")

# -------- Répertoires --------
BASE_DIR = "data"                     # racine de stockage locale (relative au projet)
FILES_DIR = os.path.join(BASE_DIR, "plans_actions", "fichiers")
CSV_PATH  = os.path.join(BASE_DIR, "plans_actions", "actions.csv")
os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# -------- Utilitaires --------
def human_size(num_bytes: int) -> str:
    for unit in ["B","KB","MB","GB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:3.1f} TB"

def safe_name(name: str) -> str:
    keep = [c for c in name if c.isalnum() or c in (" ","-","_",".")]
    return "".join(keep).strip().replace(" ", "_")

# -------- Onglets --------
tab_files, tab_table = st.tabs([" Fichiers liés", " Tableau d’actions (CSV)"])

# ============ ONGLET FICHIERS ============
with tab_files:
    st.subheader("Ajouter un fichier")
    up = st.file_uploader(
        "Dépose un fichier (PDF, DOCX, XLSX/XLS, CSV, PNG/JPG)",
        type=["pdf","docx","xlsx","xls","csv","png","jpg","jpeg"]
    )
    coln, colbtn = st.columns([3,1])
    display_name = coln.text_input("Nom lisible (facultatif)", placeholder="ex: Plan d’action audit ")
    if colbtn.button(" Enregistrer", use_container_width=True, disabled=(up is None)):
        fname = safe_name(display_name or up.name)
        # Ajoute un timestamp pour éviter les collisions
        root, ext = os.path.splitext(fname)
        fname = f"{root}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext if ext else os.path.splitext(up.name)[1]}"
        path = os.path.join(FILES_DIR, fname)
        with open(path, "wb") as f:
            f.write(up.read())
        st.success(f"Fichier enregistré : **{fname}**")

    st.divider()
    st.subheader("Fichiers existants")

    files = sorted([f for f in os.listdir(FILES_DIR) if os.path.isfile(os.path.join(FILES_DIR, f))])
    if not files:
        st.info("Aucun fichier pour le moment.")
    else:
        for f in files:
            fp = os.path.join(FILES_DIR, f)
            size = human_size(os.path.getsize(fp))
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
            c1, c2, c3, c4, c5 = st.columns([4,1.2,1.2,1.2,1.2])
            c1.write(f"**{f}**  \n*{size} — modifié le {mtime}*")

            # Aperçu rapide pour CSV/Excel/Images
            ext = os.path.splitext(f)[1].lower()
            if c2.button(" Aperçu", key=f"preview_{f}"):
                if ext in [".csv"]:
                    df = pd.read_csv(fp)
                    st.dataframe(df, use_container_width=True)
                elif ext in [".xlsx", ".xls"]:
                    df = pd.read_excel(fp)
                    st.dataframe(df, use_container_width=True)
                elif ext in [".png", ".jpg", ".jpeg"]:
                    st.image(fp, use_container_width=True)
                else:
                    st.info("Aperçu non supporté (utilise Télécharger).")

            with open(fp, "rb") as fh:
                c3.download_button("⬇ Télécharger", data=fh, file_name=f, mime=None, key=f"dl_{f}")

            if c4.button(" Supprimer", key=f"del_{f}"):
                os.remove(fp)
                st.warning(f"Supprimé : {f}")
                st.experimental_rerun()

            if c5.button(" Renommer", key=f"ren_{f}"):
                new_name = st.text_input("Nouveau nom", value=f, key=f"ren_input_{f}")
                if st.button(" Confirmer", key=f"ren_ok_{f}"):
                    new_path = os.path.join(FILES_DIR, safe_name(new_name))
                    os.rename(fp, new_path)
                    st.success("Nom modifié.")
                    st.experimental_rerun()

# ============ ONGLET TABLEAU D'ACTIONS ============
with tab_table:
    st.subheader("Éditer le tableau d’actions")

    # Crée un CSV vide si besoin
    if not os.path.exists(CSV_PATH):
        df_init = pd.DataFrame([
            # Exemple d’une ligne
            {"ID":"A-001","Intitulé":"Former opérateurs à l’évacuation",
             "Responsable":"HSE","Échéance":"2025-09-30","Priorité":"Haute",
             "Statut":"Ouverte","Commentaires":""}
        ], columns=["ID","Intitulé","Responsable","Échéance","Priorité","Statut","Commentaires"])
        df_init.to_csv(CSV_PATH, index=False)

    df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

    # Zone d’import (pour remplacer le tableau)
    with st.expander(" Importer un CSV (remplace le tableau actuel)"):
        new_csv = st.file_uploader("Sélectionne un CSV", type=["csv"], key="csv_import")
        if new_csv is not None and st.button("Remplacer"):
            tmp = pd.read_csv(new_csv, dtype=str).fillna("")
            tmp.to_csv(CSV_PATH, index=False)
            st.success("Tableau remplacé.")
            st.experimental_rerun()

    st.caption("Astuce : double-clique dans une cellule pour éditer. Ajoute des lignes avec le bouton ➕ en bas du tableau.")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Échéance": st.column_config.DateColumn("Échéance"),
            "Priorité": st.column_config.SelectboxColumn("Priorité", options=["Basse","Moyenne","Haute"]),
            "Statut":   st.column_config.SelectboxColumn("Statut", options=["Ouverte","En cours","Bloquée","Fermée"])
        },
        key="editor_actions"
    )

    csave, cexp = st.columns([1,1])
    if csave.button(" Enregistrer le tableau"):
        edited.to_csv(CSV_PATH, index=False)
        st.success("Tableau enregistré.")

    # Export rapide
    if cexp.download_button(
        "⬇ Exporter en CSV",
        data=edited.to_csv(index=False).encode("utf-8"),
        file_name="plans_actions_export.csv",
        mime="text/csv"
    ):
        pass
