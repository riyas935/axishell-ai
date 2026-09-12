import os
import re
import warnings
import json
import time
from html import escape
from io import BytesIO
from zipfile import BadZipFile, ZipFile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from axishell_runtime import APP_RELEASE, APP_VERSION, SUPPORT_BOUNDARIES, build_operational_snapshot

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AxiShell AI - Universal Excel Analyzer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Theme Preferences
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'theme_choice' not in st.session_state:
    st.session_state.theme_choice = "Dark"
if 'focus_mode' not in st.session_state:
    st.session_state.focus_mode = False
if 'app_session_started_at' not in st.session_state:
    st.session_state.app_session_started_at = time.perf_counter()

# Theme Colors Definition based on theme selection
st.session_state.dark_mode = st.session_state.theme_choice == "Dark"
if st.session_state.dark_mode:
    COLOR_PRIMARY = "#F8FAFC"    # Slate 50
    COLOR_ACCENT = "#2DD4BF"     # Teal 400
    COLOR_SECONDARY = "#94A3B8"  # Slate 400
    COLOR_LIGHT = "#0F172A"      # Slate 900
    COLOR_BORDER = "#334155"     # Slate 700
    COLOR_SIDEBAR = "#1E293B"    # Slate 800
    COLOR_CARD_BG = "#1E293B"    # Slate 800
    COLOR_TEXT = "#E2E8F0"       # Slate 200
    
    # Status card colors
    COLOR_STATUS_DEFAULT_BG = "#1E3A8A"
    COLOR_STATUS_DEFAULT_BORDER = "#2563EB"
    COLOR_STATUS_DEFAULT_TEXT = "#DBEAFE"
    COLOR_STATUS_UPLOADED_BG = "#064E3B"
    COLOR_STATUS_UPLOADED_BORDER = "#059669"
    COLOR_STATUS_UPLOADED_TEXT = "#D1FAE5"
    
    CHART_PALETTE = ["#38BDF8", "#2DD4BF", "#60A5FA", "#FBBF24", "#F87171", "#A78BFA"]
    PLOTLY_TEXT_COLOR = "#94A3B8"
    PLOTLY_GRID_COLOR = "#334155"
else:
    COLOR_PRIMARY = "#0F172A"    # Slate 900
    COLOR_ACCENT = "#0D9488"     # Teal 600
    COLOR_SECONDARY = "#475569"  # Slate 600
    COLOR_LIGHT = "#F8FAFC"      # Slate 50
    COLOR_BORDER = "#E2E8F0"     # Slate 200
    COLOR_SIDEBAR = "#F1F5F9"    # Slate 100
    COLOR_CARD_BG = "#FFFFFF"    # Pure White
    COLOR_TEXT = "#1E293B"       # Slate 800
    
    # Status card colors
    COLOR_STATUS_DEFAULT_BG = "#EFF6FF"
    COLOR_STATUS_DEFAULT_BORDER = "#BFDBFE"
    COLOR_STATUS_DEFAULT_TEXT = "#1E40AF"
    COLOR_STATUS_UPLOADED_BG = "#ECFDF5"
    COLOR_STATUS_UPLOADED_BORDER = "#A7F3D0"
    COLOR_STATUS_UPLOADED_TEXT = "#065F46"
    
    CHART_PALETTE = ["#0F172A", "#0D9488", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6"]
    PLOTLY_TEXT_COLOR = "#475569"
    PLOTLY_GRID_COLOR = "#F1F5F9"


def apply_chart_theme(fig, height=None):
    """Apply the shared AxiShell chart surface without changing chart-specific data or axes."""
    fig.update_layout(
        template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
        colorway=CHART_PALETTE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PLOTLY_TEXT_COLOR, family="Inter, ui-sans-serif, system-ui, sans-serif"),
        hoverlabel=dict(bgcolor=COLOR_CARD_BG, bordercolor=COLOR_BORDER, font=dict(color=COLOR_TEXT)),
        legend=dict(font=dict(color=PLOTLY_TEXT_COLOR)),
        height=height,
    )
    fig.update_xaxes(linecolor=COLOR_BORDER, gridcolor=PLOTLY_GRID_COLOR, tickfont=dict(color=PLOTLY_TEXT_COLOR))
    fig.update_yaxes(linecolor=COLOR_BORDER, gridcolor=PLOTLY_GRID_COLOR, tickfont=dict(color=PLOTLY_TEXT_COLOR))
    return fig

