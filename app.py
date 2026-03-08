import streamlit as st
import pandas as pd
import os
import tempfile
from langchain_utils import LangChainChat
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
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 20px;
    }
    .stFileUploadDropzone {
        border-radius: 10px;
    }
    .header-title {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
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


def initialize_chat_engine():
    """Initialize the LangChain chat engine."""
    if not GOOGLE_API_KEY:
        st.error("❌ Google API Key not found. Please set GOOGLE_API_KEY in your .env file")
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
    """Display visual dashboard insights instead of text-only LLM output."""
    if not (st.session_state.data_loaded and st.session_state.chat_engine):
        return

    df = st.session_state.chat_engine.csv_analyzer.df
    if df is None or df.empty:
        st.warning("No rows available to visualize.")
        return

    with st.expander("📊 Initial Visual Insights", expanded=True):
        # KPI row
        total_rows = len(df)
        total_columns = len(df.columns)
        missing_cells = int(df.isna().sum().sum())
        completeness = (1 - (missing_cells / max(total_rows * max(total_columns, 1), 1))) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Rows", f"{total_rows:,}")
        kpi2.metric("Columns", f"{total_columns}")
        kpi3.metric("Missing Cells", f"{missing_cells:,}")
        kpi4.metric("Completeness", f"{completeness:.1f}%")

        # Detect useful fields for business-style visuals.
        year_col = None
        claims_col = None
        lower_map = {str(col).strip().lower(): col for col in df.columns}
        if "year" in lower_map:
            year_col = lower_map["year"]
        if "total_claims_no" in lower_map:
            claims_col = lower_map["total_claims_no"]

        if year_col and claims_col:
            year_series = pd.to_numeric(
                df[year_col].astype(str).str.extract(r"(19\d{2}|20\d{2}|21\d{2})", expand=False),
                errors="coerce"
            )
            claims_series = pd.to_numeric(
                df[claims_col].astype(str).str.replace(r"[^\d\.-]", "", regex=True),
                errors="coerce"
            )
            chart_df = pd.DataFrame({"year": year_series, "total_claims_no": claims_series}).dropna()

            if not chart_df.empty:
                grouped = (
                    chart_df.groupby("year", as_index=False)["total_claims_no"]
                    .sum()
                    .sort_values("year")
                )
                grouped["year"] = grouped["year"].astype(int)

                st.markdown("#### Claims Trend")
                c1, c2 = st.columns(2)
                with c1:
                    st.line_chart(grouped.set_index("year")["total_claims_no"], use_container_width=True)
                with c2:
                    st.bar_chart(grouped.set_index("year")["total_claims_no"], use_container_width=True)

                latest_row = grouped.iloc[-1]
                peak_row = grouped.loc[grouped["total_claims_no"].idxmax()]
                m1, m2 = st.columns(2)
                m1.metric("Latest Year Claims", f"{int(latest_row['total_claims_no']):,}", f"Year {int(latest_row['year'])}")
                m2.metric("Peak Year Claims", f"{int(peak_row['total_claims_no']):,}", f"Year {int(peak_row['year'])}")

        # Generic visuals for any dataset.
        numeric_cols = list(df.select_dtypes(include="number").columns)
        object_cols = [col for col in df.columns if df[col].dtype == "object"]

        if numeric_cols:
            st.markdown("#### Numeric Distribution")
            num_col = numeric_cols[0]
            clean_num = pd.to_numeric(df[num_col], errors="coerce").dropna()
            if not clean_num.empty:
                bins = min(max(int(clean_num.nunique() / 2), 8), 30)
                hist = pd.cut(clean_num, bins=bins).value_counts().sort_index()
                hist_df = pd.DataFrame({"range": hist.index.astype(str), "count": hist.values})
                st.bar_chart(hist_df.set_index("range")["count"], use_container_width=True)

        if object_cols:
            st.markdown("#### Top Categories")
            cat_col = object_cols[0]
            top_counts = df[cat_col].fillna("Unknown").astype(str).value_counts().head(10)
            top_df = pd.DataFrame({"category": top_counts.index, "count": top_counts.values})
            st.bar_chart(top_df.set_index("category")["count"], use_container_width=True)


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
                        st.success(f"✅ Successfully loaded: {uploaded_file.name}")
                        st.rerun()
        
        if st.session_state.data_loaded:
            st.info(f"📌 Current File: {st.session_state.uploaded_filename}")
            
            if st.button("🔄 Clear Data & Chat", key="clear_btn"):
                st.session_state.chat_engine.clear_memory()
                st.session_state.chat_history = []
                st.session_state.data_loaded = False
                st.session_state.chat_engine = None
                st.session_state.uploaded_filename = None
                st.success("✅ Cleared all data and chat history")
                st.rerun()
    
    # Main Content
    if st.session_state.data_loaded and st.session_state.chat_engine:
        # Display sample data
        display_sample_data()
        
        # Display initial insights
        display_initial_insights()
        
        # Chat Interface
        st.divider()
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
                "chart": response_chart
            })
            
            st.rerun()
    
    else:
        # Landing page when no data is loaded
        st.info(
            """
            👋 **Welcome to GenAI Data Intelligence!**
            
            This application allows you to:
            - 📤 Upload CSV files
            - 🤖 Ask AI-powered questions about your data
            - 📊 Get instant insights and analysis
            - 💡 Discover patterns and trends
            
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
            ### ✨ Features
            - 🎯 Instant Data Analysis
            - 🔍 Pattern Discovery
            - 📈 Statistical Insights
            - 💬 Natural Language Queries
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Technology Stack
            - 🦙 LangChain
            - 🤖 OpenAI GPT
            - 🎨 Streamlit
            - 🐼 Pandas
            """)


if __name__ == "__main__":
    main()
