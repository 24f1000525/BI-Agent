# DataLens AI - Project Overview

Complete guide to understanding the DataLens AI codebase and architecture.

## 📁 Project Structure

```
genai-app/
│
├── 📄 Documentation
│   ├── README.md              # Complete project documentation
│   ├── QUICKSTART.md          # 5-minute getting started guide
│   ├── API_REFERENCE.md       # Complete API documentation
│   ├── CONTRIBUTING.md        # Developer contribution guide
│   └── PROJECT_OVERVIEW.md    # This file
│
├── ⚙️ Configuration
│   ├── .env                    # Environment variables (not in git)
│   ├── .env.example           # Environment template
│   ├── .gitignore             # Git ignore rules
│   ├── config.py              # Application configuration
│   ├── requirements.txt       # Python dependencies
│   ├── default_data.json      # Default/fallback data
│   └── __pycache__/           # Python cache (ignored)
│
├── 🔧 Setup Scripts
│   ├── setup.bat              # Windows setup script
│   ├── setup.sh               # Linux/macOS setup script
│   ├── start.bat              # Windows start script
│   └── start.sh               # Linux/macOS start script
│
├── 🐍 Backend (Python/Flask)
│   ├── flask_app.py           # Main Flask API server (includes chart generation)
│   ├── langchain_utils.py     # LangChain & AI integration
│   └── config.py              # Application configuration
│
├── ⚛️ Frontend (React/Vite)
│   └── frontend/
│       ├── package.json       # Node.js dependencies
│       ├── package-lock.json  # Locked dependency versions
│       ├── vite.config.js     # Vite build configuration
│       ├── eslint.config.js   # ESLint rules
│       ├── index.html         # HTML entry point
│       ├── README.md          # Frontend-specific docs
│       │
│       ├── public/            # Static assets
│       │   └── vite.svg       # Vite logo
│       │
│       ├── src/               # React source code
│       │   ├── main.jsx       # React entry point
│       │   ├── App.jsx        # Main application component
│       │   ├── index.css      # Global styles & Tailwind
│       │   │
│       │   ├── components/    # React components
│       │   │   ├── Navbar.jsx          # Top navigation bar
│       │   │   ├── Sidebar.jsx         # Left sidebar with history
│       │   │   ├── QueryBox.jsx        # Query input component
│       │   │   ├── ChartsGrid.jsx      # Chart display grid
│       │   │   ├── StatsGrid.jsx       # Statistics cards
│       │   │   ├── Overview.jsx        # Data overview panel
│       │   │   ├── Summary.jsx         # Data summary display
│       │   │   ├── Loading.jsx         # Loading spinner
│       │   │   ├── ErrorBanner.jsx     # Error messages
│       │   │   ├── EmptyState.jsx      # Empty state UI
│       │   │   ├── Header.jsx          # Section headers
│       │   │   ├── HistoryPanel.jsx    # Query history panel
│       │   │   └── ThreeBackground.jsx # 3D animated background
│       │   │
│       │   └── assets/        # Images, icons, etc.
│       │       └── react.svg  # React logo
│       │
│       ├── node_modules/      # Node dependencies (ignored)
│       └── dist/              # Production build (ignored)
│
└── 🗂️ Version Control
    └── .git/                  # Git repository data
```

## 🏗️ Architecture

### Backend Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Application                      │
│                     (flask_app.py)                        │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼─────────┐    ┌───────▼──────────┐
│  LangChain Utils│    │ Chart Generators  │
│ (langchain_utils│    │  - dashboard_gen  │
│      .py)        │    │  - orchestrator   │
│                 │    │  - dynamic_gen    │
│  - CSV Analyzer │    │                   │
│  - LLM Chat     │    │  Chart.js Config  │
│  - Data Valid.  │    │  Multi-chart Logic│
└─────────┬───────┘    └─────────┬─────────┘
          │                      │
          │     ┌────────────────┘
          │     │
     ┌────▼─────▼────┐
     │ Google Gemini  │
     │   AI Model     │
     └────────────────┘
