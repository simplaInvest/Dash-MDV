import streamlit as st

def vspace(px: int = 16):
    """Espaço em branco vertical (px)."""
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

import pandas as pd
from datetime import date

def calcular_idade(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a idade de cada indivíduo com base na coluna 'Data de Nascimento'.
    
    Args:
        df (pd.DataFrame): DataFrame contendo a coluna 'Data de Nascimento'.
    
    Returns:
        pd.DataFrame: DataFrame original com uma nova coluna 'Idade'.
    """
    # Garante que a coluna seja datetime
    df = df.copy()
    df["Data de Nascimento"] = pd.to_datetime(df["Data de Nascimento"], errors="coerce")

    hoje = date.today()
    # Calcula idade considerando ano, mês e dia
    df["Idade"] = df["Data de Nascimento"].apply(
        lambda d: hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day)) if pd.notnull(d) else None
    )
    return df

def contar_cartoes(df: pd.DataFrame, col_nome: str = "Cartões Atuais", topx: int = 10) -> pd.DataFrame:
    """
    Conta os cartões individuais mais frequentes a partir de uma coluna que pode conter múltiplos cartões separados por vírgula.
    
    Args:
        df (pd.DataFrame): DataFrame com a coluna de cartões.
        col_nome (str): Nome da coluna com os cartões.
        topx (int): Número máximo de classes a retornar (ex.: 10).
    
    Returns:
        pd.DataFrame: DataFrame com os cartões e suas frequências.
    """
    # Garante que a coluna existe
    if col_nome not in df.columns:
        raise ValueError(f"A coluna '{col_nome}' não existe no DataFrame.")

    # Separa por vírgula, empilha em série única, remove espaços e normaliza
    cartoes_explodidos = (
        df[col_nome]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .str.strip('[')
        .str.strip(']')                
        .str.title()             
    )

    # Conta frequência
    contagem = cartoes_explodidos.value_counts().reset_index()
    contagem.columns = ["Cartão", "Contagem"]

    # Pega os topx
    if topx is not None:
        contagem = contagem.head(topx)

    return contagem
