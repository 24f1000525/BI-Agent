# Developer Guide - Natural Language Dashboard Generator

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)
- Google Gemini API key configured

### Project Structure
```
genai-app/
├── app.py                     # Main Streamlit application
├── dashboard_generator.py     # NL dashboard engine
├── langchain_utils.py         # AI chat and analysis
├── config.py                  # Configuration management
└── __pycache__/              # Python bytecode
```

---

## 🏗️ Architecture Overview

### Component Interaction

```
┌─────────────┐
│   User      │
│  (Streamlit)│
└──────┬──────┘
       │ Natural Language Query
       ↓
┌─────────────────────────┐
│  DashboardGenerator     │
│  (dashboard_generator)  │
├─────────────────────────┤
│ • parse_query()         │
│ • suggest_visualization()│
│ • generate_chart_spec() │
└──────┬──────────────────┘
       │ List[ChartSpec]
       ↓
┌─────────────────────────┐
│  Streamlit Renderer     │
│  (app.py)               │
├─────────────────────────┤
│ • _render_chart()       │
│ • st.line_chart()       │
│ • st.bar_chart()        │
│ • st.scatter_chart()    │
└─────────────────────────┘
```

---

## 📦 Core Modules

### 1. `dashboard_generator.py`

#### Purpose
Transform natural language queries into structured chart specifications.

#### Key Classes

##### `ChartSpec` Dataclass
```python
@dataclass
class ChartSpec:
    chart_type: str        # Chart type identifier
    title: str             # Display title
    x_column: str          # X-axis column name
    y_column: str          # Y-axis column name
    groupby: Optional[str] # Grouping column (for multi-series)
    aggregation: str       # Aggregation function
    data: pd.DataFrame     # Prepared/aggregated data
```

**Usage Example**:
```python
spec = ChartSpec(
    chart_type='line',
    title='Monthly Sales Trends',
    x_column='Month',
    y_column='Sales',
    groupby='Region',
    aggregation='sum',
    data=aggregated_df
)
```

##### `DashboardGenerator` Class

**Main Methods**:

1. **`parse_query(query: str, df: pd.DataFrame) -> dict`**
   - Extracts intent from natural language
   - Returns dict with chart_types, metrics, dimensions, aggregations, time_filters
   
   ```python
   generator = DashboardGenerator()
   params = generator.parse_query(
       "Show monthly sales by region", 
       dataframe
   )
   # Returns: {
   #   'chart_types': ['line'],
   #   'metrics': ['sales'],
   #   'dimensions': ['month', 'region'],
   #   'aggregations': ['sum'],
   #   'time_filters': {}
   # }
   ```

2. **`suggest_visualization(df: pd.DataFrame, params: dict) -> List[str]`**
   - Analyzes data characteristics
   - Recommends appropriate chart types
   
   ```python
   chart_types = generator.suggest_visualization(df, params)
   # Returns: ['line', 'bar']
   ```

3. **`generate_chart_spec(query: str, df: pd.DataFrame) -> List[ChartSpec]`**
   - Orchestrates the full pipeline
   - Returns list of chart specifications ready for rendering
   
   ```python
   specs = generator.generate_chart_spec(
       "Compare revenue by product",
       dataframe
   )
   # Returns: [ChartSpec(...), ChartSpec(...)]
   ```

**Helper Methods**:
- `_find_best_match()`: Fuzzy column name matching
- `_get_numeric_columns()`: Filter numeric columns
- `_get_categorical_columns()`: Filter categorical columns
- `_get_temporal_columns()`: Identify date/time columns
- `_create_line_chart_spec()`: Line chart builder
- `_create_bar_chart_spec()`: Bar chart builder
- `_create_scatter_chart_spec()`: Scatter plot builder
- `_create_pie_chart_spec()`: Pie chart builder

#### Adding New Chart Types

**Step 1**: Add chart type to parse_query pattern matching
```python
def parse_query(self, query, df):
    # ... existing code ...
    if re.search(r'\b(heatmap|heat map)\b', query_lower):
        chart_types.append('heatmap')
```

**Step 2**: Update suggest_visualization logic
```python
def suggest_visualization(self, df, params):
    # ... existing code ...
    if has_two_categories and has_numeric:
        suggested_types.append('heatmap')
```

