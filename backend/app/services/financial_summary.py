from typing import Optional
from datetime import datetime
from app.services.dashboard_service import dashboard_service
from app.services.budget_service import budget_service
from app.services.forecast_service import forecast_service
from app.services.anomaly_service import anomaly_service


async def build_financial_context(
    user_id: str = "default_user",
    year: Optional[int] = None,
    month: Optional[int] = None
) -> str:
    """
    Aggregates real-time user financial data across income, expenses, top categories,
    budgets, forecasts, and anomalies into a structured string for the LLM system prompt.
    """
    today = datetime.now()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    month_name = datetime(year, month, 1).strftime("%B %Y")

    # 1. Dashboard summary
    summary_data = await dashboard_service.get_summary(user_id=user_id, year=year, month=month)
    total_income = summary_data.get("total_income", 0.0)
    total_expenses = summary_data.get("total_expenses", 0.0)
    total_savings = summary_data.get("total_savings", 0.0)
    savings_rate = summary_data.get("savings_rate", 0.0)

    # 2. Top spending categories
    top_categories = await dashboard_service.get_top_categories(user_id=user_id, year=year, month=month, limit=5)
    category_summary_lines = []
    if top_categories:
        for cat in top_categories:
            category_summary_lines.append(
                f"  - {cat.get('category', 'Other')}: Rs. {cat.get('amount', 0.0):,.2f} ({cat.get('percentage', 0.0):.1f}% of expenses)"
            )
    else:
        category_summary_lines.append("  - No category expenses recorded for this month.")

    # 3. Budget analysis
    budget_analysis = await budget_service.get_budget_analysis(user_id=user_id, year=year, month=month)
    budget_lines = []
    category_budgets = budget_analysis.get("category_budgets", [])
    overall_budget = budget_analysis.get("overall_budget")

    if overall_budget:
        ob_status = overall_budget.status.value if hasattr(overall_budget.status, 'value') else str(overall_budget.status)
        budget_lines.append(
            f"  - Overall Monthly Budget: Rs. {overall_budget.budget_amount:,.2f} | Spent: Rs. {overall_budget.actual_spending:,.2f} | Status: {ob_status}"
        )

    if category_budgets:
        for cb in category_budgets:
            status_val = cb.status.value if hasattr(cb.status, 'value') else str(cb.status)
            budget_lines.append(
                f"  - {cb.category}: Budget Rs. {cb.budget_amount:,.2f} | Spent Rs. {cb.actual_spending:,.2f} ({cb.percentage_used:.1f}%) | Status: {status_val}"
            )
    elif not overall_budget:
        budget_lines.append("  - No active budgets configured for this month.")

    # 4. Forecasts
    forecast_lines = []
    try:
        category_forecasts = await forecast_service.get_category_forecasts(user_id=user_id, year=year, month=month)
        if category_forecasts:
            for f in category_forecasts[:5]:
                f_cat = getattr(f, "category", "")
                f_proj = getattr(f, "projected_spending", 0.0)
                f_status = getattr(f, "status", "")
                forecast_lines.append(f"  - {f_cat}: Projected EOM spending Rs. {f_proj:,.2f} (Status: {f_status})")
        else:
            forecast_lines.append("  - No forecast projections available.")
    except Exception as e:
        forecast_lines.append(f"  - Forecast data unavailable ({e}).")

    # 5. Anomalies
    anomaly_lines = []
    try:
        anomaly_summary = await anomaly_service.get_anomaly_summary(user_id=user_id, year=year, month=month)
        anomalies_list = getattr(anomaly_summary, "anomalies", [])
        if anomalies_list:
            anomaly_lines.append(f"  - Total Anomalies Flagged: {len(anomalies_list)}")
            for item in anomalies_list[:4]:
                title = getattr(item, "title", "Anomaly")
                desc = getattr(item, "description", "")
                severity = getattr(item, "severity", "")
                anomaly_lines.append(f"  - [{severity.upper()}] {title}: {desc}")
        else:
            anomaly_lines.append("  - No unusual spending anomalies detected.")
    except Exception as e:
        anomaly_lines.append(f"  - Anomaly data unavailable ({e}).")

    # Construct final summary string
    context_str = f"""
USER FINANCIAL CONTEXT ({month_name})
-----------------------------------------
1. OVERVIEW:
   - Total Income: Rs. {total_income:,.2f}
   - Total Expenses: Rs. {total_expenses:,.2f}
   - Net Savings: Rs. {total_savings:,.2f}
   - Savings Rate: {savings_rate:.2f}%

2. TOP EXPENSE CATEGORIES:
{chr(10).join(category_summary_lines)}

3. BUDGET STATUS:
{chr(10).join(budget_lines)}

4. SPENDING FORECAST & PROJECTIONS:
{chr(10).join(forecast_lines)}

5. RECENT ANOMALIES & ALERTS:
{chr(10).join(anomaly_lines)}
-----------------------------------------
    """.strip()

    return context_str.replace("₹", "Rs. ")

