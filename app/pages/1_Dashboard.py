import streamlit as st
from pathlib import Path
import pandas as pd
import pytz
from datetime import datetime, timedelta
import plotly.express as px
from libs.utils import vspace
from libs.ui import criar_funil, pizza, barras_historico_maiusculas, grafico_origem
from datetime import date, timedelta
import streamlit.components.v1 as components


# ===== Config da página =====
st.set_page_config(
    page_title="Dashboard — CRM de Milhas",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Esconde o menu, a barra superior e o rodapé
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ===== Proteção básica (exige login) =====
if not st.session_state.get("is_authenticated"):
    st.warning("Você precisa estar autenticado para acessar esta página.")
    st.page_link("Home.py", label="Ir para o login 🔐")
    st.stop()

# ===== CSS Profissional =====
st.markdown("""
<style>
    /* Reset e Base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Ocultar barra lateral */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Header principal */
    .dashboard-header {
        background: linear-gradient(135deg, #0a84ff 0%, #ff7a00 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(10, 132, 255, 0.15);
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .dashboard-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    /* Seção de filtros */
    .filters-section {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .filters-title {
        color: #111827;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .filter-info {
        background: linear-gradient(135deg, #fff5f0 0%, #f0f8ff 100%);
        border-left: 4px solid #ff7a00;
        padding: 0.5rem 0.75rem;
        border-radius: 0 6px 6px 0;
        margin-top: 0.25rem;
        font-size: 0.8rem;
        color: #4b5563;
    }

    /* Métricas KPI */
    .metrics-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }

    .metrics-title {
        color: #111827;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Cards de métricas customizados */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-card:hover {
        border-color: #ff7a00;
        box-shadow: 0 4px 12px rgba(255, 122, 0, 0.15);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0a84ff 0%, #ff7a00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Seção de gráficos */
    .charts-section {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .charts-title {
        color: #111827;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Divisor estilizado */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(135deg, #0a84ff 0%, #ff7a00 100%);
        margin: 2rem 0;
        border-radius: 1px;
        opacity: 0.3;
    }

    /* Botões e inputs do Streamlit */
    .stRadio > div[role="radiogroup"] > label {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        margin-right: 0.4rem;
        transition: all 0.3s ease;
        font-size: 0.8rem;
    }

    .stRadio > div[role="radiogroup"] > label:hover {
        border-color: #ff7a00;
        background: #fff5f0;
    }

    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, #0a84ff 0%, #ff7a00 100%);
        border-color: transparent;
        color: white;
    }

    /* Multiselect styling */
    .stMultiSelect > div > div {
        border-radius: 6px;
        border: 2px solid #e5e7eb;
    }

    .stMultiSelect > div > div:focus-within {
        border-color: #ff7a00;
        box-shadow: 0 0 0 1px #ff7a00;
    }

    /* Date input styling */
    .stDateInput > div > div > input {
        border-radius: 6px;
        border: 2px solid #e5e7eb;
    }

    .stDateInput > div > div > input:focus {
        border-color: #ff7a00;
        box-shadow: 0 0 0 1px #ff7a00;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .dashboard-title {
            font-size: 1.5rem;
        }

        .metric-value {
            font-size: 1.5rem;
        }

        .filters-section, .metrics-container, .charts-section {
            padding: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===== CSS opcional adicional =====
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ===== Preferir dados da sessão; fallback carrega do Airtable =====
from libs.airtable_client import import_dados
if "df_leads" not in st.session_state or st.session_state["df_leads"] is None:
    with st.spinner("Carregando dados do Airtable..."):
        st.session_state["df_leads"] = import_dados()
        st.session_state["df_last_loaded_at"] = pd.Timestamp.now(tz="America/Sao_Paulo")

df_leads = st.session_state["df_leads"].copy()
df_clientes = st.session_state["df_clientes"].copy()

# ===== Header Principal =====
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">✈️ Dashboard CRM de Milhas</h1>
    <p class="dashboard-subtitle">Análise Completa de Performance e Conversões</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Filtros ----------------
cols_filters = st.columns([1.52,1,1,1])

with cols_filters[0]:
    # === Filtro de Data ===
    periodo = st.radio(
        "📅 Período",
        ["Dia", "Semana", "Mês", "Personalizada"],
        index=2,  # Mês como padrão
        horizontal=True
    )

    hoje = date.today()
    if periodo == "Dia":
        data_inicio = hoje
        data_fim = hoje
    elif periodo == "Semana":
        data_inicio = hoje - timedelta(days=6)
        data_fim = hoje
    elif periodo == "Mês":
        data_inicio = hoje - timedelta(days=29)
        data_fim = hoje
    elif periodo == "Personalizada":
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data inicial", hoje - timedelta(days=29))
        with col2:
            data_fim = st.date_input("Data final", hoje)

    st.markdown(f"""
    <div class="filter-info">
        <strong>Período:</strong> {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

with cols_filters[1]:
    # === Origem ===
    origens = ["TODAS"] + sorted(df_leads["ORIGEM"].dropna().unique().tolist())
    origem_sel = st.multiselect("📍 Origem", origens, default=["TODAS"])
    st.markdown(f"""
    <div class="filter-info">
        <strong>Origem:</strong> {', '.join(origem_sel[:3])}{'...' if len(origem_sel) > 3 else ''}
    </div>
    """, unsafe_allow_html=True)

with cols_filters[2]:
    # === SDR ===
    sdrs = ["TODOS"] + sorted(df_leads["SDR"].dropna().unique().tolist())
    sdr_sel = st.multiselect("👤 SDR", sdrs, default=["TODOS"])
    st.markdown(f"""
    <div class="filter-info">
        <strong>SDR:</strong> {', '.join(sdr_sel[:3])}{'...' if len(sdr_sel) > 3 else ''}
    </div>
    """, unsafe_allow_html=True)

with cols_filters[3]:
    # === Call com ===
    calls = ["TODOS"] + sorted(df_leads["CALL COM:"].dropna().unique().tolist())
    call_sel = st.multiselect("📞 Call com", calls, default=["TODOS"])
    st.markdown(f"""
    <div class="filter-info">
        <strong>Call com:</strong> {', '.join(call_sel[:3])}{'...' if len(call_sel) > 3 else ''}
    </div>
    """, unsafe_allow_html=True)

# ---------------- Aplicar Filtros ----------------
df_filtrado = df_leads.copy()

# Filtra por data
coluna_data = "Última Atualização de Status"
if coluna_data in df_filtrado.columns:
    datas = pd.to_datetime(df_filtrado[coluna_data], errors="coerce", dayfirst=True)
    mask = (datas.dt.date >= data_inicio) & (datas.dt.date <= data_fim)
    df_filtrado = df_filtrado[mask]

# Filtra por Origem
if "TODAS" not in origem_sel:
    df_filtrado = df_filtrado[df_filtrado["ORIGEM"].isin(origem_sel)]

# Filtra por SDR
if "TODOS" not in sdr_sel:
    df_filtrado = df_filtrado[df_filtrado["SDR"].isin(sdr_sel)]

# Filtra por Call com
if "TODOS" not in call_sel:
    df_filtrado = df_filtrado[df_filtrado["CALL COM:"].isin(call_sel)]

# ---------------- Métricas KPI ----------------
vspace(15)
st.markdown("""
<div class="metrics-container">
    <div class="metrics-title">📊 Funil </div>
</div>
""", unsafe_allow_html=True)

cols_metrics = st.columns(5)

# Calculando métricas
qtd_marcadas = (
    pd.to_datetime(df_filtrado['[AUTO] Data da Reunião Marcada'], errors='coerce')
    .between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim))
    .sum()
)

qtd_realizadas = (
    pd.to_datetime(df_filtrado['[AUTO] Data da Reunião Realizada'], errors='coerce')
    .between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim))
    .sum()
)

