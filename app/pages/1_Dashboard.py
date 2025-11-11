import streamlit as st
from pathlib import Path
import pandas as pd
import pytz
from datetime import datetime, timedelta
import plotly.express as px
from libs.utils import vspace, calcular_idade, contar_cartoes
from libs.ui import criar_funil, pizza, barras_historico_maiusculas, grafico_origem, histograma, barras_empilhadas, histograma_simples, barras_simples
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

# ===== Util de datas (robusto p/ ISO e dd/mm/aaaa) =====
import pandas as pd
def _parse_datetime_mixed(series: pd.Series) -> pd.Series:
    """
    Converte uma série com datas em formatos mistos:
    - ISO do Airtable (ex.: 2025-04-11T12:17:48.000Z)
    - Strings dd/mm/aaaa

    Retorna uma série datetime (timezone-aware para ISO), com NaT onde não parsear.
    """
    s = series.astype(str)
    # Detecta formatos ISO com ou sem tempo: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, etc.
    iso_mask = s.str.match(r"^\d{4}-\d{2}-\d{2}(?:[ T].*)?$", na=False)
    # Parse ISO como timezone-aware (quando aplicável) e remove o timezone para ficar consistente
    dt_iso_aw = pd.to_datetime(s.where(iso_mask), errors="coerce", utc=True)
    dt_iso = dt_iso_aw.dt.tz_localize(None)
    # Parse local dd/mm/aaaa (e variações com hífen), preferindo dia primeiro
    dt_local = pd.to_datetime(s.where(~iso_mask), errors="coerce", dayfirst=True)
    # Une resultados (todos tz-naive)
    return dt_iso.combine_first(dt_local)

# ===== Header Principal =====
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">✈️ Dashboard CRM de Milhas</h1>
    <p class="dashboard-subtitle">Análise Completa de Performance e Conversões</p>
