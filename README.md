# GenAI Data Intelligence Dashboard

A conversational AI application for instant business intelligence and data analysis using LangChain, Google Gemini, and Streamlit.

## 🌟 Features

- **CSV File Upload**: Upload and analyze your CSV files instantly
- **AI-Powered Analysis**: Ask natural language questions about your data
- **Smart Insights**: Get automatic summary insights from your uploaded data
- **Conversational Interface**: Interactive chat-based data exploration
- **Real-time Processing**: Immediate responses and analysis
- **Data Preview**: View sample data and statistics

## 🛠️ Technology Stack

- **Backend**: Python with LangChain
- **Frontend**: Streamlit
- **AI Model**: Google Gemini 1.5 Flash
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

2. **View Data Insights**
   - Automatic insights will be generated
   - View sample data in the expandable section
   - Check data summary and statistics

3. **Ask Questions**
   - Type your questions in the chat input
   - Ask about trends, patterns, statistics
   - Get AI-powered analysis instantly

### Example Questions

- "What are the main trends in this data?"
- "Summarize the key statistics"
- "Which columns have missing values?"
- "What's the distribution of [column_name]?"
- "Find any correlations in the data"
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

- `MODEL_NAME`: OpenAI model (default: gpt-3.5-turbo)
- `TEMPERATURE`: Response creativity (0-1, default: 0.7)
- `MAX_FILE_SIZE_MB`: Maximum upload size
- `CHAT_HISTORY_MAX_LENGTH`: Messages to keep in memory

## 📊 CSV File Requirements

- **Format**: Standard CSV (comma-separated values)
- **Size**: Up to 100MB (configurable)
- **Headers**: First row should contain column names
- **Content**: Any tabular data

## 🐛 Troubleshooting

### "OpenAI API Key not found"
- Check that `.env` file exists in the project directory
- Verify `OPENAI_API_KEY` is set correctly
- Restart the Streamlit app

### "Error loading CSV"
- Ensure CSV is properly formatted
- Check file size doesn't exceed limit
- Verify CSV has headers in first row

### "Error processing query"
- Check internet connection
- Verify OpenAI API key is valid
- Check OpenAI account has available credits

## 📈 Performance Tips

- Use CSV files under 50MB for faster processing
- Keep questions specific for better answers
- Clear chat history if session becomes slow
- For large datasets, consider summarizing first

## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use `.gitignore` to exclude sensitive files
- Rotate API keys periodically
- Monitor API usage in OpenAI dashboard

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
- [OpenAI API Documentation](https://platform.openai.com/docs)
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
4. Check OpenAI API status

---

**Happy Analyzing! 🎉**
