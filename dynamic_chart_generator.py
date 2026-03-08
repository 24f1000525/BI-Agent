"""
Dynamic Chart and Table Generator - Creates visualizations based on user intent
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class VisualizationRequest:
    """Parsed visualization request from user prompt"""
    metric_column: str
    groupby_column: Optional[str] = None
    time_column: Optional[str] = None
    filters: Dict = None
    request_type: str = 'basic'  # basic, trend, comparison, distribution, correlation
    show_table: bool = True
    sort_by: str = 'metric'  # metric, category, natural
    limit: Optional[int] = None

class DynamicChartGenerator:
    """Generate charts and tables dynamically based on user intent"""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.numeric_cols = list(dataframe.select_dtypes(include=['number']).columns)
        self.categorical_cols = list(dataframe.select_dtypes(include=['object', 'category']).columns)
        self.date_cols = self._detect_date_columns()
    
    def _detect_date_columns(self) -> List[str]:
        """Detect date/time columns"""
        date_cols = []
        for col in self.df.columns:
            col_lower = str(col).lower()
            if any(kw in col_lower for kw in ['date', 'year', 'month', 'time']):
                date_cols.append(col)
            elif self.df[col].dtype == 'datetime64[ns]':
                date_cols.append(col)
        return date_cols
    
    def _find_best_match(self, query_term: str, column_list: List[str]) -> Optional[str]:
        """Find best matching column for a query term"""
        term_lower = query_term.lower()
        
        # Exact match
        for col in column_list:
            if col.lower() == term_lower:
                return col
        
        # Partial match
        for col in column_list:
            if term_lower in col.lower() or col.lower() in term_lower:
                return col
        
        # Word overlap
        term_words = set(term_lower.split('_'))
        best_match = None
        best_score = 0
        for col in column_list:
            col_words = set(col.lower().split('_'))
            score = len(term_words & col_words)
            if score > best_score:
                best_score = score
                best_match = col
        
        return best_match if best_score > 0 else None
    
    def parse_and_generate(self, query: str) -> Dict:
        """
        Parse query and generate appropriate charts + tables
        Returns: {'charts': [...], 'tables': [...], 'summary': '...'}
        """
        query_lower = query.lower()
        
        # Determine request type
        if any(w in query_lower for w in ['trend', 'over time', 'by year', 'by month']):
            request_type = 'trend'
        elif any(w in query_lower for w in ['compare', 'vs', 'versus', 'difference']):
            request_type = 'comparison'
        elif any(w in query_lower for w in ['distribution', 'spread', 'histogram']):
            request_type = 'distribution'
        elif any(w in query_lower for w in ['correlation', 'relationship', 'scatter']):
            request_type = 'correlation'
        else:
            request_type = 'basic'
        
        # Extract metric and groupby
        metric_col = self._extract_metric(query)
        groupby_col = self._extract_groupby(query)
        time_col = self._extract_time_column(query) if request_type == 'trend' else None
        
        if not metric_col:
            return {'error': 'Could not identify metric column in query'}
        
        # Generate visualizations
        results = {
            'charts': [],
            'tables': [],
            'summary': ''
        }
        
        if request_type == 'trend' and time_col:
            results.update(self._generate_trend(metric_col, time_col, query))
        elif request_type == 'comparison' and groupby_col:
            results.update(self._generate_comparison(metric_col, groupby_col, query))
        elif request_type == 'distribution':
            results.update(self._generate_distribution(metric_col, query))
        elif request_type == 'correlation' and len(self.numeric_cols) > 1:
            results.update(self._generate_correlation(query))
        else:
            # Basic: if groupby, show breakdown. Otherwise show distribution
            if groupby_col:
                results.update(self._generate_comparison(metric_col, groupby_col, query))
            else:
                results.update(self._generate_distribution(metric_col, query))
        
        return results
    
    def _extract_metric(self, query: str) -> Optional[str]:
        """Extract metric column from query"""
        for col in self.numeric_cols:
            if col.lower() in query.lower() or any(w in query.lower() for w in col.lower().split('_')):
                return col
        return self.numeric_cols[0] if self.numeric_cols else None
    
    def _extract_groupby(self, query: str) -> Optional[str]:
        """Extract groupby column from 'by X' pattern"""
        import re
        match = re.search(r'by\s+(\w+)', query.lower())
        if match:
            term = match.group(1)
            return self._find_best_match(term, self.categorical_cols + self.date_cols)
        return None
    
    def _extract_time_column(self, query: str) -> Optional[str]:
        """Extract time column for trend analysis"""
        for col in self.date_cols:
            if col.lower() in query.lower():
                return col
        return self.date_cols[0] if self.date_cols else None
    
    def _generate_trend(self, metric_col: str, time_col: str, query: str) -> Dict:
        """Generate trend chart (time series)"""
        try:
            df_trend = self.df[[time_col, metric_col]].copy()
            df_trend[time_col] = pd.to_datetime(df_trend[time_col], errors='coerce')
            df_trend[metric_col] = pd.to_numeric(df_trend[metric_col], errors='coerce')
            df_trend = df_trend.dropna()
            
            if df_trend.empty:
                return {'error': f'No valid data for trend analysis'}
            
            # Group by time period
            grouped = df_trend.groupby(df_trend[time_col].dt.to_period('M'), as_index=False)[metric_col].agg(['sum', 'mean', 'count'])
            grouped[time_col] = grouped[time_col].astype(str)
            grouped = grouped.sort_values(time_col)
            
            return {
                'charts': [{
                    'type': 'line',
                    'title': f'{metric_col} Trend Over Time',
                    'data': grouped[[time_col, ('sum', '')]].rename(columns={('sum', ''): metric_col}),
                    'x': time_col,
                    'y': metric_col
                }],
                'tables': [{
                    'title': f'{metric_col} Time Series Summary',
                    'data': grouped.round(2)
                }],
                'summary': f'Trend analysis of {metric_col} over {time_col.lower()}. Peak value: {grouped[("sum", "")].max():.0f}'
            }
        except Exception as e:
            return {'error': f'Error generating trend: {str(e)}'}
    
    def _generate_comparison(self, metric_col: str, groupby_col: str, query: str) -> Dict:
        """Generate comparison chart (metric by category)"""
        try:
            grouped = self.df.groupby(groupby_col)[metric_col].agg(['sum', 'mean', 'count', 'min', 'max'])
            grouped = grouped.sort_values('sum', ascending=False)
            
            # Create simplified chart data
            chart_data = pd.DataFrame({
                groupby_col: grouped.index,
                metric_col: grouped['sum'].values
            })
            
            return {
                'charts': [{
                    'type': 'bar',
                    'title': f'{metric_col} by {groupby_col}',
                    'data': chart_data,
                    'x': groupby_col,
                    'y': metric_col
                }],
                'tables': [{
                    'title': f'{metric_col} Breakdown by {groupby_col}',
                    'data': grouped.round(2)
                }],
                'summary': f'Total {metric_col}: {grouped["sum"].sum():.0f}. ' +
                          f'Categories: {len(grouped)}. ' +
                          f'Highest: {grouped.index[0]} ({grouped["sum"].iloc[0]:.0f})'
            }
        except Exception as e:
            return {'error': f'Error generating comparison: {str(e)}'}
    
    def _generate_distribution(self, metric_col: str, query: str) -> Dict:
        """Generate distribution chart (histogram)"""
        try:
            data = pd.to_numeric(self.df[metric_col], errors='coerce').dropna()
            
            if data.empty:
                return {'error': f'No valid numeric data for {metric_col}'}
            
            bins = min(max(int(np.sqrt(len(data))), 8), 30)
            hist, bin_edges = np.histogram(data, bins=bins)
            
            chart_data = pd.DataFrame({
                'range': [f'{int(bin_edges[i])}-{int(bin_edges[i+1])}' for i in range(len(bin_edges)-1)],
                'frequency': hist
            })
            
            summary_stats = {
                'Mean': data.mean(),
                'Median': data.median(),
                'Std Dev': data.std(),
                'Min': data.min(),
                'Max': data.max()
            }
            
            return {
                'charts': [{
                    'type': 'bar',
                    'title': f'Distribution of {metric_col}',
                    'data': chart_data,
                    'x': 'range',
                    'y': 'frequency'
                }],
                'tables': [{
                    'title': f'{metric_col} Statistical Summary',
                    'data': pd.DataFrame(summary_stats, index=[0]).T.rename(columns={0: 'Value'})
                }],
                'summary': f'Distribution of {metric_col}. Mean: {data.mean():.2f}, ' +
                          f'Median: {data.median():.2f}, Range: {data.min():.2f}-{data.max():.2f}'
            }
        except Exception as e:
            return {'error': f'Error generating distribution: {str(e)}'}
    
    def _generate_correlation(self, query: str) -> Dict:
        """Generate correlation/scatter chart"""
        try:
            # Get two numeric columns
            cols = self.numeric_cols[:2]
            if len(cols) < 2:
                return {'error': 'Need at least 2 numeric columns for correlation'}
            
            data = self.df[cols].dropna()
            
            if data.empty:
                return {'error': 'No valid data for correlation analysis'}
            
            corr = data[cols[0]].corr(data[cols[1]])
            
            return {
                'charts': [{
                    'type': 'scatter',
                    'title': f'Correlation: {cols[0]} vs {cols[1]}',
                    'data': data,
                    'x': cols[0],
                    'y': cols[1]
                }],
                'tables': [{
                    'title': 'Correlation Analysis',
                    'data': data.describe()
                }],
                'summary': f'Correlation between {cols[0]} and {cols[1]}: {corr:.3f} ' +
                          ('(Strong positive)' if corr > 0.7 else '(Weak)' if corr < 0.3 else '(Moderate)')
            }
        except Exception as e:
            return {'error': f'Error generating correlation: {str(e)}'}

    def generate_from_intent(self, intent: Dict) -> Dict:
        """Generate chart + table from LLM-extracted intent dict.

        Expected intent keys: chart_type, x, y, groupby, aggregation, title
        """
        x_col = intent.get("x")
        y_col = intent.get("y")
        groupby_col = intent.get("groupby")
        chart_type = intent.get("chart_type", "bar")
        aggregation = intent.get("aggregation", "sum")
        title = intent.get("title", "")

        # Resolve columns with fuzzy matching if exact name not found
        all_cols = list(self.df.columns)
        if x_col and x_col not in self.df.columns:
            x_col = self._find_best_match(x_col, all_cols)
        if y_col and y_col not in self.df.columns:
            y_col = self._find_best_match(y_col, self.numeric_cols) or (
                self.numeric_cols[0] if self.numeric_cols else None
            )
        if groupby_col and groupby_col not in self.df.columns:
            groupby_col = self._find_best_match(groupby_col, all_cols)

        if not x_col or not y_col:
            return {"error": "Could not identify chart columns from the question"}

        if not title:
            title = f"{y_col} by {x_col}"

        try:
            df_work = self.df.copy()
            df_work[y_col] = pd.to_numeric(df_work[y_col], errors="coerce")
            df_work = df_work.dropna(subset=[y_col])

            if df_work.empty:
                return {"error": f"No valid numeric data in column '{y_col}'"}

            agg_map = {"sum": "sum", "mean": "mean", "count": "count", "max": "max", "min": "min"}
            agg_func = agg_map.get(aggregation, "sum")

            if groupby_col and groupby_col in self.df.columns:
                grouped = (
                    df_work.groupby([x_col, groupby_col])[y_col]
                    .agg(agg_func)
                    .reset_index()
                )
            else:
                grouped = (
                    df_work.groupby(x_col)[y_col]
                    .agg(agg_func)
                    .reset_index()
                )
                groupby_col = None

            grouped = grouped.sort_values(y_col, ascending=False).head(30)

            total = grouped[y_col].sum()
            top_item = str(grouped.iloc[0][x_col]) if not grouped.empty else "N/A"
            top_value = float(grouped.iloc[0][y_col]) if not grouped.empty else 0

            return {
                "charts": [
                    {
                        "type": chart_type,
                        "title": title,
                        "data": grouped,
                        "x": x_col,
                        "y": y_col,
                        "groupby": groupby_col,
                    }
                ],
                "tables": [
                    {
                        "title": f"{title} — Data Table",
                        "data": grouped,
                    }
                ],
                "summary": (
                    f"{title}. "
                    f"{aggregation.title()} of {y_col}: {total:,.0f}. "
                    f"Top: {top_item} ({top_value:,.0f})"
                ),
            }
        except Exception as e:
            return {"error": f"Error generating chart: {str(e)}"}
