"""
Dashboard Orchestrator - Creates cohesive, interactive dashboards with AI-driven chart selection
Generates multiple related charts that work together with synchronized filtering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from dashboard_generator import DashboardGenerator, ChartSpec


@dataclass
class DashboardFilter:
    """Filter configuration for dashboard interactivity"""
    column: str
    type: str  # 'slider', 'multiselect', 'date_range', 'dropdown'
    values: List = field(default_factory=list)
    current_value: any = None
    label: str = ""


@dataclass
class DashboardCard:
    """KPI or summary card"""
    metric_name: str  # e.g., "Total Revenue"
    value: any
    unit: str = ""
    trend: Optional[str] = None  # +15%, -5%
    description: str = ""


@dataclass
class InteractiveDashboard:
    """Complete dashboard specification with cohesive charts and interactivity"""
    title: str
    description: str
    charts: List[ChartSpec] = field(default_factory=list)
    cards: List[DashboardCard] = field(default_factory=list)
    filters: List[DashboardFilter] = field(default_factory=list)
    layout: Dict[str, any] = field(default_factory=dict)  # grid layout info
    filter_sync: Dict[str, List[int]] = field(default_factory=dict)  # which filters affect which charts
    suggested_insights: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to serializable dict"""
        return {
            'title': self.title,
            'description': self.description,
            'charts': [
                {
                    'chart_type': c.chart_type,
                    'title': c.title,
                    'x': c.x_column,
                    'y': c.y_column,
                    'groupby': c.groupby_column,
                    'aggregation': c.aggregation,
                    'data': c.data.to_dict(orient='records') if not c.data.empty else [],
                    'filters': c.filters
                } for c in self.charts
            ],
            'cards': [
                {
                    'metric_name': card.metric_name,
                    'value': str(card.value),
                    'unit': card.unit,
                    'trend': card.trend,
                    'description': card.description
                } for card in self.cards
            ],
            'filters': [
                {
                    'column': f.column,
                    'type': f.type,
                    'values': f.values,
                    'label': f.label
                } for f in self.filters
            ],
            'layout': self.layout,
            'filter_sync': self.filter_sync,
            'insights': self.suggested_insights
        }


