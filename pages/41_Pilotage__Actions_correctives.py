# pages/41_Pilotage_Actions_correctives.py
import streamlit as st
import pandas as pd
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

st.set_page_config(page_title="Actions correctives — Suivi simplifié", layout="wide")
st.title("🛠️ Actions correctives — Suivi simplifié")

# =============== Données / Fichier ===============
BASE_DIR = Path("data") / "pilotage"
BASE_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = BASE_DIR / "actions_correctives.csv"

VISIBLE_COLS = [
    "ID", "Description de l’action", "Responsable",
    "Échéance", "Statut", "Date de clôture", "Commentaires"
]
ALL_COLS = ["_rid"] + VISIBLE_COLS   # _rid = identifiant interne persistant

if not CSV_PATH.exists():
    pd.DataFrame(columns=ALL_COLS).to_csv(CSV_PATH, index=False)

def load_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, dtype=str).fillna("")
    for c in ALL_COLS:
        if c not in df.columns:
            df[c] = ""
    if df.empty:
        df = pd.DataFrame([{c: "" for c in ALL_COLS}])
        df.loc[0, "_rid"] = "1"
        df.to_csv(CSV_PATH, index=False)
    # attribuer _rid manquants
    mask = (df["_rid"] == "") | (df["_rid"].isna())
    if mask.any():
        max_id = pd.to_numeric(df["_rid"], errors="coerce").max()
        start = 1 if pd.isna(max_id) else int(max_id) + 1
        for idx in df.index[mask]:
            df.at[idx, "_rid"] = str(start); start += 1
        df.to_csv(CSV_PATH, index=False)
    return df

def save_df(df: pd.DataFrame):
    df = df.reindex(columns=ALL_COLS).fillna("")
    df.to_csv(CSV_PATH, index=False)

df = load_df()

# =============== Styles ===============
st.markdown("""
<style>
.ag-theme-alpine .ag-header,.ag-theme-alpine .ag-header-viewport,.ag-theme-alpine .ag-header-row{
  background:#2F80ED!important;color:#fff!important;border:none!important;}
.ag-theme-alpine .ag-header-cell-text{color:#fff!important;font-weight:600;}
.ag-theme-alpine .ag-row-odd{background:#fafafa!important;}
.ag-theme-alpine .ag-row-even{background:#fff!important;}
.ag-theme-alpine .ag-row:hover{background:#f2f6ff!important;}
.ag-popup,.ag-overlay,.ag-popup-editor{z-index:9999!important;}
/* look propre du <select> Statut */
.ag-theme-alpine .ag-cell select{
  width:100%;height:30px;border:1px solid #e3e3e3;border-radius:6px;background:#fff;padding:2px 8px;
}
</style>
""", unsafe_allow_html=True)

# =============== États UI ===============
if "show_search" not in st.session_state: st.session_state.show_search = False
if "edit_mode"  not in st.session_state: st.session_state.edit_mode  = True
if "do_add"     not in st.session_state: st.session_state.do_add     = False

# =============== Barre d’icônes ===============
c_add, c_search, c_edit, c_del, _ = st.columns([0.06, 0.06, 0.06, 0.06, 1])

if c_add.button("＋", help="Ajouter une ligne", use_container_width=True):
    st.session_state.do_add = True
    st.rerun()

if c_search.button("⌕", help="Recherche globale", use_container_width=True):
    st.session_state.show_search = not st.session_state.show_search

if c_edit.button("✎", help="Activer/Désactiver l’édition (sauf Statut)", use_container_width=True):
    st.session_state.edit_mode = not st.session_state.edit_mode

delete_click = c_del.button("🗑", help="Supprimer la sélection", use_container_width=True)

# Ajout protégé (une seule exécution)
if st.session_state.do_add:
    new_rid = str((pd.to_numeric(df["_rid"], errors="coerce").max() or 0) + 1)
    new_row = {col: "" for col in ALL_COLS}; new_row["_rid"] = new_rid
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(df)
    st.session_state.do_add = False
    st.rerun()

# =============== Recherche compacte ===============
quick = ""
if st.session_state.show_search:
    quick = st.text_input("Tape pour filtrer…", "", label_visibility="collapsed")
