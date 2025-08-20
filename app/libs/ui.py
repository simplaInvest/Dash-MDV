import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import pandas as pd
import re
import unicodedata

def criar_funil(etapas, valores):
    # Cria o gráfico de funil
    fig = go.Figure(go.Funnel(
        y=etapas,
        x=valores,
        textinfo="none",  # vamos controlar as anotações manualmente
        marker={"color": "orange"}
    ))

    # Adiciona anotações sobre cada etapa
    for etapa, valor in zip(etapas, valores):
        fig.add_annotation(
            x=0,
            y=etapa,
            text=f"<b>{etapa}</b>: {valor}",
            showarrow=False,
            font=dict(color="black", size=14)
        )

    # Layout do gráfico
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(color="black")
    )
    return fig

def barras_historico_maiusculas(df, col="HISTÓRICO"):
    # Filtra apenas strings totalmente maiúsculas
    filtrado = df[df[col].apply(lambda x: isinstance(x, str) and x.isupper())]

    # Conta as ocorrências
    counts = filtrado[col].value_counts().reset_index()
    counts.columns = [col, "Quantidade"]

    # Cria gráfico de barras horizontais
    fig = px.bar(
        counts.head(10).iloc[::-1],
        x="Quantidade",
        y=col,
        orientation="h",
        text="Quantidade",
        color="Quantidade",
        color_continuous_scale="Blues"
    )

    fig.update_traces(
        textposition="outside",
        textfont_size=14
    )

    fig.update_layout(
        title_text="📊 Histórico",
        title_x=0.5,
        title_font_size=20,
        xaxis_title="Quantidade",
        yaxis_title=None,
        margin=dict(t=50, b=0, l=0, r=0),
        coloraxis_showscale=False
    )

    return fig

def normalizar_origem_simples(s: pd.Series) -> pd.Series:
    """Normaliza ORIGEM de forma simples: lower, trim, espaços→-, e um mapa curto de aliases."""
    s = s.astype("string").fillna("Não identificado")
    base = (
        s.str.lower()
         .str.strip()
         .str.replace(r"[\s_]+", "-", regex=True)  # espaços/underscores → "-"
    )
    mapa = {
        "indicação": "Indicação", "indicacao": "Indicação",
        "active-email": "Active Email", "activeemail": "Active Email",
        "youtube": "YouTube Vídeo", "youtubevideo": "YouTube Vídeo",
        "eu-investidor": "Eu Investidor",
        "instagram": "Instagram",
        "consultor": "Consultor", "consultor-bruno": "Consultor",
        "simpla-wealth": "Simpla Wealth", "sympla-wealth": "Simpla Wealth",
        "simpla-club": "Simpla Club",
        "pagina-institucional": "Página Institucional",
        "mdv": "MDV",
        "adriel": "Adriel",
        "cardoso-cardoso": "Cardoso",
        "não-identificado": "Não identificado", "nao-identificado": "Não identificado",
    }
    # Aplica o mapa; se não estiver no mapa, só “title-case” básico
    return base.map(lambda x: mapa.get(x, x.replace("-", " ").title()))

def grafico_origem(df: pd.DataFrame, col="ORIGEM", top_n: int = 12):
    origem = normalizar_origem_simples(df[col])
    counts = (
        origem.value_counts(dropna=False)
              .reset_index()
              .rename(columns={"index": "Origem", col: "Quantidade"})
    )
    counts.columns = ["Origem", "Quantidade"]
    data_plot = counts.head(top_n).iloc[::-1]  # maior→menor de cima p/ baixo

    fig = px.bar(
        data_plot,
        x="Quantidade",
        y="Origem",
        orientation="h",
        text="Quantidade",
    )
    fig.update_traces(
        marker_color="#FF7A00",           # laranja (primária)
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Qtd: %{x}<extra></extra>",
    )
    fig.update_layout(
        title_text="📊 Origem dos Leads",
        title_x=0.5, title_font_size=20,
        xaxis_title="Quantidade", yaxis_title=None,
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color="black"),
        xaxis=dict(range=[0, data_plot["Quantidade"].max() * 1.2])
    )
    return fig, counts

###################

