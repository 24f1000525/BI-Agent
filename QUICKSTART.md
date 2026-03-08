# 🚀 Quick Start Guide

## One-Time Setup (5 minutes)

### Step 1: Get Google Gemini API Key
1. Go to [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the key (save it securely)

### Step 2: Setup Environment
```bash
# Navigate to project folder
cd genai-app

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Copy template
copy .env.example .env

# Edit .env and add your API key like:
# GOOGLE_API_KEY=your-google-api-key-here
```

## Running the App

```bash
# Make sure venv is activated
streamlit run app.py
```

Browser opens automatically at `http://localhost:8501`

## Using the App

1. **Sidebar**: Click file uploader
2. **Choose CSV**: Select any CSV file
3. **Load Data**: Click the button
4. **Ask Questions**: Type in chat box below
5. **Done!** Get instant AI insights

## Example CSV Files to Try

- **Sample provided**: `India Life Insurance Claims.csv` (in parent folder)
- **Your own data**: Any CSV with rows and columns

## Quick Keyboard Shortcuts

- `Enter`: Send message in chat
- `Ctrl+C`: Stop running app (terminal)
- `R`: Refresh browser page

## Common Questions

**Q: What questions can I ask?**
A: Anything about your data! Statistics, trends, patterns, summaries, recommendations.

**Q: How much does this cost?**
A: Google Gemini has a generous free tier and low cost for paid usage

**Q: Can I use my own CSV?**
A: YES! Any CSV file works. Upload in sidebar.

**Q: What file size limit?**
A: 100MB default (edit in config.py if needed)

## Troubleshooting

**"API Key not found"**
→ Check .env file exists and has correct key

**"CSV load error"**
→ Ensure CSV is valid (open in Excel/notepad first)

**"Network error"**
→ Check internet connection, Google API server status

## Tips for Best Results

✅ Use clean, well-formatted CSV files
✅ Ask clear, specific questions
✅ Keep uploaded files under 50MB
✅ Monitor API usage in Google AI Studio
❌ Don't share your API key
❌ Don't upload sensitive personal data

## Next Steps

1. Read full README.md for detailed docs
2. Try with different CSV files
3. Experiment with different questions
4. Customize system prompts in langchain_utils.py
5. Customize appearance in app.py

---

**Having issues?** Check README.md Troubleshooting section! 🆘