valor_noshow = (df_filtrado['STATUS'].astype(str).str.upper() == 'NO-SHOW').sum()
valor_contratos = (df_filtrado['STATUS'].astype(str).str.upper() == 'GANHOU').sum()

# Exibindo métricas com cards customizados
with cols_metrics[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(df_filtrado):,}</div>
        <div class="metric-label">Abordagens</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(qtd_marcadas):,}</div>
        <div class="metric-label">Reuniões Marcadas</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(qtd_realizadas):,}</div>
        <div class="metric-label">Reuniões Realizadas</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(valor_noshow):,}</div>
        <div class="metric-label">No Show</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[4]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(valor_contratos):,}</div>
        <div class="metric-label">Contratos Assinados</div>
    </div>
    """, unsafe_allow_html=True)

vspace(15)

# ----- Seção de Análise do Funil ----- #

# Dados do funil
etapas = ["Abordagens", "Reuniões Marcadas", "Reuniões Realizadas", "Contratos Assinados"]
valores = [
    len(df_filtrado),
    int(qtd_marcadas),
    int(qtd_realizadas),
    int(valor_contratos)
]

# Funções auxiliares
def pct(num, den):
    return (num / den * 100) if den else 0.0

def fmt_int(n):
    return f"{int(n):,}".replace(",", ".")

# >>> CORREÇÃO: função para garantir que o progress receba sempre [0.0, 1.0]
def safe_progress_from_pct(pct_value: float) -> float:
    try:
        return max(0.0, min(float(pct_value) / 100.0, 1.0))
    except Exception:
        return 0.0

# Layout em duas colunas
col1, col2 = st.columns(2)

with col1:
    # Gráfico do funil
    st.plotly_chart(criar_funil(etapas, valores), use_container_width=True)

with col2:
    # Cálculos de conversão
    conv_abord_reun_marc = pct(valores[1], valores[0])
    conv_reun_marc_real = pct(valores[2], valores[1])
    conv_real_contrato = pct(valores[3], valores[2])
    taxa_no_show = pct(valor_noshow, valores[1])


    # Métricas de conversão
    col_conv1, col_conv2 = st.columns(2)

    with col_conv1:
        st.metric(
            "Abord. → Reuniões",
            f"{conv_abord_reun_marc:.1f}%",
            f"{fmt_int(valores[1])}/{fmt_int(valores[0])}"
        )
        st.progress(safe_progress_from_pct(conv_abord_reun_marc))

        st.metric(
            "Marcadas → Realizadas",
            f"{conv_reun_marc_real:.1f}%",
            f"{fmt_int(valores[2])}/{fmt_int(valores[1])}"
        )
        st.progress(safe_progress_from_pct(conv_reun_marc_real))

    with col_conv2:
        st.metric(
            "Realizadas → Contratos",
            f"{conv_real_contrato:.1f}%",
            f"{fmt_int(valores[3])}/{fmt_int(valores[2])}"
        )
        st.progress(safe_progress_from_pct(conv_real_contrato))

        st.metric(
            "Taxa de No Show",
            f"{taxa_no_show:.1f}%",
            f"{fmt_int(valor_noshow)}/{fmt_int(valores[1])}"
        )
        st.progress(safe_progress_from_pct(taxa_no_show))

    # Conversão total

    conversao_total = pct(valores[3], valores[0])
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); border-radius: 8px; margin-top: 1rem;">
        <span style="color: #ff7a00; font-weight: 800;">Conversão Total do Funil:</span><br>
        <span style="font-weight: 900; font-size: 1.2rem; background: linear-gradient(135deg, #0a84ff 0%, #ff7a00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{conversao_total:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)
st.divider()
# ----- Seção de Gráficos Detalhados ----- #
st.markdown("""
<div class="charts-section">
    <div class="charts-title">📈 Análises Detalhadas</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(barras_historico_maiusculas(df_filtrado), use_container_width=True)
with col2:
    st.plotly_chart(grafico_origem(df_filtrado)[0], use_container_width=True)

# ----- Footer informativo ----- #
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;">
    Dashboard CRM de Milhas • Última atualização: {datetime.now().strftime("%d/%m/%Y às %H:%M")} • Dados em tempo real
</div>
""", unsafe_allow_html=True)
