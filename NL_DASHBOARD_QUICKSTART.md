# Natural Language Dashboard - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Launch the App
```bash
streamlit run app.py
```

### Step 2: Load Your Data
1. Click **"Browse files"** in the sidebar
2. Upload your CSV file
3. Click **"Load Data"** button

### Step 3: Build Your Dashboard
1. Navigate to the **"🎨 Dashboard Builder"** tab
2. Choose one of the AI-suggested queries OR type your own
3. Click **"🚀 Generate Dashboard"**

That's it! Your custom dashboard is ready.

---

## 💡 Quick Examples by Use Case

### Sales Analysis
```
"Show monthly sales trends by region"
"Compare product revenue across quarters"
"Display top 10 products by total revenue"
```

### Customer Insights
```
"Show customer distribution by segment"
"Compare average purchase value across age groups"
"Display the relationship between customer tenure and spending"
```

### Operational Metrics
```
"Show weekly production output over the last 6 months"
"Compare efficiency scores by department"
"Display the correlation between staff count and productivity"
```

### Financial Analysis
```
"Show quarterly revenue trends broken down by division"
"Compare expenses by category for 2023"
"Display profit margins over time"
```

---

## 🎯 Writing Effective Queries

### Formula: WHAT + HOW + WHEN (optional) + WHERE (optional)

#### Examples:

**Basic Trend:**
```
"Show [metric] over [time period]"
→ "Show revenue over the past year"
```

**Comparison:**
```
"Compare [metric] across [categories]"
→ "Compare sales across regions"
```

**Breakdown:**
```
"Show [metric] by [category] for [time period]"
→ "Show orders by product type for Q3"
```

**Correlation:**
```
"Display the relationship between [metric1] and [metric2]"
→ "Display the relationship between marketing spend and sales"
```

---

## 🔥 Pro Tips

### 1. Use Natural Language
✅ "Show me how sales changed this year"
❌ "SELECT sales_amount FROM data WHERE year = 2023"

### 2. Don't Worry About Exact Column Names
- The system matches intelligently
- "sales" will find "Total_Sales", "sales_amount", etc.
- "region" will find "Region_Name", "sales_region", etc.

### 3. Specify Time Periods
- "last quarter", "Q3", "2023", "past 6 months"
- Makes time-based analysis more precise

### 4. Use Comparison Keywords
- "compare", "versus", "breakdown by", "grouped by"
- Helps system understand categorical analysis

### 5. Mention Chart Types (Optional)
- "scatter plot for correlation"
- "bar chart comparing categories"
- "line chart showing trends"

---

## 📊 What You Get

Each generated dashboard includes:

✨ **1-3 Interactive Charts**
- Automatically selected based on your query
- Optimized for your data types

📈 **Visual Types**
- Line charts (trends over time)
- Bar charts (category comparisons)
- Scatter plots (correlations)
- Pie alternatives (distributions)

🔍 **Data Exploration**
- Hover for detailed values
- Expandable data tables
- Row counts and summaries

---

## 🎨 Example Workflow

### Scenario: Analyzing E-commerce Sales Data

**Step 1: Upload** `sales_data.csv`

**Step 2: Try Suggested Query**
- Click: "Show revenue trends over time by category"

**Step 3: Explore Generated Charts**
- View line chart of revenue over time
- See breakdown by product category
- Expand data table to see raw numbers

**Step 4: Ask Follow-up**
- Type: "Compare average order value by customer segment"
- Generate new dashboard

**Step 5: Deep Dive**
- Type: "Show correlation between discount percentage and sales volume"
- Analyze scatter plot

---

## 🛠️ Common Patterns

### Time-Based Analysis
```
"Show [metric] trends over [period]"
"Monthly breakdown of [metric]"
"Year-over-year comparison"
```

### Category Comparison
```
"Compare [metric] by [category]"
"Breakdown of [metric] across [groups]"
"Top N [items] by [metric]"
```

### Relationship Discovery
```
"Correlation between [metric1] and [metric2]"
"Relationship of [X] to [Y]"
"How does [A] affect [B]"
```

### Distribution Analysis
```
"Distribution of [metric] by [category]"
"Composition of [total] across [segments]"
"Percentage breakdown"
```

---

## ❓ Troubleshooting

### "Could not generate visualizations"
**Fix**: Be more specific about what you want to see
- Instead of: "show data"
- Try: "show sales by month"

### Wrong columns selected
**Fix**: Use more specific column name parts
- Instead of: "show revenue"
- Try: "show monthly_revenue_total"

### Empty charts
**Fix**: Check your data has values for those columns
- Verify column names in the data preview
- Ensure numeric columns for calculations

---

## 🎓 Learn More

- **[Complete Feature Guide](NL_DASHBOARD_GUIDE.md)** - Deep dive into capabilities
- **[Project Documentation](PROJECT_DOCS.md)** - Technical architecture
- **[Main README](README.md)** - Full application guide

---

## 🌟 Next Steps

1. ✅ Try the AI-suggested queries first
2. ✅ Experiment with different phrasings
3. ✅ Combine multiple metrics in one query
4. ✅ Use the 💬 AI Chat tab for data questions
5. ✅ Explore the 📊 Quick Insights tab for automatic analysis

**Happy Dashboard Building! 🎉**