**Step 3**: Create chart specification method
```python
def _create_heatmap_spec(self, df, params):
    x_col = params['dimensions'][0]
    y_col = params['dimensions'][1]
    value_col = params['metrics'][0]
    
    # Prepare pivot table
    pivot_data = df.pivot_table(
        values=value_col,
        index=y_col,
        columns=x_col,
        aggfunc=params['aggregations'][0]
    )
    
    return ChartSpec(
        chart_type='heatmap',
        title=f'{value_col} by {x_col} and {y_col}',
        x_column=x_col,
        y_column=y_col,
        groupby=None,
        aggregation=params['aggregations'][0],
        data=pivot_data
    )
```

**Step 4**: Update generate_chart_spec routing
```python
def generate_chart_spec(self, query, df):
    # ... existing code ...
    for chart_type in chart_types:
        if chart_type == 'heatmap':
            spec = self._create_heatmap_spec(df, params)
            chart_specs.append(spec)
```

---

### 2. `app.py` Enhancement

#### Key Functions

##### `display_nl_dashboard_generator(df, analyzer)`
Main UI for dashboard generation.

**Components**:
1. AI-suggested queries section
2. Text area for custom queries
3. Generate dashboard button
4. Chart rendering area

**Code Structure**:
```python
def display_nl_dashboard_generator(df, analyzer):
    st.header("Natural Language Dashboard Generator")
    
    # AI Suggestions
    suggestions = analyzer.suggest_dashboard_queries(df)
    # Display clickable suggestions
    
    # User Input
    user_query = st.text_area("Describe your visualization...")
    
    if st.button("Generate Dashboard"):
        # Generate chart specs
        generator = DashboardGenerator()
        specs = generator.generate_chart_spec(user_query, df)
        
        # Store in session state
        st.session_state.generated_dashboard = specs
        
    # Render stored dashboard
    if st.session_state.generated_dashboard:
        for spec in st.session_state.generated_dashboard:
            _render_chart(spec)
```

##### `_render_chart(chart_spec)`
Renders individual charts based on ChartSpec.

**Supported Chart Types**:
- `line`: `st.line_chart()`
- `bar`: `st.bar_chart()`
- `scatter`: `st.scatter_chart()`
- `pie`: `st.bar_chart()` (Streamlit limitation)

**Adding New Renderers**:
```python
def _render_chart(chart_spec):
    if chart_spec.chart_type == 'line':
        # ... existing line chart code ...
        
    elif chart_spec.chart_type == 'heatmap':
        st.subheader(chart_spec.title)
        
        # Custom heatmap rendering
        import plotly.express as px
        fig = px.imshow(
            chart_spec.data,
            labels=dict(x=chart_spec.x_column, 
                       y=chart_spec.y_column),
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("View Data Table"):
            st.dataframe(chart_spec.data)
```

---

### 3. `langchain_utils.py` Enhancement

#### `suggest_dashboard_queries(df)`
Generates AI-powered query suggestions.

**Implementation**:
```python
def suggest_dashboard_queries(self, df):
    # Analyze dataframe structure
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    date_cols = [col for col in df.columns 
                 if 'date' in col.lower() or 'year' in col.lower()]
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Create prompt for Gemini
    prompt = f"""
    Based on this dataset structure, suggest 5 insightful dashboard queries:
    
    Numeric columns: {list(numeric_cols)}
    Date columns: {list(date_cols)}
    Categorical columns: {list(categorical_cols)}
    
    Sample data:
    {df.head(3).to_string()}
    
    Generate queries like:
    - "Show [metric] trends over [time]"
    - "Compare [metric] across [categories]"
    """
    
    # Get AI response
    response = self.chat_session.invoke(prompt)
    
    # Parse suggestions
    suggestions = parse_ai_response(response)
    return suggestions
```

---

## 🧪 Testing Strategy

### Unit Testing

**Test File**: `test_dashboard_generator.py` (to be created)