st.markdown("<hr/>", unsafe_allow_html=True)

# =============== Renderer 'select' permanent (Statut) ===============
status_renderer = JsCode("""
class StatusRenderer {
  init(params){
    const select = document.createElement('select');
    const opts = ['','Ouverte','En cours','Bloquée','Fermée','Annulée'];
    for (const o of opts){
      const opt = document.createElement('option');
      opt.value = o; opt.text = o || '— Statut —';
      if ((params.value||'') === o){ opt.selected = true; }
      select.appendChild(opt);
    }
    select.addEventListener('change', () => { params.setValue(select.value); });
    this.eGui = select;
  }
  getGui(){ return this.eGui; }
  refresh(){ return false; }
}
""")

status_cell_style = JsCode("""
function(params){
  const v = (params.value||'').toString().toLowerCase();
  if (v==='en cours') return {'backgroundColor':'#FFF1BF'};
  if (v==='bloquée' || v==='bloquee') return {'backgroundColor':'#FAD4D4'};
  if (v==='fermée' || v==='fermee') return {'backgroundColor':'#DDF3E0'};
  if (v==='annulée' || v==='annulee') return {'backgroundColor':'#EEEEEE'};
  if (v==='ouverte') return {'backgroundColor':'#E5F0FF'};
  return {};
}
""")

# =============== Grille ===============
grid_df = df[["_rid"] + VISIBLE_COLS].copy()
grid_df["_rid"] = grid_df["_rid"].astype(str)  # important pour getRowId

gb = GridOptionsBuilder.from_dataframe(grid_df)
gb.configure_default_column(resizable=True, sortable=True, filter=False,
                            editable=st.session_state.edit_mode)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=25)

# Cases à cocher + case d'entête
gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=True)
# Afficher la case sur la première colonne (ID)
gb.configure_column("ID", checkboxSelection=True, headerCheckboxSelection=True)

# Empêcher la sélection au clic sur la ligne (case uniquement)
gb.configure_grid_options(suppressRowClickSelection=True)

# >>> ID de ligne AG Grid = _rid (clé stable pour la suppression)
gb.configure_grid_options(getRowId=JsCode("function(params) { return params.data._rid; }"))

gb.configure_column("_rid", hide=True)  # caché mais présent dans les data
gb.configure_column("Statut", editable=False, cellRenderer=status_renderer, cellStyle=status_cell_style)

# zébrage
gb.configure_grid_options(rowClassRules={
    "ag-row-odd": "params.node.rowIndex % 2 === 1",
    "ag-row-even": "params.node.rowIndex % 2 === 0",
})

grid_options = gb.build()
if quick:
    grid_options["quickFilterText"] = quick

resp = AgGrid(
    grid_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    data_return_mode="AS_INPUT",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    theme="alpine",
    key="grid_actions_status_select",
    height=650,
)

# Données renvoyées par AG Grid
resp_data = resp.get("data", None)
if resp_data is None:
    resp_data = grid_df.to_dict("records")

edited_df = (
    pd.DataFrame(resp_data)
    .reindex(columns=["_rid"] + VISIBLE_COLS)
    .fillna("")
)

# =============== Autosave silencieux ===============
merged = df.drop(columns=VISIBLE_COLS, errors="ignore").merge(edited_df, on="_rid", how="right")
if not merged.equals(df.reindex(columns=merged.columns)):
    save_df(merged)
    df = merged

# =============== Suppression via _rid (ultra-fiable) ===============
if delete_click:
    selected_rows = resp.get("selected_rows") or []
    rids_to_drop = set()

    # 1) essayer de lire _rid directement
    for r in selected_rows:
        rid = str(r.get("_rid", "")).strip()
        if rid:
            rids_to_drop.add(rid)

    # 2) récupérer le nodeId (AG Grid) qui == _rid grâce à getRowId
    if selected_rows:
        for r in selected_rows:
            info = (r.get("_selectedRowNodeInfo") or {})
            node_id = info.get("nodeId")
            if node_id:
                rids_to_drop.add(str(node_id))


    