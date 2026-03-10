# DataLens AI - API Reference

Complete API documentation for the Flask backend.

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Health Check

Check if the API server is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "message": "DataLens AI API is running"
}
```

**Status Codes:**
- `200 OK` - Server is healthy

---

### 2. Upload CSV

Upload a CSV file for analysis.

**Endpoint:** `POST /upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: FormData with `file` field

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:5000/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
```

**Success Response:** `200 OK`
```json
{
  "message": "File uploaded successfully",
  "filename": "sales_data.csv",
  "columns": ["Date", "Product", "Revenue", "Region"],
  "row_count": 1500,
  "preview": [
    {
      "Date": "2024-01-01",
      "Product": "Widget A",
      "Revenue": 5000,
      "Region": "North"
    }
  ],
  "data_types": {
    "Date": "object",
    "Product": "object",
    "Revenue": "int64",
    "Region": "object"
  },
  "csv_data": {
    "columns": ["Date", "Product", "Revenue", "Region"],
    "data": [ /* ... array of arrays ... */ ]
  }
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "No file provided"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "Invalid file format. Please upload a CSV file."
}
```

**Status Codes:**
- `200 OK` - File uploaded and processed successfully
- `400 Bad Request` - Invalid file or no file provided
- `500 Internal Server Error` - Server error during processing

---

### 3. Query Data

Send a natural language query about the uploaded data.

**Endpoint:** `POST /query`

**Request:**
- Content-Type: `application/json`

**Body:**
```json
{
  "query": "Show sales trends by region",
  "csv_data": {
    "columns": ["Date", "Product", "Revenue", "Region"],
    "data": [ /* ... array of arrays ... */ ]
  }
}
```

**Success Response:** `200 OK`
```json
{
  "response": "Based on the data, sales trends vary significantly by region...",
  "charts": [
    {
      "id": "chart_1",
      "type": "line",
      "title": "Sales Trends by Region",
      "description": "Monthly revenue trends across all regions",
      "data": {
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "datasets": [
          {
            "label": "North",
            "data": [5000, 6000, 5500, 7000],
            "borderColor": "rgb(75, 192, 192)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)"
          },
          {
            "label": "South",
            "data": [4500, 5000, 5200, 6000],
            "borderColor": "rgb(255, 99, 132)",
            "backgroundColor": "rgba(255, 99, 132, 0.2)"
          }
        ]
      },
      "options": {
        "responsive": true,
        "plugins": {
          "legend": {
            "position": "top"
          }
        }
      }
    }
  ]
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "Query and csv_data are required"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "Cannot answer this query with the available data"
}
```

**Status Codes:**
- `200 OK` - Query processed successfully
- `400 Bad Request` - Missing required fields or invalid query
- `500 Internal Server Error` - Server error during processing

---

### 4. Generate Dashboard

Generate a multi-chart dashboard from a natural language query.

**Endpoint:** `POST /generate-dashboard`

**Request:**
- Content-Type: `application/json`

**Body:**
```json
{
  "query": "Show me a comprehensive sales overview with trends, regional breakdown, and product comparison",
  "csv_data": {
    "columns": ["Date", "Product", "Revenue", "Region"],
    "data": [ /* ... array of arrays ... */ ]
  }
}
```

**Success Response:** `200 OK`
```json
{
  "summary": "This dashboard provides a comprehensive view of sales data...",
  "charts": [
    {
      "id": "chart_1",
      "type": "line",
      "title": "Revenue Trends Over Time",
      "description": "Monthly revenue progression",
      "data": { /* ... Chart.js data structure ... */ },
      "options": { /* ... Chart.js options ... */ }
    },
    {
      "id": "chart_2",
      "type": "bar",
      "title": "Sales by Region",
      "description": "Regional sales comparison",
      "data": { /* ... Chart.js data structure ... */ },
      "options": { /* ... Chart.js options ... */ }
    },
    {
      "id": "chart_3",
      "type": "pie",
      "title": "Product Mix",
      "description": "Revenue distribution by product",
      "data": { /* ... Chart.js data structure ... */ },
      "options": { /* ... Chart.js options ... */ }
    }
  ]
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "Query and csv_data are required"
}
```

**Status Codes:**
- `200 OK` - Dashboard generated successfully
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Server error during processing

---

## Data Structures

### CSV Data Format

The `csv_data` object should follow this structure:

```json
{
  "columns": ["Column1", "Column2", "Column3"],
  "data": [
    ["value1", "value2", "value3"],
    ["value4", "value5", "value6"]
  ]
}
```

**Notes:**
- `columns`: Array of column names (strings)
- `data`: Array of rows, where each row is an array of values
- Data types are inferred from values (numbers, strings, dates)

### Chart Data Format

Charts follow the Chart.js data structure:

```json
{
  "id": "unique_chart_id",
  "type": "line|bar|pie|doughnut|scatter|radar|polarArea",
  "title": "Chart Title",
  "description": "Chart description for context",
  "data": {
    "labels": ["Label1", "Label2", "Label3"],
    "datasets": [
      {
        "label": "Dataset Name",
        "data": [10, 20, 30],
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": true,
    "plugins": {
      "legend": {
        "display": true,
        "position": "top"
      },
      "title": {
        "display": true,
        "text": "Chart Title"
      }
    }
  }
}
```

## Chart Types

The API supports the following chart types:

| Type | Use Case | Example Query |
|------|----------|---------------|
| `line` | Trends over time | "Show sales trends over months" |
| `bar` | Category comparisons | "Compare revenue by region" |
| `pie` | Part-to-whole relationships | "Show product revenue breakdown" |
| `doughnut` | Part-to-whole (with center hole) | "Display customer segment distribution" |
| `scatter` | Correlations between variables | "Plot price vs. demand correlation" |
| `radar` | Multi-dimensional comparisons | "Compare product features" |
| `polarArea` | Magnitude comparisons in circular form | "Show regional market share" |
| `area` | Volume/magnitude over time | "Display cumulative revenue" |

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid input or missing required fields
- `404 Not Found` - Endpoint doesn't exist
- `413 Request Entity Too Large` - File size exceeds limit
- `500 Internal Server Error` - Server-side processing error

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:
- API key authentication
- Request rate limiting
- Usage quotas per user

## CORS

CORS is enabled for local development:
- Allowed origin: `http://localhost:5173`
- Methods: GET, POST, OPTIONS
- Headers: Content-Type

For production, update CORS settings in `flask_app.py`.

## Authentication

Currently no authentication is required. For production:
- Implement JWT or API key authentication
- Add user session management
- Secure sensitive endpoints

## Best Practices

### 1. Data Size
- Keep CSV files under 100MB for optimal performance
- Consider pagination for very large datasets
- Use sampling for exploratory analysis

### 2. Query Optimization
- Be specific in natural language queries
- Reference actual column names when possible
- Break complex queries into smaller parts

### 3. Error Handling
- Always check response status codes
- Handle errors gracefully in the UI
- Provide meaningful error messages to users

### 4. Performance
- Cache uploaded data on the client side
- Debounce query requests
- Use loading states for better UX

## Examples

### Complete Upload and Query Flow

```javascript
// 1. Upload CSV
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// 2. Query the data
const queryData = async (query, csvData) => {
  const response = await fetch('http://localhost:5000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      csv_data: csvData
    })
  });
  
  return await response.json();
};

// 3. Use the results
const file = document.getElementById('fileInput').files[0];
const uploadResult = await uploadFile(file);

if (uploadResult.csv_data) {
  const queryResult = await queryData(
    "Show sales trends by region",
    uploadResult.csv_data
  );
  
  // Render charts
  queryResult.charts?.forEach(chart => {
    renderChart(chart);
  });
}
```

## Support

For API issues or questions:
- Check error messages carefully
- Verify your request format matches examples
- Ensure CSV data is properly formatted
- Check browser console for detailed errors

---

**Last Updated:** March 2026  
**API Version:** 1.0  
**Framework:** Flask 3.x with Flask-CORS
