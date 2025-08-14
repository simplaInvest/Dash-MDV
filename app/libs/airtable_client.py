from pyairtable import Api
import pandas as pd
import streamlit as st
import numpy as np
import unicodedata
import re
from typing import List, Tuple,  Optional, Iterable

# --- Util ---
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

TRUE_SET = {"1", "true", "t", "yes", "y", "sim", "s", "verdadeiro"}
FALSE_SET = {"0", "false", "f", "no", "n", "nao", "não", "falso"}
_UNKNOWN = object()

def _to_bool(value):
    # Trata vazios
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return pd.NA
    # bool nativo
    if isinstance(value, bool):
        return value
    # números
    if isinstance(value, (int, np.integer)):
        return bool(value) if value in (0, 1) else _UNKNOWN
    if isinstance(value, (float, np.floating)):
        if np.isnan(value): return pd.NA
        return bool(int(value)) if float(value).is_integer() and int(value) in (0,1) else _UNKNOWN
    # strings
    if isinstance(value, str):
        s = _strip_accents(value.strip().lower())
        if s in ("", "nan", "none", "null"): return pd.NA
        if s in TRUE_SET: return True
        if s in FALSE_SET: return False
        return _UNKNOWN
    # Qualquer outro tipo (dict, list, etc.)
    return _UNKNOWN

# --- Detectores seguros (não usam .unique()) ---
def detectar_colunas_booleanas(df: pd.DataFrame) -> List[str]:
    """
    Coluna é considerada booleana se TODOS os não-nulos forem interpretáveis como booleano
    e existirem no máx. 2 valores distintos (True/False). Tolerante a dict/list.
    """
    boolean_cols = []
    for col in df.columns:
        series = df[col]
        distinct: set = set()
        has_nonnull = False
        ok = True
        for v in series:
            # pula nulos
            if v is None or (isinstance(v, float) and np.isnan(v)):
                continue
            has_nonnull = True
            m = _to_bool(v)
            if m is _UNKNOWN:
                ok = False
                break
            if pd.isna(m):
                continue
            distinct.add(bool(m))
            if len(distinct) > 2:
                ok = False
                break
        if has_nonnull and ok and 1 <= len(distinct) <= 2:
            boolean_cols.append(col)
    return boolean_cols

# Regex de “cara de data”: 12/03/2024, 2024-03-12, nomes de mês em PT
_DATE_WORDS_PT = r"(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez|janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
_DATE_LIKE_RE = re.compile(r"(?:\d{1,4}[/\-]\d{1,2}[/\-]\d{1,4})|(?:\b" + _DATE_WORDS_PT + r"\b)", re.IGNORECASE)

def _is_excel_serial_candidate(series: pd.Series,
                               *, min_numeric_ratio=0.90, min_integer_ratio=0.98,
                               min_serial=20000, max_serial=80000) -> bool:
    """Heurística conservadora p/ seriais do Excel (dias desde 1899-12-30)."""
    s = series.dropna()
    if s.empty:
        return False
    s_num = pd.to_numeric(s, errors="coerce")
    if s_num.notna().mean() < min_numeric_ratio:
        return False
    s_num = s_num.dropna()
    if s_num.empty:
        return False
    if (np.isclose(s_num, np.round(s_num))).mean() < min_integer_ratio:
        return False
    mn, mx = float(s_num.min()), float(s_num.max())
    return (mn >= min_serial) and (mx <= max_serial)