```python
import unittest
import pandas as pd
from dashboard_generator import DashboardGenerator, ChartSpec

class TestDashboardGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = DashboardGenerator()
        self.sample_df = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=10),
            'Sales': [100, 150, 120, 180, 200, 190, 210, 230, 240, 250],
            'Region': ['North']*5 + ['South']*5
        })
    
    def test_parse_query_line_chart(self):
        params = self.generator.parse_query(
            "Show sales trends over time",
            self.sample_df
        )
        self.assertIn('line', params['chart_types'])
        self.assertIn('sales', params['metrics'])
    
    def test_suggest_visualization_temporal(self):
        params = {'dimensions': ['Date'], 'metrics': ['Sales']}
        suggestions = self.generator.suggest_visualization(
            self.sample_df, params
        )
        self.assertIn('line', suggestions)
    
    def test_generate_chart_spec(self):
        specs = self.generator.generate_chart_spec(
            "Compare sales by region",
            self.sample_df
        )
        self.assertIsInstance(specs, list)
        self.assertGreater(len(specs), 0)
        self.assertIsInstance(specs[0], ChartSpec)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

**Manual Test Cases**:

1. **Time Series Analysis**
   ```
   Query: "Show monthly revenue trends"
   Expected: Line chart with time on x-axis
   Validate: Chart renders, data aggregated by month
   ```

2. **Categorical Comparison**
   ```
   Query: "Compare sales across regions"
   Expected: Bar chart with regions on x-axis
   Validate: Chart renders, data grouped by region
   ```

3. **Correlation Analysis**
   ```
   Query: "Show relationship between price and demand"
   Expected: Scatter plot
   Validate: Two numeric columns plotted
   ```

4. **Multi-Chart Dashboard**
   ```
   Query: "Show sales by product and region over time"
   Expected: 2-3 coordinated charts
   Validate: Multiple charts render coherently
   ```

---

## 🐛 Debugging Guide

### Common Issues

#### 1. Query Not Parsed Correctly

**Symptom**: Wrong chart type or columns selected

**Debug Steps**:
```python
# Add logging to parse_query
import logging
logging.basicConfig(level=logging.DEBUG)

def parse_query(self, query, df):
    logging.debug(f"Query: {query}")
    # ... parsing logic ...
    logging.debug(f"Parsed params: {params}")
    return params
```

**Fix**: Adjust regex patterns or add more keywords

#### 2. Column Not Found

**Symptom**: KeyError or empty charts

**Debug Steps**:
```python
# Check column matching
best_match = self._find_best_match(metric, df.columns)
if not best_match:
    print(f"No match found for: {metric}")
    print(f"Available columns: {df.columns.tolist()}")
```

**Fix**: Improve fuzzy matching algorithm or prompt user

#### 3. Chart Rendering Fails

**Symptom**: Streamlit error or empty display

**Debug Steps**:
```python
def _render_chart(chart_spec):
    print(f"Rendering: {chart_spec.chart_type}")
    print(f"Data shape: {chart_spec.data.shape}")
    print(f"Data preview:\n{chart_spec.data.head()}")
    
    # ... rendering logic ...
