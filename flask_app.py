import os
import json
import tempfile
import concurrent.futures
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

load_dotenv()  # must run before importing langchain_utils so GOOGLE_API_KEY is set

from langchain_utils import LangChainChat, CSVAnalyzer


def _invoke_llm_with_timeout(messages, timeout_seconds=45):
    """Invoke LLM with a hard timeout to avoid platform-level connection aborts."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(chat._invoke_with_model_fallback, messages)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError as e:
            raise TimeoutError(f"LLM request timed out after {timeout_seconds}s") from e


def _safe_int_env(name, default):
    """Parse integer env var safely, falling back when value is blank/invalid."""
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default

# Validation helpers for hallucination prevention
def validate_chart_response(result, available_cols, csv_data):
    """
    Validate LLM chart response to prevent hallucinations AND ensure completeness.
    Returns: (is_valid, error_message, sanitized_result)
    """
    if not isinstance(result, dict):
        return False, "Response is not a dictionary", None
    
    if "charts" not in result:
        return False, "Response missing 'charts' field", None
    
    charts = result.get("charts", [])
    if not charts:
        return False, "No charts generated - the model could not answer this query with the available data", None
    
    available_cols_lower = [c.lower() for c in available_cols]
    errors = []
    warnings = []
    sanitized_charts = []
    
    for i, chart in enumerate(charts):
        chart_id = chart.get("id", f"chart_{i}")
        
        # Validate chart type
        valid_types = ["line", "bar", "pie", "doughnut", "radar", "scatter", "polarArea", "area", "matrix"]
        if chart.get("type") not in valid_types:
            errors.append(f"Chart {chart_id}: Invalid type '{chart.get('type')}'")
            continue

        # Matrix charts use a dedicated structure instead of datasets
        if chart.get("type") == "matrix":
            matrix = chart.get("matrix") or {}
            rows = matrix.get("rows") or []
            columns = matrix.get("columns") or []
            values = matrix.get("values") or []
            if not rows or not columns or not values:
                errors.append(f"Chart {chart_id}: Invalid matrix structure")
                continue
            sanitized_charts.append(chart)
            continue
        
        # Validate datasets structure
        datasets = chart.get("datasets", [])
        if not datasets:
            errors.append(f"Chart {chart_id}: No datasets provided")
            continue
        
        # Check if chart references nonexistent columns
        labels = chart.get("labels", [])
        chart_seems_valid = True
        
        # Check for suspiciously small data when full data should be shown
        num_labels = len(labels)
        if chart.get("type") in ["bar", "pie", "doughnut"] and num_labels > 0:
            # If chart shows exactly 10 items, warn that it might be artificially limited
            if num_labels == 10:
                warnings.append(f"Chart {chart_id}: Shows exactly 10 items - verify this is not an artificial limit")
            
        # For non-pie charts, check if labels could be column values
        if chart.get("type") not in ["pie", "doughnut", "polarArea"]:
            # Try to infer if the chart is using real data
            if labels:
                # Check if any label matches a column name (case-insensitive)
                labels_are_columns = any(str(label).lower() in available_cols_lower for label in labels)
                
                # Check if dataset values are suspiciously round or clearly fabricated
                for ds in datasets:
                    data = ds.get("data", [])
                    if data and all(isinstance(v, (int, float)) for v in data):
                        # If all values are exactly the same or all are multiples of 10, suspect hallucination
                        if len(set(data)) == 1 and len(data) > 2:
                            errors.append(f"Chart {chart_id}: Data appears fabricated (all identical values)")
                            chart_seems_valid = False
        
        if chart_seems_valid:
            sanitized_charts.append(chart)
    
    if not sanitized_charts:
        return False, f"All charts failed validation: {'; '.join(errors)}", None
    
    if warnings:
        print(f"[Validation Warnings] {'; '.join(warnings)}")
    
    result["charts"] = sanitized_charts
    return True, None, result


def detect_query_intent(query, available_cols):
    """
    Detect what the user is asking for and validate if it's answerable.
    Returns: (is_answerable, chart_type_hint, reason)
    """
    query_lower = query.lower()
    available_cols_lower = [c.lower() for c in available_cols]
    
    # Check for specific column mentions
    mentioned_cols = [col for col in available_cols if col.lower() in query_lower]
    
    # Chart type hints based on keywords
    chart_type_hint = None
    if any(kw in query_lower for kw in ["trend", "over time", "timeline", "time series", "year", "month"]):
        chart_type_hint = "line"
    elif any(kw in query_lower for kw in ["compare", "comparison", "versus", "vs", "across"]):
        chart_type_hint = "bar"
    elif any(kw in query_lower for kw in ["proportion", "breakdown", "composition", "share", "percentage", "%"]):
        chart_type_hint = "pie"
    elif any(kw in query_lower for kw in ["correlation", "relationship", "scatter"]):
        chart_type_hint = "scatter"
    elif any(kw in query_lower for kw in ["distribution", "histogram", "frequency"]):
        chart_type_hint = "bar"
    
    # Check if query asks about non-existent columns
    if mentioned_cols:
        return True, chart_type_hint, f"Query references existing columns: {', '.join(mentioned_cols[:3])}"
    
    # Even if no specific columns mentioned, query could be generic (e.g., "show me an overview")
    if any(kw in query_lower for kw in ["overview", "summary", "dashboard", "all", "everything"]):
        return True, None, "Query requests general overview"
    
    # Query seems reasonable
    return True, chart_type_hint, "Query appears answerable with current dataset"


def _is_dynamic_matrix_request(query: str) -> bool:
    """Detect generic matrix-style prompts with or without highlight instructions."""
    q = (query or "").lower()
    has_matrix_intent = any(k in q for k in ["matrix", "pivot", "table", "broken down by", "heatmap"])
    has_dim_intent = any(k in q for k in ["by ", "across", "over", "year", "month", "category"])
    return has_matrix_intent and has_dim_intent


def _extract_highlight_rule(query: str):
    """Extract a generic highlight rule from prompt text, e.g. below 85 in red."""
    import re

    q = (query or "").lower()
    has_highlight = any(k in q for k in ["highlight", "in red", "below", "under", "less than", "greater than", "above"])
    if not has_highlight:
        return None

    color_map = {
        "red": "#D64550",
        "green": "#1AAB40",
        "orange": "#E66C37",
        "yellow": "#D9B300",
        "blue": "#118DFF",
        "pink": "#E044A7",
        "teal": "#01B8AA",
    }
    color = next((hex_code for name, hex_code in color_map.items() if name in q), "#D64550")

    operator = "lt"
    if any(k in q for k in ["below", "under", "less than", "lower than", "<"]):
        operator = "lt"
    elif any(k in q for k in ["at most", "no more than", "<="]):
        operator = "lte"
    elif any(k in q for k in ["above", "over", "greater than", "more than", "higher than", ">"]):
        operator = "gt"
    elif any(k in q for k in ["at least", "no less than", ">="]):
        operator = "gte"

    # Prefer thresholds explicitly tied to highlight comparators to avoid picking year values.
    comparator_patterns = [
        r"(?:below|under|less than|lower than|at most|no more than)\s*(-?\d+(?:\.\d+)?)\s*%?",
        r"(?:above|over|greater than|more than|higher than|at least|no less than)\s*(-?\d+(?:\.\d+)?)\s*%?",
        r"([<>]=?)\s*(-?\d+(?:\.\d+)?)\s*%?",
    ]

    threshold = None
    for pat in comparator_patterns:
        m = re.search(pat, q)
        if not m:
            continue
        try:
            if len(m.groups()) == 2 and m.group(1) in ["<", "<=", ">", ">="]:
                symbol = m.group(1)
                operator = {"<": "lt", "<=": "lte", ">": "gt", ">=": "gte"}[symbol]
                threshold = float(m.group(2))
            else:
                threshold = float(m.group(1))
            break
        except ValueError:
            continue

    # Fallback only when query is clearly highlight-related and does not contain 4-digit year tokens.
    if threshold is None:
        yearish = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", q)
        number_match = re.search(r"(-?\d+(?:\.\d+)?)\s*%?", q)
        if not number_match or yearish:
            return None
        try:
            threshold = float(number_match.group(1))
        except ValueError:
            return None



    return {
        "operator": operator,
        "threshold": threshold,
        "color": color,
    }


def _apply_highlight_rule_to_charts(result: dict, highlight_rule: dict):
    """Attach highlight rule metadata to all charts so frontend can render conditional styles."""
    if not result or not isinstance(result, dict) or not highlight_rule:
        return result

    charts = result.get("charts") or []
    if not charts:
        return result

    for chart in charts:
        if chart.get("type") == "matrix":
            matrix = chart.setdefault("matrix", {})
            matrix["highlight"] = highlight_rule
        else:
            chart["highlight"] = highlight_rule

    return result


def _build_dynamic_matrix_chart(csv_data: list, query: str, threshold: float | None = None):
    """Build a generic matrix from any CSV: row dimension x column dimension over a numeric metric."""
    if not csv_data:
        return None, "No data available"

    df = pd.DataFrame(csv_data)
    if df.empty:
        return None, "No rows available"

    q = (query or "").lower()

    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    for c in df.columns:
        if c in numeric_cols:
            continue
        cleaned = df[c].astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
        vals = pd.to_numeric(cleaned, errors="coerce")
        if vals.notna().mean() > 0.7:
            df[c] = vals
            numeric_cols.append(c)

    if not numeric_cols:
        return None, "No numeric metric column found for matrix values"

    date_like = [c for c in df.columns if any(k in str(c).lower() for k in ["year", "date", "month", "period", "fy"])]
    cat_cols = [c for c in df.columns if c not in numeric_cols]

    metric = None
    for c in numeric_cols:
        if str(c).lower() in q:
            metric = c
            break
    if not metric:
        metric = next((c for c in numeric_cols if "ratio" in str(c).lower()), None)
    if not metric:
        metric = next((c for c in numeric_cols if any(k in str(c).lower() for k in ["amount", "amt", "value", "paid", "total"])), None)
    if not metric:
        metric = numeric_cols[0]

    col_dim = None
    if any(k in q for k in ["year", "month", "date", "over time", "trend"]):
        col_dim = date_like[0] if date_like else None
    if not col_dim:
        for c in cat_cols:
            if str(c).lower() in q:
                col_dim = c
                break
    if not col_dim:
        col_dim = date_like[0] if date_like else (cat_cols[0] if cat_cols else None)

    row_dim = None
    for c in cat_cols:
        if c == col_dim:
            continue
        if str(c).lower() in q:
            row_dim = c
            break
    if not row_dim:
        row_dim = next((c for c in cat_cols if c != col_dim), None)

    if not row_dim or not col_dim:
        return None, "Could not detect two dimensions for matrix (row and column)"

    work = df[[row_dim, col_dim, metric]].copy()
    work[row_dim] = work[row_dim].astype(str)
    work[col_dim] = work[col_dim].astype(str)
    work[metric] = pd.to_numeric(work[metric], errors="coerce")
    work = work.dropna(subset=[metric])
    if work.empty:
        return None, "No valid numeric values found for matrix"

    pivot = work.pivot_table(index=row_dim, columns=col_dim, values=metric, aggfunc="mean")
    row_labels = [str(x) for x in pivot.index.tolist()]
    col_labels = [str(x) for x in pivot.columns.tolist()]

    values = []
    highlighted = 0
    for r in row_labels:
        row_vals = []
        for c in col_labels:
            val = pivot.at[r, c] if c in pivot.columns else pd.NA
            if pd.isna(val):
                row_vals.append(None)
            else:
                num = round(float(val), 2)
                if threshold is not None and num < threshold:
                    highlighted += 1
                row_vals.append(num)
        values.append(row_vals)

    matrix_meta = {
        "rowHeader": str(row_dim),
        "columnHeader": str(col_dim),
        "rows": row_labels,
        "columns": col_labels,
        "values": values,
        "unit": "%" if "ratio" in str(metric).lower() else "",
    }
    if threshold is not None:
        matrix_meta["highlight"] = {
            "operator": "lt",
            "threshold": threshold,
            "color": "#D64550",
        }

    chart = {
        "id": "dynamic_matrix",
        "type": "matrix",
        "width": "full",
        "title": f"Matrix of {metric} by {row_dim} and {col_dim}",
        "description": (
            f"Average {metric} across {row_dim} x {col_dim}."
            + (f" {highlighted} cells below {threshold} are highlighted." if threshold is not None else "")
        ),
        "matrix": matrix_meta,
    }
    return {"summary": f"Generated dynamic matrix using metric '{metric}', rows '{row_dim}', columns '{col_dim}'.", "charts": [chart]}, None


def _is_insurance_claims_dataset(cols: list) -> bool:
    """Lightweight check for insurance claims schema."""
    c = {str(x).lower() for x in cols}
    required = {"life_insurer", "year"}
    return required.issubset(c)


def _insurance_colmap(df: pd.DataFrame) -> dict:
    """Case-insensitive column resolver."""
    lower = {c.lower(): c for c in df.columns}
    return {
        "insurer": lower.get("life_insurer") or lower.get("insurer"),
        "year": lower.get("year") or lower.get("financial_year"),
        "claims_paid_ratio_amt": lower.get("claims_paid_ratio_amt"),
        "claims_paid_ratio_no": lower.get("claims_paid_ratio_no"),
        "claims_repudiated_rejected_ratio_no": lower.get("claims_repudiated_rejected_ratio_no"),
        "claims_repudiated_no": lower.get("claims_repudiated_no"),
        "claims_rejected_no": lower.get("claims_rejected_no"),
        "claims_pending_end_no": lower.get("claims_pending_end_no"),
        "claims_pending_start_no": lower.get("claims_pending_start_no"),
        "claims_paid_amt": lower.get("claims_paid_amt"),
        "claims_intimated_amt": lower.get("claims_intimated_amt"),
        "total_claims_no": lower.get("total_claims_no"),
        "total_claims_amt": lower.get("total_claims_amt"),
        "claims_unclaimed_amt": lower.get("claims_unclaimed_amt"),
        "claims_intimated_no": lower.get("claims_intimated_no"),
        "category": lower.get("category"),
    }


def _coerce_numeric(df: pd.DataFrame, cols: list):
    for c in cols:
        if c and c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def _extract_year_from_query(query: str, available_years: list[str]):
    import re
    q = (query or "")

    if not available_years:
        return None

    # Match FY style like 2021-22 first.
    m = re.search(r"\b(20\d{2}-\d{2})\b", q)
    if m:
        y = m.group(1)
        if y in available_years:
            return y

    # Match single 4-digit year and map to best candidate in available years.
    m2 = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", q)
    if m2:
        y4 = m2.group(1)
        exact = [y for y in available_years if str(y).strip() == y4]
        if exact:
            return exact[0]
        contains = [y for y in available_years if y4 in str(y)]
        if contains:
            return contains[0]

    def _year_key(v: str):
        m3 = re.search(r"(19\d{2}|20\d{2}|21\d{2})", str(v))
        return int(m3.group(1)) if m3 else -1

    # fallback to latest available year-like label
    return sorted(available_years, key=_year_key)[-1]


def _build_generic_reference_question_response(query: str, csv_data: list):
    """
    Generic deterministic handler for:
    "How much money in total ... pay out ... in <year>?"
    Works for any CSV with detectable year/date + numeric amount columns.
    """
    if not csv_data:
        return None

    q = (query or "").lower()
    is_reference_question = (
        ("how much money" in q or "total payout" in q or "total payouts" in q or "pay out" in q or "paid out" in q)
    )
    if not is_reference_question:
        return None

    df = pd.DataFrame(csv_data)
    if df.empty:
        return None

    # Detect year/date-like column.
    col_lower = {c.lower(): c for c in df.columns}
    year_col = None
    for k in ["year", "financial_year", "fy", "date", "period", "month"]:
        if k in col_lower:
            year_col = col_lower[k]
            break
    if not year_col:
        for c in df.columns:
            lc = str(c).lower()
            if any(k in lc for k in ["year", "date", "period", "fy", "month"]):
                year_col = c
                break

    inferred_year_series = None
    if not year_col:
        # Infer year labels from values when no explicit year column exists.
        import re
        best_ratio = 0.0
        best_series = None
        for c in df.columns:
            s = df[c].astype(str)
            fy = s.str.extract(r"(20\d{2}-\d{2})(?!-\d)", expand=False)
            y4 = s.str.extract(r"\b(19\d{2}|20\d{2}|21\d{2})\b", expand=False)
            candidate = fy.combine_first(y4)
            ratio = candidate.notna().mean()
            if ratio > best_ratio and ratio >= 0.5:
                best_ratio = ratio
                best_series = candidate
        if best_series is not None:
            inferred_year_series = best_series
            year_col = "__inferred_year__"
            df[year_col] = inferred_year_series

    # Detect numeric amount-like column.
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    if not numeric_cols:
        for c in df.columns:
            cleaned = df[c].astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
            vals = pd.to_numeric(cleaned, errors="coerce")
            if vals.notna().mean() > 0.7:
                numeric_cols.append(c)
                df[c] = vals
    if not numeric_cols:
        return {
            "summary": "I could not find a numeric amount column in this CSV to compute total payout.",
            "charts": [],
        }

    def _score_amount_col(col_name: str) -> int:
        lc = str(col_name).lower()
        score = 0
        for kw, pts in [
            ("paid", 8), ("payout", 8), ("payment", 6), ("amount", 6), ("amt", 5),
            ("claim", 4), ("value", 4), ("revenue", 3), ("sales", 3), ("total", 2),
        ]:
            if kw in lc:
                score += pts
        return score

    amount_col = sorted(numeric_cols, key=lambda c: (_score_amount_col(c), df[c].fillna(0).abs().sum()), reverse=True)[0]

    years = []
    target_year = None
    year_label_col = None
    if year_col and year_col in df.columns:
        raw_year = df[year_col].astype(str)
        fy = raw_year.str.extract(r"(20\d{2}-\d{2})(?!-\d)", expand=False)
        y4 = raw_year.str.extract(r"\b(19\d{2}|20\d{2}|21\d{2})\b", expand=False)
        normalized = fy.combine_first(y4).fillna(raw_year)
        year_label_col = "__year_label__"
        df[year_label_col] = normalized.astype(str)
        years = sorted(df[year_label_col].dropna().astype(str).unique().tolist())
        target_year = _extract_year_from_query(query, years)

    # Optional split/group column for richer breakdown.
    group_col = None
    preferred_group_keys = ["insurer", "company", "provider", "carrier", "category", "segment", "region", "state"]
    categorical_candidates = [c for c in df.columns if c not in numeric_cols and c != year_col and c != "__inferred_year__"]
    for c in categorical_candidates:
        lc = str(c).lower()
        if any(k in lc for k in preferred_group_keys):
            group_col = c
            break
    if not group_col and categorical_candidates:
        group_col = categorical_candidates[0]

    if target_year and year_label_col and year_label_col in df.columns:
        year_df = df[df[year_label_col] == target_year].copy()
    else:
        year_df = df.copy()

    total_value = float(pd.to_numeric(year_df[amount_col], errors="coerce").fillna(0).sum())

    charts = []
    # Primary trend across years for context.
    if year_label_col and year_label_col in df.columns and df[year_label_col].notna().any():
        yearly = df.groupby(year_label_col, as_index=False)[amount_col].sum().sort_values(year_label_col)
        charts.append({
            "id": "generic_total_trend",
            "type": "line",
            "width": "full",
            "title": f"Total {amount_col} by {year_col}",
            "description": "Year-over-year total trend",
            "labels": yearly[year_label_col].astype(str).tolist(),
            "datasets": [{"label": f"Total {amount_col}", "data": yearly[amount_col].round(2).tolist(), "color": "#118DFF"}],
        })

    # Secondary breakdown for the target year if grouping is available.
    if group_col:
        grp = year_df.groupby(group_col, as_index=False)[amount_col].sum().sort_values(amount_col, ascending=False)
        if len(grp) > 25:
            grp = grp.head(25)
        charts.append({
            "id": "generic_year_breakdown",
            "type": "bar",
            "width": "full",
            "title": f"{amount_col} Breakdown {'in ' + target_year if target_year else 'for entire dataset'} by {group_col}",
            "description": f"Top {len(grp)} groups",
            "labels": grp[group_col].astype(str).tolist(),
            "datasets": [{"label": f"{amount_col} ({target_year if target_year else 'All Data'})", "data": grp[amount_col].round(2).tolist(), "color": "#01B8AA"}],
        })
    else:
        charts.append({
            "id": "generic_year_total",
            "type": "bar",
            "width": "half",
            "title": f"Total {amount_col} {'in ' + target_year if target_year else '(All Data)'}",
            "description": "Aggregate total",
            "labels": [target_year if target_year else "All Data"],
            "datasets": [{"label": f"Total {amount_col}", "data": [round(total_value, 2)], "color": "#01B8AA"}],
        })

    if target_year:
        summary = (
            f"Total {amount_col} in {target_year} is {total_value:,.2f} "
            f"(detected year column '{year_col}' and amount column '{amount_col}')."
        )
    else:
        summary = (
            f"I could not reliably detect a year column, so using entire dataset: "
            f"total {amount_col} is {total_value:,.2f}."
        )

    return {"summary": summary, "charts": charts}


def _is_generic_reference_payout_question(query: str) -> bool:
    q = (query or "").lower()
    return ("how much money" in q or "total payout" in q or "total payouts" in q or "pay out" in q or "paid out" in q)


def _build_insurance_insight_response(query: str, csv_data: list):
    """Deterministic answers for high-value insurance insights questions."""
    if not csv_data:
        return None

    df = pd.DataFrame(csv_data)
    cmap = _insurance_colmap(df)
    if not cmap.get("insurer") or not cmap.get("year"):
        return None

    _coerce_numeric(df, [
        cmap.get("claims_paid_ratio_amt"), cmap.get("claims_paid_ratio_no"),
        cmap.get("claims_repudiated_rejected_ratio_no"), cmap.get("claims_repudiated_no"), cmap.get("claims_rejected_no"),
        cmap.get("claims_pending_end_no"), cmap.get("claims_pending_start_no"),
        cmap.get("claims_paid_amt"), cmap.get("claims_intimated_amt"),
        cmap.get("total_claims_no"), cmap.get("total_claims_amt"),
        cmap.get("claims_unclaimed_amt"), cmap.get("claims_intimated_no"),
    ])
    df[cmap["insurer"]] = df[cmap["insurer"]].astype(str)
    df[cmap["year"]] = df[cmap["year"]].astype(str)

    q = (query or "").lower()
    years = sorted(df[cmap["year"]].dropna().astype(str).unique().tolist())
    red = "#D64550"
    blue = "#118DFF"

    # User-requested strict reference mode:
    # only deterministic handling for the industry total payout question pattern.
    reference_mode_match = (
        ("how much money" in q or "total payouts" in q or "pay out" in q or "paid out" in q)
        and ("indian life insurance industry" in q or "industry" in q)
        and any(tok in q for tok in ["financial year", "year", "2020-21", "2021-22", "2019-20", "2018-19", "2017-18"])
    )
    if not reference_mode_match:
        return None

    # 1) Most likely to pay out claim (highest settlement ratio).
    if ("highest" in q or "most likely" in q) and ("claim settlement ratio" in q or "claims paid ratio" in q):
        ratio_col = cmap.get("claims_paid_ratio_amt") or cmap.get("claims_paid_ratio_no")
        if not ratio_col:
            return None
        s = df.groupby(cmap["insurer"], as_index=False)[ratio_col].mean().dropna().sort_values(ratio_col, ascending=False)
        if s.empty:
            return None
        top = s.iloc[0]
        return {
            "summary": f"{top[cmap['insurer']]} has the highest average claim settlement ratio at {top[ratio_col]*100:.2f}%.",
            "charts": [{
                "id": "highest_settlement_ratio",
                "type": "bar",
                "width": "full",
                "title": "Highest Claim Settlement Ratio by Insurer",
                "description": "Average claim settlement ratio across available years",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Settlement Ratio %", "data": (s[ratio_col] * 100).round(2).tolist(), "color": blue}],
            }],
        }

    # 2) Red flag: highest repudiation/rejection percentage.
    if ("red flag" in q or "reject" in q or "repudiat" in q) and ("highest" in q or "most" in q):
        ratio_col = cmap.get("claims_repudiated_rejected_ratio_no")
        if ratio_col:
            s = df.groupby(cmap["insurer"], as_index=False)[ratio_col].mean().dropna().sort_values(ratio_col, ascending=False)
            metric = (s[ratio_col] * 100).round(2)
        else:
            rep = cmap.get("claims_repudiated_no")
            rej = cmap.get("claims_rejected_no")
            total = cmap.get("total_claims_no")
            if not (rep and total):
                return None
            temp = df.copy()
            temp["_rej"] = temp[rep].fillna(0) + (temp[rej].fillna(0) if rej else 0)
            g = temp.groupby(cmap["insurer"], as_index=False)[["_rej", total]].sum()
            g["_ratio"] = (g["_rej"] / g[total].replace(0, pd.NA))
            s = g.dropna(subset=["_ratio"]).sort_values("_ratio", ascending=False)
            metric = (s["_ratio"] * 100).round(2)
        if s.empty:
            return None
        return {
            "summary": f"{s.iloc[0][cmap['insurer']]} has the highest average rejection/repudiation ratio at {float(metric.iloc[0]):.2f}%.",
            "charts": [{
                "id": "red_flag_rejection",
                "type": "bar",
                "width": "full",
                "title": "Rejection/Repudiation Ratio by Insurer",
                "description": "Higher values indicate greater customer risk",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Rejection Ratio %", "data": metric.tolist(), "color": red}],
                "highlight": {"operator": "gt", "threshold": float(metric.quantile(0.9)) if len(metric) > 3 else float(metric.iloc[0]), "color": red},
            }],
        }

    # 3) Speed of processing: highest pending claims at end year.
    if "pending" in q and ("slow" in q or "processing" in q or "end of the year" in q or "highest number" in q):
        pending = cmap.get("claims_pending_end_no")
        if not pending:
            return None
        s = df.groupby(cmap["insurer"], as_index=False)[pending].sum().dropna().sort_values(pending, ascending=False)
        if s.empty:
            return None
        return {
            "summary": f"{s.iloc[0][cmap['insurer']]} has the highest pending claims at year-end ({int(s.iloc[0][pending]):,}), suggesting slower processing.",
            "charts": [{
                "id": "pending_end_speed",
                "type": "bar",
                "width": "full",
                "title": "Year-End Pending Claims by Insurer",
                "description": "Higher pending claims may indicate processing backlog",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Pending Claims (No.)", "data": s[pending].fillna(0).astype(float).tolist(), "color": "#E66C37"}],
            }],
        }

    # 4) Value vs volume: ratio_no vs ratio_amt gap.
    if ("value vs" in q or "value vs. volume" in q or "small claims" in q or "high-value" in q or "claims_paid_ratio_no" in q or "claims_paid_ratio_amt" in q):
        rn = cmap.get("claims_paid_ratio_no")
        ra = cmap.get("claims_paid_ratio_amt")
        if not (rn and ra):
            return None
        g = df.groupby(cmap["insurer"], as_index=False)[[rn, ra]].mean().dropna()
        g["gap"] = (g[rn] - g[ra]) * 100
        g = g.sort_values("gap", ascending=False)
        if g.empty:
            return None
        return {
            "summary": f"Largest gap between volume and value settlement is for {g.iloc[0][cmap['insurer']]} ({g.iloc[0]['gap']:.2f} percentage points), which can indicate lower approval quality for high-value claims.",
            "charts": [{
                "id": "value_vs_volume_gap",
                "type": "bar",
                "width": "full",
                "title": "Gap: Claims Paid Ratio (No.) minus (Amount)",
                "description": "Positive gap suggests relatively weaker settlement on high-value claims",
                "labels": g[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Gap (pp)", "data": g["gap"].round(2).tolist(), "color": "#6B007B"}],
                "highlight": {"operator": "gt", "threshold": 2.0, "color": red},
            }],
        }

    # 5) Consistency high payout over years.
    if "consistent" in q or "consistently" in q:
        ra = cmap.get("claims_paid_ratio_amt") or cmap.get("claims_paid_ratio_no")
        if not ra:
            return None
        g = df.groupby([cmap["insurer"], cmap["year"]], as_index=False)[ra].mean()
        stats = g.groupby(cmap["insurer"], as_index=False).agg(
            avg=(ra, "mean"),
            std=(ra, "std"),
            min=(ra, "min"),
        )
        stats["std"] = stats["std"].fillna(0)
        stats["score"] = stats["avg"] - stats["std"]
        stats = stats.sort_values("score", ascending=False)
        if stats.empty:
            return None
        top = stats.iloc[0]
        return {
            "summary": f"{top[cmap['insurer']]} appears most consistent with average payout ratio {top['avg']*100:.2f}% and low year-to-year variability.",
            "charts": [{
                "id": "consistency_score",
                "type": "bar",
                "width": "full",
                "title": "Consistency Score by Insurer",
                "description": "Score = average payout ratio minus volatility (std dev)",
                "labels": stats[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Consistency Score", "data": (stats["score"] * 100).round(2).tolist(), "color": "#197278"}],
            }],
        }

    # 6) Total payouts for a specific year.
    if (
        ("total payouts" in q or "how much money" in q or "pay out" in q or "paid out" in q)
        and ("financial year" in q or "year" in q or any(tok in q for tok in ["2020-21", "2021-22", "2019-20", "2018-19", "2017-18"]))
    ):
        paid_amt = cmap.get("claims_paid_amt")
        if not paid_amt:
            return None
        y = _extract_year_from_query(query, years)
        ydf = df[df[cmap["year"]] == y]
        total_paid = float(ydf[paid_amt].sum()) if not ydf.empty else 0.0
        by_company = ydf.groupby(cmap["insurer"], as_index=False)[paid_amt].sum().sort_values(paid_amt, ascending=False)
        return {
            "summary": f"Total industry payout in {y} is {total_paid:,.2f} (same unit as dataset amount fields).",
            "charts": [{
                "id": "total_payout_year",
                "type": "bar",
                "width": "full",
                "title": f"Total Claims Paid Amount by Insurer ({y})",
                "description": "Industry payout split across insurers",
                "labels": by_company[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Claims Paid Amount", "data": by_company[paid_amt].round(2).tolist(), "color": blue}],
            }],
        }

    # 7) Tragic scale: total death claims filed in a year.
    if "total death claims" in q or ("tragic scale" in q):
        total_no = cmap.get("total_claims_no")
        if not total_no:
            return None
        y = _extract_year_from_query(query, years)
        ydf = df[df[cmap["year"]] == y]
        total_claims = float(ydf[total_no].sum()) if not ydf.empty else 0.0
        trend = df.groupby(cmap["year"], as_index=False)[total_no].sum()
        return {
            "summary": f"Total death claims filed in {y}: {total_claims:,.0f}.",
            "charts": [{
                "id": "death_claim_scale",
                "type": "line",
                "width": "full",
                "title": "Total Death Claims Filed by Year",
                "description": "National scale of filed death claims",
                "labels": trend[cmap["year"]].tolist(),
                "datasets": [{"label": "Total Claims (No.)", "data": trend[total_no].round(0).tolist(), "color": "#744EC2"}],
            }],
        }

    # 8) Lost money: unclaimed amount.
    if "unclaimed" in q:
        unc = cmap.get("claims_unclaimed_amt")
        if not unc:
            return None
        total_unc = float(df[unc].sum())
        by_year = df.groupby(cmap["year"], as_index=False)[unc].sum()
        return {
            "summary": f"Total unclaimed amount across all insurers is {total_unc:,.2f}.",
            "charts": [{
                "id": "unclaimed_amount",
                "type": "bar",
                "width": "full",
                "title": "Unclaimed Amount by Year",
                "description": "Money remaining unclaimed by beneficiaries",
                "labels": by_year[cmap["year"]].tolist(),
                "datasets": [{"label": "Unclaimed Amount", "data": by_year[unc].round(2).tolist(), "color": red}],
            }],
        }

    # 9) Industry improvement over years.
    if ("industry improvement" in q or "better or worse" in q or "overall claim settlement ratio" in q):
        paid_amt = cmap.get("claims_paid_amt")
        int_amt = cmap.get("claims_intimated_amt")
        ratio_amt = cmap.get("claims_paid_ratio_amt")
        if paid_amt and int_amt:
            yearly = df.groupby(cmap["year"], as_index=False)[[paid_amt, int_amt]].sum()
            yearly["ratio"] = (yearly[paid_amt] / yearly[int_amt].replace(0, pd.NA)) * 100
        elif ratio_amt:
            yearly = df.groupby(cmap["year"], as_index=False)[ratio_amt].mean()
            yearly["ratio"] = yearly[ratio_amt] * 100
        else:
            return None
        yearly = yearly.dropna(subset=["ratio"])
        if yearly.empty:
            return None
        change = float(yearly["ratio"].iloc[-1] - yearly["ratio"].iloc[0])
        direction = "improved" if change >= 0 else "worsened"
        return {
            "summary": f"Overall industry settlement ratio has {direction} by {abs(change):.2f} percentage points over the available period.",
            "charts": [{
                "id": "industry_improvement",
                "type": "line",
                "width": "full",
                "title": "Industry Claim Settlement Ratio Trend",
                "description": "Overall settlement ratio by year",
                "labels": yearly[cmap["year"]].tolist(),
                "datasets": [{"label": "Settlement Ratio %", "data": yearly["ratio"].round(2).tolist(), "color": blue}],
            }],
        }

    # 10) COVID impact on intimated claims.
    if "covid" in q or "pandemic" in q or "spike" in q:
        intimated_no = cmap.get("claims_intimated_no")
        if not intimated_no:
            return None
        by_year = df.groupby(cmap["year"], as_index=False)[intimated_no].sum()
        ymap = {str(r[cmap["year"]]): float(r[intimated_no]) for _, r in by_year.iterrows()}
        pre_years = [y for y in ymap.keys() if y < "2020-21"]
        pre_avg = (sum(ymap[y] for y in pre_years) / len(pre_years)) if pre_years else 0.0
        y20 = ymap.get("2020-21", 0.0)
        y21 = ymap.get("2021-22", 0.0)
        spike20 = ((y20 - pre_avg) / pre_avg * 100) if pre_avg else 0.0
        spike21 = ((y21 - pre_avg) / pre_avg * 100) if pre_avg else 0.0
        return {
            "summary": f"Compared to pre-pandemic average, intimated claims changed by {spike20:.2f}% in 2020-21 and {spike21:.2f}% in 2021-22.",
            "charts": [{
                "id": "covid_impact",
                "type": "line",
                "width": "full",
                "title": "Claims Intimated Trend (COVID Impact)",
                "description": "Yearly filed claims to detect pandemic spike",
                "labels": by_year[cmap["year"]].tolist(),
                "datasets": [{"label": "Claims Intimated (No.)", "data": by_year[intimated_no].round(0).tolist(), "color": "#E66C37"}],
            }],
        }

    # 11) Market leader by volume.
    if ("market leader" in q or "dominates" in q) and ("volume" in q or "highest total number of claims" in q):
        total_no = cmap.get("total_claims_no")
        if not total_no:
            return None
        s = df.groupby(cmap["insurer"], as_index=False)[total_no].sum().sort_values(total_no, ascending=False)
        if s.empty:
            return None
        return {
            "summary": f"{s.iloc[0][cmap['insurer']]} leads by claim volume with {int(s.iloc[0][total_no]):,} total claims.",
            "charts": [{
                "id": "market_leader_volume",
                "type": "bar",
                "width": "full",
                "title": "Market Leaders by Claim Volume",
                "description": "Total number of claims handled by insurer",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Total Claims (No.)", "data": s[total_no].round(0).tolist(), "color": blue}],
            }],
        }

    # 12) Market leader by value.
    if ("market leader" in q or "highest" in q) and ("value" in q or "amount" in q or "rupees" in q):
        total_amt = cmap.get("total_claims_amt") or cmap.get("claims_paid_amt")
        if not total_amt:
            return None
        s = df.groupby(cmap["insurer"], as_index=False)[total_amt].sum().sort_values(total_amt, ascending=False)
        if s.empty:
            return None
        return {
            "summary": f"{s.iloc[0][cmap['insurer']]} leads by claim value with total amount {float(s.iloc[0][total_amt]):,.2f}.",
            "charts": [{
                "id": "market_leader_value",
                "type": "bar",
                "width": "full",
                "title": "Market Leaders by Claim Value",
                "description": "Total claim amount handled by insurer",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Total Claims Amount", "data": s[total_amt].round(2).tolist(), "color": "#01B8AA"}],
            }],
        }

    # 13) Public vs private rejection comparison.
    if "public vs private" in q or ("private" in q and "lic" in q):
        ratio_col = cmap.get("claims_repudiated_rejected_ratio_no")
        if not ratio_col:
            return None
        df2 = df[[cmap["insurer"], ratio_col]].dropna().copy()
        df2["segment"] = df2[cmap["insurer"]].apply(lambda x: "Public (LIC)" if str(x).strip().upper() == "LIC" else "Private")
        s = df2.groupby("segment", as_index=False)[ratio_col].mean()
        return {
            "summary": "Public vs private rejection ratio comparison computed from average repudiated/rejected ratio.",
            "charts": [{
                "id": "public_private_reject",
                "type": "bar",
                "width": "half",
                "title": "Public vs Private Rejection Ratio",
                "description": "Average repudiated/rejected ratio by segment",
                "labels": s["segment"].tolist(),
                "datasets": [{"label": "Rejection Ratio %", "data": (s[ratio_col] * 100).round(2).tolist(), "color": red}],
            }],
        }

    # 14) Backlog management: highest pending start.
    if "backlog" in q or "pending_start" in q or "pending start" in q:
        ps = cmap.get("claims_pending_start_no")
        if not ps:
            return None
        s = df.groupby(cmap["insurer"], as_index=False)[ps].sum().sort_values(ps, ascending=False)
        if s.empty:
            return None
        return {
            "summary": f"{s.iloc[0][cmap['insurer']]} has the largest opening backlog with {int(s.iloc[0][ps]):,} pending-start claims.",
            "charts": [{
                "id": "backlog_start",
                "type": "bar",
                "width": "full",
                "title": "Opening Backlog by Insurer",
                "description": "Total claims pending at start of year",
                "labels": s[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Pending Start (No.)", "data": s[ps].round(0).tolist(), "color": "#FD625E"}],
            }],
        }

    # 15) Most improved in rejection rate over period.
    if "most improved" in q or "improvement" in q and "rejection" in q:
        rr = cmap.get("claims_repudiated_rejected_ratio_no")
        if not rr:
            return None
        yearly = df.groupby([cmap["insurer"], cmap["year"]], as_index=False)[rr].mean().dropna()
        if yearly.empty:
            return None
        first_year = sorted(yearly[cmap["year"]].unique().tolist())[0]
        last_year = sorted(yearly[cmap["year"]].unique().tolist())[-1]
        first = yearly[yearly[cmap["year"]] == first_year][[cmap["insurer"], rr]].rename(columns={rr: "first"})
        last = yearly[yearly[cmap["year"]] == last_year][[cmap["insurer"], rr]].rename(columns={rr: "last"})
        merged = pd.merge(first, last, on=cmap["insurer"], how="inner")
        merged["improvement_pp"] = (merged["first"] - merged["last"]) * 100
        merged = merged.sort_values("improvement_pp", ascending=False)
        if merged.empty:
            return None
        return {
            "summary": f"{merged.iloc[0][cmap['insurer']]} shows the biggest improvement in rejection ratio ({merged.iloc[0]['improvement_pp']:.2f} percentage points reduction from {first_year} to {last_year}).",
            "charts": [{
                "id": "most_improved_rejection",
                "type": "bar",
                "width": "full",
                "title": f"Improvement in Rejection Ratio ({first_year} to {last_year})",
                "description": "Positive values indicate reduction in rejection ratio",
                "labels": merged[cmap["insurer"]].tolist(),
                "datasets": [{"label": "Improvement (pp)", "data": merged["improvement_pp"].round(2).tolist(), "color": "#1AAB40"}],
            }],
        }

    return None


# Serve built frontend assets when running in production/container.
app = Flask(__name__, static_folder="frontend/dist", static_url_path="")
CORS(app)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Ensure API errors are always JSON instead of HTML error pages."""
    if request.path.startswith("/api/"):
        return jsonify({
            "error": e.name,
            "message": e.description,
            "status": e.code,
        }), e.code
    return e