def detectar_colunas_data(df: pd.DataFrame,
                          *, min_sucesso: float = 0.70,
                          name_regex_whitelist: Optional[re.Pattern] = None,
                          name_exclude: Optional[Iterable[str]] = None) -> List[str]:
    """
    Detecta datas por conteúdo (string com “cara de data” ou serial do Excel) e valida por parse.
    Tolerante a objetos (dict/list) convertendo-os para string somente na análise textual.
    """
    excl = set(name_exclude or [])
    date_cols: List[str] = []

    for col in df.columns:
        if col in excl:
            continue

        s = df[col]
        # Já é datetime?
        if pd.api.types.is_datetime64_any_dtype(s):
            if not name_regex_whitelist or name_regex_whitelist.search(col):
                date_cols.append(col)
            continue

        s_nonnull = s.dropna()
        if s_nonnull.empty:
            continue

        # 1) Parece string de data?
        looks_like_date = False
        try:
            # Convertendo para str só para o teste textual (suporta dict/list)
            text_sample = s_nonnull.astype(str).head(300)
            ratio_datey = text_sample.str.contains(_DATE_LIKE_RE, regex=True, na=False).mean()
            looks_like_date = ratio_datey >= 0.30
        except Exception:
            looks_like_date = False

        # 2) Parece serial de Excel?
        excel_serial = _is_excel_serial_candidate(s_nonnull)

        if not (looks_like_date or excel_serial):
            continue

        # 3) Validação por parse
        if excel_serial:
            parsed = pd.to_datetime(s, errors="coerce", unit="D", origin="1899-12-30")
        else:
            parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True, dayfirst=True)

        if parsed.notna().mean() >= min_sucesso:
            if not name_regex_whitelist or name_regex_whitelist.search(col):
                date_cols.append(col)

    return date_cols

# --- Transformador principal ---
def formatar_dataframe(
    df: pd.DataFrame,
    *, date_format: str = "%d/%m/%Y",
    min_sucesso_data: float = 0.70,
    name_regex_whitelist: Optional[re.Pattern] = None,
    name_exclude: Optional[Iterable[str]] = None,
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    - Converte colunas binárias para dtype 'boolean' (preservando NA).
    - Normaliza datas para 'dd/mm/aaaa' (mantém NaN quando não for data).
    Retorna: (df_formatado, lista_booleanas, lista_datas).
    """
    df_out = df.copy()

    bool_cols = detectar_colunas_booleanas(df_out)
    date_cols = detectar_colunas_data(
        df_out,
        min_sucesso=min_sucesso_data,
        name_regex_whitelist=name_regex_whitelist,
        name_exclude=name_exclude,
    )

    # Booleanos
    for col in bool_cols:
        mapped = [ _to_bool(v) for v in df_out[col].values ]
        # Garante dtype pandas 'boolean' (True/False/NA)
        df_out[col] = pd.Series(mapped, dtype="boolean")

    # Datas
    for col in date_cols:
        s = df_out[col]
        if _is_excel_serial_candidate(s):
            parsed = pd.to_datetime(s, errors="coerce", unit="D", origin="1899-12-30")
        else:
            parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True, dayfirst=True)
        df_out[col] = parsed.dt.strftime(date_format).where(parsed.notna())

    return df_out, bool_cols, date_cols

def import_dados():
    API_KEY = st.secrets.get("API_KEY")
    BASE_ID = st.secrets.get("BASE_ID_LEADS")
    TABLE = st.secrets.get("TABLE_LEADS")

    api = Api(API_KEY)
    table = api.table(BASE_ID, TABLE)

    records = table.all()  # busca todos os registros

    df_leads = pd.DataFrame([
        r["fields"] | {"_id": r["id"]}  # junta campos com o id do registro
        for r in records
    ])

    API_KEY = st.secrets.get("API_KEY")
    BASE_ID_CLIENTES = st.secrets.get("BASE_ID_CLIENTES")
    TABLE_CLIENTES = st.secrets.get("TABLE_CLIENTES")

    api = Api(API_KEY)
    table = api.table(BASE_ID_CLIENTES, TABLE_CLIENTES)

    records = table.all()

    df_clientes = pd.DataFrame([
        r["fields"] | {"_id": r["id"]}  # junta campos com o id do registro
        for r in records
    ])

    # -------------- Formatar dataframes -------------- #
    df_leads, bool_cols, date_cols = formatar_dataframe(df_leads)
    df_clientes, bool_cols, date_cols = formatar_dataframe(df_clientes)

    return df_leads, df_clientes 