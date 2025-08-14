# app/Home.py
import streamlit as st
from pathlib import Path
from libs.utils import vspace
from libs.airtable_client import import_dados  # função que carrega dados do Airtable

st.set_page_config(page_title="Login — CRM de Milhas", page_icon="🔐", layout="centered")

# ---- Ocultar barra lateral ----
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Carregar CSS (opcional) ----
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# =========================
# Autenticação (helpers)
# =========================
AUTH_KEY = "is_authenticated"

def check_password(pw: str) -> bool:
    """Compara a senha digitada com APP_PASSWORD em .streamlit/secrets.toml."""
    app_pw = st.secrets.get("APP_PASSWORD", "")
    return bool(pw) and pw == app_pw

def set_authenticated(flag: bool) -> None:
    st.session_state[AUTH_KEY] = bool(flag)

# Se já estiver autenticado, pula direto para o dashboard
if st.session_state.get(AUTH_KEY):
    try:
        st.switch_page("pages/1_Dashboard.py")
    except Exception:
        # Fallback se switch_page não existir nesta versão
        st.page_link("pages/1_Dashboard.py", label="Abrir Dashboard →", icon="📊")
        st.stop()

# =========================
# Header + Logo
# =========================
vspace(24)
logo_path = Path(__file__).parent / "assets" / "principal.png"
if logo_path.exists():
    st.image(str(logo_path), width=1000) 
else:
    # Placeholder se a logo não estiver presente
    st.markdown("""
    <div style="width: 220px; height: 64px; margin: 0 auto 12px auto;
                border: 1px dashed #E5E7EB; border-radius: 10px;
                display:flex; align-items:center; justify-content:center; color:#6B7280;">
        Logo da Empresa
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; margin-top: 0.75rem; margin-bottom: 1rem;">
        <h2 style="margin:0; font-size:1.15rem; line-height:1.3;">🔐 Acesso ao Dashboard</h2>
        <p style="color:#6B7280; margin-top:.25rem; font-size:0.95rem; line-height:1.5;">
            Bem-vindo! Insira sua senha para acessar o CRM de Milhas.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Formulário de Login
# =========================
with st.form("login"):
    pwd = st.text_input("Senha de acesso", type="password", help="Definida em .streamlit/secrets.toml (APP_PASSWORD).")
    submitted = st.form_submit_button("Entrar")

if submitted:
    if check_password(pwd):
        with st.spinner("Carregando dados do Airtable..."):
            df_leads, df_clientes = import_dados()  # -> DataFrame
            st.session_state["df_leads"] = df_leads
            st.session_state["df_clientes"] = df_clientes
        set_authenticated(True)
        st.success("Login realizado com sucesso. Redirecionando…")
        try:
            st.switch_page("pages/1_Dashboard.py")
        except Exception:
            st.page_link("pages/1_Dashboard.py", label="Ir para o Dashboard →", icon="📊")
            st.experimental_rerun()
    else:
        set_authenticated(False)
        st.warning("Senha incorreta. Verifique e tente novamente.")