```

**Fix**: Validate data format, handle edge cases

---

## 🎨 UI Customization

### Styling

**Location**: `app.py` - Custom CSS section

```python
st.markdown("""
<style>
    /* Customize dashboard builder */
    .viz-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Add new custom styles */
    .custom-chart-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)
```

### Layout Modifications

**Change Chart Grid**:
```python
# Current: Full width primary chart
st.plotly_chart(fig, use_container_width=True)

# New: Side-by-side charts
col1, col2 = st.columns(2)
with col1:
    _render_chart(specs[0])
with col2:
    _render_chart(specs[1])
```

---

## 📊 Performance Optimization

### Data Sampling

**For Large Datasets**:
```python
def generate_chart_spec(self, query, df):
    # Sample data if too large
    if len(df) > 10000:
        df_sample = df.sample(n=10000, random_state=42)
        st.info(f"Sampled {len(df_sample)} rows from {len(df)} total")
    else:
        df_sample = df
    
    # Continue with sampled data
    params = self.parse_query(query, df_sample)
    # ...
```

### Caching

**Cache Expensive Operations**:
```python
@st.cache_data
def generate_chart_spec_cached(query, df_hash):
    # Use hash of dataframe for cache key
    generator = DashboardGenerator()
    return generator.generate_chart_spec(query, df)

# Usage
df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
specs = generate_chart_spec_cached(user_query, df_hash)
```

---

## 🚀 Extending Functionality

### 1. Add LLM-Based Parsing

**Enhanced Intelligence**:
```python
def parse_query_with_llm(self, query, df):
    prompt = f"""
    Parse this dashboard query: "{query}"
    
    Available columns: {df.columns.tolist()}
    
    Return JSON:
    {{
        "chart_types": ["line", "bar"],
        "metrics": ["sales"],
        "dimensions": ["date", "region"],
        "aggregations": ["sum"]
    }}
    """
    
    response = self.llm.invoke(prompt)
    return json.loads(response.content)
```

### 2. Add Dashboard Templates

**Predefined Patterns**:
```python
DASHBOARD_TEMPLATES = {
    'sales_overview': {
        'queries': [
            "Show revenue trends over time",
            "Compare sales by region",
            "Display top products by revenue"
        ],
        'layout': 'primary_with_sidebars'
    },
    'customer_analysis': {
        'queries': [
            "Show customer acquisition over time",
            "Compare customer value by segment",
            "Display churn rate trends"
        ],
        'layout': 'grid_3x1'
    }
}

def apply_template(template_name, df):
    template = DASHBOARD_TEMPLATES[template_name]
    specs = []
    for query in template['queries']:
        spec = generate_chart_spec(query, df)
        specs.extend(spec)
    return specs, template['layout']
```

### 3. Add Export Functionality

**Download Dashboards**:
```python
def export_dashboard_as_image(chart_specs):
    # Convert charts to images
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(len(chart_specs), 1, figsize=(10, 6*len(chart_specs)))
    
    for idx, spec in enumerate(chart_specs):
        ax = axes[idx] if len(chart_specs) > 1 else axes
        spec.data.plot(kind=spec.chart_type, ax=ax, title=spec.title)
    
    plt.tight_layout()
    plt.savefig('dashboard_export.png', dpi=300, bbox_inches='tight')
    
    # Provide download button
    with open('dashboard_export.png', 'rb') as f:
        st.download_button(
            label="Download Dashboard",
            data=f,
            file_name="dashboard.png",
            mime="image/png"
        )
```

---

## 📝 Code Style Guide

### Naming Conventions
- **Classes**: PascalCase (e.g., `DashboardGenerator`)
- **Functions**: snake_case (e.g., `parse_query`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_CHART_COUNT`)
- **Private methods**: Prefix with underscore (e.g., `_find_best_match`)

### Documentation
- Use docstrings for all public methods
- Include type hints
- Document parameters and return values

**Example**:
```python
def generate_chart_spec(self, query: str, df: pd.DataFrame) -> List[ChartSpec]:
    """
    Generate chart specifications from natural language query.
    
    Args:
        query (str): Natural language description of desired visualization
        df (pd.DataFrame): Source data for visualization
    
    Returns:
        List[ChartSpec]: List of chart specifications ready for rendering
    
    Raises:
        ValueError: If query cannot be parsed or no suitable columns found
    """
    # Implementation
```

### Error Handling
- Use try-except for external operations
- Provide meaningful error messages
- Log errors for debugging

```python
try:
    specs = generator.generate_chart_spec(query, df)
except ValueError as e:
    st.error(f"Could not generate dashboard: {str(e)}")
    logging.error(f"Chart generation failed: {e}", exc_info=True)
except Exception as e:
    st.error("An unexpected error occurred")
    logging.critical(f"Unexpected error: {e}", exc_info=True)
```

---

## 🔧 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-chart-type

# Make changes
# Test locally

# Commit with clear message
git commit -m "Add heatmap chart type to dashboard generator"

# Push and create PR
git push origin feature/new-chart-type
```

### 2. Local Testing
```bash
# Run Streamlit in dev mode
streamlit run app.py --server.runOnSave true

# Test with sample data
python generate_sample_data.py
```

### 3. Code Quality
```bash
# Format code
black dashboard_generator.py app.py

# Check linting
pylint dashboard_generator.py

# Type checking
mypy dashboard_generator.py
```

---

## 📚 Additional Resources

### Dependencies
- **Streamlit**: Web framework - [docs](https://docs.streamlit.io)
- **Pandas**: Data manipulation - [docs](https://pandas.pydata.org/docs/)
- **LangChain**: AI integration - [docs](https://python.langchain.com)
- **Google Gemini**: LLM - [docs](https://ai.google.dev/docs)

### Related Documentation
- [NL_DASHBOARD_GUIDE.md](NL_DASHBOARD_GUIDE.md) - User guide
- [NL_DASHBOARD_QUICKSTART.md](NL_DASHBOARD_QUICKSTART.md) - Quick start
- [PROJECT_DOCS.md](PROJECT_DOCS.md) - Technical architecture
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

---

**Happy Coding! 🚀**

For questions or contributions, refer to the main project documentation.
