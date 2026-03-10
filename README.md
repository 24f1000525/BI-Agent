# DataLens AI - GenAI Data Intelligence Dashboard

A modern conversational AI application for instant business intelligence and data analysis. Built with Flask, React, LangChain, and Google Gemini.

## 🌟 Features

### Core Capabilities
- **CSV File Upload**: Upload and analyze CSV files instantly through a modern web interface
- **AI-Powered Analysis**: Ask natural language questions about your data and get instant insights
- **Smart Visualizations**: Automatically generated charts and graphs based on your queries
- **Conversational Interface**: Interactive chat-based data exploration with real-time responses
- **Multi-Chart Dashboards**: Generate comprehensive dashboards with multiple coordinated visualizations
- **Data Preview**: View sample data, statistics, and data quality metrics
- **Query History**: Keep track of your analysis sessions

### 🎨 Natural Language Dashboard Generator
Transform plain English into interactive, professional dashboards:

- **Plain English Queries**: Simply describe what you want to see
  - Example: "Show monthly sales trends by region"
  - Example: "Compare revenue across product categories"
  - Example: "Display the correlation between price and demand"

- **Intelligent Chart Selection**: AI automatically picks the best visualization type
  - Line charts for trends over time
  - Bar charts for categorical comparisons
  - Scatter plots for correlations
  - Pie/Doughnut charts for composition analysis
  - Radar charts for multi-dimensional comparisons

- **AI-Powered Suggestions**: Get smart query recommendations based on your data structure

- **Interactive Charts**: Built with Chart.js for smooth, responsive visualizations
  - Hover to see detailed values
  - Responsive design for all screen sizes
  - Export-ready visualizations

### 🛡️ AI Safety & Validation Features

**100% Data Accuracy Guarantee**
- Uses ALL relevant data points matching user queries (not arbitrary "top 10" limits)
- Smart thresholds: Shows all categories if ≤30, otherwise top 20 with "Others" aggregate
- Transparent labeling: Charts clearly indicate "All" vs "Top N of Total"
- Full dataset processing: Sends complete data (≤1000 rows) to LLM for accurate analysis
- Respects explicit limits: "Show top 5" correctly displays exactly 5 items
- Server-side validation and logging

**Data Retrieval Validation**
- Pre-validates queries against available columns before LLM processing
- Detects impossible queries and returns clear error messages
- Prevents wasted API calls on unanswerable queries
- Column name suggestions for typos and similar names

**Contextual Chart Selection**
- Keyword-based detection: "trend" → line, "compare" → bar, "breakdown" → pie
- LLM receives explicit chart type selection rules
- Post-generation validation ensures chart type appropriateness
- Server console monitoring of AI chart selection decisions

**Hallucination Prevention**
- Multi-layer validation: column existence, data patterns, structural integrity
- Detects and rejects fabricated data (identical values, suspicious patterns)
- Returns user-friendly error messages instead of fake data
- LLM explicitly instructed to refuse unanswerable queries with available columns

## 🛠️ Technology Stack

### Backend
- **Flask**: RESTful API server with CORS support
- **LangChain**: LLM orchestration and prompt engineering
- **Google Gemini 2.0 Flash**: Advanced AI model for natural language understanding
- **Pandas & NumPy**: Data processing and analysis

### Frontend
- **React 19**: Modern UI library with hooks
- **Vite**: Lightning-fast development and build tool
- **Tailwind CSS v4**: Utility-first styling with modern design
- **Chart.js**: Professional chart visualizations
- **Three.js**: Interactive 3D background effects

## 📋 Prerequisites

