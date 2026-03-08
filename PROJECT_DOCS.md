# Project Structure & Documentation

## 📁 Directory Layout

```
genai-app/
├── app.py                      # Main Streamlit application
├── langchain_utils.py          # LangChain utilities and CSV analyzer
├── config.py                   # Configuration management
├── generate_sample_data.py     # Utility to generate test CSV files
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.bat                   # Automated setup for Windows
├── setup.sh                    # Automated setup for macOS/Linux
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Comprehensive documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_DOCS.md            # This file
```

## 📄 File Descriptions

### Core Application Files

#### `app.py` (Main Application)
**Purpose**: Streamlit frontend and main application logic
**Key Components**:
- Session state management
- Chat interface
- File upload handling
- Data preview and visualization
- Chat history display
- Initial insights generation

**Key Functions**:
- `initialize_chat_engine()`: Set up LangChain
- `load_csv_data()`: Handle file uploads
- `display_sample_data()`: Show data preview
- `display_initial_insights()`: Generate AI insights
- `main()`: Primary application flow

**Features**:
- Real-time chat interface
- File upload with validation
- Data preview section
- Automatic insights generation
- Chat history persistence

---

#### `langchain_utils.py` (Backend Logic)
**Purpose**: LangChain integration and data analysis utilities
**Key Classes**:
- `CSVAnalyzer`: Handles CSV data loading and analysis
- `LangChainChat`: Main chat engine with LLM integration

**CSVAnalyzer Methods**:
- `load_data()`: Load and parse CSV files
- `_extract_data_info()`: Extract column information
- `get_sample_data()`: Retrieve sample rows
- `get_data_description()`: Statistical summary
- `get_context()`: Formatted data context for LLM

**LangChainChat Methods**:
- `chat()`: Process user queries with context
- `get_data_insights()`: Generate automatic insights
- `load_dataset()`: Load CSV for analysis
- `get_data_context()`: Retrieve data context
- `get_chat_history()`: Access conversation history
- `clear_memory()`: Reset chat

---

#### `config.py` (Configuration)
**Purpose**: Centralized configuration management
**Configuration Options**:
```python
# API Settings
GOOGLE_API_KEY          # Your Google Gemini API key
MODEL_NAME              # Model to use (default: gemini-1.5-flash)
TEMPERATURE             # Response creativity (0-1)

# Application Settings
APP_TITLE              # Application title
APP_DESCRIPTION        # App description
MAX_FILE_SIZE_MB       # Upload size limit
ALLOWED_EXTENSIONS     # Supported file types
CHAT_HISTORY_MAX_LENGTH # Messages to keep
```

---

### Utility Files

#### `generate_sample_data.py` (Test Data Generator)
**Purpose**: Create sample CSV files for testing
**Datasets Generated**:
1. `sample_sales_data.csv` (100 records)
   - sales transactions with regions and products
   
2. `sample_customer_data.csv` (100 records)
   - customer information and purchase history
   
3. `sample_product_inventory.csv` (50 records)
   - inventory and product details
   
4. `sample_student_performance.csv` (100 records)
   - academic performance metrics

**Usage**:
```bash
python generate_sample_data.py
```

---

### Setup & Installation

#### `setup.bat` (Windows Setup)
**Purpose**: Automated environment setup for Windows
**What it does**:
1. Checks Python installation
2. Creates virtual environment
3. Installs dependencies
4. Creates .env file
5. Generates sample data

**Usage**:
```bash
setup.bat
```

---

#### `setup.sh` (macOS/Linux Setup)
**Purpose**: Automated environment setup for Unix systems
**What it does**: Same as setup.bat for Unix systems

**Usage**:
```bash
bash setup.sh
```

---

### Configuration Files

#### `.env.example` (Environment Template)
**Purpose**: Template for environment variables
**Variables**:
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `APP_TITLE`: Application title
- `APP_DESCRIPTION`: App description
- `MODEL_NAME`: LLM model name
- `TEMPERATURE`: LLM temperature parameter

**Setup Instructions**:
1. Copy to `.env`
2. Add your Google Gemini API key
3. Customize other settings as needed

---

#### `.gitignore` (Git Ignore Rules)
**Purpose**: Prevent sensitive files from being committed
**Ignored Items**:
- `.env` file (API keys)
- Virtual environment (`venv/`)
- Python cache (`__pycache__/`)
- IDE settings (`.vscode/`, `.idea/`)
- Streamlit cache (`.streamlit/`)
- Log files (`*.log`)

---

#### `requirements.txt` (Dependencies)
**Purpose**: Python package dependencies
**Packages**:
- `streamlit`: Web interface
- `langchain`: AI framework
- `langchain-google-genai`: Google Gemini integration
- `langchain-community`: Chat history and integrations
- `langchain-core`: Core prompt/message abstractions
- `python-dotenv`: Environment management
- `pandas`: Data processing
- `numpy`: Numerical computing

