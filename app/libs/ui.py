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

def pizza(df, col="Qualificado?"):
    s = df[col]

    # Contagens (preserva NA)
    counts = s.value_counts(dropna=False)

    # Ordem desejada e filtrada aos presentes
    order = [True, False, pd.NA]
    order = [x for x in order if x in counts.index]
    counts = counts.reindex(order)

    # Rótulos humanizados
    label_map = {True: "Sim", False: "Não", pd.NA: "Sem dados"}
    labels = [label_map[i] for i in counts.index]
    values = counts.values

    # Cores pela identidade visual
    color_map = {"Sim": "#0A84FF", "Não": "orange", "Sem dados": "#101923"}

    fig = px.pie(
        values=values,
        names=labels,
        color=labels,                  # <- usa os rótulos como chave de cor
        color_discrete_map=color_map,
        hole=0.45
    )
    fig.update_traces(
        textinfo="label+percent",
        textfont_size=16,
        pull=[0.05 if lab == "Sim" else 0 for lab in labels],
    )
    fig.update_layout(
        title_text="📊 Qualificação dos Leads",
        title_x=0.2, title_font_size=20,
        showlegend=False,
        margin=dict(t=50, b=80, l=80, r=80),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color="black"),
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
