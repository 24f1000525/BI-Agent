import streamlit as st
import pandas as pd
import os
import tempfile
import numpy as np
from typing import Dict
from langchain_utils import LangChainChat
from dashboard_generator import DashboardGenerator
from dashboard_orchestrator import DashboardOrchestrator, InteractiveDashboard
from dynamic_chart_generator import DynamicChartGenerator
from config import APP_TITLE, APP_DESCRIPTION, GOOGLE_API_KEY

# Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS — dark theme
st.markdown("""
<style>
/* ── Force dark mode ── */
:root {
    color-scheme: dark !important;
}

/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e2e8f0;
}
.main {
    padding-top: 0;
    background: #0f172a !important;
    color: #e2e8f0 !important;
}

/* ── Global text ── */
p, span, li, td, th, label, div,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stText"],
.stMarkdown, .stMarkdown p {
    color: #cbd5e1;
}
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5 {
    color: #f1f5f9 !important;
}
a { color: #818cf8; }
code {
    color: #e2e8f0;
    background: #1e293b;
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebarCollapsedControl"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: #1e293b !important;
    background-color: #1e293b !important;
}
section[data-testid="stSidebar"] {
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * {
    color: #cbd5e1;
}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
    color: #64748b !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
section[data-testid="stSidebar"] hr { border-color: #334155; }

/* ── Chat bubbles ── */
[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 16px 20px;
    border: 1px solid #334155;
    background: #1e293b !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    margin-bottom: 0.5rem;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] div {
    color: #e2e8f0 !important;
    background: transparent !important;
}
[data-testid="stChatMessage"][aria-label="user"] {
    border-left: 3px solid #818cf8;
    background: #1a2236 !important;
}
[data-testid="stChatMessage"][aria-label="assistant"] {
    border-left: 3px solid #34d399;
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    border-color: #334155 !important;
}

/* ── Header ── */
.app-header { margin-bottom: 1.5rem; }
.app-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f1f5f9 !important;
    margin: 0 0 0.25rem 0;
    letter-spacing: -0.02em;
}
.app-header p {
    font-size: 0.95rem;
    color: #94a3b8 !important;
    margin: 0;
}

/* ── Cards / KPI ── */
.kpi-grid { display: flex; gap: 0.75rem; margin-bottom: 1.25rem; }
.kpi-card {
    flex: 1;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.15rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}
.kpi-card .kpi-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8 !important;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.kpi-card .kpi-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9 !important;
}
.kpi-card .kpi-sub {
    font-size: 0.72rem;
    color: #64748b !important;
    margin-top: 0.15rem;
}

/* ── Chart wrapper ── */
.chart-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.15rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}
.chart-card .chart-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #f1f5f9 !important;
    margin-bottom: 0.15rem;
}
.chart-card .chart-sub {
    font-size: 0.75rem;
    color: #94a3b8 !important;
    margin-bottom: 0.75rem;
}

/* ── Chips / Tags ── */
.chip {
    display: inline-block;
    margin: 0.2rem 0.3rem 0.2rem 0;
    padding: 0.22rem 0.62rem;
    border-radius: 999px;
    background: #334155;
    color: #cbd5e1 !important;
    font-size: 0.78rem;
    font-weight: 500;
    border: 1px solid #475569;
}

/* ── Section title ── */
.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 1.25rem 0 0.6rem 0;
}

/* ── Landing page ── */
.landing-hero { text-align: center; padding: 3rem 1rem 2rem; }
.landing-hero h1 {
    font-size: 2.25rem;
    font-weight: 700;
    color: #f1f5f9 !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
.landing-hero p {
    font-size: 1.05rem;
    color: #94a3b8 !important;
    max-width: 540px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}
.feature-grid { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.feature-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.5rem;
    width: 220px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
    transition: box-shadow 0.2s, border-color 0.2s;
}
.feature-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    border-color: #818cf8;
}
.feature-icon { margin-bottom: 0.6rem; display: flex; justify-content: center; }
.feature-card h3 { font-size: 0.92rem; font-weight: 600; color: #f1f5f9 !important; margin: 0 0 0.3rem; }
.feature-card p { font-size: 0.78rem; color: #94a3b8 !important; margin: 0; line-height: 1.45; }

/* ── Sidebar file badge ── */
.file-badge {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.3);
    border-radius: 8px; padding: 0.55rem 0.75rem;
    margin-bottom: 0.75rem;
}
.file-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: #34d399; }
.file-badge span { font-size: 0.82rem; color: #6ee7b7 !important; font-weight: 500; }

/* ── Streamlit overrides ── */
.stFileUploadDropzone {
    border-radius: 12px;
    border: 2px dashed #475569 !important;
    background: #1e293b !important;
}
.stFileUploadDropzone p, .stFileUploadDropzone span,
.stFileUploadDropzone small, .stFileUploadDropzone label {
    color: #94a3b8 !important;
}
/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #cbd5e1 !important;
    border-color: #475569 !important;
    background: #1e293b !important;
}
.stButton > button:hover {
    border-color: #818cf8 !important;
    color: #818cf8 !important;
    background: #1a2236 !important;
}
.stButton > button[kind="primary"],
button[kind="primary"] {
    background: #6366f1 !important;
    color: #ffffff !important;
    border-color: #6366f1 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #818cf8 !important;
}
/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 2px solid #334155; }
.stTabs [data-baseweb="tab"] {
    border-radius: 0;
    font-weight: 500;
    padding: 0.65rem 1.25rem;
    color: #94a3b8 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #818cf8 !important;
    border-bottom: 2px solid #818cf8;
    background: transparent !important;
}
/* Metrics */
[data-testid="stMetric"] {
    background: #1e293b !important;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
[data-testid="stMetricLabel"] { font-size: 0.75rem; color: #94a3b8 !important; }
[data-testid="stMetricValue"] { font-size: 1.4rem; font-weight: 700; color: #f1f5f9 !important; }
[data-testid="stMetricDelta"] { color: #34d399 !important; }
/* Expanders */
[data-testid="stExpander"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #e2e8f0 !important;
    font-weight: 500;
}
/* Info / Warning / Error boxes */
[data-testid="stAlert"] {
    background: rgba(129, 140, 248, 0.08) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(129, 140, 248, 0.25) !important;
    border-radius: 8px;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #e2e8f0 !important;
}
.stCaption, [data-testid="stCaption"] {
    color: #64748b !important;
}
/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 8px;
}
/* Spinner */
.stSpinner > div { color: #818cf8 !important; }
.stSpinner > div > span { color: #94a3b8 !important; }
/* Select / Multiselect */
[data-baseweb="select"] {
    border-radius: 8px !important;
}
[data-baseweb="select"] > div {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #475569 !important;
}
</style>
""", unsafe_allow_html=True)

