"""
Intelligent Dashboard Generator
Converts natural language queries into interactive data visualizations
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ChartSpec:
    """Specification for a chart to be rendered"""
    chart_type: str  # 'line', 'bar', 'scatter', 'area', 'pie'
    title: str
    x_column: Optional[str]
    y_column: Optional[str]
    groupby_column: Optional[str]
    aggregation: str  # 'sum', 'mean', 'count', 'max', 'min'
    data: pd.DataFrame
    filters: Dict[str, any]


class DashboardGenerator:
    """Generates interactive dashboards from natural language queries"""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.numeric_columns = list(dataframe.select_dtypes(include=['number']).columns)
        self.categorical_columns = list(dataframe.select_dtypes(include=['object', 'category']).columns)
        self.date_columns = self._detect_date_columns()
        
    def _detect_date_columns(self) -> List[str]:
        """Detect columns that contain date/time data"""
        date_cols = []
        for col in self.df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['date', 'time', 'year', 'month', 'day', 'quarter']):
                date_cols.append(col)
            elif self.df[col].dtype == 'datetime64[ns]':
                date_cols.append(col)
        return date_cols

    def _normalize_text(self, text: str) -> str:
        """Normalize text for robust name matching."""
        text = re.sub(r"[^a-z0-9]+", " ", str(text).lower())
        return re.sub(r"\s+", " ", text).strip()

    def _resolve_column_name(self, raw_name: str) -> Optional[str]:
        """Resolve a raw query token to an exact dataframe column if possible."""
        if not raw_name:
            return None

        raw = str(raw_name).strip().lower()
        cols = list(self.df.columns)

        # 1) Exact lowercase match
        for col in cols:
            if str(col).strip().lower() == raw:
                return col

        # 2) Normalized match (handles spaces/underscores)
        raw_norm = self._normalize_text(raw)
        for col in cols:
            if self._normalize_text(col) == raw_norm:
                return col

        # 3) Token-inclusive fallback (prefer the most specific column)
        raw_tokens = [t for t in raw_norm.split() if t]
        if not raw_tokens:
            return None

        best_col = None
        best_score = 0
        for col in cols:
            col_norm = self._normalize_text(col)
            score = sum(1 for t in raw_tokens if t in col_norm)
            if score > best_score:
                best_score = score
                best_col = col

        # Require strong overlap for fallback
        if best_col is not None and best_score >= max(2, len(raw_tokens)):
            return best_col
        return None
    
    def parse_query(self, query: str) -> Dict[str, any]:
        """Extract intent and parameters from natural language query"""
        query_lower = query.lower()
        query_norm = self._normalize_text(query)
        
        intent = {
            'chart_types': [],
            'metrics': [],
            'dimensions': [],
            'time_period': None,
            'aggregation': 'sum',
            'filters': {},
            'breakdowns': [],
            'comparisons': [],
            'show_all_categories': False
        }

        # Detect intent to include all categories (no top-N truncation)
        if any(phrase in query_lower for phrase in ["all category", "all categories", "all insurer", "all insures", "all groups"]):
            intent['show_all_categories'] = True
        
        # Detect chart type preferences
        if any(word in query_lower for word in ['trend', 'over time', 'timeline', 'progression']):
            intent['chart_types'].append('line')
        if any(word in query_lower for word in ['compare', 'comparison', 'versus', 'vs', 'breakdown']):
            intent['chart_types'].append('bar')
        if any(word in query_lower for word in ['distribution', 'spread', 'histogram']):
            intent['chart_types'].append('bar')
        if any(word in query_lower for word in ['correlation', 'relationship', 'scatter']):
            intent['chart_types'].append('scatter')
        if any(word in query_lower for word in ['composition', 'proportion', 'percentage', 'share']):
            intent['chart_types'].append('pie')
        
        # Default to bar if no preference detected
        if not intent['chart_types']:
            intent['chart_types'] = ['bar', 'line']
        
        # Detect aggregation function
        if any(word in query_lower for word in ['average', 'avg', 'mean']):
            intent['aggregation'] = 'mean'
        elif any(word in query_lower for word in ['total', 'sum']):
            intent['aggregation'] = 'sum'
        elif any(word in query_lower for word in ['count', 'number of']):
            intent['aggregation'] = 'count'
        elif any(word in query_lower for word in ['maximum', 'max', 'highest', 'top']):
            intent['aggregation'] = 'max'
        elif any(word in query_lower for word in ['minimum', 'min', 'lowest', 'bottom']):
            intent['aggregation'] = 'min'
        
        # Detect time periods
        time_patterns = {
            'quarter': r'q[1-4]|quarter [1-4]',
            'month': r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            'year': r'\b(19\d{2}|20\d{2}|21\d{2})\b'
        }
        
        for period, pattern in time_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                intent['time_period'] = {
                    'type': period,
                    'value': match.group(0)
                }
                break

        # Parse explicit "X vs Y" queries first (strong signal).
        vs_match = re.search(r"([a-zA-Z0-9_ ]+)\s+(?:vs|versus)\s+([a-zA-Z0-9_ ]+)", query_lower)
        if vs_match:
            left_raw = vs_match.group(1).strip(" ,.-")
            right_raw = vs_match.group(2).strip(" ,.-")
            left_col = self._resolve_column_name(left_raw)
            right_col = self._resolve_column_name(right_raw)

            if left_col:
                if left_col in self.numeric_columns:
                    intent['metrics'].append(left_col)
                else:
                    intent['dimensions'].append(left_col)

            if right_col and right_col != left_col:
                if right_col in self.numeric_columns:
                    intent['metrics'].append(right_col)
                else:
                    intent['dimensions'].append(right_col)

            # For numeric vs category, bar is usually the expected output.
            if len(intent['metrics']) == 1 and len(intent['dimensions']) >= 1:
                intent['chart_types'] = ['bar'] + [c for c in intent['chart_types'] if c != 'bar']
        
        # Match explicitly mentioned full column names (exact priority).
        explicit_cols = []
        for col in self.df.columns:
            col_lower = str(col).lower()
            col_norm = self._normalize_text(col)
            if re.search(rf"(?<![a-zA-Z0-9_]){re.escape(col_lower)}(?![a-zA-Z0-9_])", query_lower) or (
                col_norm and col_norm in query_norm
            ):
                explicit_cols.append(col)

        for col in explicit_cols:
            if col in self.numeric_columns and col not in intent['metrics']:
                intent['metrics'].append(col)
            elif col not in self.numeric_columns and col not in intent['dimensions']:
                intent['dimensions'].append(col)

        # Conservative fuzzy matching for non-explicit columns.
        for col in self.df.columns:
            if col in explicit_cols:
                continue

            col_norm = self._normalize_text(col)
            col_tokens = [t for t in col_norm.split() if len(t) > 3]
            token_hits = sum(1 for t in col_tokens if t in query_norm)

            # Require stronger overlap to avoid wrong matches like claims_pending_* for "claims".
            is_match = (
                (col_norm and col_norm in query_norm) or
                (len(col_tokens) >= 2 and token_hits >= 2) or
                (len(col_tokens) >= 3 and token_hits >= 2)
            )

            if is_match:
                if col in self.numeric_columns:
                    if col not in intent['metrics']:
                        intent['metrics'].append(col)
                else:
                    if col not in intent['dimensions']:
                        intent['dimensions'].append(col)
        
        # Detect breakdown/grouping keywords
        breakdown_match = re.search(r'(?:by|breakdown by|broken down by|grouped by|per)\s+(\w+)', query_lower)
        if breakdown_match:
            breakdown_term = breakdown_match.group(1)
            for col in self.categorical_columns + self.date_columns:
                if breakdown_term in str(col).lower():
                    intent['breakdowns'].append(col)
                    # Also add to dimensions so primary chart is created
                    if col not in intent['dimensions']:
                        intent['dimensions'].append(col)

        # Metric prioritization based on semantic intent (e.g., amount vs count)
        amount_intent = any(word in query_lower for word in ['amount', 'amt', 'value', 'rupee', 'inr'])
        count_intent = any(word in query_lower for word in ['count', 'number', 'no']) and not amount_intent

        if amount_intent and intent['metrics']:
            amount_metrics = [m for m in intent['metrics'] if any(tok in str(m).lower() for tok in ['amount', 'amt', 'value'])]
            if amount_metrics:
                # Keep amount-like metrics first, then others.
                remaining = [m for m in intent['metrics'] if m not in amount_metrics]
                intent['metrics'] = amount_metrics + remaining

        if count_intent and intent['metrics']:
            count_metrics = [m for m in intent['metrics'] if any(tok in str(m).lower() for tok in ['_no', 'count', 'number'])]
            if count_metrics:
                remaining = [m for m in intent['metrics'] if m not in count_metrics]
                intent['metrics'] = count_metrics + remaining
        
        return intent
    
    def suggest_visualization(self, intent: Dict) -> List[str]:
        """Suggest best chart types based on intent and data characteristics"""
        suggestions = []
        
        has_time = bool(intent.get('time_period')) or any(col in self.date_columns for col in intent['dimensions'])
        num_metrics = len(intent['metrics'])
        num_dimensions = len(intent['dimensions'])
        
        # Time series data -> line chart
        if has_time and num_metrics >= 1:
            suggestions.append('line')
        
        # Categorical comparison -> bar chart
        if num_dimensions >= 1 and num_metrics >= 1:
            suggestions.append('bar')
        
        # Two numeric columns -> scatter
        if num_metrics >= 2:
            suggestions.append('scatter')
        
        # Single dimension breakdown -> pie chart
        if num_dimensions == 1 and num_metrics == 1:
            unique_vals = self.df[intent['dimensions'][0]].nunique()
            if unique_vals <= 10:
                suggestions.append('pie')
        
        # Use user preferences if available
        if intent['chart_types']:
            suggestions = intent['chart_types'] + suggestions
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in suggestions if not (x in seen or seen.add(x))]
    
    def generate_chart_spec(self, query: str) -> List[ChartSpec]:
        """Generate chart specifications from natural language query"""
        try:
            intent = self.parse_query(query)
            chart_types = self.suggest_visualization(intent)
            
            specs = []
            
            # Apply filters if time period specified
            filtered_df = self.df.copy()
            if intent['time_period']:
                filtered_df = self._apply_time_filter(filtered_df, intent['time_period'])
            
            # Select best metrics and dimensions
            metrics = intent['metrics'][:2] if intent['metrics'] else self.numeric_columns[:1]
            dimensions = intent['dimensions'][:2] if intent['dimensions'] else self.categorical_columns[:1]
            breakdowns = intent['breakdowns'] if intent['breakdowns'] else []
            
            if not metrics and self.numeric_columns:
                metrics = [self.numeric_columns[0]]
            if not dimensions and (self.categorical_columns or self.date_columns):
                dimensions = [self.categorical_columns[0]] if self.categorical_columns else [self.date_columns[0]]
            
            # Validate that we have necessary columns
            if not metrics:
                raise ValueError("No numeric columns found for visualization")
            if not dimensions:
                raise ValueError("No categorical or date columns found for visualization")
            
            # Generate specs for each suggested chart type
            for i, chart_type in enumerate(chart_types[:3]):  # Limit to 3 charts
                try:
                    if chart_type == 'line' and dimensions and metrics:
                        spec = self._create_line_chart_spec(
                            filtered_df, metrics[0], dimensions[0], 
                            breakdowns[0] if breakdowns else None,
                            intent['aggregation']
                        )
                        if not spec.data.empty:
                            specs.append(spec)
                        
                    elif chart_type == 'bar' and dimensions and metrics:
                        spec = self._create_bar_chart_spec(
                            filtered_df, metrics[0], dimensions[0],
                            breakdowns[0] if breakdowns else None,
                            intent['aggregation'],
                            limit=None if intent.get('show_all_categories') else 15
                        )
                        if not spec.data.empty:
                            specs.append(spec)
                        
                    elif chart_type == 'scatter' and len(metrics) >= 2:
                        spec = self._create_scatter_chart_spec(
                            filtered_df, metrics[0], metrics[1],
                            dimensions[0] if dimensions else None
                        )
                        if not spec.data.empty:
                            specs.append(spec)
                        
                    elif chart_type == 'pie' and dimensions and metrics:
                        spec = self._create_pie_chart_spec(
                            filtered_df, metrics[0], dimensions[0],
                            intent['aggregation']
                        )
                        if not spec.data.empty:
                            specs.append(spec)
                except ValueError as e:
                    # Skip this chart type if column doesn't exist
                    print(f"Skipping {chart_type} chart: {str(e)}")
                    continue
                except Exception as e:
                    # Skip this chart on any error
                    print(f"Error creating {chart_type} chart: {str(e)}")
                    continue
            
            return specs
            
        except Exception as e:
            print(f"Error generating chart specs: {str(e)}")
            return []
    
    def _apply_time_filter(self, df: pd.DataFrame, time_period: Dict) -> pd.DataFrame:
        """Apply time-based filtering"""
        if not self.date_columns:
            return df
        
        date_col = self.date_columns[0]
        period_type = time_period['type']
        period_value = time_period['value']
        
        if period_type == 'year':
            year = int(re.search(r'\d{4}', period_value).group(0))
            return df[df[date_col].astype(str).str.contains(str(year))]
        elif period_type == 'quarter':
            # Simplified quarter filtering
            return df
        elif period_type == 'month':
            # Simplified month filtering
            return df
        
        return df
    
    def _create_line_chart_spec(self, df: pd.DataFrame, metric: str, dimension: str, 
                                 groupby: Optional[str], agg: str) -> ChartSpec:
        """Create specification for line chart"""
        # Validate columns exist
        if dimension not in df.columns:
            raise ValueError(f"Column '{dimension}' not found in dataframe")
        if metric not in df.columns:
            raise ValueError(f"Column '{metric}' not found in dataframe")
        
        plot_data = df[[dimension, metric]].copy()
        plot_data[metric] = pd.to_numeric(plot_data[metric], errors='coerce')
        plot_data = plot_data.dropna()
        
        if plot_data.empty:
            # Return empty spec if no data
            return ChartSpec(
                chart_type='line',
                title=f'{agg.capitalize()} {metric} by {dimension}',
                x_column=dimension,
                y_column=metric,
                groupby_column=groupby,
                aggregation=agg,
                data=pd.DataFrame(),
                filters={}
            )
        
        if groupby and groupby in df.columns:
            grouped = plot_data.groupby([dimension, groupby])[metric].agg(agg).reset_index()
        else:
            grouped = plot_data.groupby(dimension)[metric].agg(agg).reset_index()
        
        return ChartSpec(
            chart_type='line',
            title=f'{agg.capitalize()} {metric} by {dimension}',
            x_column=dimension,
            y_column=metric,
            groupby_column=groupby,
            aggregation=agg,
            data=grouped,
            filters={}
        )
    
    def _create_bar_chart_spec(self, df: pd.DataFrame, metric: str, dimension: str,
                                groupby: Optional[str], agg: str, limit: Optional[int] = 15) -> ChartSpec:
        """Create specification for bar chart"""
        # Validate columns exist
        if dimension not in df.columns:
            raise ValueError(f"Column '{dimension}' not found in dataframe")
        if metric not in df.columns:
            raise ValueError(f"Column '{metric}' not found in dataframe")
        
        plot_data = df[[dimension, metric]].copy()
        plot_data[metric] = pd.to_numeric(plot_data[metric], errors='coerce')
        plot_data = plot_data.dropna()
        
        if plot_data.empty:
            return ChartSpec(
                chart_type='bar',
                title=f'{agg.capitalize()} {metric} by {dimension}',
                x_column=dimension,
                y_column=metric,
                groupby_column=groupby,
                aggregation=agg,
                data=pd.DataFrame(),
                filters={}
            )
        
        if groupby and groupby in df.columns:
            grouped = plot_data.groupby([dimension, groupby])[metric].agg(agg).reset_index()
        else:
            grouped = plot_data.groupby(dimension)[metric].agg(agg).reset_index()
            if limit is not None:
                grouped = grouped.head(limit)
        
        return ChartSpec(
            chart_type='bar',
            title=f'{agg.capitalize()} {metric} by {dimension}',
            x_column=dimension,
            y_column=metric,
            groupby_column=groupby,
            aggregation=agg,
            data=grouped,
            filters={}
        )
    
    def _create_scatter_chart_spec(self, df: pd.DataFrame, metric1: str, metric2: str,
                                    color_by: Optional[str]) -> ChartSpec:
        """Create specification for scatter chart"""
        # Validate columns exist
        if metric1 not in df.columns:
            raise ValueError(f"Column '{metric1}' not found in dataframe")
        if metric2 not in df.columns:
            raise ValueError(f"Column '{metric2}' not found in dataframe")
        
        plot_data = df[[metric1, metric2]].copy()
        if color_by and color_by in df.columns:
            plot_data[color_by] = df[color_by]
        
        plot_data[metric1] = pd.to_numeric(plot_data[metric1], errors='coerce')
        plot_data[metric2] = pd.to_numeric(plot_data[metric2], errors='coerce')
        plot_data = plot_data.dropna().head(1000)
        
        if plot_data.empty:
            return ChartSpec(
                chart_type='scatter',
                title=f'{metric1} vs {metric2}',
                x_column=metric1,
                y_column=metric2,
                groupby_column=color_by,
                aggregation='none',
                data=pd.DataFrame(),
                filters={}
            )
        
        return ChartSpec(
            chart_type='scatter',
            title=f'{metric1} vs {metric2}',
            x_column=metric1,
            y_column=metric2,
            groupby_column=color_by,
            aggregation='none',
            data=plot_data,
            filters={}
        )
    
    def _create_pie_chart_spec(self, df: pd.DataFrame, metric: str, dimension: str,
                                agg: str) -> ChartSpec:
        """Create specification for pie chart"""
        # Validate columns exist
        if dimension not in df.columns:
            raise ValueError(f"Column '{dimension}' not found in dataframe")
        if metric not in df.columns:
            raise ValueError(f"Column '{metric}' not found in dataframe")
        
        plot_data = df[[dimension, metric]].copy()
        plot_data[metric] = pd.to_numeric(plot_data[metric], errors='coerce')
        plot_data = plot_data.dropna()
        
        if plot_data.empty:
            return ChartSpec(
                chart_type='pie',
                title=f'{agg.capitalize()} {metric} by {dimension}',
                x_column=dimension,
                y_column=metric,
                groupby_column=None,
                aggregation=agg,
                data=pd.DataFrame(),
                filters={}
            )
        
        grouped = plot_data.groupby(dimension)[metric].agg(agg).reset_index().head(10)
        
        return ChartSpec(
            chart_type='pie',
            title=f'{agg.capitalize()} {metric} by {dimension}',
            x_column=dimension,
            y_column=metric,
            groupby_column=None,
            aggregation=agg,
            data=grouped,
            filters={}
        )