</div>
""", unsafe_allow_html=True)


tab_comercial, tab_perfis, tab_clientes = st.tabs(tabs = ['Comercial', 'Captação', 'Clientes'])

with tab_comercial:
    # ---------------- Filtros ----------------
    cols_filters = st.columns([1.52,1,1,1])

    with cols_filters[0]:
        # === Filtro de Data ===
        periodo = st.radio(
            "📅 Período",
            ["Dia", "Semana", "Mês", "Personalizada", "Todo o período"],  # + opção nova
            index=2,  # Mês como padrão
            horizontal=True
        )

        hoje = date.today()
        coluna_data = "Última Atualização de Status"

        # Converte a coluna de data com segurança (suporta ISO e dd/mm/aaaa)
        datas_col = _parse_datetime_mixed(df_leads.get(coluna_data, pd.Series(dtype="object")))
        min_data_valida = datas_col.min()
        max_data_valida = datas_col.max()

        # Fallback caso a coluna não exista ou não tenha datas válidas
        if pd.isna(min_data_valida) or pd.isna(max_data_valida):
            min_data_valida = hoje - timedelta(days=365)
            max_data_valida = hoje

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
                data_inicio = st.date_input("Data inicial", max(min_data_valida.date(), hoje - timedelta(days=29)))
            with col2:
                data_fim = st.date_input("Data final", max_data_valida.date())
        elif periodo == "Todo o período":
            data_inicio = min_data_valida.date()
            data_fim = max_data_valida.date()

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
        # Converte datas com robustez (ISO e dd/mm/aaaa)
        datas = _parse_datetime_mixed(df_filtrado[coluna_data])
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
    qtd_abordados = (
        pd.to_datetime(df_filtrado['Abordado'], errors='coerce')
        .between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim))
        .sum()
    )

    qtd_marcadas = (
        pd.to_datetime(df_filtrado['Call Agendada'], errors='coerce')
        .between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim))
        .sum()
    )

    qtd_realizadas = (
        pd.to_datetime(df_filtrado['Reunião Realizada'], errors='coerce')
        .between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim))
        .sum()
    )

    valor_noshow = (df_filtrado['STATUS'].astype(str).str.upper() == 'NO-SHOW').sum()
    valor_contratos = (df_filtrado['STATUS'].astype(str).str.upper() == 'GANHOU').sum()

    # Exibindo métricas com cards customizados
    with cols_metrics[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{qtd_abordados:,}</div>
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
        int(qtd_abordados),
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

    # ----- SLA dentro da aba Comercial ----- #
    st.markdown("""
    <div class="charts-section">
        <div class="charts-title">⏱ SLA de Etapas</div>
    </div>
    """, unsafe_allow_html=True)

    def _fmt_timedelta(td: pd.Timedelta) -> str:
        if td is None or pd.isna(td):
            return "—"
        secs = int(td.total_seconds())
        d = secs // 86400
        h = (secs % 86400) // 3600
        m = (secs % 3600) // 60
        parts = []
        if d:
            parts.append(f"{d}d")
        if h or d:
            parts.append(f"{h}h")
        parts.append(f"{m}m")
        return " ".join(parts)

    def _avg_duration(df: pd.DataFrame, start_col: str, end_col: str) -> pd.Timedelta | None:
        if start_col not in df.columns or end_col not in df.columns:
            return None
        s_start = _parse_datetime_mixed(df[start_col])
        s_end = _parse_datetime_mixed(df[end_col])
        # Fallback: se 'Abordado' estiver vazio, usa 'Call Agendada' (quando existir)
        if start_col.strip().lower() == "abordado" and "Call Agendada" in df.columns:
            s_ab_fallback = _parse_datetime_mixed(df["Call Agendada"])
            s_start = s_start.fillna(s_ab_fallback)
        delta = s_end - s_start
        valid = delta.dropna()
        valid = valid[valid >= pd.Timedelta(0)]
        if valid.empty:
            return None
        return valid.mean()

    # Usar sempre o df_filtrado para os cálculos
    base = df_filtrado

    # Cálculos das durações médias por etapa
    avg_criado_abordado = _avg_duration(base, "CRIADO", "Abordado")
    avg_abordado_call = _avg_duration(base, "Abordado", "Call Agendada")
    avg_call_realizada = _avg_duration(base, "Call Agendada", "Reunião Realizada")
    avg_realizada_ganhou = _avg_duration(base, "Reunião Realizada", "GANHOU")
    avg_realizada_perdeu = _avg_duration(base, "Reunião Realizada", "PERDEU")
    avg_abordado_ganhou = _avg_duration(base, "Abordado", "GANHOU")
    avg_abordado_perdeu = _avg_duration(base, "Abordado", "PERDEU")

    # Card inicial (CRIADO → Abordado) ocupando toda a largura
    st.markdown(f"""
    <div class="metric-card" style="margin-bottom: 0.75rem;">
        <div class="metric-value">{_fmt_timedelta(avg_criado_abordado)}</div>
        <div class="metric-label">CRIADO → Abordado</div>
    </div>
    """, unsafe_allow_html=True)

    # Duas colunas verticais separando os caminhos GANHOU e PERDEU
    c_ganhou, c_perdeu = st.columns(2)

    with c_ganhou:
        st.markdown("""
        <div class="metrics-title">Rumo a GANHOU</div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_abordado_call)}</div>
            <div class="metric-label">Abordado → Call Agendada</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_call_realizada)}</div>
            <div class="metric-label">Call Agendada → Reunião Realizada</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_realizada_ganhou)}</div>
            <div class="metric-label">Reunião Realizada → GANHOU</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_abordado_ganhou)}</div>
            <div class="metric-label">Abordado → GANHOU</div>
        </div>
        """, unsafe_allow_html=True)

    with c_perdeu:
        st.markdown("""
        <div class="metrics-title">Rumo a PERDEU</div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_abordado_call)}</div>
            <div class="metric-label">Abordado → Call Agendada</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_call_realizada)}</div>
            <div class="metric-label">Call Agendada → Reunião Realizada</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_realizada_perdeu)}</div>
            <div class="metric-label">Reunião Realizada → PERDEU</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_timedelta(avg_abordado_perdeu)}</div>
            <div class="metric-label">Abordado → PERDEU</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    data_rows = [
        {"Transição": "CRIADO → Abordado", "Média": _fmt_timedelta(avg_criado_abordado)},
        {"Transição": "Abordado → Call Agendada", "Média": _fmt_timedelta(avg_abordado_call)},
        {"Transição": "Call Agendada → Reunião Realizada", "Média": _fmt_timedelta(avg_call_realizada)},
        {"Transição": "Reunião Realizada → GANHOU", "Média": _fmt_timedelta(avg_realizada_ganhou)},
        {"Transição": "Reunião Realizada → PERDEU", "Média": _fmt_timedelta(avg_realizada_perdeu)},
        {"Transição": "Abordado → GANHOU", "Média": _fmt_timedelta(avg_abordado_ganhou)},
        {"Transição": "Abordado → PERDEU", "Média": _fmt_timedelta(avg_abordado_perdeu)},
    ]
    st.dataframe(pd.DataFrame(data_rows), use_container_width=True)

    # (Tabela de diagnóstico removida conforme solicitação)

    # ----- Footer informativo ----- #
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;">
        Dashboard CRM de Milhas • Última atualização: {datetime.now().strftime("%d/%m/%Y às %H:%M")} • Dados em tempo real
    </div>
    """, unsafe_allow_html=True)

with tab_perfis:
    # ---------------- Filtros ----------------
    cols_filters = st.columns(2)

    with cols_filters[0]:
        # === Filtro de Data ===
        periodo = st.radio(
            "📅 Captado",
            ["Dia", "Semana", "Mês", "Personalizada", "Todo o período"],  # + opção nova
            index=2,  # Mês como padrão
            horizontal=True
        )

        hoje = date.today()
        coluna_data = "CRIADO"

        # Converte a coluna de data com segurança (suporta ISO e dd/mm/aaaa)
        datas_col = _parse_datetime_mixed(df_leads.get(coluna_data, pd.Series(dtype="object")))
        min_data_valida = datas_col.min()
        max_data_valida = datas_col.max()

        # Fallback caso a coluna não exista ou não tenha datas válidas
        if pd.isna(min_data_valida) or pd.isna(max_data_valida):
            min_data_valida = hoje - timedelta(days=365)
            max_data_valida = hoje

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
                data_inicio = st.date_input("Data inicial", max(min_data_valida.date(), hoje - timedelta(days=29)))
            with col2:
                data_fim = st.date_input("Data final", max_data_valida.date())
        elif periodo == "Todo o período":
            data_inicio = min_data_valida.date()
            data_fim = max_data_valida.date()

        st.markdown(f"""
        <div class="filter-info">
            <strong>Período:</strong> {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}
        </div>
        """, unsafe_allow_html=True)


    with cols_filters[1]:
        # === Origem ===
        origens = ["TODAS"] + sorted(df_leads["ORIGEM"].dropna().unique().tolist())
        origem_sel = st.multiselect("📍 Origem da captação", origens, default=["TODAS"])
        st.markdown(f"""
        <div class="filter-info">
            <strong>Origem:</strong> {', '.join(origem_sel[:3])}{'...' if len(origem_sel) > 3 else ''}
        </div>
        """, unsafe_allow_html=True)

    # ---------------- Aplicar Filtros ----------------
    df_cap = df_leads.copy()

    # Filtra por data
    coluna_data = "CRIADO"
    if coluna_data in df_cap.columns:
        # Converte datas com robustez (ISO e dd/mm/aaaa)
        datas = _parse_datetime_mixed(df_cap[coluna_data])
        mask = (datas.dt.date >= data_inicio) & (datas.dt.date <= data_fim)
        df_cap = df_cap[mask]

    # Filtra por Origem
    if "TODAS" not in origem_sel:
        df_cap = df_cap[df_cap["ORIGEM"].isin(origem_sel)]

    # ---------------- Gráficos ----------------

    # ====== Seção: Visão Financeira (2 colunas) ======
    st.markdown("""
    <div class="charts-section">
    <div class="charts-title">💰 Visão Financeira</div>
    </div>
    """, unsafe_allow_html=True)

    fin_col1, fin_col2 = st.columns(2, vertical_alignment="top")
    with fin_col1:
        st.caption("Distribuição do gasto mensal (padrão cortado na média)")
        histograma(df_cap, 'GASTO MÉDIO MENSAL', 20)

    with fin_col2:
        st.caption("Distribuição do limite total (padrão cortado na média)")
        histograma(df_cap, 'LIMITE DOS CARTÕES SOMADOS', 15)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ====== Seção: Perfil & Jornada (2 colunas) ======
    st.markdown("""
    <div class="charts-section">
    <div class="charts-title">🧭 Perfil & Jornada</div>
    </div>
    """, unsafe_allow_html=True)

    perfil_col1, perfil_col2 = st.columns(2, vertical_alignment="top")
    with perfil_col1:
        st.caption("Nível de conhecimento em milhas (empilhado por status de acúmulo)")
        barras_empilhadas(df_cap, 'NÍVEL DE CONHECIMENTO EM MILHAS')

    with perfil_col2:
        st.caption("Frequência de viagens no ano (empilhado por status de acúmulo)")
        # mantido o nome do parâmetro conforme seu uso atual
        barras_empilhadas(df_cap, 'QUANTAS VEZES COSTUMA VIAJAR NO ANO', stat_col='JÁ ACUMULA MILHAS?')

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ====== Seção: Status & Qualificação (3 colunas) ======
    st.markdown("""
    <div class="charts-section">
    <div class="charts-title">✅ Status & Qualificação</div>
    </div>
    """, unsafe_allow_html=True)

    status_col1, status_col2, status_col3 = st.columns(3, vertical_alignment="top")
    with status_col1:
        st.caption("Status: já acumula milhas?")
        pizza(df_cap, 'JÁ ACUMULA MILHAS?')

    with status_col2:
        st.caption("Qualificado?")
        pizza(df_cap, 'Qualificado?')

    with status_col3:
        st.caption("Distribuição por consultor")
        barras_empilhadas(df_cap, 'Qual Consultor da Simpla Invest')

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ====== Seção: Objetivos (1 coluna cheia) ======
    st.markdown("""
    <div class="charts-section">
    <div class="charts-title">🎯 Objetivos Declarados</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Principais objetivos informados pelos leads")
    pizza(df_cap, 'OBJETIVO')