class DashboardOrchestrator:
    """Orchestrates intelligent dashboard creation with multiple related charts"""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.generator = DashboardGenerator(dataframe)
        
    def create_dashboard(self, query: str) -> Optional[InteractiveDashboard]:
        """
        Create a complete interactive dashboard from a natural language query.
        Returns a dashboard with:
        - Multiple complementary charts
        - KPI cards
        - Interactive filters
        - Synchronized filtering across charts
        """
        
        # Parse the query to understand intent
        intent = self.generator.parse_query(query)
        # Store the original query for later reference
        intent['query'] = query
        
        if not intent['metrics'] and not intent['dimensions']:
            return None
        
        # Analyze available data to recommend chart types
        chart_specs = self._generate_cohesive_charts(intent)
        
        if not chart_specs:
            return None
        
        # Create KPI cards from the analysis
        cards = self._generate_kpi_cards(intent, chart_specs)
        
        # Determine interactive filters for user control
        filters = self._generate_filters(intent)
        
        # Map which filters affect which charts (filter sync)
        filter_sync = self._map_filter_sync(filters, chart_specs)
        
        # Create dashboard title and description
        title, description = self._generate_dashboard_title(intent)
        
        # Generate insights from the data
        insights = self._generate_insights(intent, chart_specs)
        
        # Define layout (how charts are arranged)
        layout = self._define_layout(len(chart_specs))
        
        dashboard = InteractiveDashboard(
            title=title,
            description=description,
            charts=chart_specs,
            cards=cards,
            filters=filters,
            layout=layout,
            filter_sync=filter_sync,
            suggested_insights=insights
        )
        
        return dashboard
    
    def _generate_cohesive_charts(self, intent: Dict) -> List[ChartSpec]:
        """Generate multiple related charts that work together"""
        charts = []
        
        metrics = intent.get('metrics', [])
        dimensions = intent.get('dimensions', [])
        breakdowns = intent.get('breakdowns', [])
        
        if not metrics or not dimensions:
            return charts
        
        # Resolve column names with multiple strategies
        metric_cols = []
        for m in metrics:
            resolved = self.generator._resolve_column_name(m)
            if resolved:
                metric_cols.append(resolved)
            else:
                # Fallback: try to find numeric column that matches any word in the metric name
                for col in self.generator.numeric_columns:
                    if any(word.lower() in col.lower() for word in str(m).split()):
                        metric_cols.append(col)
                        break
        
        dim_cols = []
        for d in dimensions:
            resolved = self.generator._resolve_column_name(d)
            if resolved:
                dim_cols.append(resolved)
            else:
                # Fallback: try to find categorical column
                for col in self.generator.categorical_columns:
                    if any(word.lower() in col.lower() for word in str(d).split()):
                        dim_cols.append(col)
                        break
        
        if not metric_cols or not dim_cols:
            # Last resort: use first numeric and first categorical
            if self.generator.numeric_columns and self.generator.categorical_columns:
                metric_cols = [self.generator.numeric_columns[0]]
                dim_cols = [self.generator.categorical_columns[0]]
            else:
                return charts
        
        # Chart 1: Primary relationship (metric vs dimension)
        primary_chart = self._select_best_chart(
            metric=metric_cols[0],
            dimension=dim_cols[0],
            data=self.df,
            intent=intent
        )
        if primary_chart:
            charts.append(primary_chart)
        
        # Chart 2: Breakdown/comparison (if breakdown requested)
        if breakdowns and len(metric_cols) > 0 and len(dim_cols) > 0:
            breakdown_col = self.generator._resolve_column_name(breakdowns[0])
            if breakdown_col and breakdown_col != dim_cols[0]:
                breakdown_chart = self._create_breakdown_chart(
                    metric=metric_cols[0],
                    dimension=dim_cols[0],
                    breakdown=breakdown_col,
                    data=self.df,
                    intent=intent
                )
                if breakdown_chart:
                    charts.append(breakdown_chart)
        
        # Chart 3: Trend over time (if time dimension available)
        if self.generator.date_columns and metric_cols:
            trend_chart = self._create_trend_chart(
                metric=metric_cols[0],
                time_col=self.generator.date_columns[0],
                data=self.df,
                intent=intent
            )
            if trend_chart:
                charts.append(trend_chart)
        
        # Chart 4: Distribution (if numeric metric)
        if metric_cols and self.df[metric_cols[0]].dtype in ['int64', 'float64']:
            dist_chart = self._create_distribution_chart(metric_cols[0], self.df)
            if dist_chart:
                charts.append(dist_chart)
        
        return charts
    
    def _select_best_chart(self, metric: str, dimension: str, data: pd.DataFrame, intent: Dict) -> Optional[ChartSpec]:
        """AI logic to select the most appropriate chart type"""
        
        # Analyze data characteristics
        unique_dims = data[dimension].nunique()
        metric_dtype = data[metric].dtype
        
        # Determine best chart type based on data analysis
        chart_type = 'bar'  # Default
        
        if unique_dims > 20:
            chart_type = 'line'  # Too many categories for bar
        elif unique_dims <= 10 and metric_dtype in ['int64', 'float64']:
            chart_type = 'bar'  # Good for categorical comparison
        
        # Check for trend keywords
        if any(word in intent.get('query', '').lower() for word in ['trend', 'time', 'history']):
            chart_type = 'line'
        
        # Create chart spec with aggregated data
        try:
            grouped_data = data.groupby(dimension, as_index=False)[metric].agg(intent.get('aggregation', 'sum'))
        except Exception as e:
            # If groupby fails, try without conversion
            return None
        
        # Sort by metric value, descending
        grouped_data = grouped_data.sort_values(metric, ascending=False)
        
        # Show all categories if <= 20, otherwise limit to top 20
        # This ensures we don't miss categories in the visualization
        show_limit = 50 if unique_dims <= 20 else 20
        grouped_data = grouped_data.head(show_limit)
        
        if grouped_data.empty:
            return None
        
        return ChartSpec(
            chart_type=chart_type,
            title=f"{intent.get('aggregation', 'Total').title()} {metric} by {dimension}",
            x_column=dimension,
            y_column=metric,
            groupby_column=None,
            aggregation=intent.get('aggregation', 'sum'),
            data=grouped_data,
            filters={}
        )
    
    def _create_breakdown_chart(self, metric: str, dimension: str, breakdown: str, 
                                data: pd.DataFrame, intent: Dict) -> Optional[ChartSpec]:
        """Create a breakdown/comparison chart"""
        
        try:
            grouped = data.groupby([dimension, breakdown], as_index=False)[metric].agg(intent.get('aggregation', 'sum'))
            # Show all categories for dimension, limit breakdown to top 3-5
            grouped = grouped.sort_values([dimension, metric], ascending=[True, False])
            
            # Get unique dimensions and keep all of them
            unique_dim_count = grouped[dimension].nunique()
            show_limit = 100 if unique_dim_count <= 20 else 30
            grouped = grouped.head(show_limit)
        except Exception as e:
            return None
        
        if grouped.empty:
            return None
        
        return ChartSpec(
            chart_type='bar',
            title=f"{metric} by {dimension} (grouped by {breakdown})",
            x_column=dimension,
            y_column=metric,
            groupby_column=breakdown,
            aggregation=intent.get('aggregation', 'sum'),
            data=grouped,
            filters={}
        )
    
    def _create_trend_chart(self, metric: str, time_col: str, data: pd.DataFrame, intent: Dict) -> Optional[ChartSpec]:
        """Create a time-based trend chart"""
        
        df_copy = data.copy()
        df_copy[time_col] = pd.to_datetime(df_copy[time_col], errors='coerce')
        df_copy = df_copy.dropna(subset=[time_col, metric])
        
        if df_copy.empty:
            return None
        
        # Group by time period
        grouped = df_copy.groupby(df_copy[time_col].dt.to_period('M'), as_index=False)[metric].agg(intent.get('aggregation', 'sum'))
        grouped[time_col] = grouped[time_col].astype(str)
        grouped = grouped.sort_values(time_col)
        
        if grouped.empty:
            return None
        
        return ChartSpec(
            chart_type='line',
            title=f"{metric} Trend Over Time",
            x_column=time_col,
            y_column=metric,
            groupby_column=None,
            aggregation=intent.get('aggregation', 'sum'),
            data=grouped,
            filters={}
        )
    
    def _create_distribution_chart(self, metric: str, data: pd.DataFrame) -> Optional[ChartSpec]:
        """Create a distribution/histogram chart"""
        
        values = pd.to_numeric(data[metric], errors='coerce').dropna()
        
        if len(values) < 2:
            return None
        
        # Create bins for histogram
        bins = min(max(int(np.sqrt(len(values))), 8), 20)
        hist, bin_edges = np.histogram(values, bins=bins)
        
        bin_labels = [f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}" for i in range(len(bin_edges)-1)]
        
        hist_df = pd.DataFrame({
            'range': bin_labels,
            'count': hist
        })
        
        return ChartSpec(
            chart_type='bar',
            title=f"Distribution of {metric}",
            x_column='range',
            y_column='count',
            groupby_column=None,
            aggregation='count',
            data=hist_df,
            filters={}
        )
    
    def _generate_kpi_cards(self, intent: Dict, charts: List[ChartSpec]) -> List[DashboardCard]:
        """Generate KPI summary cards"""
        cards = []
        
        metrics = intent.get('metrics', [])
        if not metrics or not charts:
            return cards
        
        metric_col = charts[0].y_column
        if not metric_col:
            return cards
        
        # Total metric
        total = self.df[metric_col].sum()
        cards.append(DashboardCard(
            metric_name=f"Total {metric_col}",
            value=f"{total:,.0f}",
            unit="",
            description=f"Overall {metric_col} across all records"
        ))
        
        # Average metric
        avg = self.df[metric_col].mean()
        cards.append(DashboardCard(
            metric_name=f"Average {metric_col}",
            value=f"{avg:,.0f}",
            unit="",
            description=f"Mean value of {metric_col}"
        ))
        
        # Record count
        count = len(self.df)
        cards.append(DashboardCard(
            metric_name="Total Records",
            value=f"{count:,}",
            unit="",
            description="Total number of records analyzed"
        ))
        
        return cards
    
    def _generate_filters(self, intent: Dict) -> List[DashboardFilter]:
        """Generate interactive filters for user control"""
        filters = []
        
        dimensions = intent.get('dimensions', [])
        
        for dim in dimensions[:2]:  # Limit to 2 filters to avoid clutter
            dim_col = self.generator._resolve_column_name(dim)
            if not dim_col:
                continue
            
            unique_vals = self.df[dim_col].nunique()
            
            if unique_vals <= 10:
                filter_type = 'multiselect'
                values = self.df[dim_col].dropna().unique().tolist()
            elif unique_vals > 10 and unique_vals <= 100:
                filter_type = 'multiselect'
                values = self.df[dim_col].dropna().unique()[:20].tolist()
            else:
                filter_type = 'dropdown'
                values = self.df[dim_col].dropna().unique()[:10].tolist()
            
            filters.append(DashboardFilter(
                column=dim_col,
                type=filter_type,
                values=values,
                label=dim_col.replace('_', ' ').title()
            ))
        
        return filters
    
    def _map_filter_sync(self, filters: List[DashboardFilter], charts: List[ChartSpec]) -> Dict[str, List[int]]:
        """Map which filters affect which charts"""
        sync = {}
        
        for i, f in enumerate(filters):
            affected_charts = []
            for j, chart in enumerate(charts):
                if f.column in [chart.x_column, chart.groupby_column]:
                    affected_charts.append(j)
            sync[f.column] = affected_charts
        
        return sync
    
    def _generate_dashboard_title(self, intent: Dict) -> Tuple[str, str]:
        """Generate descriptive title and description"""
        
        metrics = intent.get('metrics', [])
        dimensions = intent.get('dimensions', [])
        
        if metrics and dimensions:
            title = f"{metrics[0].title()} Analysis by {dimensions[0].title()}"
            desc = f"Interactive dashboard showing {metrics[0]} broken down by {dimensions[0]}"
        else:
            title = "Data Dashboard"
            desc = "Comprehensive analysis of your data"
        
        return title, desc
    
    def _define_layout(self, num_charts: int) -> Dict[str, any]:
        """Define how charts are arranged in the dashboard"""
        
        if num_charts == 1:
            return {'structure': 'single', 'cols': [[0]]}
        elif num_charts == 2:
            return {'structure': 'two_cols', 'cols': [[0], [1]]}
        elif num_charts == 3:
            return {'structure': 'mixed', 'cols': [[0, 1], [2]]}
        else:
            return {'structure': 'grid', 'cols': [[0, 1], [2, 3]]}
    
    def _generate_insights(self, intent: Dict, charts: List[ChartSpec]) -> List[str]:
        """Generate actionable insights from the dashboard"""
        
        insights = []
        
        if not charts:
            return insights
        
        # Find top category insight
        if charts[0].chart_type == 'bar':
            top_row = charts[0].data.iloc[0]
            metric_val = top_row.get(charts[0].y_column, 0)
            dim_val = top_row.get(charts[0].x_column, "")
            insights.append(f"Top performer: {dim_val} with {metric_val:,.0f}")
        
        # Find trend insight
        if len(charts) > 2 and charts[2].chart_type == 'line':
            first_val = charts[2].data[charts[2].y_column].iloc[0]
            last_val = charts[2].data[charts[2].y_column].iloc[-1]
            change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            direction = "increasing" if change_pct > 0 else "decreasing"
            insights.append(f"Trend is {direction} by {abs(change_pct):.1f}%")
        
        insights.append("Use filters above to explore specific segments")
        
        return insights
