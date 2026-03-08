import streamlit as st
import pandas as pd
import os
import tempfile
import numpy as np
from langchain_utils import LangChainChat
from dashboard_generator import DashboardGenerator
from config import APP_TITLE, APP_DESCRIPTION, GOOGLE_API_KEY

# Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
        background: linear-gradient(160deg, #f6fbff 0%, #eef7f2 55%, #fff7ee 100%);
    }
    .stChatMessage,
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(31, 93, 167, 0.18);
        background: transparent !important;
        box-shadow: none;
    }
    .stChatMessage * {
        background: transparent !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        background: transparent !important;
    }
    [data-testid="stChatMessage"][aria-label="user"] {
        border-color: rgba(31, 93, 167, 0.26);
    }
    [data-testid="stChatMessage"][aria-label="assistant"] {
        border-color: rgba(31, 93, 167, 0.16);
    }
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input {
        background: transparent !important;
    }
    .stFileUploadDropzone {
        border-radius: 10px;
    }
    .header-title {
        color: #144e8c;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #3f5971;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .viz-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f8ff 100%);
        border: 1px solid #deebf8;
        border-radius: 16px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 6px 16px rgba(31, 93, 167, 0.08);
    }
    .viz-chip {
        display: inline-block;
        margin: 0.25rem 0.35rem 0.2rem 0;
        padding: 0.28rem 0.68rem;
        border-radius: 999px;
        background: #eaf3ff;
        color: #0f4d90;
        font-size: 0.82rem;
        border: 1px solid #d1e4fc;
    }
    .viz-section-title {
        margin-top: 0.2rem;
        margin-bottom: 0.5rem;
        color: #144e8c;
        font-size: 1rem;
        font-weight: 600;
    }
    .viz-chart-container {
        background: #ffffff;
        border: 1px solid #e8f0f9;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .viz-chart-title {
        color: #144e8c;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .viz-chart-subtitle {
        color: #5a7894;
        font-size: 0.78rem;
        margin-bottom: 0.7rem;
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
        with st.expander("📊 View Sample Data", expanded=False):
            sample_df = st.session_state.chat_engine.get_sample_data(rows=10)
            if sample_df is not None:
                st.dataframe(sample_df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 Total Rows", len(sample_df))
                with col2:
                    st.metric("📋 Total Columns", len(sample_df.columns))


def display_initial_insights():
    """Display a colorful Power BI-style starter dashboard from uploaded data."""
    if not (st.session_state.data_loaded and st.session_state.chat_engine):
        return

    df = st.session_state.chat_engine.csv_analyzer.df
    if df is None or df.empty:
        st.warning("No rows available to visualize.")
        return

    with st.expander("📊 Initial Visual Insights", expanded=True):
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e5ead 0%, #2d7dd2 100%); 
                    color: white; padding: 0.8rem 1.2rem; border-radius: 10px; margin-bottom: 1.2rem;">
            <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 0.2rem;">Executive Dashboard</div>
            <div style="font-size: 0.85rem; opacity: 0.95;">Key performance indicators and visual analytics</div>
        </div>
        """, unsafe_allow_html=True)

        total_rows = len(df)
        total_columns = len(df.columns)
        missing_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        completeness = (1 - (missing_cells / max(total_rows * max(total_columns, 1), 1))) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown('<div class="viz-chart-container">', unsafe_allow_html=True)
            st.metric("Total Rows", f"{total_rows:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        with kpi2:
            st.markdown('<div class="viz-chart-container">', unsafe_allow_html=True)
            st.metric("Columns", f"{total_columns}")
            st.markdown('</div>', unsafe_allow_html=True)
        with kpi3:
            st.markdown('<div class="viz-chart-container">', unsafe_allow_html=True)
            st.metric("Missing Cells", f"{missing_cells:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        with kpi4:
            st.markdown('<div class="viz-chart-container">', unsafe_allow_html=True)
            st.metric("Data Quality", f"{completeness:.1f}%", f"{duplicate_rows:,} dupes")
            st.markdown('</div>', unsafe_allow_html=True)

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

        st.markdown('<div style="margin: 1.5rem 0 1rem 0;"><div class="viz-section-title">Key Columns Selected for Analysis</div>', unsafe_allow_html=True)
        chips = "".join([f'<span class="viz-chip">{col}</span>' for col in selected_columns])
        st.markdown(chips + '</div>', unsafe_allow_html=True)

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
                <div class="viz-chart-container">
                    <div class="viz-chart-title">Time Series Trend</div>
                    <div class="viz-chart-subtitle">Average {main_num} over {date_like_col}</div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(                    trend_grouped.set_index(date_like_col)[main_num],
                    use_container_width=True,
                    color="#1f8ef1"
                )
        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        viz_left, viz_right = st.columns(2, gap="medium")

        with viz_left:
            if main_num:
                num_series = pd.to_numeric(df[main_num], errors="coerce").dropna()
                if not num_series.empty:
                    st.markdown(f"""
                    <div class="viz-chart-container">
                        <div class="viz-chart-title">Value Distribution</div>
                        <div class="viz-chart-subtitle">Frequency histogram for {main_num}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    bins = min(max(int(np.sqrt(len(num_series))), 8), 28)
                    hist = pd.cut(num_series, bins=bins).value_counts().sort_index()
                    hist_df = pd.DataFrame({"range": hist.index.astype(str), "count": hist.values})
                    st.bar_chart(
                        hist_df.set_index("range")["count"],
                        use_container_width=True,
                        color="#28b67a"
                    )
                else:
                    st.info("Not enough numeric values for distribution chart.")
            else:
                st.info("No numeric column available for distribution chart.")

        with viz_right:
            if main_cat:
                st.markdown(f"""
                <div class="viz-chart-container">
                    <div class="viz-chart-title">Category Composition</div>
                    <div class="viz-chart-subtitle">Top 10 categories in {main_cat}</div>
                </div>
                """, unsafe_allow_html=True)
                top_counts = df[main_cat].fillna("Unknown").astype(str).value_counts().head(10)
                cat_df = pd.DataFrame({"Category": top_counts.index, "Count": top_counts.values})
                st.bar_chart(
                    cat_df.set_index("Category")["Count"],
                    use_container_width=True,
                    color="#ff8a3d"
                )
            else:
                st.info("No categorical column available for category mix.")

        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
        comp_left, comp_right = st.columns(2, gap="medium")

        with comp_left:
            st.markdown(f"""
            <div class="viz-chart-container">
                <div class="viz-chart-title">Data Quality Overview</div>
                <div class="viz-chart-subtitle">Missing values across selected columns</div>
            </div>
            """, unsafe_allow_html=True)
            miss = df[selected_columns].isna().sum().sort_values(ascending=False)
            miss_df = pd.DataFrame({"Column": miss.index, "Missing": miss.values})
            st.bar_chart(
                miss_df.set_index("Column")["Missing"],
                use_container_width=True,
                color="#f4516c"
            )

        with comp_right:
            if main_num and second_num:
                st.markdown(f"""
                <div class="viz-chart-container">
                    <div class="viz-chart-title">🔗 Correlation Analysis</div>
                    <div class="viz-chart-subtitle">{main_num} vs {second_num}</div>
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
                        color="#8b5cf6"
                    )
                else:
                    st.info("🔗 Not enough valid rows for relationship chart.")
            else:
                st.info("🔗 Need at least two numeric columns for correlation analysis.")


def display_nl_dashboard_generator():
    """Display natural language dashboard generator interface"""
    if not (st.session_state.data_loaded and st.session_state.chat_engine):
        return
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); 
                color: white; padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.3rem;">🎨 Natural Language Dashboard Builder</div>
        <div style="font-size: 0.9rem; opacity: 0.95;">Describe your visualization in plain English, and watch it come to life instantly</div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI-generated suggestions based on actual data
    suggestions = st.session_state.chat_engine.suggest_dashboard_queries()
    if suggestions:
        with st.expander("✨ AI-Recommended Queries for Your Data", expanded=True):
            st.markdown("*Click any suggestion to use it:*")
            cols = st.columns(len(suggestions))
            for idx, (col, suggestion) in enumerate(zip(cols, suggestions)):
                with col:
                    if st.button(f"📊 Option {idx+1}", key=f"suggest_{idx}", use_container_width=True):
                        st.session_state.nl_dashboard_query = suggestion
                        st.rerun()
            for suggestion in suggestions:
                st.markdown(f"- *\"{suggestion}\"*")
    
    # Example prompts
    with st.expander("💡 More Example Prompts", expanded=False):
        examples = [
            "Show me the monthly sales revenue for Q3 broken down by region",
            "Compare values across different categories using a bar chart",
            "Display the correlation between two numeric columns",
            "Show the distribution grouped by category",
            "Create a trend showing how metrics changed over time"
        ]
        for ex in examples:
            st.markdown(f"- *\"{ex}\"*")
    
    # Natural language input
    nl_query = st.text_area(
        "Describe the dashboard you want to create:",
        placeholder="e.g., Show me total sales by region with a breakdown by product category...",
        height=100,
        key="nl_dashboard_query"
    )
    
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        generate_btn = st.button("🚀 Generate Dashboard", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.nl_dashboard_query = ""
            st.session_state.generated_dashboard = None
            st.rerun()
    
    if generate_btn and nl_query:
        with st.spinner("🎨 Creating your dashboard..."):
            try:
                df = st.session_state.chat_engine.csv_analyzer.df
                generator = DashboardGenerator(df)
                chart_specs = generator.generate_chart_spec(nl_query)
                
                if chart_specs:
                    st.session_state.generated_dashboard = chart_specs
                    st.success(f"✨ Generated {len(chart_specs)} visualization(s) from your query!")
                else:
                    st.warning("Could not generate visualizations. Try being more specific about columns or chart types.")
            except Exception as e:
                st.error(f"Error generating dashboard: {str(e)}")
    
    # Render generated dashboard
    if 'generated_dashboard' in st.session_state and st.session_state.generated_dashboard:
        st.markdown("---")
        st.markdown("### 📊 Your Generated Dashboard")
        
        specs = st.session_state.generated_dashboard
        
        # Layout based on number of charts
        if len(specs) == 1:
            _render_chart(specs[0])
        elif len(specs) == 2:
            col1, col2 = st.columns(2, gap="large")
            with col1:
                _render_chart(specs[0])
            with col2:
                _render_chart(specs[1])
        else:
            # First chart full width
            _render_chart(specs[0])
            # Remaining charts in columns
            if len(specs) > 1:
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    if len(specs) > 1:
                        _render_chart(specs[1])
                with col2:
                    if len(specs) > 2:
                        _render_chart(specs[2])


def _render_chart(spec):
    """Render a single chart based on its specification"""
    from dashboard_generator import ChartSpec
    
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e8f0f9; border-radius: 12px; 
                padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="color: #144e8c; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
            {spec.title}
        </div>
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
            st.caption(f"💡 Showing as bar chart - {spec.aggregation} of {spec.y_column} by {spec.x_column}")
        
        # Show data table option
        with st.expander(f"📋 View Data ({len(spec.data)} rows)"):
            st.dataframe(spec.data, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")


def main():
    # Header
    st.markdown('<h1 class="header-title">🤖 GenAI Data Intelligence Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown(f'<p class="header-subtitle">{APP_DESCRIPTION}</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File Upload Section
        st.subheader("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file to analyze",
            type=['csv'],
            help="Upload your CSV file to start analyzing with AI"
        )
        
        if uploaded_file is not None:
            if st.button("🚀 Load Data", key="load_data_btn"):
                with st.spinner("Loading data..."):
                    if st.session_state.chat_engine is None:
                        if not initialize_chat_engine():
                            st.stop()
                    
                    if load_csv_data(uploaded_file):
                        st.success(f"Successfully loaded: {uploaded_file.name}")
                        st.rerun()
        
        if st.session_state.data_loaded:
            st.info(f"Current File: {st.session_state.uploaded_filename}")
            
            if st.button("🔄 Clear Data & Chat", key="clear_btn"):
                st.session_state.chat_engine.clear_memory()
                st.session_state.chat_history = []
                st.session_state.data_loaded = False
                st.session_state.chat_engine = None
                st.session_state.uploaded_filename = None
                st.success("Cleared all data and chat history")
                st.rerun()
    
    # Main Content
    if st.session_state.data_loaded and st.session_state.chat_engine:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Quick Insights", "🎨 Dashboard Builder", "💬 AI Chat"])
        
        with tab1:
            # Display sample data
            display_sample_data()
            
            # Display initial insights
            display_initial_insights()
        
        with tab2:
            # Natural Language Dashboard Generator
            display_nl_dashboard_generator()
        
        with tab3:
            # Chat Interface
            st.subheader("💬 Conversational Analysis")
            
            # Chat messages display
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        with st.chat_message("user", avatar="👤"):
                            st.markdown(message["content"])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(message["content"])
                        
                        # Display generated charts from dashboard generator
                        if message.get("generated_charts"):
                            st.markdown("---")
                            st.markdown("### 📊 Generated Visualizations")
                            for chart_info in message["generated_charts"]:
                                chart_data = chart_info.get("data", [])
                                if not chart_data:
                                    st.caption(f"✓ {chart_info.get('type', 'chart').title()} Chart: {chart_info.get('title', 'Untitled')}")
                                    continue

                                chart_df = pd.DataFrame(chart_data)
                                chart_type = chart_info.get("type", "bar")
                                x_col = chart_info.get("x")
                                y_col = chart_info.get("y")
                                group_col = chart_info.get("groupby")

                                if not x_col or not y_col or x_col not in chart_df.columns or y_col not in chart_df.columns:
                                    st.caption(f"✓ {chart_type.title()} Chart: {chart_info.get('title', 'Untitled')}")
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
                                    st.caption(f"✓ {chart_type.title()} Chart: {chart_info.get('title', 'Untitled')}")
                        
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
        
        # Chat input
        col1, col2 = st.columns([1, 0.1])
        
        with col1:
            user_input = st.chat_input(
                "Ask me anything about your data...",
                key="chat_input"
            )
        
        # Process user input
        if user_input:
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            # Add to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Detect if user wants a visualization
            viz_keywords = [
                'show', 'display', 'visualize', 'plot', 'chart', 'graph',
                'trend', 'compare', 'comparison', 'correlation', 'relationship',
                'distribution', 'breakdown', 'analyze', 'analysis'
            ]
            wants_visualization = any(keyword in user_input.lower() for keyword in viz_keywords)
            
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
                                generator = DashboardGenerator(df)
                                chart_specs = generator.generate_chart_spec(user_input)
                                
                                if chart_specs:
                                    st.markdown("---")
                                    st.markdown("### 📊 Generated Visualizations")
                                    for spec in chart_specs:
                                        _render_chart(spec)
                                        generated_charts.append({
                                            'type': spec.chart_type,
                                            'title': spec.title,
                                            'x': spec.x_column,
                                            'y': spec.y_column,
                                            'groupby': spec.groupby_column,
                                            'aggregation': spec.aggregation,
                                            'data': spec.data.to_dict(orient='records')
                                        })
                                else:
                                    st.info("💡 Tip: Try being more specific about columns or chart types. Or visit the '🎨 Dashboard Builder' tab for AI-suggested queries.")
                        except Exception as e:
                            st.info(f"💡 Could not generate visualization: {str(e)[:100]}... Try the '🎨 Dashboard Builder' tab for better results.")

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
        # Landing page when no data is loaded
        st.info(
            """
            **Welcome to GenAI Data Intelligence!**
            
            This application allows you to:
            - Upload CSV files
            - Ask AI-powered questions about your data
            - Get instant insights and analysis
            - Discover patterns and trends
            
            **Getting Started:**
            1. Upload a CSV file using the sidebar
            2. Click 'Load Data' to process it
            3. Start asking questions about your data!
            
            **Example Questions:**
            - "What are the main trends in this data?"
            - "Summarize the key statistics"
            - "Which columns have missing values?"
            - "What insights can you provide about specific columns?"
            """
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Features
            - Instant Data Analysis
            - Pattern Discovery
            - Statistical Insights
            - Natural Language Queries
            """)
        
        with col2:
            st.markdown("""
            ### Technology Stack
            - LangChain
            - Google Gemini
            - Streamlit
            - Pandas
            """)


if __name__ == "__main__":
    main()