---

#### `requirements-dev.txt` (Development Dependencies)
**Purpose**: Additional packages for development
**Includes**:
- Testing: `pytest`, `pytest-cov`
- Code quality: `black`, `flake8`, `pylint`
- Debugging: `ipython`, `ipdb`
- Documentation: `sphinx`, `sphinx-rtd-theme`

---

### Documentation Files

#### `README.md` (Main Documentation)
**Sections**:
- Features overview
- Technology stack
- Installation instructions
- Usage guide
- Configuration options
- Troubleshooting
- Performance tips
- Security notes
- Example use cases
- Resource links

---

#### `QUICKSTART.md` (Quick Reference)
**Sections**:
- One-time setup (5 minutes)
- Running the app
- Using the app
- Example questions
- Quick shortcuts
- Common Q&A
- Troubleshooting
- Tips & best practices

---

#### `PROJECT_DOCS.md` (This File)
**Contents**:
- Complete project structure
- File descriptions and purposes
- Function documentation
- Usage examples
- Integration information

---

## 🔄 Data Flow

```
User CSV Upload
       ↓
File Validation (app.py)
       ↓
CSV Loading (langchain_utils.py → CSVAnalyzer)
       ↓
Data Analysis & Context Extraction
       ↓
Store in Session State
       ↓
Display Sample Data & Insights
       ↓
User Question Input
       ↓
Format with Data Context (langchain_utils.py)
       ↓
LangChain + Google Gemini Processing
       ↓
Return AI Response
       ↓
Display in Chat Interface
       ↓
Store in Chat History
```

---

## 🔌 API Integration

### Google Gemini Integration
```python
# Initialized in langchain_utils.py
ChatGoogleGenerativeAI(
       google_api_key=GOOGLE_API_KEY,
       model=MODEL_NAME,
    temperature=TEMPERATURE
)
```

### Data Processing Flow
1. **Load**: CSV → Pandas DataFrame
2. **Analyze**: Extract columns, types, stats
3. **Context**: Format data info for LLM
4. **Query**: User question + data context
5. **Response**: LLM generates answer
6. **Store**: Add to conversation memory

---

## 🎯 Key Features Implementation

### CSV File Upload
- Streamlit file uploader widget
- Temporary file handling
- Error handling and validation
- File cleanup after processing

### Data Analysis
- DataFrame loading and parsing
- Column type detection
- Statistical summaries
- Sample data extraction

### AI Conversation
- LangChain memory management
- Context-aware responses
- Message formatting
- History persistence

### Chat Interface
- Streamlit chat messages
- User/AI message formatting
- Real-time message display
- Input validation

---

## 🚀 Extension Points

### Adding New Features

**Custom Data Loaders**:
```python
# In langchain_utils.py CSVAnalyzer class
def load_json_data(self, file_path):
    # Add JSON support
```

**Custom Prompts**:
```python
# In app.py or langchain_utils.py
system_prompt = "Your custom system message"
```

**Extended Analysis**:
```python
# In CSVAnalyzer class
def advanced_statistics(self):
    # Add custom analysis
```

---

## 📊 Session State Variables

```python
st.session_state {
    'chat_engine': LangChainChat,      # Main chat engine
    'data_loaded': bool,                # Data status
    'chat_history': list,               # Message history
    'uploaded_filename': str            # Current file name
}
```

---

## 🔐 Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **File Upload**: Validated before processing
3. **Data Privacy**: Processed locally when possible
4. **Temporary Files**: Cleaned up after use
5. **Chat History**: Stored in session (ephemeral)

---

## 💡 Best Practices

1. **Code Organization**: Separated concerns (app, utils, config)
2. **Error Handling**: Try-catch blocks with user feedback
3. **Documentation**: Comprehensive docstrings
4. **Configuration**: Centralized config management
5. **Session Management**: Proper state handling

---

## 📈 Performance Optimization

1. **CSV Size**: Keep under 50MB for best performance
2. **Token Usage**: Monitor Google Gemini API usage
3. **Cache**: Streamlit caching for repeated operations
4. **Memory**: Limit chat history to recent messages

---

## 🧪 Testing

Run tests with:
```bash
pytest
pytest --cov           # With coverage
```

---

## 📚 Additional Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [LangChain Docs](https://docs.langchain.com)
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs)

---

## 📞 Support & Troubleshooting

**Issue**: API key not found
- ✅ Check `.env` file exists
- ✅ Verify key format
- ✅ Restart application

**Issue**: CSV won't load
- ✅ Validate CSV format
- ✅ Check file size
- ✅ Ensure headers present

**Issue**: Slow responses
- ✅ Reduce CSV size
- ✅ Simplify queries
- ✅ Check internet connection

---

**Last Updated**: 2026
**Version**: 1.0.0
