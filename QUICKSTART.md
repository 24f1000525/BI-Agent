# DataLens AI - Quick Start Guide

Get up and running with DataLens AI in 5 minutes!

## 🚀 What You'll Need

- ✅ Python 3.8+ ([Download](https://www.python.org/downloads/))
- ✅ Node.js 16+ ([Download](https://nodejs.org/))
- ✅ Google Gemini API Key ([Get Free Key](https://aistudio.google.com/app/apikey))

## ⚡ Quick Setup (3 Steps)

### Step 1: Run Setup Script

**Windows:**
```cmd
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

This installs all dependencies for both backend and frontend.

### Step 2: Add Your API Key

1. Open the `.env` file that was created
2. Add your Google Gemini API key:

```env
GOOGLE_API_KEY=your-api-key-here
```

**Get your free API key:** https://aistudio.google.com/app/apikey

### Step 3: Start the App

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

Your browser will open to `http://localhost:5173` 🎉

## 📊 Using DataLens AI

### 1. Upload Your Data

Click **"Upload CSV"** and select your file.

**Example CSV format:**
```csv
Date,Product,Revenue,Region
2024-01-01,Widget A,5000,North
2024-01-02,Widget B,7500,South
2024-01-03,Widget C,6200,East
```

### 2. Ask Questions

Type natural language questions like:

- **"Show sales trends by region"**
- **"Compare revenue across products"**
- **"What are the top 5 products by revenue?"**
- **"Display monthly growth over time"**

### 3. View Results

Get:
- ✨ AI-powered text insights
- 📊 Beautiful interactive charts
- 📈 Multi-chart dashboards
- 💾 Query history

## 💡 Example Queries

### For Sales Data
```
"Show monthly revenue trends"
"Compare sales performance by region"
"What products generate the most revenue?"
"Display revenue distribution as a pie chart"
```

### For Customer Data
```
"Show customer distribution by segment"
"What's the average purchase amount per region?"
"Display customer growth trends"
"Compare customer behavior across categories"
```

### For Financial Data
```
"Show profit trends over quarters"
"Compare expenses across departments"
"What's driving revenue growth?"
"Display cash flow patterns"
```

## 🎯 Pro Tips

### Get Better Results
1. **Be Specific**: "Show Q1 2024 sales" vs "Show sales"
2. **Use Column Names**: Reference actual columns from your CSV
3. **Specify Chart Types**: "Create a line chart" or "Show as bar chart"
4. **Ask Follow-ups**: Build on previous queries

### Dashboard Creation
Ask comprehensive questions to get multiple charts:

```
"Create a sales dashboard with:
- Revenue trends over time
- Regional breakdown
- Top products
- Monthly comparison"
```

### Performance Tips
- Keep CSV files under 50MB for fast processing
- Use clear column headers
- Remove unnecessary columns before uploading

## 🐛 Troubleshooting

### "Cannot connect to backend"
**Fix:** Make sure Flask is running on port 5000
```cmd
python flask_app.py
```

### "API Key not valid"
**Fix:** Check your `.env` file has the correct key:
```env
GOOGLE_API_KEY=your-actual-key-here
```

### "Charts not showing"
**Fix:** Check browser console (F12) for errors and refresh the page

### "File upload fails"
**Fix:** Ensure:
- File is a valid CSV
- File size is under 100MB
- CSV has headers in first row

## 📚 What's Next?

### Explore Features
- 📊 Try different chart types (line, bar, pie, scatter)
- 🎨 Generate complex multi-chart dashboards
- 📜 Review your query history
- 🔍 Deep dive into specific data patterns

### Learn More
- Read [README.md](README.md) for complete documentation
- Check [API_REFERENCE.md](API_REFERENCE.md) for API details
- Explore sample queries for your data type

### Need Help?
- Review error messages—they're helpful!
- Check the Troubleshooting section in README.md
- Verify your API key has quota remaining

## ⚙️ Advanced Setup (Manual)

If you prefer manual setup:

### Backend
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Flask
python flask_app.py
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

### Configure
```bash
# Create .env file
cp .env.example .env

# Edit and add your API key
# GOOGLE_API_KEY=your-key-here
```

## 🎉 You're Ready!

Start exploring your data with AI-powered insights!

1. ✅ Upload a CSV file
2. ✅ Ask natural language questions
3. ✅ Get instant visualizations
4. ✅ Discover insights

**Need sample data?** Try these datasets:
- Sales data (date, product, revenue, region)
- Customer data (id, name, purchase_amount, segment)
- Financial data (date, category, amount, department)

---

**Happy Analyzing! 🚀📊**

For more details, see the complete [README.md](README.md)