@app.errorhandler(Exception)
def handle_unexpected_exception(e):
    """Catch uncaught backend errors and return JSON for API callers."""
    print(f"[Unhandled Error] {type(e).__name__}: {str(e)}")
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "status": 500,
        }), 500
    return jsonify({"error": "Internal Server Error"}), 500

# Single LangChain chat instance (per process — extends with session support if needed)
chat = LangChainChat()

# In-memory CSV store (keyed by session_id sent from frontend)
_csv_store: dict[str, list] = {}

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "default_data.json")


def _load_default_data():
    """Load default insurance claims data embedded in the project."""
    if os.path.exists(DEFAULT_DATA_PATH):
        with open(DEFAULT_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.route("/api/health", methods=["GET"])
def health():
    api_key_present = bool(
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or getattr(chat, "api_key", "")
    )
    return jsonify({
        "status": "ok",
        "model": chat.active_model,
        "api_key_configured": api_key_present,
    })


@app.route("/api/test-key", methods=["GET"])
def test_key():
    """Quick endpoint to verify Gemini API key & connectivity."""
    try:
        llm_timeout_seconds = _safe_int_env("LLM_TIMEOUT_SECONDS", 60)
        resp = _invoke_llm_with_timeout(
            [{"type": "system", "content": "Reply with exactly: OK"},
             {"type": "human", "content": "Test"}]
            , timeout_seconds=llm_timeout_seconds
        )
        return jsonify({"status": "ok", "model": chat.active_model, "response": resp.content[:100]})
    except Exception as e:
        return jsonify({"status": "error", "error": f"{type(e).__name__}: {e}"}), 500


@app.route("/api/schema", methods=["GET"])
def get_schema():
    """Return schema info for the default dataset."""
    data = _load_default_data()
    if not data:
        return jsonify({"name": "No data", "rows": 0, "cols": 0, "columns": []})
    cols = list(data[0].keys()) if data else []
    return jsonify({
        "name": "India_Life_Insurance_Claims",
        "rows": len(data),
        "cols": len(cols),
        "columns": cols,
    })


@app.route("/api/upload", methods=["POST"])
def upload_csv():
    """Accept a CSV file, parse it, store in memory, return schema."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are accepted"}), 400

    # Sanitize filename to prevent path traversal
    safe_name = os.path.basename(file.filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        analyzer = CSVAnalyzer()
        analyzer.load_data(tmp_path)
        data = analyzer.df.to_dict(orient="records")

        session_id = request.form.get("session_id", "default")
        _csv_store[session_id] = data

        cols = list(analyzer.df.columns)
        return jsonify({
            "name": safe_name.replace(".csv", ""),
            "rows": len(data),
            "cols": len(cols),
            "columns": cols,
        })
    finally:
        os.unlink(tmp_path)


@app.route("/api/overview", methods=["POST"])
def get_overview():
    """Return KPI stats + key columns + auto-chart data for the overview tab."""
    import numpy as np
    body = request.get_json(force=True) or {}
    session_id = body.get("session_id", "default")
    csv_data = _csv_store.get(session_id) or _load_default_data()

    if not csv_data:
        return jsonify({"error": "No data"}), 400

    # Power BI color palette
    PBI = ["#118DFF", "#12239E", "#E66C37", "#6B007B", "#E044A7",
           "#744EC2", "#D9B300", "#D64550", "#197278", "#1AAB40",
           "#01B8AA", "#FD625E", "#F2C80F", "#8AD4EB", "#FE9666"]

    df = pd.DataFrame(csv_data)

    # KPIs
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    completeness = round((1 - missing_cells / max(total_rows * total_cols, 1)) * 100, 1)

    # Detect numeric / categorical columns
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    if not numeric_cols:
        numeric_cols = [
            col for col in df.columns
            if pd.to_numeric(df[col], errors="coerce").notna().mean() > 0.7
        ]
        # Convert detected numeric columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    categorical_cols = [
        col for col in df.columns
        if col not in numeric_cols and df[col].nunique(dropna=True) > 1
    ]

    # Top 5 key columns ranked by completeness
    non_null_ratio = (df.notna().sum() / max(total_rows, 1)).sort_values(ascending=False)
    ranked = list(non_null_ratio.index)
    key_columns = []
    for col in ranked:
        if col in numeric_cols or col in categorical_cols:
            key_columns.append(col)
        if len(key_columns) >= 5:
            break
    if not key_columns:
        key_columns = list(df.columns[:5])

    main_num = next((c for c in key_columns if c in numeric_cols), None)
    # Fallback: pick first numeric column even if not in key_columns
    if not main_num and numeric_cols:
        main_num = numeric_cols[0]
    second_num = next((c for c in numeric_cols if c != main_num), None)
    main_cat = next((c for c in key_columns if c in categorical_cols), None)
    # Fallback: pick first categorical column
    if not main_cat and categorical_cols:
        main_cat = categorical_cols[0]
    second_cat = next((c for c in categorical_cols if c != main_cat), None)

    # Find date/year column
    date_col = None
    for col in list(df.columns):
        lowered = str(col).lower()
        if "date" in lowered or "year" in lowered or "month" in lowered or "period" in lowered:
            date_col = col
            break

    charts = []

    # 1. Time series trend (line chart, full width)
    if date_col and main_num:
        trend = df[[date_col, main_num]].copy()
        trend[main_num] = pd.to_numeric(trend[main_num], errors="coerce")
        if "year" in str(date_col).lower():
            extracted = trend[date_col].astype(str).str.extract(r"(19\d{2}|20\d{2}|21\d{2})", expand=False)
            trend[date_col] = pd.to_numeric(extracted, errors="coerce")
        trend = trend.dropna()
        if not trend.empty:
            grouped = trend.groupby(date_col, as_index=False)[main_num].mean().sort_values(date_col)
            datasets = [{"label": main_num, "data": [round(float(v), 2) for v in grouped[main_num].tolist()], "color": PBI[0]}]
            # Add second numeric as overlay if available
            if second_num:
                trend2 = df[[date_col, second_num]].copy()
                trend2[second_num] = pd.to_numeric(trend2[second_num], errors="coerce")
                if "year" in str(date_col).lower():
                    ext2 = trend2[date_col].astype(str).str.extract(r"(19\d{2}|20\d{2}|21\d{2})", expand=False)
                    trend2[date_col] = pd.to_numeric(ext2, errors="coerce")
                trend2 = trend2.dropna()
                if not trend2.empty:
                    g2 = trend2.groupby(date_col, as_index=False)[second_num].mean().sort_values(date_col)
                    datasets.append({"label": second_num, "data": [round(float(v), 2) for v in g2[second_num].tolist()], "color": PBI[2]})
            charts.append({
                "id": "time_series", "type": "line", "width": "full",
                "title": f"Trend Over {date_col}",
                "description": f"Average values over {date_col}",
                "labels": [str(x) for x in grouped[date_col].tolist()],
                "datasets": datasets,
            })

    # 2. Category composition – PIE chart (Power BI style)
    if main_cat:
        all_cats = df[main_cat].fillna("Unknown").astype(str).value_counts()
        # Use all categories if reasonable, otherwise top 15 with "Others"
        if len(all_cats) <= 15:
            cat_data = all_cats
        else:
            top_cats = all_cats.head(14)
            others_count = all_cats[14:].sum()
            cat_data = pd.concat([top_cats, pd.Series({"Others": others_count})])
        
        charts.append({
            "id": "cat_pie", "type": "doughnut", "width": "half",
            "title": f"{main_cat} Breakdown" + (" (All Categories)" if len(all_cats) <= 15 else " (Top 14 + Others)"),
            "description": f"Distribution of categories in {main_cat} ({len(all_cats)} total categories)",
            "labels": cat_data.index.tolist(),
            "datasets": [{"label": "Count", "data": cat_data.values.tolist(), "color": PBI[0]}],
        })

    # 3. Value distribution histogram (bar chart)
    if main_num:
        num_series = pd.to_numeric(df[main_num], errors="coerce").dropna()
        if not num_series.empty:
            bins = min(max(int(len(num_series) ** 0.5), 6), 15)
            counts, bin_edges = np.histogram(num_series, bins=bins)
            charts.append({
                "id": "distribution", "type": "bar", "width": "half",
                "title": f"{main_num} Distribution",
                "description": f"Frequency distribution of {main_num}",
                "labels": [f"{e:.1f}" for e in bin_edges[:-1]],
                "datasets": [{"label": "Frequency", "data": counts.tolist(), "color": PBI[10]}],
            })

    # 4. Category comparison – BAR chart with numeric metric
    if main_cat and main_num:
        cat_agg = df.groupby(main_cat)[main_num].mean().sort_values(ascending=False)
        # Use all categories if reasonable (<= 30), otherwise top 20
        if len(cat_agg) <= 30:
            cat_agg_display = cat_agg
            title_suffix = " (All)"
        else:
            cat_agg_display = cat_agg.head(20)
            title_suffix = f" (Top 20 of {len(cat_agg)})"
        
        if not cat_agg_display.empty:
            charts.append({
                "id": "cat_bar", "type": "bar", "width": "full" if len(cat_agg_display) > 15 else "half",
                "title": f"Avg {main_num} by {main_cat}{title_suffix}",
                "description": f"Average {main_num} per {main_cat} category",
                "labels": [str(x) for x in cat_agg_display.index.tolist()],
                "datasets": [{"label": f"Avg {main_num}", "data": [round(float(v), 2) for v in cat_agg_display.values.tolist()], "color": PBI[2]}],
            })

    # 5. Second category pie (if available)
    if second_cat:
        all_cats2 = df[second_cat].fillna("Unknown").astype(str).value_counts()
        # Use all categories if <= 12, otherwise consolidate
        if len(all_cats2) <= 12:
            cat_data2 = all_cats2
        else:
            top_cats2 = all_cats2.head(11)
            others_count2 = all_cats2[11:].sum()
            cat_data2 = pd.concat([top_cats2, pd.Series({"Others": others_count2})])
        
        charts.append({
            "id": "cat2_pie", "type": "pie", "width": "half",
            "title": f"{second_cat} Composition" + ("" if len(all_cats2) <= 12 else f" ({len(all_cats2)} total)"),
            "description": f"Proportion of categories in {second_cat}",
            "labels": cat_data2.index.tolist(),
            "datasets": [{"label": "Count", "data": cat_data2.values.tolist(), "color": PBI[3]}],
        })

    # 6. Data quality – missing per key column
    miss = df[key_columns].isna().sum().sort_values(ascending=False)
    if miss.sum() > 0:
        charts.append({
            "id": "quality", "type": "bar", "width": "half",
            "title": "Data Quality",
            "description": "Missing values per key column",
            "labels": miss.index.tolist(),
            "datasets": [{"label": "Missing", "data": miss.values.tolist(), "color": PBI[7]}],
        })

    # 7. Correlation scatter (if two numeric cols)
    if main_num and second_num:
        scatter_df = df[[main_num, second_num]].copy()
        scatter_df[main_num] = pd.to_numeric(scatter_df[main_num], errors="coerce")
        scatter_df[second_num] = pd.to_numeric(scatter_df[second_num], errors="coerce")
        scatter_df = scatter_df.dropna()
        # Use all points if <= 500, otherwise sample evenly
        if len(scatter_df) > 500:
            scatter_df = scatter_df.sample(n=500, random_state=42)
        
        if not scatter_df.empty:
            charts.append({
                "id": "correlation", "type": "scatter", "width": "half",
                "title": f"{main_num} vs {second_num}",
                "description": f"Correlation between {main_num} and {second_num}",
                "labels": [],
                "datasets": [{
                    "label": f"{main_num} vs {second_num}",
                    "data": [{"x": float(r[main_num]), "y": float(r[second_num])} for _, r in scatter_df.iterrows()],
                    "color": PBI[5],
                }],
            })

    # 8. Column data types breakdown (always useful)
    dtype_counts = {}
    for col in df.columns:
        if col in numeric_cols:
            dtype_counts["Numeric"] = dtype_counts.get("Numeric", 0) + 1
        elif col in categorical_cols:
            dtype_counts["Categorical"] = dtype_counts.get("Categorical", 0) + 1
        else:
            dtype_counts["Other"] = dtype_counts.get("Other", 0) + 1
    charts.append({
        "id": "dtypes", "type": "doughnut", "width": "half",
        "title": "Column Types",
        "description": "Breakdown of column data types",
        "labels": list(dtype_counts.keys()),
        "datasets": [{"label": "Columns", "data": list(dtype_counts.values()), "color": PBI[0]}],
    })

    return jsonify({
        "kpi": {
            "rows": total_rows, "cols": total_cols,
            "missing": missing_cells, "duplicates": duplicate_rows,
            "completeness": completeness,
        },
        "key_columns": key_columns,
        "charts": charts,
    })


@app.route("/api/query", methods=["POST"])
def query():
    """
    Accept a natural-language query + optional csv_data, return chart JSON.
    Body: { query, csv_data (optional array), conversation_history (optional) }
    """
    body = request.get_json(force=True)
    if not body or not body.get("query"):
        return jsonify({"error": "Missing 'query' field"}), 400

    # Fail fast with explicit guidance if Gemini key is missing in deployment.
    api_key_present = bool(
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or getattr(chat, "api_key", "")
    )
    if not api_key_present:
        return jsonify({
            "summary": "⚠️ Gemini API key is not configured on the server.",
            "charts": [],
            "error": "Missing GOOGLE_API_KEY (or GEMINI_API_KEY). Set it in deployment environment variables.",
        }), 200

    user_query: str = body["query"]
    highlight_rule = _extract_highlight_rule(user_query)
    session_id: str = body.get("session_id", "default")
    csv_data: list = body.get("csv_data") or _csv_store.get(session_id) or _load_default_data()
    conversation_history: list = body.get("conversation_history", [])

    if not csv_data:
        return jsonify({"error": "No data available. Please upload a CSV or use the default dataset."}), 400

    # Generic deterministic handler for the reference payout question on any CSV schema.
    generic_reference_result = _build_generic_reference_question_response(user_query, csv_data)
    if generic_reference_result:
        generic_reference_result = _apply_highlight_rule_to_charts(generic_reference_result, highlight_rule)
        return jsonify(generic_reference_result)
    if _is_generic_reference_payout_question(user_query):
        return jsonify({
            "summary": "I could not confidently detect required payout columns for this CSV. Please specify which amount column to use and, if available, the year/date column.",
            "charts": [],
            "error": "Reference payout question detected but dataset mapping failed.",
        }), 200

    # Dynamic matrix path for any CSV schema.
    if _is_dynamic_matrix_request(user_query):
        matrix_threshold = (highlight_rule or {}).get("threshold")
        matrix_result, matrix_error = _build_dynamic_matrix_chart(csv_data, user_query, threshold=matrix_threshold)
        if matrix_result:
            matrix_result = _apply_highlight_rule_to_charts(matrix_result, highlight_rule)
            return jsonify(matrix_result)
        return jsonify({
            "summary": f"⚠️ Unable to build matrix for this CSV: {matrix_error}",
            "charts": [],
            "error": matrix_error,
        }), 200

    # ===== DATA RETRIEVAL: Detect query intent and validate against available data =====
    cols = list(csv_data[0].keys()) if csv_data else []
    is_answerable, chart_type_hint, reason = detect_query_intent(user_query, cols)
    
    if not is_answerable:
        return jsonify({
            "summary": f"⚠️ Cannot answer this query: {reason}",
            "charts": [],
            "error": f"Query cannot be answered with available data. Reason: {reason}"
        }), 200  # Return 200 so frontend can display the message
    
    print(f"[Query Intent] Answerable: {is_answerable}, Chart Hint: {chart_type_hint}, Reason: {reason}")

    # Build schema description
    cols = list(csv_data[0].keys()) if csv_data else []
    schema_parts = []
    for col in cols:
        vals = [row.get(col) for row in csv_data if row.get(col) is not None]
        num_vals = [v for v in vals if isinstance(v, (int, float))]
        if num_vals and len(num_vals) > len(vals) * 0.5:
            mn, mx = min(num_vals), max(num_vals)
            schema_parts.append(f"{col} (number, min={mn:.2f}, max={mx:.2f})")
        else:
            uniq = list(dict.fromkeys(str(v) for v in vals))[:6]
            schema_parts.append(f"{col} (text, values: {', '.join(uniq)})")

    schema_desc = "\n  ".join(schema_parts)
    sample_rows = json.dumps(csv_data[:5], indent=2)
    
    # Smart data sampling: Send full data if small, otherwise send representative sample
    total_rows = len(csv_data)
    if total_rows <= 1000:
        # Send ALL data for accurate analysis
        data_for_llm = csv_data
        print(f"[Data Sampling] Using FULL dataset: {total_rows} rows")
    else:
        # For large datasets, send first 800 + last 200 rows to capture range
        data_for_llm = csv_data[:800] + csv_data[-200:]
        print(f"[Data Sampling] Large dataset ({total_rows} rows), sending {len(data_for_llm)} representative rows to LLM")
    
    all_data_json = json.dumps(data_for_llm)
    data_info = f"Total dataset: {total_rows} rows. Provided: {len(data_for_llm)} rows for analysis."

    system_prompt = """You are an expert Business Intelligence AI that creates Power BI-style dashboards. Analyze the user's question about any dataset and generate the most appropriate dashboard charts.

CRITICAL - HALLUCINATION PREVENTION:
- You MUST use ONLY the columns listed in the SCHEMA below
- You MUST calculate values from the actual DATA provided - NEVER invent numbers
- If the query asks about columns/data that don't exist, return an empty charts array and explain in the summary
- If you cannot answer the query with the available data, respond with: {"summary": "⚠️ I cannot answer this query because [reason]", "charts": []}

Respond ONLY with a valid JSON object (no markdown, no extra text, no explanation):
{
  "summary": "1-2 sentence insight about the data OR explanation if query cannot be answered",
  "charts": [
    {
      "id": "chart_1",
      "type": "line|bar|pie|doughnut|radar|scatter|polarArea|area",
      "title": "Chart Title",
      "description": "What it shows",
      "width": "full|half|third",
      "labels": ["label1","label2",...],
      "datasets": [
        {"label":"Series Name","data":[1,2,3...],"color":"#hex"}
            ],
            "highlight": {"operator":"lt|lte|gt|gte", "threshold": 85, "color":"#D64550"}
    }
  ]
}

CONTEXTUAL CHART TYPE SELECTION RULES (pick the most appropriate type):
- Trends over time / timeline data → line chart (width=full)
- Comparing values across categories → bar chart (width=full or half)
- Composition / proportions / share / percentage → pie or doughnut (width=half)
- Multi-metric comparison across a few items → radar (width=half)
- Correlation between two numeric values → scatter (width=half)
- Cumulative or area trends → area chart (width=full)
- Distribution / frequency → bar chart (width=half)
- If user asks "compare" → prefer bar chart
- If user asks "trend" or "over time" → prefer line chart
- If user asks "breakdown" or "proportion" → prefer doughnut or pie
- If query is broad/general → generate 2-3 varied charts (mix of line, bar, pie)

DATA RETRIEVAL & FORMATTING RULES:
- First, identify which columns from the SCHEMA are needed to answer the query
- Aggregate/filter the DATA as needed (sum, average, count, group by, etc.)
- **CRITICAL: Include ALL relevant data points matching the query - do NOT arbitrarily limit to "top 10" or "top 20" unless:**
  * User explicitly asks for "top N" (e.g., "top 5 insurers", "top 10 products")
  * There are >50 categories (then use top 40 + "Others" category with sum of remaining)
  * User asks for a specific subset (e.g., "insurers in region X")
- If showing all categories (e.g., all insurers, all regions), include ALL of them in the chart
- For queries like "show claims by all insurers" or "compare across all categories" → use COMPLETE data
- Generate 1-4 charts most relevant to the query — create a cohesive dashboard
- width: full for primary chart (especially if many categories), half for supporting charts, third for small summaries
- Use ONLY columns and values that exist in the schema and data — never fabricate numbers
- Power BI Colors: use these hex codes: #118DFF (blue), #E66C37 (orange), #6B007B (purple), #D9B300 (gold), #1AAB40 (green), #D64550 (red), #744EC2 (violet), #01B8AA (teal), #E044A7 (pink), #197278 (dark teal)
- datasets.data must be parallel to labels array with the same length
- For pie/doughnut: single dataset, data is numbers, labels are category names
- Sort bar charts by value for readability (but include ALL values)
- All numeric values in datasets.data must be plain numbers (not strings)
- Multiple datasets per chart are encouraged for comparisons (e.g. 2 lines on same line chart)
- In chart title/description, mention if showing "All X" or "Top N of Y" for transparency
- If user asks to highlight values (e.g., "highlight below 85 in red"), include a chart.highlight object with operator/threshold/color
- Apply highlight rules to all relevant charts, not just tables/matrices

Remember: If you cannot properly answer with the available data, return empty charts array and explain why in the summary.
REMEMBER: 100% ACCURACY = Include ALL relevant data unless user explicitly asks for subset!"""

    user_msg = f"""SCHEMA:\n  {schema_desc}\n\nSAMPLE (5 rows):\n{sample_rows}\n\n{data_info}\nDATA:\n{all_data_json}\n\nUSER QUERY: {user_query}\n\nIMPORTANT: Unless the user explicitly asks for "top N" or a subset, include ALL categories/values that match the query. For example:\n- "Compare insurers" = ALL insurers, not just top 10\n- "Show sales by region" = ALL regions\n- "Breakdown by category" = ALL categories (or top 40 + Others if >50)\n- If user asks highlight conditions (e.g., below/above threshold), include chart.highlight metadata\n\nGenerate complete, accurate dashboard JSON now."""

    # Build messages as plain dicts
    messages = [{"type": "system", "content": system_prompt}]
    for msg in conversation_history[-6:]:
        if msg.get("role") == "user":
            messages.append({"type": "human", "content": msg["content"]})
        elif msg.get("role") == "assistant":
            messages.append({"type": "ai", "content": msg["content"]})
    messages.append({"type": "human", "content": user_msg})

    try:
        import re
        llm_timeout_seconds = _safe_int_env("LLM_TIMEOUT_SECONDS", 60)
        response = _invoke_llm_with_timeout(messages, timeout_seconds=llm_timeout_seconds)
        text = response.content.strip()
        # Extract JSON robustly — find the first { ... } block
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return jsonify({
                "summary": "⚠️ The AI model did not return a valid response. Please try rephrasing your query.",
                "charts": [],
                "error": "LLM did not return a JSON object"
            }), 200
        text = match.group(0)
        result = json.loads(text)
        result = _apply_highlight_rule_to_charts(result, highlight_rule)
        
        # ===== HALLUCINATION VALIDATION: Check if LLM response is valid =====
        is_valid, error_msg, sanitized_result = validate_chart_response(result, cols, csv_data)
        
        if not is_valid:
            print(f"[Validation Failed] {error_msg}")
            return jsonify({
                "summary": f"⚠️ {error_msg}. The model may have hallucinated or misunderstood the query. Please try asking in a different way.",
                "charts": [],
                "error": error_msg
            }), 200
        
        # ===== CONTEXTUAL CHART SELECTION: Log what chart types were chosen and why =====
        selected_types = [c.get("type") for c in sanitized_result.get("charts", [])]
        chart_data_counts = [len(c.get("labels", [])) for c in sanitized_result.get("charts", [])]
        print(f"[Chart Selection] Query: '{user_query[:60]}...' → Types: {selected_types}, Data points: {chart_data_counts}")
        if chart_type_hint:
            if chart_type_hint in selected_types:
                print(f"[Chart Selection] ✓ Correct: Expected '{chart_type_hint}' based on query, found it")
            else:
                print(f"[Chart Selection] ⚠ Model chose {selected_types} instead of expected '{chart_type_hint}'")
        
        if highlight_rule and sanitized_result.get("summary"):
            sanitized_result["summary"] = (
                f"{sanitized_result['summary']} Highlight rule applied: "
                f"{highlight_rule['operator']} {highlight_rule['threshold']} in {highlight_rule['color']}."
            )

        return jsonify(sanitized_result)
    except json.JSONDecodeError as e:
        print(f"[JSON Error] {str(e)}")
        return jsonify({
            "summary": "⚠️ The AI returned invalid data. This might indicate the query cannot be answered with the available dataset.",
            "charts": [],
            "error": f"LLM returned invalid JSON: {str(e)}"
        }), 200
    except Exception as e:
        print(f"[Error] {str(e)}")
        return jsonify({
            "summary": f"⚠️ An error occurred: {str(e)}",
            "charts": [],
            "error": str(e)
        }), 200


@app.route("/", methods=["GET"])
def serve_root():
    """Serve frontend entrypoint when the production build exists."""
    index_path = os.path.join(app.static_folder or "", "index.html")
    if app.static_folder and os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")

    return jsonify({
        "message": "Frontend build not found. Build frontend with 'npm run build' in /frontend.",
        "health": "/api/health"
    }), 200


@app.route("/<path:path>", methods=["GET"])
def serve_frontend(path):
    """Serve static assets and SPA routes for the React frontend."""
    # Let undefined API paths return a clean API-style 404.
    if path.startswith("api/"):
        return jsonify({"error": "Not Found"}), 404

    static_file = os.path.join(app.static_folder or "", path)
    if app.static_folder and os.path.exists(static_file):
        return send_from_directory(app.static_folder, path)

    index_path = os.path.join(app.static_folder or "", "index.html")
    if app.static_folder and os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")

    return jsonify({"error": "Frontend build not found"}), 404


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)