with tab_clientes:
    # ===== Helpers =====
    def _to_num(s, dec=0):
        v = pd.to_numeric(s, errors="coerce")
        if v.ndim == 0:
            return 0 if pd.isna(v) else (round(float(v), dec))
        return v

    def _fmt_moeda(v):
        try:
            v = float(v)
            return "R$ {:,.0f}".format(v).replace(",", ".")
        except Exception:
            return "R$ 0"
        
    from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

    def delete_outlier(df: pd.DataFrame, coluna: str, which: str = "max", remove_all: bool = False) -> pd.DataFrame:
        """
        Remove o menor ou o maior valor de uma coluna (apenas uma ocorrência por padrão).
        Suporta colunas numéricas e de data.

        Params
        ------
        df : DataFrame
        coluna : nome da coluna
        which : "max" ou "min"
        remove_all : se True, remove todas as linhas iguais ao valor extremo; se False, remove só a primeira ocorrência

        Returns
        -------
        DataFrame filtrado
        """
        if coluna not in df.columns:
            raise ValueError(f"Coluna '{coluna}' não existe no DataFrame.")

        out = df.copy()

        # Normaliza a série dependendo do tipo
        s = out[coluna]

        if is_datetime64_any_dtype(s):
            s_dt = s
        else:
            # tenta numérico; se não rolar, tenta datetime
            s_num = pd.to_numeric(s, errors="coerce")
            if s_num.notna().any():
                s_dt = s_num  # usamos s_dt só como "série de comparação"
            else:
                s_dt = pd.to_datetime(s, errors="coerce")

        if s_dt.isna().all():
            # nada a fazer
            return out

        if which.lower() == "max":
            extremo = s_dt.max()
            if remove_all:
                out = out[s_dt != extremo]
            else:
                idx = s_dt.idxmax()
                out = out.drop(index=idx)
        elif which.lower() == "min":
            extremo = s_dt.min()
            if remove_all:
                out = out[s_dt != extremo]
            else:
                idx = s_dt.idxmin()
                out = out.drop(index=idx)
        else:
            raise ValueError("Parâmetro 'which' deve ser 'max' ou 'min'.")

        return out

    df_clientes = delete_outlier(df_clientes, "Gasto Mensal", which="max", remove_all=False)
    df_clientes = delete_outlier(df_clientes, "Data de Nascimento", which="min")

    # ===== KPIs (topo) =====
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)

    total_econ = _to_num(df_clientes["Total Economia"]).sum()
    total_clientes = len(df_clientes)
    gasto_mensal_med = _to_num(df_clientes.get("Gasto Mensal", pd.Series(dtype=float))).mean()

    # idade média (usa sua função)
    try:
        df_idades_tmp = calcular_idade(df_clientes.copy())
        idade_media = pd.to_numeric(df_idades_tmp.get("Idade"), errors="coerce").dropna().mean()
    except Exception:
        idade_media = None

    with col_k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_moeda(total_econ)}</div>
            <div class="metric-label">Economia Gerada</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_clientes}</div>
            <div class="metric-label">Clientes Ativos</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{_fmt_moeda(gasto_mensal_med)}</div>
            <div class="metric-label">Gasto Mensal Médio</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{idade_media:.1f}</div>
            <div class="metric-label">Idade Média</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ===== Demografia =====
    st.markdown("""
    <div class="charts-section">
      <div class="charts-title">🧑‍🤝‍🧑 Demografia</div>
    </div>
    """, unsafe_allow_html=True)

    dem_c1, dem_c2, dem_c3 = st.columns(3, vertical_alignment="top")
    with dem_c1:
        st.caption("Filhos")
        pizza(df_clientes, "Filhos")

    with dem_c2:
        st.caption("Estado civil")
        pizza(df_clientes, "Estado Civil")

    with dem_c3:
        st.caption("Distribuição de idades")
        # usa sua própria função para gerar a coluna Idade
        df_idades = calcular_idade(df_clientes.copy())
        histograma_simples(df_idades, "Idade", bins=20)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ===== Finanças =====
    st.markdown("""
    <div class="charts-section">
      <div class="charts-title">💰 Finanças</div>
    </div>
    """, unsafe_allow_html=True)

    fin_c1, fin_c2 = st.columns(2, vertical_alignment="top")
    with fin_c1:
        st.caption("Distribuição do gasto mensal")
        histograma(df_clientes, "Gasto Mensal", bins=10)

    with fin_c2:
        # Você pode adicionar outro chart financeiro aqui no futuro (ex.: economia por faixa etc.)
        # Por ora, deixamos um espaço com uma observação discreta:
        st.caption("—")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ===== Cartões =====
    st.markdown("""
    <div class="charts-section">
      <div class="charts-title">💳 Cartões</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Top 10 cartões individuais mais frequentes (desmembrando combinações)")
    df_cartoes = contar_cartoes(df_clientes)  # retorna colunas: Cartão, Contagem
    barras_simples(df_cartoes, "Cartão", "Contagem")

    # ===== Tabela (opcional) =====
    st.markdown("---")
    st.dataframe(df_clientes, use_container_width=True)



    
st.dataframe(df_filtrado)
df_filtrado['Abordado'].iloc[0]