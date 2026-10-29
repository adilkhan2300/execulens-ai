"""
ExecuLens AI - UI Design System & Plotly Visualization Components
Provides custom executive corporate CSS themes, metric scorecard cards,
and standardized interactive Plotly visualization charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional
from config.settings import PALETTE, format_currency, format_percentage

def apply_executive_styles():
    """Inject custom executive CSS styling into Streamlit."""
    css = f"""
    <style>
        /* Import clean corporate font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Metric Cards */
        .exec-card {{
            background: #FFFFFF;
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            border: 1px solid #E2E8F0;
            margin-bottom: 12px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .exec-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.09), 0 2px 4px -1px rgba(0,0,0,0.05);
        }}
        .exec-card-title {{
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .exec-card-value {{
            font-size: 1.65rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
            margin-bottom: 6px;
        }}
        .exec-badge-pos {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #DCFCE7;
            color: #15803D;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .exec-badge-neg {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #FEE2E2;
            color: #B91C1C;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .exec-badge-neutral {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #F1F5F9;
            color: #475569;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        /* Section Containers */
        .exec-section-box {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 22px;
            margin-bottom: 20px;
        }}
        
        /* Alert Banners */
        .exec-alert-critical {{
            background-color: #FEF2F2;
            border-left: 4px solid #DC2626;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 10px;
        }}
        .exec-alert-warning {{
            background-color: #FFFBEB;
            border-left: 4px solid #D97706;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 10px;
        }}
        
        /* Header Title Banner */
        .exec-page-header {{
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid #E2E8F0;
        }}
        .exec-page-title {{
            font-size: 1.85rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 4px;
        }}
        .exec-page-desc {{
            font-size: 0.95rem;
            color: #64748B;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, badge: str = "Executive Intelligence"):
    """Render standardized corporate page banner."""
    apply_executive_styles()
    html = f"""
    <div class="exec-page-header">
        <span class="exec-badge-neutral" style="margin-bottom: 8px;">{badge}</span>
        <div class="exec-page-title">{title}</div>
        <div class="exec-page-desc">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(
    title: str,
    value_str: str,
    change_pct: Optional[float] = None,
    favorable: bool = True,
    target_str: Optional[str] = None,
    prefix_badge: Optional[str] = None
):
    """Render single executive metric card with badge and target info."""
    badge_html = ""
    if change_pct is not None:
        badge_class = "exec-badge-pos" if favorable else "exec-badge-neg"
        sign = "+" if change_pct > 0 else ""
        badge_html = f'<span class="{badge_class}">{sign}{change_pct:.1f}%</span>'

    target_html = f'<span style="font-size: 0.75rem; color: #64748B; margin-left: 6px;">Target: {target_str}</span>' if target_str else ""

    card_html = f"""
    <div class="exec-card">
        <div class="exec-card-title">{title}</div>
        <div class="exec-card-value">{value_str}</div>
        <div>{badge_html} {target_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# --- Standard Plotly Chart Generators ---

def create_revenue_profit_trend_chart(financial_df: pd.DataFrame) -> go.Figure:
    """Generate combined monthly Revenue & Operating Profit dual-axis trend chart."""
    df_agg = financial_df.groupby("date").agg(
        revenue=("revenue", "sum"),
        operating_profit=("operating_profit", "sum"),
        budget_revenue=("budget_revenue", "sum"),
        budget_profit=("budget_operating_profit", "sum")
    ).reset_index()

    fig = go.Figure()

    # Revenue Bar
    fig.add_trace(go.Bar(
        x=df_agg["date"],
        y=df_agg["revenue"],
        name="Actual Revenue",
        marker_color="#1E3A8A",
        opacity=0.85,
        yaxis="y1"
    ))

    # Budget Revenue dashed line
    fig.add_trace(go.Scatter(
        x=df_agg["date"],
        y=df_agg["budget_revenue"],
        name="Budget Revenue",
        line=dict(color="#64748B", width=2, dash="dash"),
        yaxis="y1"
    ))

    # Operating Profit Line on secondary axis
    fig.add_trace(go.Scatter(
        x=df_agg["date"],
        y=df_agg["operating_profit"],
        name="Operating Profit",
        line=dict(color="#0D9488", width=3),
        mode="lines+markers",
        marker=dict(size=6),
        yaxis="y2"
    ))

    fig.update_layout(
        title=dict(text="Revenue & Operating Profit Historical Performance", font=dict(size=14, color="#0F172A")),
        xaxis=dict(title="Period", tickangle=-30),
        yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor="#F1F5F9"),
        yaxis2=dict(
            title="Operating Profit ($)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x unified",
        height=380,
    )
    return fig


def create_waterfall_chart(waterfall_items: List[Dict[str, Any]]) -> go.Figure:
    """Generate corporate waterfall profit variance decomposition chart."""
    x = [item["name"] for item in waterfall_items]
    y = [item["value"] for item in waterfall_items]
    measures = [item["measure"] for item in waterfall_items]

    fig = go.Figure(go.Waterfall(
        name="Profit Variance",
        orientation="v",
        measure=measures,
        x=x,
        textposition="outside",
        text=[format_currency(v) for v in y],
        y=y,
        connector=dict(line=dict(color="#CBD5E1")),
        decreasing=dict(marker=dict(color="#DC2626")),
        increasing=dict(marker=dict(color="#16A34A")),
        totals=dict(marker=dict(color="#1E3A8A"))
    ))

    fig.update_layout(
        title=dict(text="Operating Profit Variance Waterfall Decomposition", font=dict(size=14, color="#0F172A")),
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig


def create_driver_ranking_chart(drivers_df: pd.DataFrame, max_n: int = 8) -> go.Figure:
    """Generate horizontal bar chart of ranked operational KPI drivers."""
    if drivers_df.empty:
        return go.Figure()

    top_df = drivers_df.head(max_n).sort_values("driver_score", ascending=True)

    fig = go.Figure(go.Bar(
        x=top_df["driver_score"],
        y=top_df["kpi_name"],
        orientation="h",
        marker=dict(
            color=top_df["pearson_r"].apply(lambda r: "#16A34A" if r > 0 else "#DC2626"),
            opacity=0.85
        ),
        text=top_df.apply(lambda r: f"r = {r['pearson_r']:+.2f} ({r['department']})", axis=1),
        textposition="inside",
        insidetextanchor="middle"
    ))

    fig.update_layout(
        title=dict(text="Ranked Operational Drivers (Explainable Driver Score)", font=dict(size=14, color="#0F172A")),
        xaxis=dict(title="Composite Driver Score (0-100)", range=[0, 100]),
        yaxis=dict(title=""),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=140, r=30, t=50, b=40),
        height=360,
    )
    return fig


def create_forecast_chart(forecast_data: Dict[str, Any]) -> go.Figure:
    """Generate fan chart showing historical actuals, forecasts, and 95% confidence intervals."""
    hist = forecast_data.get("historical_series", [])
    fc = forecast_data.get("forecast_series", [])

    df_hist = pd.DataFrame(hist)
    df_fc = pd.DataFrame(fc)

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=df_hist["date"],
        y=df_hist["actual_value"],
        name="Historical Actual",
        line=dict(color="#1E3A8A", width=2.5),
        mode="lines+markers"
    ))

    # Upper CI
    fig.add_trace(go.Scatter(
        x=df_fc["date"],
        y=df_fc["ci_upper_95"],
        name="95% Upper CI",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Lower CI with fill
    fig.add_trace(go.Scatter(
        x=df_fc["date"],
        y=df_fc["ci_lower_95"],
        name="95% Confidence Interval",
        fill="tonexty",
        fillcolor="rgba(13, 148, 136, 0.15)",
        line=dict(width=0),
        hoverinfo="skip"
    ))

    # Forecast Line
    fig.add_trace(go.Scatter(
        x=df_fc["date"],
        y=df_fc["forecast_value"],
        name="Projected Forecast",
        line=dict(color="#0D9488", width=3, dash="dash"),
        mode="lines+markers",
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=dict(text=f"Performance Trajectory & Horizon Forecast ({forecast_data.get('metric', 'Metric').title()})", font=dict(size=14, color="#0F172A")),
        xaxis=dict(title="Date"),
        yaxis=dict(title="Amount ($)", gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig


def create_scenario_comparison_chart(scenario_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart comparing revenue and operating profit across simulation scenarios."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=scenario_df["Scenario Name"],
        y=scenario_df["Revenue"],
        name="Simulated Revenue",
        marker_color="#1E3A8A"
    ))

    fig.add_trace(go.Bar(
        x=scenario_df["Scenario Name"],
        y=scenario_df["Operating Profit"],
        name="Simulated Operating Profit",
        marker_color="#0D9488"
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="Comparative Strategic Scenarios Analysis", font=dict(size=14, color="#0F172A")),
        xaxis=dict(tickangle=-15),
        yaxis=dict(title="USD ($)", gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig
