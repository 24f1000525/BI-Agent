import pandas as pd
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE


class CSVAnalyzer:
    """Handles CSV data analysis and context preparation for LangChain."""
    
    def __init__(self):
        self.df = None
        self.columns_info = None
        self.data_summary = None
    
    def load_data(self, file_path):
        """Load CSV file and extract data information."""
        # List of encodings to try
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        
        for encoding in encodings:
            try:
                self.df = pd.read_csv(file_path, encoding=encoding)
                self._extract_data_info()
                return True
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # If it's not an encoding error, raise it
                if encoding == encodings[-1]:  # Last encoding attempt
                    raise Exception(f"Error loading CSV file: {str(e)}")
                continue
        
        # If all encodings failed, try with error handling
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8', encoding_errors='replace')
            self._extract_data_info()
            return True
        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")
    
    def _extract_data_info(self):
        """Extract column info and data summary from loaded DataFrame."""
        if self.df is None:
            return
        
        self.columns_info = {
            "columns": list(self.df.columns),
            "shape": self.df.shape,
            "dtypes": self.df.dtypes.to_dict(),
            "sample": self.df.head(3).to_dict(orient='records')
        }
        
        self.data_summary = f"""
Dataset Summary:
- Total Rows: {self.df.shape[0]}
- Total Columns: {self.df.shape[1]}
- Columns: {', '.join(self.df.columns)}
- Data Types: {dict(self.df.dtypes)}
- Missing Values: {self.df.isnull().sum().to_dict()}
"""
    
    def get_sample_data(self, rows=5):
        """Get sample data from the uploaded CSV."""
        if self.df is None:
            return None
        return self.df.head(rows)
    
    def get_data_description(self):
        """Get statistical description of the data."""
        if self.df is None:
            return None
        return self.df.describe()
    
    def get_context(self):
        """Get formatted context about the data for LLM."""
        if self.df is None:
            return "No data loaded"
        
        context = f"""
You have access to the following dataset:
{self.data_summary}

Sample Data (first 3 rows):
{self.df.head(3).to_string()}
"""
        return context


class LangChainChat:
    """LangChain-based conversational AI for data analysis."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or GOOGLE_API_KEY
        self.model_candidates = self._build_model_candidates()
        self.active_model = self.model_candidates[0]
        self.llm = self._create_llm(self.active_model)
        self.chat_history = ChatMessageHistory()
        self.csv_analyzer = CSVAnalyzer()

    def _build_model_candidates(self):
        """Build ordered unique model candidates for runtime fallback."""
        candidates = [
            MODEL_NAME,
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
        ]
        # Preserve order while removing duplicates/empty values.
        seen = set()
        unique_candidates = []
        for model in candidates:
            if model and model not in seen:
                seen.add(model)
                unique_candidates.append(model)
        return unique_candidates

    def _create_llm(self, model_name):
        """Create a Gemini client for a specific model without probing."""
        return ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model=model_name,
            temperature=TEMPERATURE
        )

    def _invoke_with_model_fallback(self, messages):
        """Invoke LLM with automatic fallback across candidate models."""
        last_error = None
        for model_name in self.model_candidates:
            try:
                llm = self._create_llm(model_name)
                response = llm.invoke(messages)
                self.llm = llm
                self.active_model = model_name
                return response
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            "Unable to call any Gemini model. "
            "Please set MODEL_NAME in .env to a model available for your API key. "
            f"Tried: {', '.join(self.model_candidates)}. "
            f"Last error: {str(last_error)}"
        )
    
    def load_dataset(self, file_path):
        """Load dataset for analysis."""
        self.csv_analyzer.load_data(file_path)
    
    def get_data_context(self):
        """Get the data context for the chat."""
        return self.csv_analyzer.get_context()

    def _find_column_case_insensitive(self, target_name):
        """Return matching column name from DataFrame with case-insensitive lookup."""
        if self.csv_analyzer.df is None:
            return None

        cols = list(self.csv_analyzer.df.columns)
        lower_map = {str(col).strip().lower(): col for col in cols}
        return lower_map.get(target_name.strip().lower())

    def _normalize_claims_series(self, series):
        """Normalize claims values like '1,234' or '12,000.5' into numeric form."""
        as_text = series.astype(str).str.strip()
        # Keep only digits, minus sign, and decimal point for robust numeric coercion.
        cleaned = as_text.str.replace(r"[^\d\.-]", "", regex=True)
        return pd.to_numeric(cleaned, errors="coerce")

    def _normalize_year_series(self, series):
        """Normalize year values from formats like '2021', '2021-22', 'FY 2021-22'."""
        raw = series.astype(str).str.strip()

        # First, try direct numeric conversion for clean year columns.
        numeric_year = pd.to_numeric(raw, errors="coerce")

        # Then extract the first 4-digit year from textual formats.
        extracted = raw.str.extract(r"(19\d{2}|20\d{2}|21\d{2})", expand=False)
        extracted_year = pd.to_numeric(extracted, errors="coerce")

        return numeric_year.fillna(extracted_year)

    def _build_year_claims_grouped(self, df, year_col, claims_col):
        """Build grouped year-wise claims DataFrame after robust normalization."""
        year_series = self._normalize_year_series(df[year_col])
        claims_series = self._normalize_claims_series(df[claims_col])
        valid_df = pd.DataFrame({"year": year_series, "claims": claims_series}).dropna()

        if valid_df.empty:
            return valid_df, valid_df

        grouped = (
            valid_df.groupby("year", as_index=False)["claims"]
            .sum()
            .sort_values("year")
        )
        return valid_df, grouped

    def _handle_claims_year_query(self, user_query):
        """Handle common claims/year aggregation queries deterministically with pandas."""
        if self.csv_analyzer.df is None:
            return None

        query = (user_query or "").lower()
        has_year_in_query = bool(re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", query))
        if "claim" not in query or ("year" not in query and not has_year_in_query):
            return None

        df = self.csv_analyzer.df.copy()
        claims_col = self._find_column_case_insensitive("total_claims_no")
        year_col = self._find_column_case_insensitive("year")

        if not claims_col or not year_col:
            return None

        valid_df, grouped = self._build_year_claims_grouped(df, year_col, claims_col)

        if valid_df.empty:
            return "I found `year` and `total_claims_no`, but values are not numeric enough to aggregate."

        chart_keywords = ("plot", "graph", "chart", "visual", "visualize", "vs")
        if any(keyword in query for keyword in chart_keywords):
            chart_df = grouped.copy()
            chart_df["year"] = chart_df["year"].astype(int)
            chart_df["total_claims_no"] = chart_df["claims"].astype(float)
            chart_records = chart_df[["year", "total_claims_no"]].to_dict(orient="records")
            lines = ["Year-wise total `total_claims_no`:"]
            for _, row in chart_df.iterrows():
                lines.append(f"- {int(row['year'])}: {int(row['total_claims_no']):,}")
            return {
                "response": "\n".join(lines),
                "chart": {
                    "type": "line",
                    "x": "year",
                    "y": "total_claims_no",
                    "data": chart_records,
                    "title": "Total Claims by Year"
                }
            }

        years = [int(match) for match in re.findall(r"\b(19\d{2}|20\d{2}|21\d{2})\b", query)]

        if len(years) >= 2:
            start_year = min(years)
            end_year = max(years)
            filtered = valid_df[(valid_df["year"] >= start_year) & (valid_df["year"] <= end_year)]

            total = int(filtered["claims"].sum())
            return (
                f"Total `total_claims_no` from {start_year} to {end_year}: **{total:,}** "
                f"(based on {len(filtered)} records)."
            )

        if len(years) == 1:
            target_year = years[0]
            filtered = valid_df[valid_df["year"] == target_year]
            total = int(filtered["claims"].sum())
            return (
                f"Total `total_claims_no` in {target_year}: **{total:,}** "
                f"(based on {len(filtered)} records)."
            )

        lines = ["Year-wise total `total_claims_no`:"]
        for _, row in grouped.iterrows():
            lines.append(f"- {int(row['year'])}: {int(row['claims']):,}")
        return "\n".join(lines)
    
    def chat(self, user_query):
        """Process user query with context from loaded data."""
        try:
            if self.csv_analyzer.df is None:
                return "Please upload a CSV file first to start analyzing data."

            # First try deterministic handling for common aggregation requests.
            deterministic_response = self._handle_claims_year_query(user_query)
            if deterministic_response is not None:
                self.chat_history.add_user_message(user_query)
                history_text = deterministic_response
                if isinstance(deterministic_response, dict):
                    history_text = deterministic_response.get("response", "")
                self.chat_history.add_ai_message(history_text)
                return deterministic_response
            
            # Prepare the system prompt with data context
            data_context = self.get_data_context()
            
            system_prompt = f"""You are a helpful data analysis assistant powered by advanced AI. 
You have access to a dataset that has been uploaded by the user.

{data_context}

Help the user understand and analyze their data. Provide insights, answer questions, and suggest relevant analysis.
Be clear, concise, and data-driven in your responses.
Use only columns that actually exist in the dataset and preserve exact column names/case.
If a requested field is missing, clearly say which column is unavailable and ask for a valid alternative.
Do not output Python code, SQL, or plotting scripts unless the user explicitly asks for code."""
            
            # Use direct message objects so braces in dataset context are treated as literal text.
            response = self._invoke_with_model_fallback([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ])
            
            # Store in memory
            self.chat_history.add_user_message(user_query)
            self.chat_history.add_ai_message(response.content)
            
            return response.content
        
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_data_insights(self):
        """Generate initial insights about the data."""
        try:
            if self.csv_analyzer.df is None:
                return "No data loaded"
            
            data_context = self.get_data_context()
            
            prompt = f"""{data_context}

Based on the dataset above, provide 3-5 key insights or observations about this data. 
Focus on interesting patterns, distributions, or characteristics."""
            
            response = self._invoke_with_model_fallback([
                SystemMessage(content="You are a data analysis expert. Provide clear, actionable insights from the data."),
                HumanMessage(content=prompt)
            ])
            
            return response.content
        
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def get_chat_history(self):
        """Get chat history."""
        return self.chat_history.messages
    
    def clear_memory(self):
        """Clear chat history."""
        self.chat_history.clear()
    
    def get_sample_data(self, rows=5):
        """Get sample data from the dataset."""
        return self.csv_analyzer.get_sample_data(rows)
    
    def suggest_dashboard_queries(self):
        """Generate suggested dashboard queries based on the dataset."""
        if self.csv_analyzer.df is None:
            return []
        
        df = self.csv_analyzer.df
        suggestions = []
        
        numeric_cols = list(df.select_dtypes(include=['number']).columns)
        categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
        
        # Detect date columns
        date_cols = []
        for col in df.columns:
            col_lower = str(col).lower()
            if 'date' in col_lower or 'year' in col_lower or 'month' in col_lower:
                date_cols.append(col)
        
        # Generate suggestions
        if date_cols and numeric_cols:
            suggestions.append(f"Show the trend of {numeric_cols[0]} over {date_cols[0]}")
        
        if categorical_cols and numeric_cols:
            suggestions.append(f"Compare {numeric_cols[0]} across different {categorical_cols[0]}")
        
        if len(numeric_cols) >= 2:
            suggestions.append(f"Show the correlation between {numeric_cols[0]} and {numeric_cols[1]}")
        
        if categorical_cols and numeric_cols:
            suggestions.append(f"Display the distribution of {numeric_cols[0]} by {categorical_cols[0]}")
        
        if len(categorical_cols) >= 2 and numeric_cols:
            suggestions.append(f"Break down {numeric_cols[0]} by {categorical_cols[0]} and {categorical_cols[1]}")
        
        return suggestions[:5]
