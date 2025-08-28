import streamlit as st

if not st.session_state.get("auth"):
    st.warning("Veuillez vous connecter.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()