- **Python 3.8 or higher**
- **Node.js 16 or higher** (for the React frontend)
- **Google Gemini API Key** (Get one free from [aistudio.google.com](https://aistudio.google.com/app/apikey))
- **pip** (Python package manager)
- **npm** (Node package manager, comes with Node.js)

## 🚀 Quick Start

### Automated Setup (Recommended)

#### Windows
```cmd
setup.bat
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Set up Node.js dependencies for the React frontend
- Create a `.env` file from the example

#### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

#### 3. Environment Configuration
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google Gemini API Key
# GOOGLE_API_KEY=your-google-api-key-here
```

On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
# Then edit .env with Notepad or your preferred editor
notepad .env
```

## 🎯 Running the Application

### Automated Start (Recommended)

#### Windows
```cmd
start.bat
```

#### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

This will start both:
- **Flask Backend** at `http://localhost:5000`
- **React Frontend** at `http://localhost:5173`

The application will automatically open in your browser at `http://localhost:5173`.

### Manual Start

#### Terminal 1 - Backend
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start Flask server
python flask_app.py
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## 💡 Usage Guide

### 1. **Upload Your Data**
   - Click "Upload CSV" button in the interface
   - Select your CSV file (up to 100MB)
   - Wait for processing confirmation
   - View data preview and column information

### 2. **Explore with AI Chat**
   - Type natural language questions in the chat box
   - Get instant AI-powered insights and analysis
   - Charts are automatically generated for visual queries
   - View response with both text explanations and visualizations

### 3. **Generate Dashboards**
   - Use the dashboard generator feature
   - Type a comprehensive query describing what you want to see
   - AI will create multiple coordinated charts
   - Example: "Show sales trends by region with product breakdown"

### 4. **Review History**
   - Access your query history from the sidebar
   - Replay previous analyses
   - Track your exploration journey

## 📝 Example Queries

### Data Exploration
- "What are the main trends in this data?"
- "Summarize the key statistics for all columns"
- "Which columns have missing or null values?"
- "Show me the data types and ranges"

### Visual Analysis
- "Show the distribution of sales by region"
- "Display revenue trends over time"
- "Compare product performance across categories"
- "Visualize the correlation between price and demand"
- "Create a breakdown of customer segments"

### Specific Insights
- "What are the top 10 products by revenue?"
- "Show year-over-year growth for Q3 2025"
- "Identify outliers in the price column"
- "Calculate average sale amount by region"

## 📁 Project Structure

```
genai-app/
├── backend/
│   ├── flask_app.py              # Main Flask API server (with chart generation)
│   ├── langchain_utils.py        # LangChain integration & CSV analyzer
│   ├── config.py                 # Application configuration
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── default_data.json        # Default/fallback data
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Navbar.jsx       # Top navigation
│   │   │   ├── Sidebar.jsx      # Side panel
│   │   │   ├── QueryBox.jsx     # Query input component
│   │   │   ├── ChartsGrid.jsx   # Chart display grid
│   │   │   ├── Overview.jsx     # Data overview
│   │   │   ├── ThreeBackground.jsx # 3D background
│   │   │   └── ...
│   │   ├── App.jsx              # Main application component
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js           # Vite configuration
│   └── index.html               # HTML template
│
├── setup.bat / setup.sh          # Automated setup scripts
├── start.bat / start.sh          # Automated start scripts
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🔑 Configuration

### Backend Configuration (`config.py`)
Edit to customize:
- `MODEL_NAME`: Google Gemini model (default: `gemini-2.0-flash`)
- `TEMPERATURE`: Response creativity (0-1, default: 0.7)
- `MAX_FILE_SIZE_MB`: Maximum upload size (default: 100MB)
- `CHAT_HISTORY_MAX_LENGTH`: Messages to keep in memory

### Environment Variables (`.env`)
Required:
```env
GOOGLE_API_KEY=your-api-key-here
```

Optional:
```env
APP_TITLE=DataLens AI
APP_DESCRIPTION=GenAI Data Intelligence
MODEL_NAME=gemini-2.0-flash
TEMPERATURE=0.7
```

## 📊 CSV File Requirements

- **Format**: Standard CSV (comma-separated values)
- **Size**: Up to 100MB (configurable in `config.py`)
- **Headers**: First row must contain column names
- **Content**: Any tabular data (sales, customer, financial, etc.)
- **Encoding**: UTF-8 recommended

### Example CSV Structures

**Sales Data**
```csv
Date,Product,Quantity,Revenue,Region
2024-01-01,Widget A,100,5000,North
2024-01-02,Widget B,150,7500,South
```

**Customer Data**
```csv
CustomerID,Name,Email,PurchaseAmount,Region,Segment
C001,John Doe,john@example.com,1500,West,Premium
C002,Jane Smith,jane@example.com,800,East,Standard
```

## � Troubleshooting

### Backend Issues

**"Google API Key not found"**
- Verify `.env` file exists in the root directory
- Check that `GOOGLE_API_KEY` is set correctly in `.env`
- Restart the Flask server after making changes
- Ensure `.env` file is in the same directory as `flask_app.py`

**"Port 5000 already in use"**
- Kill existing process: `taskkill /F /IM python.exe` (Windows)
- Or change port in `flask_app.py`: `app.run(port=5001)`

**"Module not found" errors**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version is 3.8+

### Frontend Issues

**"Port 5173 already in use"**
- Kill existing Vite process
- Or Vite will automatically try the next available port

**"npm install fails"**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then reinstall
- Ensure Node.js version is 16 or higher

**"Cannot connect to backend"**
- Verify Flask server is running on `http://localhost:5000`
- Check CORS is enabled in `flask_app.py`
- Look for network/firewall blocking requests

### Data Processing Issues

**"Error loading CSV"**
- Ensure CSV is properly formatted with headers in first row
- Check file size doesn't exceed 100MB limit
- Verify CSV uses comma separators (not semicolons or tabs)
- Try opening CSV in Excel/Notepad to check formatting

**"Error processing query"**
- Check internet connection (required for Gemini API)
- Verify Google Gemini API key is valid and has quota
- Check Google AI Studio for rate limits or billing issues
- Try simplifying your query

**Charts not displaying**
- Check browser console for JavaScript errors
- Ensure data was successfully uploaded
- Try a simpler query like "Show column distribution"
- Verify response format in browser Network tab

## 📈 Performance Optimization

### For Better Speed
- Use CSV files under 50MB for faster upload and processing
- Keep queries specific and focused
- Limit number of simultaneous chart generations
- Clear browser cache if interface becomes sluggish

### For Better Results
- Ensure clean data with proper headers
- Use descriptive column names
- Remove unnecessary columns before uploading
- Provide specific queries rather than vague ones

### Resource Management
- Monitor API usage in Google AI Studio
- Close unused browser tabs
- Restart services if memory usage grows high
- Use production build (`npm run build`) for deployment

## 🔐 Security Best Practices

### API Key Security
- **Never** commit `.env` file to version control
- `.gitignore` is configured to exclude `.env` automatically
- Rotate API keys periodically
- Use separate API keys for development and production

### Data Privacy
- CSV files are processed in-memory only
- No data is permanently stored on the server
- Files are deleted after session ends
- Be cautious with sensitive or PII data

### Network Security
- CORS is configured for local development only
- Update CORS settings in `flask_app.py` for production
- Use HTTPS in production environments
- Implement authentication if deploying publicly

## 🚀 Deployment

### Production Build

1. **Frontend Build**
```bash
cd frontend
npm run build
```
This creates optimized static files in `frontend/dist/`

2. **Backend Configuration**
- Update CORS settings for your domain
- Set environment variables on server
- Use production WSGI server (Gunicorn, uWSGI)

3. **Hosting Options**
- **Vercel/Netlify**: Frontend static files
- **Heroku/Railway**: Backend Flask app
- **AWS/Azure/GCP**: Full stack deployment
- **Docker**: Containerized deployment

### Environment Variables for Production
```env
GOOGLE_API_KEY=your-production-key
FLASK_ENV=production
FRONTEND_URL=https://your-domain.com
```

## 🎨 Customization

### Adding New Chart Types
Edit the chart generation functions in `flask_app.py` to add custom chart configurations.

### Modifying UI Theme
Update Tailwind classes in React components or modify `frontend/src/index.css`.

### Custom System Prompts
Edit prompts in `langchain_utils.py` to customize AI behavior and response style.

### Extended Data Processing
Modify `CSVAnalyzer` class in `langchain_utils.py` for custom data cleaning or transformations.

## 📚 API Documentation

### Backend Endpoints

**POST /upload**
- Upload CSV file
- Returns: Data preview and column information

**POST /query**
- Send natural language query
- Body: `{ query: string, csv_data: object }`
- Returns: AI response with optional charts

**POST /generate-dashboard**
- Generate multi-chart dashboard
- Body: `{ query: string, csv_data: object }`
- Returns: Array of chart configurations

**GET /health**
- Health check endpoint
- Returns: Server status

## 🧪 Development

### Running Tests
```bash
# Backend tests (if available)
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ESLint configured in frontend
- Run linter: `npm run lint` in frontend directory

### Hot Reload
- Flask: Auto-reloads on file changes (debug mode)
- Vite: Instant HMR (Hot Module Replacement)

## 📚 Resources & Documentation

- [LangChain Documentation](https://docs.langchain.com)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Flask Documentation](https://flask.palletsprojects.com)
- [React Documentation](https://react.dev)
- [Chart.js Documentation](https://www.chartjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vite Documentation](https://vite.dev)

## 💡 Tips & Best Practices

### Data Quality
1. **Clean Headers**: Use descriptive, consistent column names
2. **Data Types**: Ensure proper data types (numbers, dates, strings)
3. **Missing Values**: Handle or document missing data appropriately
4. **Consistency**: Use consistent formats throughout the file

### Query Writing
1. **Be Specific**: "Show sales by region for Q1 2024" vs "Show sales"
2. **Use Column Names**: Reference actual column names from your data
3. **Specify Chart Types**: "Create a line chart" vs "Show data"
4. **Multiple Dimensions**: "Compare X by Y over time"

### API Cost Management
1. **Monitor Usage**: Check Google AI Studio dashboard regularly
2. **Optimize Queries**: Avoid redundant or overly broad queries
3. **Batch Operations**: Combine related questions when possible
4. **Cache Results**: Store and reuse common analyses

### File Size Management
1. **Under 50MB**: Optimal performance
2. **50-100MB**: Works but may be slower
3. **Over 100MB**: Consider preprocessing or sampling
4. **Sampling**: Use representative subsets for very large datasets

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed description
2. **Suggest Features**: Share ideas for improvements
3. **Submit PRs**: Fork, create feature branch, submit pull request
4. **Improve Docs**: Help make documentation clearer

### Contribution Guidelines
- Follow existing code style
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📄 License

This project is open source and available under the MIT License.

## 🏆 Acknowledgments

- **Google Gemini**: Powerful LLM for natural language understanding
- **LangChain**: Excellent framework for LLM applications
- **Chart.js**: Beautiful, responsive charts
- **React & Vite**: Modern, fast development experience
- **Open Source Community**: For amazing tools and libraries

## 📞 Support & Contact

### Getting Help
1. **Check Documentation**: Review this README thoroughly
2. **Search Issues**: Look for similar problems in issues
3. **Error Messages**: Read error messages carefully—they often contain solutions
4. **Google AI Studio**: Check API status and quota

### Common Resources
- [Google AI Studio](https://aistudio.google.com)
- [Project Repository](https://github.com/your-repo) (if applicable)
- [Stack Overflow](https://stackoverflow.com) for technical questions

---

**Happy Analyzing! 🎉📊**