```

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      App.jsx                             │
│         (Main State & API Communication)                 │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼─────┐ ┌──▼────┐ ┌────▼─────┐
│   Navbar    │ │Sidebar│ │QueryBox  │
└─────────────┘ └───────┘ └──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
            ┌─────▼──────┐          ┌──────▼─────┐
            │ChartsGrid  │          │ Overview   │
            │ (Chart.js) │          │ StatsGrid  │
            └────────────┘          └────────────┘
```

### Data Flow

```
User Action
    │
    ▼
┌────────────────┐
│ React Frontend │  ← User uploads CSV or submits query
└───────┬────────┘
        │ HTTP POST
        ▼
┌────────────────┐
│  Flask Backend │  ← Receives request at /upload or /query
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Data Validation│  ← Validates CSV structure and query
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  LangChain     │  ← Processes with Google Gemini API
│  + Gemini AI   │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Chart Generator│  ← Converts AI response to Chart.js format
└───────┬────────┘
        │ JSON Response
        ▼
┌────────────────┐
│ React Frontend │  ← Renders charts and displays insights
└────────────────┘
```

## 🔑 Key Components

### Backend Components

#### 1. flask_app.py
**Purpose:** Main Flask server handling HTTP requests

**Key Functions:**
- `upload()` - Handles CSV file uploads
- `query()` - Processes natural language queries
- `generate_dashboard()` - Creates multi-chart dashboards
- `health()` - Health check endpoint

**Endpoints:**
- `POST /upload` - File upload
- `POST /query` - Single query
- `POST /generate-dashboard` - Multi-chart generation
- `GET /health` - Server status

#### 2. langchain_utils.py
**Purpose:** LangChain integration and CSV analysis

**Key Classes:**
- `LangChainChat` - Manages LLM conversations
- `CSVAnalyzer` - Analyzes CSV data structure

**Key Functions:**
- `chat()` - Send queries to Gemini AI
- `analyze()` - Analyze CSV columns and data types
- Data validation and preprocessing

#### 3. config.py
**Purpose:** Application configuration and settings

**Key Functions:**
- Environment variable management
- App title and description
- Model configuration (Gemini settings)
- File size limits and constraints

**Note:** All chart generation logic is built directly into `flask_app.py` for simplicity and maintainability.

### Frontend Components

#### Core Application

**App.jsx**
- Central state management
- API communication
- Route coordination
- Error handling

**main.jsx**
- React application entry point
- Root DOM rendering

#### Navigation Components

**Navbar.jsx**
- Top navigation bar
- Application branding
- Actions toolbar

**Sidebar.jsx**
- Left sidebar panel
- Query history display
- Navigation links

#### Data Input Components

**QueryBox.jsx**
- Query input field
- AI-suggested queries
- Submit functionality

#### Data Display Components

**ChartsGrid.jsx**
- Chart display grid
- Chart.js integration
- Responsive layout

**Overview.jsx**
- Data overview panel
- Column information
- Summary statistics

**StatsGrid.jsx**
- Statistics cards
- Key metrics display
- Visual indicators

#### UI Components

**Loading.jsx** - Loading states
**ErrorBanner.jsx** - Error displays
**EmptyState.jsx** - Empty state UI
**Header.jsx** - Section headers
**HistoryPanel.jsx** - Query history
**ThreeBackground.jsx** - 3D background

## 🔄 Request Flow Examples

### Example 1: File Upload

```
1. User selects CSV file in browser
   ↓
2. Frontend sends FormData to POST /upload
   ↓
3. Flask receives file and validates format
   ↓
4. CSVAnalyzer processes the file:
   - Extracts column names
   - Determines data types
   - Generates preview
   ↓
5. Returns JSON with:
   - Column list
   - Row count
   - Data preview
   - Full CSV data structure
   ↓
6. Frontend stores data and displays overview
```

### Example 2: Natural Language Query

```
1. User types "Show sales trends by region"
   ↓
2. Frontend sends query + CSV data to POST /query
   ↓
3. Flask validates query against available columns
   ↓
4. LangChainChat sends query to Gemini AI with:
   - CSV structure
   - Available columns
   - Chart generation instructions
   ↓
5. Gemini AI responds with:
   - Text analysis
   - Chart specifications
   ↓
6. Chart generator creates Chart.js configs
   ↓
7. Validation ensures data accuracy
   ↓
8. Returns JSON with response + charts
   ↓
9. Frontend renders text and charts
```

## 🛠️ Technology Decisions