def histograma(data, coluna, bins):
    # Garante numérico e remove NaN
    serie = pd.to_numeric(data[coluna], errors='coerce').dropna()
    if serie.empty:
        st.warning(f"A coluna '{coluna}' não possui valores numéricos válidos para o histograma.")
        return

    # Define limites
    xmax_media = float(serie.mean())
    xmax_total = float(serie.max())
    xmin = float(serie.min())

    # --- Dados filtrados (padrão) ---
    dados_media = serie[serie <= xmax_media]

    # Cria histograma inicial (padrão = média)
    fig = px.histogram(
        x=dados_media,
        nbins=bins,
        title=coluna,
        text_auto=True
    )
    fig.update_xaxes(range=[xmin, xmax_media])

    # --- Adiciona botões para alternar entre "Média" e "Completo" ---
    fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": "Até a Média",
                        "method": "update",
                        "args": [
                            {"x": [dados_media]},  # dados filtrados
                            {"xaxis": {"range": [xmin, xmax_media]}}
                        ]
                    },
                    {
                        "label": "Série Completa",
                        "method": "update",
                        "args": [
                            {"x": [serie]},       # todos os dados
                            {"xaxis": {"range": [xmin, xmax_total]}}
                        ]
                    }
                ],
                "direction": "right",
                "x": 0.5,
                "y": 1.15,
                "showactive": True
            }
        ]
    )

    return st.plotly_chart(fig, use_container_width=True)

def pizza(data, coluna):
    df = data.copy()

    # Conta a frequência de cada categoria
    contagem = df[coluna].value_counts().reset_index()
    contagem.columns = [coluna, "Frequência"]

    # Gera o gráfico de pizza
    fig = px.pie(
        contagem,
        names=coluna,         # rótulos das fatias
        values="Frequência",  # tamanhos proporcionais
        title=f"Distribuição de {coluna}",
        hole=0.3              # opcional: transforma em gráfico de rosca
    )

    return st.plotly_chart(fig, use_container_width=True)

def barras_empilhadas(data, coluna, stat_col: str = ""):
    df = data.copy()

    # --- validações ---
    if coluna not in df.columns:
        st.error(f"A coluna principal '{coluna}' não existe no DataFrame.")
        return

    # ordem desejada para alguns casos conhecidos
    if coluna == 'QUANTAS VEZES COSTUMA VIAJAR NO ANO':
        ordem_categorias = ["Apenas uma vez", "2 vezes", "3 vezes", "Mais que 3 vezes"]
    elif coluna == 'NÍVEL DE CONHECIMENTO EM MILHAS':
        ordem_categorias = ['Leigo', 'Iniciante', 'Intermediário', 'Avançado']
    else:
        # ordem automática (ordenada alfabeticamente pelas categorias vistas)
        ordem_categorias = sorted(df[coluna].dropna().unique().tolist())

    # --- caso 1: sem coluna de empilhamento (barras simples) ---
    if not stat_col:
        contagem = df[coluna].value_counts(dropna=False).reset_index()
        contagem.columns = [coluna, "Frequência"]

        fig = px.bar(
            contagem,
            x=coluna,
            y="Frequência",
            text="Frequência",
            title=f"{coluna}"
        )
        fig.update_layout(barmode="relative")
        fig.update_traces(textposition="inside")
        fig.update_xaxes(categoryorder="array", categoryarray=ordem_categorias)

        return st.plotly_chart(fig, use_container_width=True)

    # --- caso 2: com coluna de empilhamento (barras empilhadas) ---
    if stat_col not in df.columns:
        st.error(f"A coluna de empilhamento '{stat_col}' não existe no DataFrame.")
        return

    # Opcional: tratar ausentes para não quebrar a legenda
    df[stat_col] = df[stat_col].fillna("Não informado")

    contagem = df.groupby([coluna, stat_col]).size().reset_index(name="Frequência")

    fig = px.bar(
        contagem,
        x=coluna,
        y="Frequência",
        color=stat_col,
        text="Frequência",
        title=f"{coluna} por {stat_col}",
        category_orders={coluna: ordem_categorias}
    )
    fig.update_layout(barmode="stack")
    fig.update_traces(textposition="inside")

    return st.plotly_chart(fig, use_container_width=True)

def histograma_simples(data, coluna, bins):
    # Garante numérico e remove NaN
    serie = pd.to_numeric(data[coluna], errors='coerce').dropna()
    if serie.empty:
        st.warning(f"A coluna '{coluna}' não possui valores numéricos válidos para o histograma.")
        return

    # Cria histograma inicial (padrão = média)
    fig = px.histogram(
        x= serie,
        nbins=bins,
        title=coluna,
        text_auto=True
    )

    return st.plotly_chart(fig, use_container_width=True)

def barras_simples(data, x, y):
    df = data.copy()
    fig = px.bar(df, x = x, y = y, text_auto=True)

    return st.plotly_chart(fig)