# Session State Management
if 'chat_engine' not in st.session_state:
    st.session_state.chat_engine = None

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None

if 'generated_dashboard' not in st.session_state:
    st.session_state.generated_dashboard = None


def initialize_chat_engine():
    """Initialize the LangChain chat engine."""
    if not GOOGLE_API_KEY:
        st.error("Google API Key not found. Please set GOOGLE_API_KEY in your .env file")
        return False
    
    try:
        st.session_state.chat_engine = LangChainChat(api_key=GOOGLE_API_KEY)
        return True
    except Exception as e:
        st.error(f"Error initializing chat engine: {str(e)}")
        return False


def load_csv_data(uploaded_file):
    """Load CSV data from uploaded file."""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        # Load data using chat engine
        st.session_state.chat_engine.load_dataset(tmp_path)
        st.session_state.data_loaded = True
        st.session_state.uploaded_filename = uploaded_file.name
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return True
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return False


def display_sample_data():
    """Display sample data from the loaded CSV."""
    if st.session_state.data_loaded and st.session_state.chat_engine:
        with st.expander("Preview data", expanded=False):
            sample_df = st.session_state.chat_engine.get_sample_data(rows=10)
            if sample_df is not None:
                st.dataframe(sample_df, use_container_width=True)


def display_initial_insights():
    """Display a colorful Power BI-style starter dashboard from uploaded data."""
    if not (st.session_state.data_loaded and st.session_state.chat_engine):
        return

    df = st.session_state.chat_engine.csv_analyzer.df
    if df is None or df.empty:
        st.warning("No rows available to visualize.")
        return

    with st.expander("Dataset Overview", expanded=True):
        total_rows = len(df)
        total_columns = len(df.columns)
        missing_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        completeness = (1 - (missing_cells / max(total_rows * max(total_columns, 1), 1))) * 100

        st.markdown(
            '<div class="kpi-grid">'
            f'  <div class="kpi-card"><div class="kpi-label">Rows</div><div class="kpi-value">{total_rows:,}</div></div>'
            f'  <div class="kpi-card"><div class="kpi-label">Columns</div><div class="kpi-value">{total_columns}</div></div>'
            f'  <div class="kpi-card"><div class="kpi-label">Missing</div><div class="kpi-value">{missing_cells:,}</div></div>'
            f'  <div class="kpi-card"><div class="kpi-label">Quality</div><div class="kpi-value">{completeness:.0f}%</div>'
            f'    <div class="kpi-sub">{duplicate_rows:,} duplicates</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )

        non_null_score = (
            df.notna().sum() / max(total_rows, 1)
        ).sort_values(ascending=False)

        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        if not numeric_cols:
            numeric_cols = [
                col for col in df.columns
                if pd.to_numeric(df[col], errors="coerce").notna().mean() > 0.7
            ]

        categorical_cols = [
            col for col in df.columns
            if col not in numeric_cols and df[col].nunique(dropna=True) > 1
        ]

        ranked_cols = list(non_null_score.index)
        selected_columns = []
        for col in ranked_cols:
            if col in numeric_cols or col in categorical_cols:
                selected_columns.append(col)
            if len(selected_columns) >= 5:
                break

        if not selected_columns:
            selected_columns = list(df.columns[:5])

        st.markdown('<div class="section-title">Key Columns</div>', unsafe_allow_html=True)
        chips = "".join([f'<span class="chip">{col}</span>' for col in selected_columns])
        st.markdown(chips, unsafe_allow_html=True)

        main_num = next((c for c in selected_columns if c in numeric_cols), None)
        second_num = next((c for c in selected_columns if c in numeric_cols and c != main_num), None)
        main_cat = next((c for c in selected_columns if c in categorical_cols), None)

        date_like_col = None
        for col in selected_columns + list(df.columns):
            lowered = str(col).lower()
            if "date" in lowered or "year" in lowered or "month" in lowered:
                date_like_col = col
                break

        if date_like_col and main_num:
            trend_df = df[[date_like_col, main_num]].copy()
            trend_df[main_num] = pd.to_numeric(trend_df[main_num], errors="coerce")

            if "year" in str(date_like_col).lower():
                extracted_year = trend_df[date_like_col].astype(str).str.extract(
                    r"(19\d{2}|20\d{2}|21\d{2})", expand=False
                )
                trend_df[date_like_col] = pd.to_numeric(extracted_year, errors="coerce")
            else:
                trend_df[date_like_col] = pd.to_datetime(
                    trend_df[date_like_col],
                    errors="coerce",
                    infer_datetime_format=True
                )

            trend_df = trend_df.dropna()
            if not trend_df.empty:
                trend_grouped = (
                    trend_df.groupby(date_like_col, as_index=False)[main_num]
                    .mean()
                    .sort_values(date_like_col)
                )

                st.markdown(f"""
                <div class="chart-card">
                    <div class="chart-title">Time Series Trend</div>
                    <div class="chart-sub">Average {main_num} over {date_like_col}</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(                    trend_grouped.set_index(date_like_col)[main_num],
                    use_container_width=True,
                    color="#818cf8"
                )
        viz_left, viz_right = st.columns(2, gap="medium")

        with viz_left:
            if main_num:
                num_series = pd.to_numeric(df[main_num], errors="coerce").dropna()
                if not num_series.empty:
                    st.markdown(f"""
                    <div class="chart-card">
                        <div class="chart-title">Value Distribution</div>
                        <div class="chart-sub">Frequency histogram for {main_num}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    bins = min(max(int(np.sqrt(len(num_series))), 8), 28)
                    hist = pd.cut(num_series, bins=bins).value_counts().sort_index()
                    hist_df = pd.DataFrame({"range": hist.index.astype(str), "count": hist.values})
                    st.bar_chart(
                        hist_df.set_index("range")["count"],
                        use_container_width=True,
                        color="#34d399"
                    )
                else:
                    st.info("Not enough numeric values for distribution chart.")
            else:
                st.info("No numeric column available for distribution chart.")

        with viz_right:
            if main_cat:
                st.markdown(f"""
                <div class="chart-card">
                    <div class="chart-title">Category Composition</div>
                    <div class="chart-sub">Top 10 categories in {main_cat}</div>
                </div>
                """, unsafe_allow_html=True)
                top_counts = df[main_cat].fillna("Unknown").astype(str).value_counts().head(10)
                cat_df = pd.DataFrame({"Category": top_counts.index, "Count": top_counts.values})
                st.bar_chart(
                    cat_df.set_index("Category")["Count"],
                    use_container_width=True,
                    color="#fbbf24"
                )
            else:
                st.info("No categorical column available for category mix.")

        comp_left, comp_right = st.columns(2, gap="medium")

        with comp_left:
            st.markdown("""
            <div class="chart-card">
                <div class="chart-title">Data Quality</div>
                <div class="chart-sub">Missing values per column</div>
            </div>
            """, unsafe_allow_html=True)
            miss = df[selected_columns].isna().sum().sort_values(ascending=False)
            miss_df = pd.DataFrame({"Column": miss.index, "Missing": miss.values})
            st.bar_chart(
                miss_df.set_index("Column")["Missing"],
                use_container_width=True,
                color="#f87171"
            )

        with comp_right:
            if main_num and second_num:
                st.markdown(f"""
                <div class="chart-card">
                    <div class="chart-title">Correlation</div>
                    <div class="chart-sub">{main_num} vs {second_num}</div>
                </div>
                """, unsafe_allow_html=True)
                rel_df = df[[main_num, second_num]].copy()
                rel_df[main_num] = pd.to_numeric(rel_df[main_num], errors="coerce")
                rel_df[second_num] = pd.to_numeric(rel_df[second_num], errors="coerce")
                rel_df = rel_df.dropna().head(1200)
                if not rel_df.empty:
                    st.scatter_chart(
                        rel_df,
                        x=main_num,
                        y=second_num,
                        use_container_width=True,
                        color="#a78bfa"

                    )
                else:
                    st.info("Not enough valid rows for relationship chart.")
            else:
                st.info("Need at least two numeric columns for correlation analysis.")


def _render_chart(spec):
    """Render a single chart based on its specification"""
    from dashboard_generator import ChartSpec
    
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-title">{spec.title}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if spec.data.empty:
        st.info("No data available for this visualization")
        return
    
    try:
        if spec.chart_type == 'line':
            if spec.groupby_column and spec.groupby_column in spec.data.columns:
                # Multi-line chart
                pivot_data = spec.data.pivot(index=spec.x_column, columns=spec.groupby_column, values=spec.y_column)
                st.line_chart(pivot_data, use_container_width=True)
            else:
                st.line_chart(spec.data.set_index(spec.x_column)[spec.y_column], use_container_width=True)
        
        elif spec.chart_type == 'bar':
            if spec.groupby_column and spec.groupby_column in spec.data.columns:
                # Grouped bar chart
                pivot_data = spec.data.pivot(index=spec.x_column, columns=spec.groupby_column, values=spec.y_column)
                st.bar_chart(pivot_data, use_container_width=True)
            else:
                st.bar_chart(spec.data.set_index(spec.x_column)[spec.y_column], use_container_width=True)
        
        elif spec.chart_type == 'scatter':
            st.scatter_chart(
                spec.data,
                x=spec.x_column,
                y=spec.y_column,
                color=spec.groupby_column if spec.groupby_column else None,
                use_container_width=True
            )
        
        elif spec.chart_type == 'pie':
            # Streamlit doesn't have native pie chart, use bar as alternative
            st.bar_chart(spec.data.set_index(spec.x_column)[spec.y_column], use_container_width=True)
            st.caption(f"Showing as bar chart — {spec.aggregation} of {spec.y_column} by {spec.x_column}")
        
        # Show data table option
        with st.expander(f"View Data ({len(spec.data)} rows)"):
            st.dataframe(spec.data, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")


def _render_dynamic_chart(chart_spec: Dict):
    """Render a chart from DynamicChartGenerator"""
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-title">{chart_spec['title']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    data = chart_spec.get('data')
    if data is None or data.empty:
        st.info("No data available for this visualization")
        return
    
    try:
        chart_type = chart_spec.get('type', 'bar')
        x_col = chart_spec.get('x')
        y_col = chart_spec.get('y')
        group_col = chart_spec.get('groupby')
        
        if not x_col or not y_col:
            st.warning("Missing chart configuration")
            return
        
        if x_col not in data.columns or y_col not in data.columns:
            st.warning(f"Chart columns not found in data")
            return
        
        if chart_type == 'line':
            if group_col and group_col in data.columns:
                pivot = data.pivot_table(index=x_col, columns=group_col, values=y_col, aggfunc='sum')
                st.line_chart(pivot, use_container_width=True)
            else:
                st.line_chart(data.set_index(x_col)[y_col], use_container_width=True)
        elif chart_type == 'scatter':
            st.scatter_chart(
                data, x=x_col, y=y_col,
                color=group_col if group_col and group_col in data.columns else None,
                use_container_width=True
            )
        elif chart_type == 'area':
            if group_col and group_col in data.columns:
                pivot = data.pivot_table(index=x_col, columns=group_col, values=y_col, aggfunc='sum')
                st.area_chart(pivot, use_container_width=True)
            else:
                st.area_chart(data.set_index(x_col)[y_col], use_container_width=True)
        else:  # bar (default)
            if group_col and group_col in data.columns:
                pivot = data.pivot_table(index=x_col, columns=group_col, values=y_col, aggfunc='sum')
                st.bar_chart(pivot, use_container_width=True)
            else:
                st.bar_chart(data.set_index(x_col)[y_col], use_container_width=True)
        
        # Show data table option
        with st.expander(f"View Data ({len(data)} rows)"):
            st.dataframe(data, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")


def _render_interactive_dashboard(dashboard: InteractiveDashboard):
    """Render a cohesive, interactive dashboard with multiple charts and filters"""
    
    # Dashboard header
    st.markdown(f"""
    <div class="chart-card" style="border-left: 4px solid #818cf8;">
        <div class="chart-title" style="font-size: 1.15rem;">{dashboard.title}</div>
        <div class="chart-sub">{dashboard.description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive Filters Section
    if dashboard.filters:
        st.markdown("### Interactive Filters")
        filter_cols = st.columns(len(dashboard.filters))
        active_filters = {}
        
        for col, filter_spec in zip(filter_cols, dashboard.filters):
            with col:
                if filter_spec.type == 'multiselect':
                    selected = st.multiselect(
                        filter_spec.label,
                        options=filter_spec.values,
                        default=filter_spec.values[:min(3, len(filter_spec.values))],
                        key=f"filter_{filter_spec.column}"
                    )
                    active_filters[filter_spec.column] = selected
                elif filter_spec.type == 'dropdown':
                    selected = st.selectbox(
                        filter_spec.label,
                        options=filter_spec.values,
                        key=f"filter_{filter_spec.column}"
                    )
                    active_filters[filter_spec.column] = [selected]
        
        st.markdown("---")
    
    # KPI Cards Section
    if dashboard.cards:
        st.markdown("### Key Metrics")
        card_cols = st.columns(min(4, len(dashboard.cards)))
        
        for col, card in zip(card_cols, dashboard.cards):
            with col:
                st.metric(
                    label=card.metric_name,
                    value=card.value,
                    delta=card.trend,
                    help=card.description
                )
        
        st.markdown("---")
    
    # Charts Section with Layout
    if dashboard.charts:
        st.markdown("### Visualizations")
        
        layout = dashboard.layout.get('structure', 'grid')
        
        if layout == 'single':
            _render_chart(dashboard.charts[0])
        
        elif layout == 'two_cols':
            col1, col2 = st.columns(2, gap='large')
            with col1:
                _render_chart(dashboard.charts[0])
            with col2:
                if len(dashboard.charts) > 1:
                    _render_chart(dashboard.charts[1])
        
        elif layout == 'mixed':
            # First row: full width
            _render_chart(dashboard.charts[0])
            # Second row: two columns
            col1, col2 = st.columns(2, gap='large')
            with col1:
                if len(dashboard.charts) > 1:
                    _render_chart(dashboard.charts[1])
            with col2:
                if len(dashboard.charts) > 2:
                    _render_chart(dashboard.charts[2])
        
        else:  # grid
            for i in range(0, len(dashboard.charts), 2):
                col1, col2 = st.columns(2, gap='large')
                with col1:
                    _render_chart(dashboard.charts[i])
                with col2:
                    if i + 1 < len(dashboard.charts):
                        _render_chart(dashboard.charts[i + 1])
    
    # Insights Section
    if dashboard.suggested_insights:
        st.markdown("### Key Insights")
        for insight in dashboard.suggested_insights:
            st.info(f"{insight}")

    st.markdown("---")
    st.caption("Tip — Refine your question in the chat to explore different aspects of your data")

def main():
    # Header
    st.markdown(
        '<div class="app-header">'
        '<h1>DataLens AI</h1>'
        f'<p>{APP_DESCRIPTION}</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Upload Data")
        uploaded_file = st.file_uploader(
            "Drop a CSV file here",
            type=['csv'],
            label_visibility="collapsed",
        )
        
        if uploaded_file is not None:
            if st.button("Load Dataset", key="load_data_btn", use_container_width=True, type="primary"):
                with st.spinner("Processing..."):
                    if st.session_state.chat_engine is None:
                        if not initialize_chat_engine():
                            st.stop()
                    
                    if load_csv_data(uploaded_file):
                        st.rerun()
        
        if st.session_state.data_loaded:
            st.markdown(
                f'<div class="file-badge"><span class="dot"></span>'
                f'<span>{st.session_state.uploaded_filename}</span></div>',
                unsafe_allow_html=True,
            )
            
            if st.button("Clear Data & Chat", key="clear_btn", use_container_width=True):
                st.session_state.chat_engine.clear_memory()
                st.session_state.chat_history = []
                st.session_state.data_loaded = False
                st.session_state.chat_engine = None
                st.session_state.uploaded_filename = None
                st.rerun()
        
        st.markdown("---")
        st.caption("Powered by Google Gemini & LangChain")
    
    # Main Content
    if st.session_state.data_loaded and st.session_state.chat_engine:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Overview", "Chat"])
        
        with tab1:
            # Display sample data
            display_sample_data()
            
            # Display initial insights
            display_initial_insights()
        
        with tab2:
            st.markdown('<div class="section-title">Chat</div>', unsafe_allow_html=True)
            
            # Chat messages display
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        with st.chat_message("user", avatar="🧑‍💻"):
                            st.markdown(message["content"])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(message["content"])
                        
                        # Display generated charts from dashboard generator
                        if message.get("generated_charts"):
                            st.markdown("---")
                            dashboard_data = message["generated_charts"]
                            
                            # Handle new InteractiveDashboard format (dict)
                            if isinstance(dashboard_data, dict) and 'charts' in dashboard_data:
                                # New cohesive dashboard format
                                st.markdown(f"### {dashboard_data.get('title', 'Dashboard')}")
                                st.markdown(dashboard_data.get('description', ''))
                                
                                # Render KPI cards
                                if dashboard_data.get('cards'):
                                    card_cols = st.columns(min(3, len(dashboard_data['cards'])))
                                    for col, card in zip(card_cols, dashboard_data['cards']):
                                        with col:
                                            st.metric(
                                                label=card.get('metric_name', 'Metric'),
                                                value=card.get('value', '0'),
                                                help=card.get('description', '')
                                            )
                                    st.markdown("---")
                                
                                # Render charts
                                if dashboard_data.get('charts'):
                                    st.markdown("### Visualizations")
                                    for chart_spec in dashboard_data['charts']:
                                        raw_chart_data = chart_spec.get('data')
                                        if raw_chart_data is None:
                                            continue

                                        if isinstance(raw_chart_data, pd.DataFrame):
                                            if raw_chart_data.empty:
                                                continue
                                            chart_df = raw_chart_data.copy()
                                        else:
                                            if not raw_chart_data:
                                                continue
                                            chart_df = pd.DataFrame(raw_chart_data)

                                        if chart_df.empty:
                                            continue

                                        x_col = chart_spec.get('x')
                                        y_col = chart_spec.get('y')
                                        group_col = chart_spec.get('groupby')
                                        chart_type = chart_spec.get('chart_type') or chart_spec.get('type', 'bar')
                                        
                                        if not x_col or not y_col or x_col not in chart_df.columns or y_col not in chart_df.columns:
                                            continue
                                        
                                        st.markdown(f"##### {chart_spec.get('title', 'Chart')}")
                                        try:
                                            if chart_type == 'line':
                                                if group_col and group_col in chart_df.columns:
                                                    pivot = chart_df.pivot(index=x_col, columns=group_col, values=y_col)
                                                    st.line_chart(pivot, use_container_width=True)
                                                else:
                                                    st.line_chart(chart_df.set_index(x_col)[y_col], use_container_width=True)
                                            elif chart_type == 'scatter':
                                                st.scatter_chart(
                                                    chart_df,
                                                    x=x_col,
                                                    y=y_col,
                                                    color=group_col if group_col and group_col in chart_df.columns else None,
                                                    use_container_width=True
                                                )
                                            else:  # bar, area, etc.
                                                if group_col and group_col in chart_df.columns:
                                                    pivot = chart_df.pivot(index=x_col, columns=group_col, values=y_col)
                                                    st.bar_chart(pivot, use_container_width=True)
                                                else:
                                                    st.bar_chart(chart_df.set_index(x_col)[y_col], use_container_width=True)
                                        except Exception:
                                            st.caption(f"Could not render {chart_type} chart")

                                # Render dynamic tables (for prompt-based chart+table mode)
                                if dashboard_data.get('tables'):
                                    st.markdown("### Tables")
                                    for table_spec in dashboard_data['tables']:
                                        table_title = table_spec.get('title', 'Table')
                                        table_data = table_spec.get('data')
                                        st.markdown(f"##### {table_title}")
                                        if isinstance(table_data, pd.DataFrame):
                                            st.dataframe(table_data, use_container_width=True)
                                        elif table_data is not None:
                                            st.dataframe(pd.DataFrame(table_data), use_container_width=True)

                                if dashboard_data.get('summary'):
                                    st.info(f"{dashboard_data['summary']}")
                                
                                # Render insights
                                if dashboard_data.get('insights'):
                                    st.markdown("### Key Insights")
                                    for insight in dashboard_data['insights']:
                                        st.info(f"{insight}")
                            
                            # Handle old chart list format (backward compatibility)
                            elif isinstance(dashboard_data, list):
                                st.markdown("### Generated Visualizations")
                                for chart_info in dashboard_data:
                                    if not isinstance(chart_info, dict):
                                        continue
                                    
                                    chart_data = chart_info.get("data", [])
                                    if not chart_data:
                                        st.caption(f"{chart_info.get('type', 'chart').title()} Chart: {chart_info.get('title', 'Untitled')}")
                                        continue

                                    chart_df = pd.DataFrame(chart_data)
                                    chart_type = chart_info.get("type", "bar")
                                    x_col = chart_info.get("x")
                                    y_col = chart_info.get("y")
                                    group_col = chart_info.get("groupby")

                                    if not x_col or not y_col or x_col not in chart_df.columns or y_col not in chart_df.columns:
                                        st.caption(f"{chart_type.title()} Chart: {chart_info.get('title', 'Untitled')}")
                                        continue

                                    st.markdown(f"#### {chart_info.get('title', 'Generated Chart')}")
                                    try:
                                        if chart_type == "line":
                                            if group_col and group_col in chart_df.columns:
                                                pivot_data = chart_df.pivot(index=x_col, columns=group_col, values=y_col)
                                                st.line_chart(pivot_data, use_container_width=True)
                                            else:
                                                st.line_chart(chart_df.set_index(x_col)[y_col], use_container_width=True)
                                        elif chart_type == "scatter":
                                            st.scatter_chart(
                                                chart_df,
                                                x=x_col,
                                                y=y_col,
                                                color=group_col if group_col in chart_df.columns else None,
                                                use_container_width=True,
                                            )
                                        else:
                                            if group_col and group_col in chart_df.columns:
                                                pivot_data = chart_df.pivot(index=x_col, columns=group_col, values=y_col)
                                                st.bar_chart(pivot_data, use_container_width=True)
                                            else:
                                                st.bar_chart(chart_df.set_index(x_col)[y_col], use_container_width=True)
                                    except Exception:
                                        st.caption(f"{chart_type.title()} Chart: {chart_info.get('title', 'Untitled')}")
                        
                        # Legacy chart support (backward compatibility)
                        if message.get("chart"):
                            chart_meta = message["chart"]
                            chart_data = chart_meta.get("data", [])
                            if chart_data:
                                chart_df = pd.DataFrame(chart_data)
                                x_col = chart_meta.get("x", "year")
                                y_col = chart_meta.get("y", "total_claims_no")
                                if x_col in chart_df.columns and y_col in chart_df.columns:
                                    st.line_chart(
                                        chart_df.set_index(x_col)[y_col],
                                        use_container_width=True
                                    )
        
        col1, col2 = st.columns([1, 0.1])
        
        with col1:
            user_input = st.chat_input(
                "Ask anything about your data...",
                key="chat_input"
            )
        
        # Process user input
        if user_input:
            # Display user message
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(user_input)
            
            # Add to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Smart visualization detection
            def should_generate_dashboard(query):
                """Return True for any data-related question (skip pure greetings)."""
                q = query.lower().strip()
                non_data = [
                    'hello', 'hi', 'hey', 'thanks', 'thank you',
                    'who are you', 'what are you', 'how are you',
                    'goodbye', 'bye', 'ok', 'okay', 'yes', 'no'
                ]
                return not any(
                    q == p or q.startswith(p + ' ') or q.startswith(p + ',')
                    for p in non_data
                )
            
            wants_visualization = should_generate_dashboard(user_input)
            
            # Get AI response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_engine.chat(user_input)
                    response_text = response
                    response_chart = None
                    if isinstance(response, dict):
                        response_text = response.get("response", "")
                        response_chart = response.get("chart")

                    st.markdown(response_text)
                    
                    # Generate visualization if requested
                    generated_charts = []
                    if wants_visualization:
                        try:
                            df = st.session_state.chat_engine.csv_analyzer.df
                            if df is not None and not df.empty:
                                generator = DynamicChartGenerator(df)
                                result = None

                                # --- LLM-driven intent extraction ---
                                with st.spinner("Generating chart..."):
                                    intent = st.session_state.chat_engine.get_chart_intent(user_input)

                                if intent.get("should_plot", False):
                                    result = generator.generate_from_intent(intent)

                                # --- Fallback: heuristic chart generator ---
                                if result is None or "error" in result:
                                    result = generator.parse_and_generate(user_input)

                                if result and "error" not in result and (result.get("charts") or result.get("tables")):
                                    st.markdown("---")
                                    for chart_spec in result.get("charts", []):
                                        _render_dynamic_chart(chart_spec)
                                    for table_spec in result.get("tables", []):
                                        st.markdown(f"### {table_spec['title']}")
                                        st.dataframe(table_spec["data"], use_container_width=True)
                                    if result.get("summary"):
                                        st.info(f"{result['summary']}")
                                    generated_charts = result
                        except Exception as e:
                            st.info(f"Could not generate visualization: {str(e)[:120]}")

                    # Legacy chart support (backward compatibility)
                    if response_chart:
                        chart_data = response_chart.get("data", [])
                        if chart_data:
                            chart_df = pd.DataFrame(chart_data)
                            x_col = response_chart.get("x", "year")
                            y_col = response_chart.get("y", "total_claims_no")
                            if x_col in chart_df.columns and y_col in chart_df.columns:
                                st.line_chart(
                                    chart_df.set_index(x_col)[y_col],
                                    use_container_width=True
                                )
            
            # Add to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_text,
                "chart": response_chart,
                "generated_charts": generated_charts if wants_visualization else None
            })
            
            st.rerun()
    
    else:
        # Landing page
        st.markdown(
            '<div class="landing-hero">'
            '<h1>Ask your data anything</h1>'
            '<p>Upload a CSV, then chat with AI to uncover insights, '
            'generate charts, and explore trends — no code needed.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="feature-grid">'
            '  <div class="feature-card">'
            '    <div class="feature-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg></div>'
            '    <h3>Upload</h3>'
            '    <p>Drop any CSV file and start instantly</p>'
            '  </div>'
            '  <div class="feature-card">'
            '    <div class="feature-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>'
            '    <h3>Ask</h3>'
            '    <p>Chat in plain English to query your data</p>'
            '  </div>'
            '  <div class="feature-card">'
            '    <div class="feature-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg></div>'
            '    <h3>Visualize</h3>'
            '    <p>Auto-generated charts for every question</p>'
            '  </div>'
            '  <div class="feature-card">'
            '    <div class="feature-icon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg></div>'
            '    <h3>Discover</h3>'
            '    <p>AI finds patterns and trends you\'d miss</p>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
