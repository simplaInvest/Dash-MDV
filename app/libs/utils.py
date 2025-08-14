import streamlit as st

def vspace(px: int = 16):
    """Espaço em branco vertical (px)."""
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)