# Custom CSS styling for premium look and feel
st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{
        background-color: {COLOR_LIGHT};
        color: {COLOR_TEXT};
    }}
    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_SIDEBAR} !important;
        border-right: 1px solid {COLOR_BORDER};
    }}
    /* Sidebar Header Colors */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{
        color: {COLOR_PRIMARY} !important;
    }}
    /* Sidebar text colors */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] li, 
    section[data-testid="stSidebar"] span {{
        color: {COLOR_TEXT};
    }}
    /* Title and Header customization */
    h1 {{
        color: {COLOR_PRIMARY};
        font-weight: 800 !important;
        margin-bottom: 2px !important;
    }}
    h3 {{
        color: {COLOR_SECONDARY};
        font-weight: 600 !important;
    }}
    /* Metric container styling (styled into clean cards) */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 28px !important;
        font-weight: 700 !important;
        color: {COLOR_PRIMARY} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: {COLOR_SECONDARY} !important;
        font-weight: 600 !important;
    }}
    /* File uploader outer card and internal dropzone */
    div[data-testid="stFileUploader"] {{
        background-color: {COLOR_CARD_BG} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    /* Upload dropzone - always dark with white text */
    div[data-testid="stFileUploaderDropzone"] {{
        border: 2px dashed {COLOR_ACCENT} !important;
        background-color: #1E293B !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] p {{
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }}
    /* Upload button - white text on dark */
    div[data-testid="stFileUploaderDropzone"] button {{
        background-color: {COLOR_ACCENT} !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
        border-radius: 6px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button span,
    div[data-testid="stFileUploaderDropzone"] button p,
    div[data-testid="stFileUploaderDropzone"] button small,
    div[data-testid="stFileUploaderDropzone"] button * {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    /* Toggle - always dark background with white text */
    div[data-testid="stToggle"] {{
        background-color: #1E293B !important;
        border: 2px solid {COLOR_ACCENT} !important;
        padding: 12px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }}
    div[data-testid="stToggle"] *,
    div[data-testid="stToggle"] p,
    div[data-testid="stToggle"] span,
    div[data-testid="stToggle"] label,
    div[data-testid="stToggle"] label span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }}
    /* Upload icon color fix */
    div[data-testid="stFileUploaderDropzone"] svg {{
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }}
    /* File uploader status custom card */
    .status-card {{
        padding: 12px;
        border-radius: 8px;
        font-size: 13px;
        margin-bottom: 15px;
        line-height: 1.4;
    }}
    .status-default {{
        background-color: {COLOR_STATUS_DEFAULT_BG};
        border: 1px solid {COLOR_STATUS_DEFAULT_BORDER};
        color: {COLOR_STATUS_DEFAULT_TEXT};
    }}
    .status-uploaded {{
        background-color: {COLOR_STATUS_UPLOADED_BG};
        border: 1px solid {COLOR_STATUS_UPLOADED_BORDER};
        color: {COLOR_STATUS_UPLOADED_TEXT};
    }}
    .axi-guide {{
        background: linear-gradient(135deg, {COLOR_CARD_BG}, {COLOR_STATUS_DEFAULT_BG});
        border: 1px solid {COLOR_BORDER};
        border-radius: 14px;
        padding: 14px 16px;
        margin: 0 0 22px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .axi-guide-mark {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: {COLOR_ACCENT};
        color: #FFFFFF;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 16px;
        flex: 0 0 38px;
    }}
    .axi-guide p {{
        margin: 0;
        color: {COLOR_TEXT};
        font-size: 14px;
    }}
    .axi-workspace-nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0 0 22px 0;
        padding: 10px;
        background: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
    }}
    .axi-workspace-nav a {{
        color: {COLOR_TEXT};
        text-decoration: none;
        border: 1px solid {COLOR_BORDER};
        border-radius: 999px;
        padding: 6px 11px;
        font-size: 13px;
        font-weight: 600;
    }}
    .axi-workspace-nav a:hover, .axi-workspace-nav a:focus-visible {{
        background: {COLOR_ACCENT};
        border-color: {COLOR_ACCENT};
        color: #FFFFFF;
    }}
    .axi-section-anchor {{
        scroll-margin-top: 1rem;
    }}
    .axi-context-bar {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 0 0 18px 0;
    }}
    .axi-context-item, .axi-status-card {{
        background: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 12px 14px;
    }}
    .axi-context-label, .axi-status-label {{
        display: block;
        color: {COLOR_SECONDARY};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .axi-context-value {{
        display: block;
        color: {COLOR_TEXT};
        font-size: 14px;
        font-weight: 650;
        margin-top: 4px;
        overflow-wrap: anywhere;
    }}
    .axi-status-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 12px 0 16px 0;
    }}
    .axi-status-value {{
        display: block;
        color: {COLOR_PRIMARY};
        font-size: 22px;
        font-weight: 750;
        margin-top: 5px;
    }}
    .axi-status-detail {{
        display: block;
        color: {COLOR_SECONDARY};
        font-size: 12px;
        margin-top: 4px;
    }}
    .axi-status-card--good {{ border-left: 4px solid #10B981; }}
    .axi-status-card--review {{ border-left: 4px solid #F59E0B; }}
    .axi-status-card--risk {{ border-left: 4px solid #EF4444; }}
    .axi-empty-state {{
        display: grid;
        grid-template-columns: auto 1fr;
        align-items: center;
        gap: 16px;
        padding: 20px;
        margin: 14px 0;
        background: {COLOR_CARD_BG};
        border: 1px dashed {COLOR_BORDER};
        border-radius: 14px;
    }}
    .axi-empty-illustration {{
        width: 58px;
        height: 58px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 5px;
        padding: 7px;
        border-radius: 12px;
        background: {COLOR_STATUS_DEFAULT_BG};
    }}
    .axi-empty-illustration span {{
        border-radius: 3px;
        background: {COLOR_ACCENT};
        opacity: 0.92;
    }}
    .axi-empty-title {{
        margin: 0;
        color: {COLOR_TEXT};
        font-size: 16px;
        font-weight: 750;
    }}
    .axi-empty-detail {{
        margin: 4px 0 0;
        color: {COLOR_SECONDARY};
        font-size: 13px;
    }}
    @media (max-width: 900px) {{
        .axi-context-bar, .axi-status-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
        .axi-context-bar, .axi-status-grid {{ grid-template-columns: 1fr; }}
        .axi-empty-state {{ grid-template-columns: 1fr; }}
    }}
    button:focus-visible, a:focus-visible, input:focus-visible, [role="button"]:focus-visible {{
        outline: 3px solid {COLOR_ACCENT} !important;
        outline-offset: 3px !important;
    }}
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


def render_empty_state(title, detail):
    """Render a code-native visual empty state without changing application behavior."""
    st.markdown(
        f"""<div class="axi-empty-state" role="status">
        <div class="axi-empty-illustration" aria-hidden="true">
            <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
        </div>
        <div><p class="axi-empty-title">{escape(title)}</p><p class="axi-empty-detail">{escape(detail)}</p></div>
        </div>""",
        unsafe_allow_html=True,
    )

# Helper to extract digits for chronological sorting of periods/files
def get_period_sort_key(period_name):
    numbers = re.findall(r'\d+', str(period_name))
    if numbers:
        return int(numbers[0])
    return str(period_name)

STARTER_SCHEMA_COLUMNS = ['Product', 'Units Sold', 'Revenue', 'Region']
SOURCE_COLUMNS = ['Source File', 'Source Sheet']
MAX_UPLOAD_FILES = 10
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024
MAX_SHEETS_PER_WORKBOOK = 25
MAX_ROWS_PER_TABLE = 250_000
MAX_COLUMNS_PER_TABLE = 250
MAX_TOTAL_ROWS = 500_000
DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
MAX_AI_CONTEXT_CHARS = 12_000
WELCOME_MESSAGES = [
    "Bring a spreadsheet and we will make its structure easier to explore.",
    "Start with a file, then narrow the view to the questions that matter.",
    "Every finding keeps its method and context close at hand.",
    "Axi is ready to help you get oriented without changing your source data.",
]
LOADING_MESSAGES = [
    "Checking the workbook structure...",
    "Preparing a safe, read-only view of your data...",
    "Building profiles and source lineage...",
    "Getting your data ready to explore...",
]
if "experience_message_index" not in st.session_state:
    st.session_state.experience_message_index = 0
SEMANTIC_ROLE_OPTIONS = [
    "Identifier",
    "Date",
    "Currency / Amount",
    "Quantity",
    "Percentage / Rate",
    "Category",
    "Free Text",
    "Sensitive Personal Data",
    "Ignore",
]
DOMAIN_TEMPLATE_GUIDANCE = {
    "Sales": "Compare monetary amounts and quantities by product, customer, channel, region, or date.",
    "HR": "Explore headcount, compensation, departments, roles, and employment dates while handling personal data carefully.",
    "Finance": "Analyze amounts, balances, transactions, accounts, and periods with clear reconciliation checks.",
    "Operations": "Analyze quantities, inventory, locations, statuses, cycle times, and operational trends.",
    "Healthcare": "Explore operational or aggregate healthcare data cautiously; avoid exposing identifiable patient information.",
}


def clean_column_headers(df):
    """Normalize blank and duplicate headers without changing data values."""
    cleaned_columns = []
    seen = {}

    for index, col in enumerate(df.columns, 1):
        base_name = str(col).strip()
        if not base_name or base_name.lower().startswith("unnamed:"):
            base_name = f"Column {index}"

        count = seen.get(base_name, 0)
        seen[base_name] = count + 1
        cleaned_columns.append(base_name if count == 0 else f"{base_name}_{count + 1}")

    df = df.copy()
    df.columns = cleaned_columns
    return df


def normalize_starter_schema(df):
    """Map familiar sales-dashboard columns when present, without requiring them."""
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if col in SOURCE_COLUMNS:
            continue
        if 'product' in col_lower:
            column_mapping[col] = 'Product'
        elif 'unit' in col_lower:
            column_mapping[col] = 'Units Sold'
        elif 'revvenue' in col_lower or 'revenue' in col_lower:
            column_mapping[col] = 'Revenue'
        elif 'region' in col_lower:
            column_mapping[col] = 'Region'

    return df.rename(columns=column_mapping)


def clean_universal_df(df):
    """
    Cleans an arbitrary tabular dataset while preserving its original schema.
    Returns: (cleaned_df, is_valid, error_message)
    """
    if df is None or df.empty:
        return None, False, "No readable rows found."

    try:
        df_cleaned = clean_column_headers(df)
        df_cleaned = df_cleaned.dropna(how='all').dropna(axis=1, how='all')

        if df_cleaned.empty or len(df_cleaned.columns) == 0:
            return None, False, "The sheet is empty after removing blank rows and columns."

        df_cleaned = normalize_starter_schema(df_cleaned)

        if set(STARTER_SCHEMA_COLUMNS).issubset(df_cleaned.columns):
            df_cleaned['Product'] = df_cleaned['Product'].astype(str).str.strip()
            df_cleaned['Units Sold'] = pd.to_numeric(df_cleaned['Units Sold'], errors='coerce')
            df_cleaned['Revenue'] = pd.to_numeric(df_cleaned['Revenue'], errors='coerce')
            df_cleaned['Region'] = df_cleaned['Region'].astype(str).str.strip()
            df_cleaned['Avg Price'] = df_cleaned['Revenue'].fillna(0) / df_cleaned['Units Sold'].replace(0, pd.NA).fillna(1)

        return df_cleaned, True, ""
    except Exception as e:
        return None, False, f"Cleaning failed: {str(e)}"


def infer_column_type(series):
    non_null = series.dropna()
    if non_null.empty:
        return "empty"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    numeric_candidate = pd.to_numeric(non_null, errors='coerce')
    if numeric_candidate.notna().mean() >= 0.85:
        return "numeric-like"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        datetime_candidate = pd.to_datetime(non_null, errors='coerce')
    if datetime_candidate.notna().mean() >= 0.85:
        return "datetime-like"

    unique_ratio = non_null.nunique(dropna=True) / len(non_null)
    if unique_ratio <= 0.5 or non_null.nunique(dropna=True) <= 25:
        return "categorical"
    return "text"


@st.cache_data(show_spinner=False)
def build_dataset_profile(df):
    profile_rows = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        non_null_count = int(series.notna().sum())
        unique_count = int(series.nunique(dropna=True))
        inferred_type = infer_column_type(series)

        profile_row = {
            "Column": col,
            "Inferred Type": inferred_type,
            "Pandas Type": str(series.dtype),
            "Non-Null Rows": non_null_count,
            "Missing Rows": missing_count,
            "Missing %": (missing_count / total_rows * 100) if total_rows else 0,
            "Unique Values": unique_count
        }

        if inferred_type in ["numeric", "numeric-like"]:
            numeric_series = pd.to_numeric(series, errors='coerce')
            profile_row["Min"] = numeric_series.min()
            profile_row["Max"] = numeric_series.max()
            profile_row["Mean"] = numeric_series.mean()
        else:
            profile_row["Min"] = None
            profile_row["Max"] = None
            profile_row["Mean"] = None

        profile_rows.append(profile_row)

    return pd.DataFrame(profile_rows)


def scan_xlsx_safety(file_bytes):
    """Inspect an Office Open XML workbook without executing its contents."""
    try:
        with ZipFile(BytesIO(file_bytes)) as workbook:
            names = workbook.namelist()
            has_macros = any(name.lower().endswith("vbaproject.bin") for name in names)
            has_formulas = any(
                b"<f" in workbook.read(name)
                for name in names
                if name.startswith("xl/worksheets/") and name.endswith(".xml")
            )
        return has_macros, has_formulas, ""
    except BadZipFile:
        return False, False, "The workbook is not a valid .xlsx archive."
    except Exception as error:
        return False, False, f"Safety inspection could not be completed: {error}"


def build_integrity_summary(df, profile_df, lineage_df):
    """Summarize reproducible quality signals without changing uploaded data."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    identifier_like = profile_df.loc[
        profile_df["Column"].str.lower().str.contains(r"(?:^|\s)(?:id|code|number|reference|ref)(?:\s|$)", regex=True),
        "Column",
    ].tolist()
    warnings_list = []
    if missing_cells:
        warnings_list.append(f"{missing_cells:,} missing cell(s) are present.")
    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        warnings_list.append(f"{duplicate_rows:,} duplicate row(s) are present in the active scope.")
    if identifier_like:
        warnings_list.append("Identifier-like fields are present; review type and semantic-role suggestions before aggregation.")
    formula_sources = lineage_df.loc[lineage_df["Formulas Detected"], "Source"].tolist() if not lineage_df.empty else []
    if formula_sources:
        warnings_list.append("Formula cells were detected. AxiShell AI analyzes stored workbook values and never recalculates formulas.")

    summary = pd.DataFrame([
        {"Check": "Rows in active scope", "Result": f"{len(df):,}", "Status": "Info"},
        {"Check": "Missing cells", "Result": f"{missing_cells:,} ({(missing_cells / total_cells * 100) if total_cells else 0:.1f}%)", "Status": "Warning" if missing_cells else "Pass"},
        {"Check": "Duplicate rows", "Result": f"{duplicate_rows:,}", "Status": "Warning" if duplicate_rows else "Pass"},
        {"Check": "Identifier-like fields", "Result": ", ".join(identifier_like) if identifier_like else "None detected", "Status": "Review" if identifier_like else "Pass"},
        {"Check": "Formula sources", "Result": ", ".join(formula_sources) if formula_sources else "None detected", "Status": "Review" if formula_sources else "Pass"},
    ])
    return summary, warnings_list


@st.cache_data(show_spinner=False)
def build_quality_scorecard(df, profile_df):
    """Calculate a transparent 0-100 quality score from the active dataset."""
    total_cells = df.shape[0] * df.shape[1]
    missing_rate = (df.isna().sum().sum() / total_cells) if total_cells else 0
    duplicate_rate = (df.duplicated().sum() / len(df)) if len(df) else 0
    sparse_column_rate = (
        (profile_df["Missing %"] >= 50).sum() / len(profile_df)
        if len(profile_df) else 0
    )
    parse_failures = 0
    parsed_candidates = 0
    for _, row in profile_df.iterrows():
        column = row["Column"]
        if row["Inferred Type"] == "numeric-like":
            source = df[column]
            parsed_candidates += int(source.notna().sum())
            parse_failures += int((source.notna() & pd.to_numeric(source, errors="coerce").isna()).sum())
        elif row["Inferred Type"] == "datetime-like":
            source = df[column]
            parsed_candidates += int(source.notna().sum())
            parse_failures += int((source.notna() & pd.to_datetime(source, errors="coerce").isna()).sum())

    parse_failure_rate = (parse_failures / parsed_candidates) if parsed_candidates else 0
    deductions = {
        "Missing data": min(40, missing_rate * 40),
        "Duplicate rows": min(30, duplicate_rate * 30),
        "Parse failures": min(20, parse_failure_rate * 20),
        "Sparse columns": min(10, sparse_column_rate * 10),
    }
    score = max(0, round(100 - sum(deductions.values()), 1))
    rating = "Good" if score >= 90 else "Needs review" if score >= 70 else "High risk"
    scorecard = pd.DataFrame([
        {"Metric": "Quality score", "Value": f"{score:.1f}/100", "Status": rating, "Method": "100 minus capped deductions for missing data, duplicates, parse failures, and sparse columns."},
        {"Metric": "Completeness", "Value": f"{(1 - missing_rate) * 100:.1f}%", "Status": "Pass" if missing_rate < 0.05 else "Review", "Method": f"Missing-cell rate: {missing_rate * 100:.1f}%; deduction: {deductions['Missing data']:.1f} points."},
        {"Metric": "Row uniqueness", "Value": f"{(1 - duplicate_rate) * 100:.1f}%", "Status": "Pass" if duplicate_rate == 0 else "Review", "Method": f"Duplicate-row rate: {duplicate_rate * 100:.1f}%; deduction: {deductions['Duplicate rows']:.1f} points."},
        {"Metric": "Parse consistency", "Value": f"{(1 - parse_failure_rate) * 100:.1f}%", "Status": "Pass" if parse_failure_rate == 0 else "Review", "Method": f"Numeric/date-like parse failures: {parse_failures:,}; deduction: {deductions['Parse failures']:.1f} points."},
        {"Metric": "Column coverage", "Value": f"{(1 - sparse_column_rate) * 100:.1f}%", "Status": "Pass" if sparse_column_rate == 0 else "Review", "Method": f"Columns at least 50% missing: {int((profile_df['Missing %'] >= 50).sum())}; deduction: {deductions['Sparse columns']:.1f} points."},
    ])
    return score, rating, scorecard


def build_deterministic_findings(df, profile_df, semantic_profile, analysis_context):
    """Return reproducible findings with calculations and limitations, never AI interpretation."""
    findings = []
    type_map = profile_df.set_index("Column")["Inferred Type"].to_dict()
    role_map = semantic_profile.set_index("Column")["Applied Role"].to_dict()

    def add_finding(finding_type, severity, fields, observation, calculation, limitation):
        findings.append({
            "Finding Type": finding_type,
            "Severity": severity,
            "Fields": ", ".join(fields),
            "Observation": observation,
            "Calculation": calculation,
            "Active Context": analysis_context,
            "Limitation": limitation,
        })

    missing_columns = profile_df.loc[profile_df["Missing %"] >= 5, ["Column", "Missing %"]]
    for _, row in missing_columns.head(5).iterrows():
        severity = "High" if row["Missing %"] >= 25 else "Medium"
        add_finding(
            "Missingness", severity, [row["Column"]],
            f"{row['Column']} has {row['Missing %']:.1f}% missing values.",
            f"Missing values / active rows = {int(df[row['Column']].isna().sum()):,} / {len(df):,}.",
            "Missing values may be intentional, unavailable, or caused by ingestion; this check does not infer the cause.",
        )

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        add_finding(
            "Duplicate rows", "High" if duplicate_rows / len(df) >= 0.05 else "Medium", list(df.columns),
            f"{duplicate_rows:,} exact duplicate row(s) are present.",
            f"Exact duplicates / active rows = {duplicate_rows:,} / {len(df):,}.",
            "Rows that are legitimately repeated business events can appear as duplicates; review source keys before removal.",
        )

    numeric_columns = [
        column for column, inferred_type in type_map.items()
        if inferred_type in ["numeric", "numeric-like"] and column not in SOURCE_COLUMNS
        and role_map.get(column) not in ["Identifier", "Sensitive Personal Data"]
    ]
    for column in numeric_columns[:8]:
        numeric_values = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(numeric_values) < 4:
            continue
        lower_quartile, upper_quartile = numeric_values.quantile([0.25, 0.75])
        iqr = upper_quartile - lower_quartile
        if iqr <= 0:
            continue
        lower_bound, upper_bound = lower_quartile - 1.5 * iqr, upper_quartile + 1.5 * iqr
        outlier_count = int(((numeric_values < lower_bound) | (numeric_values > upper_bound)).sum())
        if outlier_count:
            severity = "High" if outlier_count / len(numeric_values) >= 0.1 else "Medium"
            add_finding(
                "Outliers", severity, [column],
                f"{outlier_count:,} value(s) fall outside the IQR outlier bounds for {column}.",
                f"IQR = {iqr:,.3g}; bounds = [{lower_bound:,.3g}, {upper_bound:,.3g}]; flagged = {outlier_count:,} / {len(numeric_values):,}.",
                "The IQR rule flags unusual values statistically; it does not establish that a value is erroneous or material.",
            )

    categorical_columns = [
        column for column, inferred_type in type_map.items()
        if inferred_type in ["categorical", "boolean"] and column not in SOURCE_COLUMNS
        and role_map.get(column) != "Sensitive Personal Data"
    ]
    for column in categorical_columns[:5]:
        counts = df[column].dropna().astype(str).value_counts()
        if len(counts) < 2:
            continue
        top_value, top_count = counts.index[0], int(counts.iloc[0])
        top_share = top_count / counts.sum()
        if top_share >= 0.6:
            add_finding(
                "Distribution", "Medium" if top_share < 0.8 else "High", [column],
                f"{top_value!r} represents {top_share * 100:.1f}% of non-missing {column} values.",
                f"Top-category count / non-missing values = {top_count:,} / {int(counts.sum()):,}.",
                "A concentrated category may reflect the real population, collection bias, or a coding default.",
            )

    date_columns = [column for column, inferred_type in type_map.items() if inferred_type in ["datetime", "datetime-like"]]
    if date_columns and numeric_columns:
        date_column = date_columns[0]
        parsed_dates = pd.to_datetime(df[date_column], errors="coerce")
        for measure in numeric_columns[:3]:
            trend_frame = pd.DataFrame({"date": parsed_dates, "value": pd.to_numeric(df[measure], errors="coerce")}).dropna()
            trend_frame["period"] = trend_frame["date"].dt.to_period("M")
            monthly = trend_frame.groupby("period")["value"].mean()
            if len(monthly) < 2:
                continue
            first_period, last_period = monthly.index[0], monthly.index[-1]
            first_value, last_value = monthly.iloc[0], monthly.iloc[-1]
            if first_value == 0:
                change_text = f"changed from 0 to {last_value:,.3g}"
            else:
                change_text = f"changed {((last_value - first_value) / abs(first_value)) * 100:+.1f}%"
            add_finding(
                "Trend", "Medium", [date_column, measure],
                f"Monthly average {measure} {change_text} from {first_period} to {last_period}.",
                f"First monthly mean = {first_value:,.3g}; last monthly mean = {last_value:,.3g}; periods = {len(monthly):,}.",
                "This compares endpoint monthly averages only; it does not establish seasonality, causation, or statistical significance.",
            )

    for index, left_column in enumerate(numeric_columns[:8]):
        for right_column in numeric_columns[index + 1:8]:
            paired = pd.DataFrame({
                "left": pd.to_numeric(df[left_column], errors="coerce"),
                "right": pd.to_numeric(df[right_column], errors="coerce"),
            }).dropna()
            if len(paired) < 5:
                continue
            correlation = paired["left"].corr(paired["right"])
            if pd.notna(correlation) and abs(correlation) >= 0.7:
                add_finding(
                    "Relationship", "Medium" if abs(correlation) < 0.9 else "High", [left_column, right_column],
                    f"{left_column} and {right_column} have a Pearson correlation of {correlation:.2f}.",
                    f"Pearson r calculated from {len(paired):,} paired non-missing rows.",
                    "Correlation measures linear association and does not establish causation; outliers can materially affect r.",
                )

    if not findings:
        add_finding(
            "Coverage", "Info", [], "No deterministic threshold was triggered in the active dataset.",
            "Applied missingness, duplicate, IQR outlier, concentration, trend, and correlation rules to the active scope.",
            "No alert does not guarantee data quality or the absence of meaningful patterns.",
        )

    severity_order = {"High": 0, "Medium": 1, "Info": 2}
    result = pd.DataFrame(findings)
    return result.sort_values("Severity", key=lambda values: values.map(severity_order), kind="stable").reset_index(drop=True)


def build_ai_analysis_context(profile_df, semantic_profile, quality_scorecard, findings_df, analysis_context):
    """Build a compact, provenance-first AI context without sending raw dataset rows."""
    profile_columns = ["Column", "Inferred Type", "Non-Null Rows", "Missing Rows", "Missing %", "Unique Values"]
    semantic_columns = ["Column", "Inferred Type", "Applied Role", "Source", "Confidence", "Evidence"]
    finding_columns = ["Finding Type", "Severity", "Fields", "Observation", "Calculation", "Active Context", "Limitation"]
    context = {
        "data_boundary": "No raw spreadsheet rows are included. This context contains computed summaries from the active filtered dataset only.",
        "active_context": analysis_context,
        "column_profile": profile_df.reindex(columns=profile_columns).to_dict(orient="records"),
        "semantic_profile": semantic_profile.reindex(columns=semantic_columns).to_dict(orient="records"),
        "quality_scorecard": quality_scorecard.to_dict(orient="records"),
        "deterministic_findings": findings_df.reindex(columns=finding_columns).head(12).to_dict(orient="records"),
    }
    serialized = json.dumps(context, default=str, ensure_ascii=False)
    return serialized[:MAX_AI_CONTEXT_CHARS]


def request_ai_analysis(api_key, question, context, model=DEFAULT_OPENAI_MODEL, client=None):
    """Request a grounded explanation from OpenAI while disabling API response storage."""
    if not api_key:
        raise ValueError("No OpenAI API key is configured.")
    if not question or not question.strip():
        raise ValueError("Enter a question before requesting AI-assisted analysis.")

    if client is None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("The OpenAI Python package is not installed. Install dependencies before enabling AI-assisted analysis.") from error
        client = OpenAI(api_key=api_key)

    instructions = """You are AxiShell AI's optional analysis assistant. Use only the supplied computed context.
Do not invent values, fields, filters, trends, or causal explanations. Treat deterministic findings as computed facts only when their calculation is shown.
Clearly separate your generated interpretation from the computed evidence. State uncertainty and limitations, especially for healthcare, finance, HR, or sensitive-data contexts.
Never request, reconstruct, or expose raw rows or sensitive personal data. If the question cannot be answered from the context, say what computed analysis is needed next.
Use this concise structure: Grounded answer; Computed evidence; AI interpretation; Limitations and next check."""
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=f"User question: {question.strip()}\n\nComputed active-dataset context:\n{context}",
        store=False,
    )
    answer = getattr(response, "output_text", None)
    if not answer:
        raise RuntimeError("The AI service returned no text response.")
    return answer


def infer_semantic_role(column, series, inferred_type):
    """Infer an explainable business role without modifying the source data."""
    column_name = str(column).lower().replace("_", " ").replace("-", " ")
    column_tokens = set(re.findall(r"[a-z0-9]+", column_name))
    numeric_types = ["numeric", "numeric-like"]

    sensitive_terms = [
        "email", "phone", "mobile", "address", "ssn", "social security", "passport",
        "patient", "medical record", "first name", "last name", "full name", "employee name",
        "patient name", "date of birth", "dob",
    ]
    if any(term in column_name for term in sensitive_terms):
        return "Sensitive Personal Data", "High", "Column name suggests personal or sensitive information."
    if column_tokens.intersection({"id", "code", "number", "reference", "ref"}):
        return "Identifier", "High", "Column name suggests an identifier or reference value."
    if inferred_type in ["datetime", "datetime-like"] or any(term in column_name for term in ["date", "time", "month", "year", "day"]):
        return "Date", "High" if inferred_type in ["datetime", "datetime-like"] else "Medium", "Detected date-like values or date-related column name."
    if inferred_type in numeric_types and any(term in column_name for term in ["revenue", "sales", "price", "cost", "salary", "budget", "amount", "payment", "balance", "profit", "expense"]):
        return "Currency / Amount", "High", "Numeric field name suggests a monetary value."
    if inferred_type in numeric_types and any(term in column_name for term in ["unit", "qty", "quantity", "count", "volume", "stock", "inventory"]):
        return "Quantity", "High", "Numeric field name suggests a count or quantity."
    if inferred_type in numeric_types and any(term in column_name for term in ["percent", "percentage", "rate", "ratio", "margin"]):
        return "Percentage / Rate", "High", "Numeric field name suggests a rate or percentage."
    if inferred_type in ["categorical", "boolean"]:
        return "Category", "Medium", "Detected low-cardinality categorical or boolean values."
    if inferred_type == "text":
        return "Free Text", "Medium", "Detected high-cardinality text values."
    return "Unclassified", "Low", "No strong semantic signal was detected."


def build_semantic_profile(df, dataset_profile, overrides):
    """Build a role profile that exposes automatic inference and user overrides."""
    profile_types = dataset_profile.set_index("Column")["Inferred Type"].to_dict()
    semantic_rows = []

    for column in df.columns:
        automatic_role, confidence, evidence = infer_semantic_role(
            column, df[column], profile_types.get(column, "empty")
        )
        applied_role = overrides.get(column, automatic_role)
        semantic_rows.append({
            "Column": column,
            "Inferred Type": profile_types.get(column, "empty"),
            "Automatic Role": automatic_role,
            "Applied Role": applied_role,
            "Source": "User override" if column in overrides else "Automatic",
            "Confidence": confidence,
            "Evidence": evidence,
        })

    return pd.DataFrame(semantic_rows)


def recommend_domain_templates(semantic_profile):
    """Return explainable, optional domain-template suggestions from roles and names."""
    column_names = " ".join(semantic_profile["Column"].astype(str).str.lower())
    roles = semantic_profile["Applied Role"].tolist()
    scores = {
        "Sales": sum(term in column_names for term in ["product", "customer", "revenue", "sales", "region", "unit"]),
        "HR": sum(term in column_names for term in ["employee", "department", "salary", "role", "hire", "start date"]),
        "Finance": sum(term in column_names for term in ["transaction", "account", "balance", "payment", "expense", "budget"]),
        "Operations": sum(term in column_names for term in ["inventory", "location", "status", "quantity", "shipment", "cycle"]),
        "Healthcare": sum(term in column_names for term in ["patient", "diagnosis", "treatment", "clinical", "appointment", "medical"]),
    }

    if "Currency / Amount" in roles:
        scores["Sales"] += 1
        scores["Finance"] += 1
    if "Quantity" in roles:
        scores["Sales"] += 1
        scores["Operations"] += 1
    if "Sensitive Personal Data" in roles:
        scores["HR"] += 1
        scores["Healthcare"] += 1

    return [domain for domain, score in scores.items() if score >= 2]


def apply_dynamic_filters(df, container=st.sidebar):
    """Render schema-aware sidebar filters and return the filtered dataset and applied controls."""
    profile = build_dataset_profile(df)
    filterable_columns = profile.loc[
        profile["Inferred Type"] != "empty", "Column"
    ].tolist()

    selected_columns = container.multiselect(
        "Fields to filter",
        options=filterable_columns,
        help="Choose one or more fields. Controls adapt to the detected data type."
    )

    filtered_df = df.copy()
    filter_details = []
    for index, column in enumerate(selected_columns):
        inferred_type = profile.loc[profile["Column"] == column, "Inferred Type"].iloc[0]
        series = filtered_df[column]
        widget_key = f"dynamic_filter_{index}_{column}"

        if inferred_type in ["numeric", "numeric-like"]:
            numeric_series = pd.to_numeric(series, errors="coerce")
            minimum, maximum = numeric_series.min(), numeric_series.max()
            if pd.isna(minimum) or pd.isna(maximum):
                container.caption(f"{column}: no numeric values available.")
                continue
            if minimum == maximum:
                container.caption(f"{column}: all values are {minimum:g}.")
                continue
            selected_range = container.slider(
                column,
                min_value=float(minimum),
                max_value=float(maximum),
                value=(float(minimum), float(maximum)),
                key=widget_key,
            )
            filtered_df = filtered_df[numeric_series.between(*selected_range)]
            filter_details.append(f"{column}: {selected_range[0]:g} to {selected_range[1]:g}")
        elif inferred_type in ["datetime", "datetime-like"]:
            date_series = pd.to_datetime(series, errors="coerce")
            minimum, maximum = date_series.min(), date_series.max()
            if pd.isna(minimum) or pd.isna(maximum):
                container.caption(f"{column}: no valid dates available.")
                continue
            selected_dates = container.date_input(
                column,
                value=(minimum.date(), maximum.date()),
                min_value=minimum.date(),
                max_value=maximum.date(),
                key=widget_key,
            )
            if len(selected_dates) == 2:
                start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
                filtered_df = filtered_df[date_series.between(start_date, end_date + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))]
                filter_details.append(f"{column}: {start_date.date()} to {end_date.date()}")
        else:
            values = sorted(series.dropna().astype(str).unique())
            if len(values) <= 100:
                selected_values = container.multiselect(
                    column,
                    options=values,
                    default=values,
                    key=widget_key,
                )
                filtered_df = filtered_df[series.astype(str).isin(selected_values)]
                filter_details.append(f"{column}: {len(selected_values)} selected value(s)")
            else:
                search_text = container.text_input(
                    f"{column} contains",
                    key=widget_key,
                    help="Use text search for fields with more than 100 distinct values.",
                )
                if search_text:
                    filtered_df = filtered_df[series.astype(str).str.contains(search_text, case=False, na=False, regex=False)]
                    filter_details.append(f"{column}: contains search applied")

    return filtered_df, selected_columns, filter_details


def build_schema_aggregation(df, measure, dimension, date_column, frequency, aggregation):
    """Create a generic aggregation using user-selected, schema-aware fields."""
    working_df = df.copy()
    group_columns = []

    if date_column != "No date grouping":
        parsed_dates = pd.to_datetime(working_df[date_column], errors="coerce")
        working_df = working_df.loc[parsed_dates.notna()].copy()
        parsed_dates = parsed_dates.loc[parsed_dates.notna()]
        frequency_map = {"Day": "D", "Month": "M", "Quarter": "Q", "Year": "Y"}
        working_df["Analysis Period"] = parsed_dates.dt.to_period(frequency_map[frequency]).dt.to_timestamp()
        group_columns.append("Analysis Period")

    if dimension != "No grouping":
        group_columns.append(dimension)

    value_label = "Rows" if measure == "Row count" else f"{aggregation} of {measure}"
    if measure == "Row count":
        if group_columns:
            result = working_df.groupby(group_columns, dropna=False).size().reset_index(name=value_label)
        else:
            result = pd.DataFrame({value_label: [len(working_df)]})
    else:
        working_df["Analysis Value"] = pd.to_numeric(working_df[measure], errors="coerce")
        working_df = working_df.loc[working_df["Analysis Value"].notna()].copy()
        aggregation_map = {
            "Sum": "sum",
            "Average": "mean",
            "Median": "median",
            "Minimum": "min",
            "Maximum": "max",
            "Count": "count",
        }
        if group_columns:
            result = (
                working_df.groupby(group_columns, dropna=False)["Analysis Value"]
                .agg(aggregation_map[aggregation])
                .reset_index(name=value_label)
            )
        else:
            result = pd.DataFrame({value_label: [working_df["Analysis Value"].agg(aggregation_map[aggregation])]})

    return result, group_columns, value_label

def process_data_sources(uploaded_files):
    dfs = []
    validation_reports = []
    lineage_rows = []
    
    if uploaded_files:
        if len(uploaded_files) > MAX_UPLOAD_FILES:
            validation_reports.append({
                "file": "Upload batch",
                "status": "Limit Exceeded",
                "details": f"Upload no more than {MAX_UPLOAD_FILES} files at a time."
            })

        # Process uploaded files dynamically
        for file_index, file_obj in enumerate(uploaded_files):
            try:
                if file_index >= MAX_UPLOAD_FILES:
                    validation_reports.append({
                        "file": file_obj.name,
                        "status": "Limit Exceeded",
                        "details": f"Only the first {MAX_UPLOAD_FILES} files in an upload batch are processed."
                    })
                    continue
                if sum(len(df) for df in dfs) >= MAX_TOTAL_ROWS:
                    validation_reports.append({
                        "file": file_obj.name,
                        "status": "Limit Exceeded",
                        "details": f"The combined upload is limited to {MAX_TOTAL_ROWS:,} loaded rows."
                    })
                    continue
                # Explicit File Type Validation
                file_name_lower = file_obj.name.lower()
                if not file_name_lower.endswith(('.xlsx', '.xls', '.csv')):
                    validation_reports.append({
                        "file": file_obj.name,
                        "status": "Invalid File Type",
                        "details": "Wrong file type. Supported files: .xlsx, .xls, and .csv."
                    })
                    continue

                file_size = getattr(file_obj, "size", 0)
                if file_size > MAX_FILE_SIZE_BYTES:
                    validation_reports.append({
                        "file": file_obj.name,
                        "status": "Limit Exceeded",
                        "details": f"Files must be {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB or smaller."
                    })
                    continue

                source_name = file_obj.name.rsplit('.', 1)[0]
                file_bytes = file_obj.getvalue()
                formulas_detected = False
                parser_notes = []

                if file_name_lower.endswith('.csv'):
                    try:
                        loaded_tables = {"CSV": pd.read_csv(BytesIO(file_bytes), on_bad_lines="error")}
                    except UnicodeDecodeError:
                        loaded_tables = {"CSV": pd.read_csv(BytesIO(file_bytes), encoding="latin-1", on_bad_lines="error")}
                        parser_notes.append("CSV was decoded with latin-1 after UTF-8 decoding failed; verify accented characters.")
                else:
                    if file_name_lower.endswith(".xlsx"):
                        has_macros, formulas_detected, safety_error = scan_xlsx_safety(file_bytes)
                        if safety_error:
                            raise ValueError(safety_error)
                        if has_macros:
                            validation_reports.append({
                                "file": file_obj.name,
                                "status": "Security Blocked",
                                "details": "Macro-enabled workbook content was detected. Macros are not supported or executed."
                            })
                            continue
                    else:
                        parser_notes.append("Legacy .xls files cannot be scanned for macros or formulas; review the source before analysis.")

                    loaded_tables = pd.read_excel(BytesIO(file_bytes), sheet_name=None)
                    if len(loaded_tables) > MAX_SHEETS_PER_WORKBOOK:
                        raise ValueError(f"Workbooks may contain at most {MAX_SHEETS_PER_WORKBOOK} sheets.")

                loaded_rows = 0
                loaded_sheets = []
                sheet_errors = []

                for sheet_name, df_raw in loaded_tables.items():
                    if df_raw.shape[0] > MAX_ROWS_PER_TABLE or df_raw.shape[1] > MAX_COLUMNS_PER_TABLE:
                        sheet_errors.append(
                            f"{sheet_name}: exceeds the {MAX_ROWS_PER_TABLE:,}-row or {MAX_COLUMNS_PER_TABLE}-column limit."
                        )
                        continue
                    if sum(len(df) for df in dfs) + loaded_rows + len(df_raw) > MAX_TOTAL_ROWS:
                        sheet_errors.append(f"{sheet_name}: would exceed the {MAX_TOTAL_ROWS:,}-row combined-upload limit.")
                        continue
                    cleaned_df, is_valid, err_msg = clean_universal_df(df_raw)
                    if is_valid:
                        cleaned_df['Source File'] = source_name
                        cleaned_df['Source Sheet'] = str(sheet_name)
                        dfs.append(cleaned_df)
                        loaded_rows += len(cleaned_df)
                        loaded_sheets.append(str(sheet_name))
                        lineage_rows.append({
                            "Source": source_name,
                            "Sheet": str(sheet_name),
                            "Original Rows": int(df_raw.shape[0]),
                            "Loaded Rows": int(len(cleaned_df)),
                            "Original Columns": int(df_raw.shape[1]),
                            "Loaded Columns": int(len(cleaned_df.columns) - len(SOURCE_COLUMNS)),
                            "Transformations": "Normalized headers; removed fully blank rows and columns; added source metadata.",
                            "Formulas Detected": formulas_detected,
                        })
                    else:
                        sheet_errors.append(f"{sheet_name}: {err_msg}")

                if loaded_rows:
                    detail = f"Loaded {loaded_rows} rows from {len(loaded_sheets)} sheet(s): {', '.join(loaded_sheets[:5])}"
                    if len(loaded_sheets) > 5:
                        detail += ", ..."
                    if sheet_errors:
                        detail += f". Skipped {len(sheet_errors)} empty/unreadable sheet(s)."
                    detail += ". " + " ".join(parser_notes) if parser_notes else ""
                    validation_reports.append({"file": file_obj.name, "status": "Valid with warnings" if parser_notes or formulas_detected else "Valid", "details": detail})
                else:
                    validation_reports.append({"file": file_obj.name, "status": "Invalid", "details": "; ".join(sheet_errors) or "No readable tables found."})
            except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as error:
                validation_reports.append({"file": file_obj.name, "status": "Invalid Data", "details": str(error)})
            except Exception as e:
                validation_reports.append({"file": file_obj.name, "status": "Read Error", "details": f"Failed to parse file: {str(e)}"})
    else:
        # Default fallback files
        default_files = ["sales_1.xlsx", "sales_2.xlsx", "sales_3.xlsx"]
        for i, file_name in enumerate(default_files, 1):
            if os.path.exists(file_name):
                try:
                    df_raw = pd.read_excel(file_name, sheet_name="Sales Data")
                    source_name = f"Source {i}"
                    cleaned_df, is_valid, _ = clean_universal_df(df_raw)
                    if is_valid:
                        cleaned_df['Source File'] = source_name
                        cleaned_df['Source Sheet'] = "Sales Data"
                        dfs.append(cleaned_df)
                        lineage_rows.append({
                            "Source": source_name,
                            "Sheet": "Sales Data",
                            "Original Rows": int(df_raw.shape[0]),
                            "Loaded Rows": int(len(cleaned_df)),
                            "Original Columns": int(df_raw.shape[1]),
                            "Loaded Columns": int(len(cleaned_df.columns) - len(SOURCE_COLUMNS)),
                            "Transformations": "Demo source: normalized headers; removed fully blank rows and columns; added source metadata.",
                            "Formulas Detected": False,
                        })
                except Exception:
                    pass
                    
    combined_df = pd.DataFrame()
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df, validation_reports, pd.DataFrame(lineage_rows)

# ================= SIDEBAR DATA PANEL =================
st.sidebar.markdown(f"<h2 style='color: {COLOR_PRIMARY}; font-weight: 700; margin-top: 15px;'>Upload data</h2>", unsafe_allow_html=True)

experience_message_index = st.session_state.experience_message_index % len(WELCOME_MESSAGES)
if not st.session_state.focus_mode:
    st.sidebar.info("Axi is here to help you explore the shape of your data. Nothing is changed in the process.")
    if st.sidebar.button("Show another welcome", use_container_width=True):
        st.session_state.experience_message_index = (experience_message_index + 1) % len(WELCOME_MESSAGES)
        st.rerun()

# Required format message
st.sidebar.markdown(
    f"""<div style='background-color: {COLOR_STATUS_DEFAULT_BG}; border: 1px solid {COLOR_STATUS_DEFAULT_BORDER}; 
    border-radius: 8px; padding: 10px; margin-bottom: 10px; font-size: 12px; color: {COLOR_STATUS_DEFAULT_TEXT};'>
    <b>Universal Ingestion:</b><br>
    Upload Excel or CSV files from any domain.<br>
    AxiShell AI will load readable sheets, preserve columns, and build a data profile.<br><br>
    <b>Starter analytics:</b> Sales-style charts appear only when Product, Units Sold, Revenue, and Region are available.
    </div>""",
    unsafe_allow_html=True
)

# Drag-and-drop uploader for multiple Excel files
st.sidebar.caption("Maximum file size: 25 MB per file.")
uploaded_files = st.sidebar.file_uploader(
    "Upload Excel or CSV Files:",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=True,
    help="Upload one or more spreadsheets. AxiShell AI profiles arbitrary schemas and provides type-aware filters."
)

# Load and validate files with a loading spinner
loading_message = (
    "Processing and validating workbook data..."
    if st.session_state.focus_mode
    else LOADING_MESSAGES[experience_message_index]
)
with st.spinner(loading_message):
    df_all, validation_reports, lineage_df = process_data_sources(uploaded_files)

# Show data source status
if uploaded_files:
    valid_count = sum(1 for r in validation_reports if r['status'].startswith("Valid"))
    st.sidebar.markdown(
        f"<div class='status-card status-uploaded'><b>Active Dataset</b><br>Using {valid_count} valid uploaded spreadsheet(s).</div>",
        unsafe_allow_html=True
    )
    
    # Validation expander to show dynamic file validation feedback
    with st.sidebar.expander("File Validation Reports"):
        for report in validation_reports:
            st.markdown(f"**File:** `{report['file']}`")
            st.markdown(f"**Status:** {report['status']}")
            st.markdown(f"**Details:** {report['details']}")
            st.markdown("---")
else:
    demo_copy = (
        "Demo Mode Active: Using default local sample files when available. Upload Excel or CSV files to profile your own dataset."
        if st.session_state.focus_mode
        else "No file yet? That is okay. Upload an Excel or CSV file when you are ready, and AxiShell AI will build a read-only profile of it."
    )
    st.sidebar.markdown(
        f"<div class='status-card status-default'><b>Demo Mode Active</b><br>{demo_copy}</div>",
        unsafe_allow_html=True
    )

# Show prominent error messages in sidebar for incorrect file types or general validation failures
invalid_reports = [r for r in validation_reports if not r['status'].startswith("Valid")]
if invalid_reports:
    for r in invalid_reports:
        if "Invalid File Type" in r['status']:
            st.sidebar.warning(f"**{r['file']}** could not be used here. Please choose a **.xlsx**, **.xls**, or **.csv** file.")
        else:
            st.sidebar.warning(f"**{r['file']}** needs attention: {r['details']}")

# ================= SIDEBAR DATASET CONTROLS =================
# Check if data is empty after loading
# ================= MAIN HERO / HEADER =================
st.markdown("<h1>AxiShell AI</h1>", unsafe_allow_html=True)
if st.session_state.focus_mode:
    st.markdown(f"<p style='font-size: 16px; color: {COLOR_SECONDARY}; margin-bottom: 25px;'>Universal Excel analyzer with schema-aware exploration, analytics, visualization, and optional domain guidance.</p>", unsafe_allow_html=True)
else:
    st.markdown(
        f"<div class='axi-guide'><span class='axi-guide-mark'>A</span><p><b>Axi</b> · {WELCOME_MESSAGES[experience_message_index]}</p></div>",
        unsafe_allow_html=True,
    )

if df_all.empty:
    empty_data_message = (
        "No data is available. Upload a valid Excel or CSV file with at least one readable table."
        if st.session_state.focus_mode
        else "There is no readable data to explore yet. Upload a valid Excel or CSV file with at least one table, and AxiShell AI will take it from there."
    )
    st.error(empty_data_message)
    st.stop()

st.sidebar.markdown(f"<h2 style='color: {COLOR_PRIMARY}; font-weight: 700; margin-top: 15px;'>Dataset controls</h2>", unsafe_allow_html=True)
scope_options = ["All loaded sources"] + [
    f"{source} — {sheet}"
    for source, sheet in df_all[SOURCE_COLUMNS].drop_duplicates().itertuples(index=False, name=None)
]
selected_scope = st.sidebar.selectbox(
    "Dataset scope",
    options=scope_options,
    help="Analyze all loaded sources together, or select one source sheet to avoid combining unrelated tables.",
)
if selected_scope == "All loaded sources":
    df_scoped = df_all.copy()
    scoped_lineage_df = lineage_df.copy()
else:
    selected_source, selected_sheet = selected_scope.split(" — ", 1)
    df_scoped = df_all.loc[
        (df_all["Source File"] == selected_source) & (df_all["Source Sheet"] == selected_sheet)
    ].copy()
    scoped_lineage_df = lineage_df.loc[
        (lineage_df["Source"] == selected_source) & (lineage_df["Sheet"] == selected_sheet)
    ].copy()

has_starter_schema = set(STARTER_SCHEMA_COLUMNS).issubset(df_scoped.columns)
with st.sidebar.expander("Filters", expanded=False) as filter_panel:
    st.caption("Choose fields to filter. Controls adapt to the detected data type.")
    df_filtered, active_filter_columns, active_filter_details = apply_dynamic_filters(df_scoped, filter_panel)
    if filter_panel.button("Reset Filters", use_container_width=True):
        st.rerun()

with st.sidebar.expander("Preferences", expanded=False):
    st.selectbox(
        "Theme",
        options=["Dark", "Light"],
        key="theme_choice",
        help="Choose the visual theme for this session. It does not change your data or analysis.",
    )
    st.checkbox(
        "Focus Mode",
        key="focus_mode",
        help="Use concise, neutral presentation copy. This does not change data, analysis, or safety controls.",
    )
    if st.session_state.focus_mode:
        st.caption("Focus Mode is active. Analysis and data-protection behavior are unchanged.")

# Empty State Check
if df_filtered.empty:
    empty_filter_message = (
        "No data matches the current filters. Expand or reset the filter selections in the sidebar."
        if st.session_state.focus_mode
        else "Nothing matches this filter combination yet. Try widening a filter or use Reset Filters to return to the full selected scope."
    )
    st.warning(empty_filter_message)
    st.stop()

# ================= UNIVERSAL DATA PROFILE =================
profile_df = build_dataset_profile(df_filtered)
total_cells = df_filtered.shape[0] * df_filtered.shape[1]
missing_cells = int(df_filtered.isna().sum().sum())
duplicate_rows = int(df_filtered.duplicated().sum())
numeric_columns = profile_df[profile_df["Inferred Type"].isin(["numeric", "numeric-like"])]
categorical_columns = profile_df[profile_df["Inferred Type"].isin(["categorical", "boolean"])]
datetime_columns = profile_df[profile_df["Inferred Type"].isin(["datetime", "datetime-like"])]

st.markdown("<div id='overview' class='axi-section-anchor'></div>", unsafe_allow_html=True)
st.markdown("### Dataset Overview")
overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    st.metric("Rows", f"{len(df_filtered):,}")
with overview_col2:
    st.metric("Columns", f"{len(df_filtered.columns):,}")
with overview_col3:
    missing_pct = (missing_cells / total_cells * 100) if total_cells else 0
    st.metric("Missing Cells", f"{missing_cells:,}", delta=f"{missing_pct:.1f}%")
with overview_col4:
    st.metric("Duplicate Rows", f"{duplicate_rows:,}")

type_col1, type_col2, type_col3 = st.columns(3)
with type_col1:
    st.metric("Numeric Columns", f"{len(numeric_columns):,}")
with type_col2:
    st.metric("Category/Boolean Columns", f"{len(categorical_columns):,}")
with type_col3:
    st.metric("Date-Like Columns", f"{len(datetime_columns):,}")

st.markdown("### Column Profile")
st.dataframe(
    profile_df.style.format({
        "Missing %": "{:.2f}%",
        "Min": "{:,.2f}",
        "Max": "{:,.2f}",
        "Mean": "{:,.2f}"
    }, na_rep=""),
    use_container_width=True,
    hide_index=True
)

if "semantic_overrides" not in st.session_state:
    st.session_state.semantic_overrides = {}

semantic_profile = build_semantic_profile(
    df_filtered,
    profile_df,
    st.session_state.semantic_overrides,
)
suggested_domains = recommend_domain_templates(semantic_profile)
sensitive_columns = semantic_profile.loc[
    semantic_profile["Applied Role"] == "Sensitive Personal Data", "Column"
].tolist()
integrity_summary, integrity_warnings = build_integrity_summary(
    df_filtered, profile_df, scoped_lineage_df
)
analysis_context = (
    f"Scope: {selected_scope}. Active rows: {len(df_filtered):,} of {len(df_scoped):,}. "
    + ("Filters: " + "; ".join(active_filter_details) + "." if active_filter_details else "No field filters applied.")
)
quality_score, quality_rating, quality_scorecard = build_quality_scorecard(df_filtered, profile_df)
deterministic_findings = build_deterministic_findings(
    df_filtered, profile_df, semantic_profile, analysis_context
)
operational_snapshot = build_operational_snapshot(
    dataset_rows=len(df_filtered),
    dataset_columns=len(df_filtered.columns),
    source_tables=len(scoped_lineage_df),
    uploaded_files=len(uploaded_files or []),
    elapsed_seconds=time.perf_counter() - st.session_state.app_session_started_at,
    focus_mode=st.session_state.focus_mode,
)

high_findings = int((deterministic_findings["Severity"] == "High").sum()) if not deterministic_findings.empty else 0
integrity_attention = int((integrity_summary["Status"] != "Pass").sum()) if not integrity_summary.empty else 0
quality_card_class = "good" if quality_rating == "Good" else "review" if quality_rating == "Needs review" else "risk"
findings_card_class = "risk" if high_findings else "review" if len(deterministic_findings) else "good"
integrity_card_class = "review" if integrity_attention else "good"
privacy_card_class = "review" if sensitive_columns else "good"
filter_label = f"{len(active_filter_columns)} active" if active_filter_columns else "None active"
privacy_label = "Review before export" if sensitive_columns else "No sensitivity flag"

st.markdown(
    """<nav class="axi-workspace-nav" aria-label="Workspace sections">
    <a href="#overview">Overview</a>
    <a href="#insights">Insights</a>
    <a href="#ai-analysis">AI analysis</a>
    <a href="#explorer">Explore data</a>
    <a href="#analytics">Analyze</a>
    <a href="#sales-template">Sales template</a>
    </nav>""",
    unsafe_allow_html=True,
)
st.markdown(
    f"""<div class="axi-context-bar" aria-label="Active dataset context">
    <div class="axi-context-item"><span class="axi-context-label">Dataset scope</span><span class="axi-context-value">{escape(selected_scope)}</span></div>
    <div class="axi-context-item"><span class="axi-context-label">Active data</span><span class="axi-context-value">{len(df_filtered):,} of {len(df_scoped):,} rows</span></div>
    <div class="axi-context-item"><span class="axi-context-label">Filters</span><span class="axi-context-value">{filter_label}</span></div>
    <div class="axi-context-item"><span class="axi-context-label">Data protection</span><span class="axi-context-value">{privacy_label}</span></div>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown(
    f"""<div class="axi-status-grid" aria-label="Dataset health summary">
    <div class="axi-status-card axi-status-card--{quality_card_class}"><span class="axi-status-label">Data quality</span><span class="axi-status-value">{quality_score:.1f}/100</span><span class="axi-status-detail">{escape(quality_rating)}</span></div>
    <div class="axi-status-card axi-status-card--{findings_card_class}"><span class="axi-status-label">Findings</span><span class="axi-status-value">{len(deterministic_findings):,}</span><span class="axi-status-detail">{high_findings:,} high-severity</span></div>
    <div class="axi-status-card axi-status-card--{integrity_card_class}"><span class="axi-status-label">Integrity checks</span><span class="axi-status-value">{integrity_attention:,}</span><span class="axi-status-detail">items need review</span></div>
    <div class="axi-status-card axi-status-card--{privacy_card_class}"><span class="axi-status-label">Data protection</span><span class="axi-status-value">{len(sensitive_columns):,}</span><span class="axi-status-detail">sensitive fields flagged</span></div>
    </div>""",
    unsafe_allow_html=True,
)

with st.expander("Reliability, Lineage & Data Protection", expanded=True):
    st.markdown(
        "AxiShell AI does not execute spreadsheet formulas or macros, does not modify uploaded data, "
        "and does not implement persistent upload storage or analytics logging. Analyses use the active scope and filters shown in this session."
    )
    st.markdown("#### Dataset lineage")
    if scoped_lineage_df.empty:
        st.info("No lineage records are available for this dataset.")
    else:
        st.dataframe(scoped_lineage_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="Download Lineage Summary as CSV",
            data=scoped_lineage_df.to_csv(index=False).encode("utf-8"),
            file_name="axishell_ai_dataset_lineage.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("#### Integrity checks")
    st.dataframe(integrity_summary, use_container_width=True, hide_index=True)
    for integrity_warning in integrity_warnings:
        st.warning(integrity_warning)

    st.markdown("#### Privacy and export controls")
    if sensitive_columns:
        st.warning(
            "Potential sensitive personal-data fields were detected: "
            + ", ".join(sensitive_columns)
            + ". Review them before sharing or exporting results."
        )
        export_acknowledged = st.checkbox(
            "I understand that exports may contain sensitive personal data and I am authorized to export them.",
            key="sensitive_export_acknowledged",
        )
    else:
        export_acknowledged = True
        st.caption("No fields are currently classified as sensitive personal data. Review the semantic profile because detection is heuristic.")

data_exports_allowed = export_acknowledged
if not data_exports_allowed:
    st.info("Data exports are disabled until the sensitive-data acknowledgement is selected.")

st.markdown("<div id='insights' class='axi-section-anchor'></div>", unsafe_allow_html=True)
st.markdown("### Data Quality Scorecard & Deterministic Findings")
st.caption(analysis_context)
with st.expander("Quality score details"):
    st.caption("The summary cards above are calculated from the active scope and filters. This table shows the transparent scoring method.")
    st.dataframe(quality_scorecard, use_container_width=True, hide_index=True)

with st.expander("Deterministic Findings", expanded=True):
    st.markdown("These findings are rule-based calculations, not AI-generated interpretations. Review the stated limitations before acting on them.")
    st.dataframe(deterministic_findings, use_container_width=True, hide_index=True)
    st.download_button(
        label="Download Deterministic Findings as CSV",
        data=deterministic_findings.to_csv(index=False).encode("utf-8"),
        file_name="axishell_ai_deterministic_findings.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=not data_exports_allowed,
    )

with st.expander("Operational Status & Support Boundary", expanded=False):
    st.caption(f"AxiShell AI {APP_VERSION} | {APP_RELEASE}")
    st.dataframe(operational_snapshot, use_container_width=True, hide_index=True)
    st.markdown("#### Support boundary")
    for boundary in SUPPORT_BOUNDARIES:
        st.markdown(f"- {boundary}")
    st.caption("This panel is session-only observability. It is not persistent monitoring or a substitute for deployment-level logging and alerting.")

st.markdown("<div id='ai-analysis' class='axi-section-anchor'></div>", unsafe_allow_html=True)
st.markdown("### AI-Assisted Analysis")
st.caption(
    "Optional OpenAI-powered explanations use the active scope, filters, column profile, quality scorecard, and deterministic findings. "
    "Raw spreadsheet rows are not sent. AI interpretation is always distinct from computed facts."
)
try:
    configured_openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    configured_openai_key = os.getenv("OPENAI_API_KEY", "")

if "ai_conversation" not in st.session_state:
    st.session_state.ai_conversation = []

ai_context = build_ai_analysis_context(
    profile_df, semantic_profile, quality_scorecard, deterministic_findings, analysis_context
)
ai_consent = True
if sensitive_columns:
    ai_consent = st.checkbox(
        "I understand that computed summaries about this sensitive dataset will be sent to OpenAI for this request.",
        key="sensitive_ai_acknowledged",
    )

if not configured_openai_key:
    st.info("AI-assisted analysis is not configured. Set `OPENAI_API_KEY` in the app environment or Streamlit secrets, then restart the app. The key is never entered into or stored by this interface.")
elif not ai_consent:
    st.info("AI-assisted analysis is disabled until the sensitive-data acknowledgement is selected.")
else:
    ai_question = st.text_area(
        "Ask about the active filtered dataset",
        placeholder="For example: What should I investigate first, based on the quality score and deterministic findings?",
        key="ai_analysis_question",
        help="The assistant can explain the computed results and suggest a next check. It cannot access raw spreadsheet rows.",
    )
    ai_action_col1, ai_action_col2 = st.columns([2, 1])
    with ai_action_col1:
        run_ai_analysis = st.button("Generate Grounded AI Analysis", type="primary", use_container_width=True)
    with ai_action_col2:
        if st.button("Clear AI Conversation", type="secondary", use_container_width=True):
            st.session_state.ai_conversation = []
            st.rerun()

    if run_ai_analysis:
        try:
            with st.spinner("Generating a grounded explanation from the active computed context..."):
                ai_answer = request_ai_analysis(
                    configured_openai_key, ai_question, ai_context,
                    model=os.getenv("AXISHELL_OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
                )
            st.session_state.ai_conversation.append({"question": ai_question.strip(), "answer": ai_answer})
        except (ValueError, RuntimeError) as error:
            st.error(f"AI-assisted analysis could not run: {error}")
        except Exception:
            st.error("AI-assisted analysis could not be completed. Check the API key, model access, network connection, and account limits, then try again.")

    for exchange in reversed(st.session_state.ai_conversation):
        with st.expander(f"AI response: {exchange['question']}", expanded=True):
            st.markdown(exchange["answer"])
            st.caption("Generated interpretation; verify it against the computed evidence and limitations above.")

with st.expander("Semantic Profile & Domain Templates"):
    st.markdown("Review explainable field-role suggestions, override any role, and optionally use a domain template as an analysis guide. These settings do not change the uploaded data.")
    st.dataframe(semantic_profile, use_container_width=True, hide_index=True)

    semantic_col1, semantic_col2 = st.columns(2)
    with semantic_col1:
        semantic_column = st.selectbox(
            "Column to review",
            options=list(df_filtered.columns),
            key="semantic_column_to_review",
        )
    with semantic_col2:
        current_override = st.session_state.semantic_overrides.get(semantic_column)
        override_options = ["Automatic (inferred)"] + SEMANTIC_ROLE_OPTIONS
        override_index = override_options.index(current_override) if current_override in override_options else 0
        selected_role = st.selectbox(
            "Applied role",
            options=override_options,
            index=override_index,
            key=f"semantic_role_{semantic_column}",
        )

    if st.button("Apply Role Setting", key="apply_semantic_role", type="primary"):
        if selected_role == "Automatic (inferred)":
            st.session_state.semantic_overrides.pop(semantic_column, None)
        else:
            st.session_state.semantic_overrides[semantic_column] = selected_role
        st.rerun()

    if suggested_domains:
        st.caption(f"Optional template suggestions based on detected field names and roles: {', '.join(suggested_domains)}.")
    else:
        st.caption("No strong domain-template match was detected. Generic analysis remains available for this dataset.")

    selected_template = st.selectbox(
        "Optional analysis template",
        options=["No template"] + list(DOMAIN_TEMPLATE_GUIDANCE),
        key="selected_domain_template",
    )
    if selected_template != "No template":
        role_fields = semantic_profile.loc[
            semantic_profile["Applied Role"].isin(["Date", "Currency / Amount", "Quantity", "Category", "Identifier"]),
            "Column",
        ].tolist()
        st.info(DOMAIN_TEMPLATE_GUIDANCE[selected_template])
        st.caption(f"Fields available for this template: {', '.join(role_fields) if role_fields else 'No strongly matched fields yet; review role overrides above.'}")

with st.expander("Preview Loaded Data"):
    st.dataframe(df_filtered.head(100), use_container_width=True, hide_index=True)

st.markdown("<div id='explorer' class='axi-section-anchor'></div>", unsafe_allow_html=True)
with st.expander("Data Explorer & Export", expanded=True):
    st.markdown("Search, sort, choose visible columns, and export the currently filtered data.")
    explorer_search = st.text_input(
        "Search all fields",
        placeholder="Enter text to find across the filtered dataset...",
        key="universal_explorer_search",
    )
    explorer_df = df_filtered.copy()
    if explorer_search:
        search_mask = explorer_df.astype(str).apply(
            lambda column: column.str.contains(explorer_search, case=False, na=False, regex=False)
        ).any(axis=1)
        explorer_df = explorer_df[search_mask]

    explorer_col1, explorer_col2 = st.columns(2)
    with explorer_col1:
        visible_columns = st.multiselect(
            "Visible columns",
            options=list(explorer_df.columns),
            default=list(explorer_df.columns),
            key="universal_explorer_columns",
        )
    with explorer_col2:
        sort_column = st.selectbox(
            "Sort by",
            options=["No sorting"] + list(explorer_df.columns),
            key="universal_explorer_sort",
        )
        sort_ascending = st.checkbox("Ascending", value=True, key="universal_explorer_ascending")

    if sort_column != "No sorting":
        explorer_df = explorer_df.sort_values(sort_column, ascending=sort_ascending, na_position="last")

    if visible_columns:
        st.dataframe(explorer_df[visible_columns], use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one column to display the table.")

        st.download_button(
            label="Download Explorer Results as CSV",
            data=explorer_df.to_csv(index=False).encode("utf-8"),
            file_name="axishell_ai_filtered_data.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not data_exports_allowed,
    )

# ================= SCHEMA-AWARE ANALYTICS =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
st.markdown("<div id='analytics' class='axi-section-anchor'></div>", unsafe_allow_html=True)
st.markdown("### Schema-Aware Analytics")
st.markdown("Choose fields from your dataset to build a reusable summary and recommended visualization.")

inferred_types = profile_df.set_index("Column")["Inferred Type"].to_dict()
measure_options = [
    column for column, inferred_type in inferred_types.items()
    if inferred_type in ["numeric", "numeric-like"] and column not in SOURCE_COLUMNS
]
dimension_options = [
    column for column, inferred_type in inferred_types.items()
    if inferred_type in ["categorical", "boolean", "text"]
]
date_options = [
    column for column, inferred_type in inferred_types.items()
    if inferred_type in ["datetime", "datetime-like"]
]

analytics_col1, analytics_col2, analytics_col3 = st.columns(3)
with analytics_col1:
    selected_measure = st.selectbox(
        "Measure",
        options=["Row count"] + measure_options,
        help="Choose a numeric field, or count the rows in each group.",
    )
with analytics_col2:
    selected_dimension = st.selectbox(
        "Group by",
        options=["No grouping"] + dimension_options,
        help="Choose a categorical or text field to compare groups.",
    )
with analytics_col3:
    selected_date = st.selectbox(
        "Date grouping",
        options=["No date grouping"] + date_options,
        help="Choose a detected date field to create a time trend.",
    )

analytics_col4, analytics_col5 = st.columns(2)
with analytics_col4:
    selected_aggregation = st.selectbox(
        "Aggregation",
        options=["Count"] if selected_measure == "Row count" else ["Sum", "Average", "Median", "Minimum", "Maximum", "Count"],
        help="Select how the numeric measure should be summarized.",
    )
with analytics_col5:
    selected_frequency = st.selectbox(
        "Time granularity",
        options=["Day", "Month", "Quarter", "Year"],
        disabled=selected_date == "No date grouping",
    )

analytics_result, analytics_groups, analytics_value_label = build_schema_aggregation(
    df_filtered,
    selected_measure,
    selected_dimension,
    selected_date,
    selected_frequency,
    selected_aggregation,
)

if analytics_result.empty:
    st.info("The selected fields do not contain enough valid values for this analysis.")
else:
    if selected_date != "No date grouping":
        recommendation = "Recommended visualization: line chart, because a date field is being used for the grouping."
    elif selected_dimension != "No grouping":
        recommendation = "Recommended visualization: bar chart, because the analysis compares categories."
    elif selected_measure != "Row count":
        recommendation = "Recommended visualization: histogram, because no grouping was selected and the numeric distribution is most useful."
    else:
        recommendation = "Recommended visualization: a KPI card, because this analysis is a single row count."

    st.caption(recommendation)
    analytics_table_col, analytics_chart_col = st.columns([2, 3])
    with analytics_table_col:
        st.dataframe(
            analytics_result,
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            label="Download Analysis Results as CSV",
            data=analytics_result.to_csv(index=False).encode("utf-8"),
            file_name="axishell_ai_analysis_results.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not data_exports_allowed,
        )
    with analytics_chart_col:
        if selected_date != "No date grouping":
            line_color = selected_dimension if selected_dimension != "No grouping" else None
            fig_generic = px.line(
                analytics_result,
                x="Analysis Period",
                y=analytics_value_label,
                color=line_color,
                markers=True,
                color_discrete_sequence=CHART_PALETTE,
            )
            fig_generic.update_layout(xaxis_title=selected_date)
            apply_chart_theme(fig_generic)
            st.plotly_chart(fig_generic, use_container_width=True)
        elif selected_dimension != "No grouping":
            fig_generic = px.bar(
                analytics_result,
                x=selected_dimension,
                y=analytics_value_label,
                color_discrete_sequence=[COLOR_ACCENT],
            )
            apply_chart_theme(fig_generic)
            st.plotly_chart(fig_generic, use_container_width=True)
        elif selected_measure != "Row count":
            histogram_values = pd.to_numeric(df_filtered[selected_measure], errors="coerce").dropna()
            fig_generic = px.histogram(
                histogram_values,
                nbins=min(30, max(5, int(histogram_values.nunique()))),
                color_discrete_sequence=[COLOR_ACCENT],
                labels={"value": selected_measure, "count": "Rows"},
            )
            apply_chart_theme(fig_generic)
            st.plotly_chart(fig_generic, use_container_width=True)
        else:
            st.metric("Filtered rows", f"{int(analytics_result.iloc[0][analytics_value_label]):,}")

if not has_starter_schema:
    st.info("Starter sales analytics are hidden because this dataset does not contain Product, Units Sold, Revenue, and Region.")

    st.markdown("### Download Profile And Data")
    generic_dl1, generic_dl2 = st.columns(2)
    with generic_dl1:
        st.download_button(
            label="Download Loaded Data as CSV",
            data=df_filtered.to_csv(index=False).encode('utf-8'),
            file_name="axishell_ai_loaded_data.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
            disabled=not data_exports_allowed,
        )
    with generic_dl2:
        st.download_button(
            label="Download Column Profile as CSV",
            data=profile_df.to_csv(index=False).encode('utf-8'),
            file_name="axishell_ai_column_profile.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown(
        f"<p style='text-align: center; color: {COLOR_SECONDARY}; font-size: 12px; margin-top: 50px;'>AxiShell AI {APP_RELEASE} | Powered by Streamlit & Plotly</p>",
        unsafe_allow_html=True
    )
    st.stop()

# ================= KPI METRIC CARDS =================
st.markdown("<div id='sales-template' class='axi-section-anchor'></div>", unsafe_allow_html=True)
# Calculate KPIs
total_revenue = df_filtered['Revenue'].sum()
total_units = df_filtered['Units Sold'].sum()
avg_unit_price = total_revenue / total_units if total_units > 0 else 0

# Calculate growth for comparison dynamically from the earliest to the latest selected periods
sorted_filtered_periods = sorted(df_filtered['Source File'].unique(), key=get_period_sort_key)
if len(sorted_filtered_periods) >= 2:
    first_period = sorted_filtered_periods[0]
    last_period = sorted_filtered_periods[-1]
    
    first_rev = df_filtered[df_filtered['Source File'] == first_period]['Revenue'].sum()
    last_rev = df_filtered[df_filtered['Source File'] == last_period]['Revenue'].sum()
    
    if first_rev > 0:
        overall_growth_pct = ((last_rev - first_rev) / first_rev) * 100
        delta_label = f"+{overall_growth_pct:.1f}% ({first_period} to {last_period})" if overall_growth_pct >= 0 else f"{overall_growth_pct:.1f}% ({first_period} to {last_period})"
    else:
        delta_label = None
else:
    delta_label = None

# Identify best performers
best_product_row = df_filtered.groupby('Product')['Revenue'].sum().idxmax()
best_product_rev = df_filtered.groupby('Product')['Revenue'].sum().max()
best_region_row = df_filtered.groupby('Region')['Revenue'].sum().idxmax()
best_region_rev = df_filtered.groupby('Region')['Revenue'].sum().max()

# Display KPIs in columns (4 beautifully styled summary cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value=f"${total_revenue:,.2f}",
        delta=delta_label,
        help="Aggregated revenue from selected products, regions, and periods."
    )

with col2:
    st.metric(
        label="Total Units Sold",
        value=f"{total_units:,.0f}",
        help="Aggregated number of units sold across selections."
    )

with col3:
    st.metric(
        label="Average Selling Price (ASP)",
        value=f"${avg_unit_price:,.2f}",
        help="Calculated as Total Revenue divided by Total Units Sold."
    )

with col4:
    st.metric(
        label="Top Performer (Product)",
        value=best_product_row,
        delta=f"${best_product_rev:,.0f} Total",
        delta_color="normal",
        help="The product generating the highest total revenue in the filtered dataset."
    )


# ================= VISUALIZATIONS SECTION =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)

# ROW 1: Trend Line (Dual-Axis) & Region Donut
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    st.markdown("### Revenue & Volume Trend")
    # Aggregate by source file
    trend_data = df_filtered.groupby('Source File').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    # Sort chronologically using our numeric sorting key helper
    trend_data['sort_key'] = trend_data['Source File'].apply(get_period_sort_key)
    if trend_data['sort_key'].apply(lambda x: isinstance(x, int)).all():
        trend_data = trend_data.sort_values('sort_key')
    else:
        trend_data['sort_key_str'] = trend_data['sort_key'].astype(str)
        trend_data = trend_data.sort_values('sort_key_str')
        if 'sort_key_str' in trend_data.columns:
            trend_data = trend_data.drop(columns='sort_key_str')
    trend_data = trend_data.drop(columns='sort_key')
    
    if len(trend_data) > 1:
        # Create professional dual-axis chart matching standard reports
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary axis: Revenue (Solid line)
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['Source File'],
                y=trend_data['Revenue'],
                name="Revenue ($)",
                line=dict(color=COLOR_PRIMARY, width=3),
                marker=dict(symbol="circle", size=8, color=COLOR_PRIMARY),
                hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Secondary axis: Units Sold (Dashed line)
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['Source File'],
                y=trend_data['Units Sold'],
                name="Units Sold",
                line=dict(color=COLOR_ACCENT, width=2.5, dash="dash"),
                marker=dict(symbol="square", size=8, color=COLOR_ACCENT),
                hovertemplate="<b>%{x}</b><br>Units Sold: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Style layout
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(248, 250, 252, 0.8)" if not st.session_state.dark_mode else "rgba(15, 23, 42, 0.8)",
                bordercolor=COLOR_BORDER,
                borderwidth=1,
                font=dict(color=PLOTLY_TEXT_COLOR)
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            font=dict(color=PLOTLY_TEXT_COLOR)
        )
        
        fig_trend.update_xaxes(showgrid=False, linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR))
        fig_trend.update_yaxes(
            title_text="<b>Revenue ($)</b>",
            title_font=dict(size=11, color=COLOR_PRIMARY),
            gridcolor=PLOTLY_GRID_COLOR,
            tickformat="$~s",
            secondary_y=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(color=PLOTLY_TEXT_COLOR)
        )
        fig_trend.update_yaxes(
            title_text="<b>Units Sold</b>",
            title_font=dict(size=11, color=COLOR_ACCENT),
            secondary_y=True,
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(color=PLOTLY_TEXT_COLOR)
        )
        apply_chart_theme(fig_trend, height=320)
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        # Single period selected - display bar instead
        fig_single = px.bar(
            trend_data,
            x='Source File',
            y='Revenue',
            text_auto='$,.2f',
            title="Selected Source Revenue",
            color_discrete_sequence=[COLOR_PRIMARY]
        )
        fig_single.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(color=PLOTLY_TEXT_COLOR),
            xaxis=dict(linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR)),
            yaxis=dict(linecolor=COLOR_BORDER, gridcolor=PLOTLY_GRID_COLOR, tickformat="$~s", tickfont=dict(color=PLOTLY_TEXT_COLOR))
        )
        apply_chart_theme(fig_single, height=320)
        st.plotly_chart(fig_single, use_container_width=True)

with chart_col2:
    st.markdown("### Group Contribution")
    contribution_data = (
        df_filtered.groupby('Region', as_index=False)['Revenue']
        .sum()
        .sort_values('Revenue', ascending=True)
    )
    contribution_total = contribution_data['Revenue'].sum()
    contribution_data['Contribution %'] = (
        contribution_data['Revenue'] / contribution_total * 100 if contribution_total else 0
    )
    fig_contribution = px.bar(
        contribution_data,
        x='Revenue',
        y='Region',
        orientation='h',
        text='Contribution %',
        color_discrete_sequence=[COLOR_ACCENT],
        hover_data={'Revenue': ':$,.2f', 'Contribution %': ':.1f'},
    )
    fig_contribution.update_traces(texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
    fig_contribution.update_layout(
        margin=dict(l=10, r=55, t=20, b=20),
        xaxis_title='Revenue ($)',
        yaxis_title=None,
        showlegend=False,
    )
    fig_contribution.update_xaxes(tickformat='$~s')
    apply_chart_theme(fig_contribution, height=340)
    st.plotly_chart(fig_contribution, use_container_width=True)


# ROW 2: Product Breakdown Grouped Bar & Performance Table
chart_col3, chart_col4 = st.columns([3, 2])

with chart_col3:
    st.markdown("### Product Revenue by Source")
    # Group by Product and Source File
    prod_period_data = df_filtered.groupby(['Product', 'Source File'])['Revenue'].sum().reset_index()
    
    # Sort sources chronologically when source names contain numbers
    prod_period_data['sort_key'] = prod_period_data['Source File'].apply(get_period_sort_key)
    if prod_period_data['sort_key'].apply(lambda x: isinstance(x, int)).all():
        prod_period_data = prod_period_data.sort_values(['Product', 'sort_key'])
    else:
        prod_period_data['sort_key_str'] = prod_period_data['sort_key'].astype(str)
        prod_period_data = prod_period_data.sort_values(['Product', 'sort_key_str'])
        if 'sort_key_str' in prod_period_data.columns:
            prod_period_data = prod_period_data.drop(columns='sort_key_str')
    prod_period_data = prod_period_data.drop(columns='sort_key')
    
    fig_prod_bar = px.bar(
        prod_period_data,
        x="Product",
        y="Revenue",
        color="Source File",
        barmode="group",
        color_discrete_sequence=CHART_PALETTE
    )
    
    fig_prod_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=PLOTLY_TEXT_COLOR)),
        xaxis_title=None,
        yaxis_title="Revenue ($)",
        yaxis=dict(gridcolor=PLOTLY_GRID_COLOR, tickformat="$~s", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        xaxis=dict(linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR)),
        font=dict(color=PLOTLY_TEXT_COLOR)
    )
    apply_chart_theme(fig_prod_bar, height=350)
    st.plotly_chart(fig_prod_bar, use_container_width=True)

with chart_col4:
    st.markdown("### Performance Matrix")
    # Bubble/Scatter plot of units sold vs revenue by region/product
    scatter_data = df_filtered.groupby(['Product', 'Region']).agg({
        'Revenue': 'sum',
        'Units Sold': 'sum',
        'Avg Price': 'mean'
    }).reset_index()
    
    fig_scatter = px.scatter(
        scatter_data,
        x="Units Sold",
        y="Revenue",
        size="Avg Price",
        color="Region",
        hover_name="Product",
        color_discrete_sequence=CHART_PALETTE,
        size_max=30
    )
    
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=30, b=60),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=PLOTLY_TEXT_COLOR, size=11),
            title=None
        ),
        xaxis=dict(gridcolor=PLOTLY_GRID_COLOR, title="Units Sold", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        yaxis=dict(gridcolor=PLOTLY_GRID_COLOR, title="Revenue ($)", tickformat="$~s", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        font=dict(color=PLOTLY_TEXT_COLOR)
    )
    apply_chart_theme(fig_scatter, height=350)
    
    st.plotly_chart(fig_scatter, use_container_width=True)


# ================= ANALYTICAL PERFORMANCE TABLE =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
st.markdown("### Consolidated Product Performance Summary")

# Group and calculate aggregated analytics
product_summary = df_filtered.groupby('Product').agg(
    total_units=('Units Sold', 'sum'),
    total_rev=('Revenue', 'sum')
).reset_index()

product_summary['Average Price per Unit'] = product_summary['total_rev'] / product_summary['total_units'].replace(0, 1)
total_filtered_rev = product_summary['total_rev'].sum()
product_summary['Revenue Contribution (%)'] = (product_summary['total_rev'] / total_filtered_rev) * 100

# Rename columns for presentation
product_summary.rename(columns={
    'Product': 'Product Name',
    'total_units': 'Units Sold',
    'total_rev': 'Total Revenue ($)'
}, inplace=True)

# Sort by Revenue descending
product_summary = product_summary.sort_values('Total Revenue ($)', ascending=False).reset_index(drop=True)

# Display a formatted copy to avoid pandas Styler serialization failures in hosted environments.
product_summary_display = product_summary.copy()
product_summary_display['Units Sold'] = product_summary_display['Units Sold'].map(lambda value: f'{value:,.0f}')
product_summary_display['Total Revenue ($)'] = product_summary_display['Total Revenue ($)'].map(lambda value: f'${value:,.2f}')
product_summary_display['Average Price per Unit'] = product_summary_display['Average Price per Unit'].map(lambda value: f'${value:,.2f}')
product_summary_display['Revenue Contribution (%)'] = product_summary_display['Revenue Contribution (%)'].map(lambda value: f'{value:.2f}%')
st.dataframe(product_summary_display, use_container_width=True, hide_index=True)


# ================= DOWNLOAD REPORT BUTTON =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
st.markdown("### Download Your Report")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv_full = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Data as CSV",
        data=csv_full,
        file_name="axishell_ai_full_data.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
        disabled=not data_exports_allowed,
    )
with col_dl2:
    summary_csv = product_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Product Summary as CSV",
        data=summary_csv,
        file_name="axishell_ai_product_summary.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=not data_exports_allowed,
    )

# Footer credits
st.markdown(
    f"<p style='text-align: center; color: {COLOR_SECONDARY}; font-size: 12px; margin-top: 50px;'>AxiShell AI {APP_RELEASE} | Powered by Streamlit & Plotly</p>",
    unsafe_allow_html=True
)