### Why Flask?
- Lightweight and fast
- Easy to understand and maintain
- Excellent Python library ecosystem
- Perfect for RESTful APIs

### Why React + Vite?
- Modern, fast development experience
- Component-based architecture
- Huge ecosystem of libraries
- Vite provides instant HMR

### Why Tailwind CSS?
- Utility-first approach
- Rapid development
- Consistent design system
- Great performance

### Why Chart.js?
- Powerful and flexible
- Excellent documentation
- React integration available
- Beautiful default styles

### Why Google Gemini?
- Advanced AI capabilities
- Generous free tier
- Excellent at reasoning
- Good structured output

### Why LangChain?
- Simplifies LLM integration
- Prompt management
- Memory and context handling
- Extensible architecture

## 📊 Data Models

### CSV Data Model
```javascript
{
  columns: string[],      // Column names
  data: any[][]          // 2D array of values
}
```

### Chart Data Model
```javascript
{
  id: string,
  type: 'line' | 'bar' | 'pie' | 'scatter' | ...,
  title: string,
  description: string,
  data: {
    labels: string[],
    datasets: [{
      label: string,
      data: number[],
      backgroundColor: string,
      borderColor: string,
      // ... more Chart.js options
    }]
  },
  options: { /* Chart.js options */ }
}
```

## 🔐 Security Considerations

### Current Implementation
- CORS enabled for local dev
- Environment variables for secrets
- No data persistence (memory only)
- Input validation on backend

### For Production
- Add authentication (JWT/OAuth)
- Implement rate limiting
- Add HTTPS/SSL
- Enhance input sanitization
- Add request logging
- Implement CSRF protection

## 🚀 Performance Considerations

### Optimizations
- Client-side data caching
- Debounced API requests
- Code splitting with React lazy
- Efficient Chart.js rendering
- Pandas for fast data processing

### Scalability
- Current: Single-server setup
- Future: Load balancing, Redis cache, CDN

## 📚 Configuration Files

### Python Configuration
**requirements.txt**
- Flask and Flask-CORS
- LangChain libraries
- Google Generative AI
- Pandas, NumPy
- Python-dotenv

**config.py**
- App title and description
- Model name (gemini-2.0-flash)
- Temperature setting
- File size limits

### Frontend Configuration
**package.json**
- React 19
- Vite 7
- Tailwind CSS v4
- Chart.js 4
- Three.js

**vite.config.js**
- React plugin
- Build optimization
- Dev server settings

## 🧪 Testing Strategy

### Current Status
Manual testing only

### Recommended Tests
- **Backend:**
  - Unit tests for data validation
  - Integration tests for API endpoints
  - Test LLM prompt effectiveness
  
- **Frontend:**
  - Component unit tests
  - Integration tests for API calls
  - E2E tests for critical flows

## 📈 Future Enhancements

### Planned Features
1. Export charts as images (PNG/SVG)
2. Save and share dashboards
3. Multiple file upload support
4. Dashboard templates
5. Real-time data updates
6. Advanced chart customization
7. User authentication
8. Data transformation tools

### Technical Debt
- Add comprehensive test coverage
- Implement proper error logging
- Add API documentation with Swagger
- Optimize for large datasets
- Add TypeScript to frontend

## 🆘 Common Issues

### Port Conflicts
**Problem:** Port 5000 or 5173 already in use
**Solution:** Kill process or change port in config

### API Key Issues
**Problem:** "API key not found"
**Solution:** Check .env file exists and has correct key

### Module Not Found
**Problem:** Python import errors
**Solution:** Activate venv and reinstall requirements

### Charts Not Rendering
**Problem:** Blank charts or errors
**Solution:** Check browser console, verify data format

## 📖 Learning Resources

### For React Development
- [React Docs](https://react.dev)
- [Vite Guide](https://vite.dev/guide)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### For Python/Flask
- [Flask Documentation](https://flask.palletsprojects.com)
- [LangChain Docs](https://docs.langchain.com)
- [Pandas Guide](https://pandas.pydata.org/docs/getting_started)

### For AI Integration
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [Prompt Engineering Guide](https://www.promptingguide.ai)

---

**Last Updated:** March 2026  
**Project Version:** 1.0  
**Maintained by:** DataLens AI Team
