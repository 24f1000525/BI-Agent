# GenAI Data Intelligence Dashboard

A conversational AI application for instant business intelligence and data analysis using LangChain, Google Gemini, and Streamlit.

## 🌟 Features

### Core Capabilities
- **CSV File Upload**: Upload and analyze your CSV files instantly
- **AI-Powered Analysis**: Ask natural language questions about your data
- **Smart Insights**: Get automatic summary insights from your uploaded data
- **Conversational Interface**: Interactive chat-based data exploration with **auto-generated visualizations**
- **Real-time Processing**: Immediate responses and analysis
- **Data Preview**: View sample data and statistics

### 🎨 Natural Language Dashboard Generator
Transform plain English into interactive dashboards - **works in both Chat and Dashboard Builder!**

- **Plain English Queries**: Simply describe what you want to see
  - Example: "Show monthly sales trends by region"
  - Example: "Compare revenue across product categories"
  - Example: "Display the correlation between price and demand"

- **Intelligent Chart Selection**: Automatically picks the best visualization
  - Line charts for trends over time
  - Bar charts for categorical comparisons
  - Scatter plots for correlations
  - Pie charts for composition analysis

- **AI-Powered Suggestions**: Get smart query recommendations based on your data structure

- **Multi-Chart Dashboards**: Generate multiple coordinated visualizations from a single query

- **Interactive Exploration**: Hover details, data tables, and visual insights

- **🆕 Chat Integration**: Ask for visualizations directly in the AI Chat tab - get text answers AND charts together!

📖 **[Complete NL Dashboard Guide →](NL_DASHBOARD_GUIDE.md)**

## 🛠️ Technology Stack

- **Backend**: Python with LangChain
- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.0 Flash
- **Data Processing**: Pandas, NumPy

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key (Get one from [aistudio.google.com](https://aistudio.google.com/app/apikey))
- pip (Python package manager)

## 🚀 Installation

### 1. Clone/Create Project Structure
```bash
cd genai-app
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google Gemini API Key
# GOOGLE_API_KEY=your-google-api-key-here
```

On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
# Then edit .env with your editor
```

## 🎯 Usage

### Start the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Workflow

1. **Upload Data**
   - Click on the file uploader in the sidebar
   - Select your CSV file
   - Click "Load Data" to process

2. **📊 Quick Insights Tab**
   - View Power BI-style dashboard with 5 automatic visualizations
   - See trend analysis, distributions, and relationships
   - Explore data summary and statistics

3. **🎨 Dashboard Builder Tab** (NEW!)
   - Use natural language to create custom dashboards
   - Click AI-suggested queries or type your own
   - Generate interactive multi-chart dashboards instantly
   - Example: "Show sales trends by region for Q3"

4. **💬 AI Chat Tab** (Enhanced!)
   - Type your questions in the chat input
   - Ask about trends, patterns, statistics
   - Get AI-powered analysis instantly
   - **NEW**: Automatically generates visualizations when you ask for them!
   - Example: "Show me sales trends" → Gets text answer + visual chart

### Example Queries

#### AI Chat Questions (Now with Auto-Visualizations!)
- "What are the main trends in this data?"
- "Summarize the key statistics"
- "Which columns have missing values?"
- "Show the distribution of [column_name]" ← Generates chart!
- "Display correlations in the data" ← Generates chart!
- "Compare [metric] by [category]" ← Generates chart!
- "Visualize [column] over time" ← Generates chart!

#### Dashboard Builder Queries
- "Show monthly sales trends by region"
- "Compare revenue across product categories"
- "Display the correlation between price and demand"
- "Create a breakdown of customer segments"
- "Show year-over-year growth for Q3"
- "What are the top values in [column_name]?"
- "Provide insights about [specific_column]"

## 📁 Project Structure

```
genai-app/
├── app.py                 # Main Streamlit application
├── langchain_utils.py     # LangChain utilities and CSV analyzer
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## 🔑 Configuration

Edit `config.py` to customize:

- `MODEL_NAME`: Google Gemini model (default: gemini-1.5-flash)
- `TEMPERATURE`: Response creativity (0-1, default: 0.7)
- `MAX_FILE_SIZE_MB`: Maximum upload size
- `CHAT_HISTORY_MAX_LENGTH`: Messages to keep in memory

## 📊 CSV File Requirements

- **Format**: Standard CSV (comma-separated values)
- **Size**: Up to 100MB (configurable)
- **Headers**: First row should contain column names
- **Content**: Any tabular data

## 🐛 Troubleshooting

### "Google API Key not found"
- Check that `.env` file exists in the project directory
- Verify `GOOGLE_API_KEY` is set correctly
- Restart the Streamlit app

### "Error loading CSV"
- Ensure CSV is properly formatted
- Check file size doesn't exceed limit
- Verify CSV has headers in first row

### "Error processing query"
- Check internet connection
- Verify Google Gemini API key is valid
- Check Google AI Studio project/usage limits

## 📈 Performance Tips

- Use CSV files under 50MB for faster processing
- Keep questions specific for better answers
- Clear chat history if session becomes slow
- For large datasets, consider summarizing first

## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use `.gitignore` to exclude sensitive files
- Rotate API keys periodically
- Monitor API usage in Google AI Studio

## 📝 Example CSV Columns

The application works with any CSV structure. Examples:

**Sales Data**
- Date, Product, Quantity, Revenue, Region

**Customer Data**
- Customer_ID, Name, Email, Purchase_Amount, Region

**Insurance Data** (included in workspace)
- life_insurer, year, claims_pending, claims_paid, etc.

## 🚀 Advanced Usage

### Custom System Prompts
Edit the system prompt in `langchain_utils.py` `chat()` method to customize AI behavior.

### Extended Data Preprocessing
Modify `CSVAnalyzer` class to add custom data cleaning or transformation.

### Multiple File Format Support
Extend `app.py` to support Excel, JSON, or other formats.

## 📚 Resources

- [LangChain Documentation](https://docs.langchain.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs)

## 📄 License

This project is open source and available under the MIT License.

## 💡 Tips & Best Practices

1. **Data Quality**: Ensure CSV has clean headers and consistent formatting
2. **API Costs**: Monitor token usage (LLM calls cost money)
3. **Prompt Engineering**: Be specific in your questions for better results
4. **File Size**: Start with smaller files to test before large datasets

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages carefully
3. Verify environment setup
4. Check Google AI/Gemini API status

---

**Happy Analyzing! 🎉**
