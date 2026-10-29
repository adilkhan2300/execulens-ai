"""
ExecuLens AI - PDF Executive Report Generation Engine
Uses ReportLab to generate publication-grade executive PDF performance reports
containing scorecards, driver rankings, root-cause diagnostics, and action registers.
"""

import io
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config.settings import format_currency, format_percentage

def generate_pdf_executive_report(
    scorecard: Dict[str, Any],
    top_drivers: List[Dict[str, Any]],
    hypotheses: List[Dict[str, Any]],
    actions: List[Dict[str, Any]],
    briefing_text: str = ""
) -> bytes:
    """
    Generate an executive PDF briefing document and return raw bytes for download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Corporate Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
    )
    
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
    )
    
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )

    cell_body = ParagraphStyle(
        "CellBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("ExecuLens AI — Executive Decision Intelligence Report", title_style))
    curr_date = scorecard.get("current_period", datetime.now().strftime("%Y-%m-%d"))
    gen_time = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
    story.append(Paragraph(f"Reporting Period: <b>{curr_date}</b> | Generated: {gen_time} | Governance: Internal Executive Use Only", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=14))

    # 2. Executive Scorecard Table
    story.append(Paragraph("1. Corporate Financial Performance Scorecard", section_heading))
    
    rev_info = scorecard.get("revenue", {})
    op_info = scorecard.get("operating_profit", {})
    margin_info = scorecard.get("operating_margin", {})
    cf_info = scorecard.get("cash_flow", {})
    
    scorecard_data = [
        [
            Paragraph("Metric", cell_bold),
            Paragraph("Current Value", cell_bold),
            Paragraph("Prior Period", cell_bold),
            Paragraph("Variance", cell_bold),
            Paragraph("Target Status", cell_bold),
        ],
        [
            Paragraph("Total Revenue", cell_body),
            Paragraph(format_currency(rev_info.get("value", 0)), cell_body),
            Paragraph(format_currency(rev_info.get("prev_value", 0)), cell_body),
            Paragraph(format_percentage(rev_info.get("change_pct", 0), show_sign=True), cell_body),
            Paragraph("On Track" if rev_info.get("favorable") else "Below Target", cell_body),
        ],
        [
            Paragraph("Operating Profit", cell_body),
            Paragraph(format_currency(op_info.get("value", 0)), cell_body),
            Paragraph(format_currency(op_info.get("prev_value", 0)), cell_body),
            Paragraph(format_percentage(op_info.get("change_pct", 0), show_sign=True), cell_body),
            Paragraph("Favorable" if op_info.get("favorable") else "Unfavorable", cell_body),
        ],
        [
            Paragraph("Operating Margin", cell_body),
            Paragraph(f"{margin_info.get('value', 0):.1f}%", cell_body),
            Paragraph(f"{margin_info.get('prev_value', 0):.1f}%", cell_body),
            Paragraph(f"{margin_info.get('change_pts', 0):+.1f} pts", cell_body),
            Paragraph("Stable" if margin_info.get("favorable") else "Under Pressure", cell_body),
        ],
        [
            Paragraph("Operating Cash Flow", cell_body),
            Paragraph(format_currency(cf_info.get("value", 0)), cell_body),
            Paragraph(format_currency(cf_info.get("prev_value", 0)), cell_body),
            Paragraph(format_percentage(cf_info.get("change_pct", 0), show_sign=True), cell_body),
            Paragraph("Adequate", cell_body),
        ],
    ]

    t_scorecard = Table(scorecard_data, colWidths=[1.8 * inch, 1.4 * inch, 1.3 * inch, 1.1 * inch, 1.4 * inch])
    t_scorecard.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_scorecard)
    story.append(Spacer(1, 14))

    # 3. Top Key Operational Drivers Table
    story.append(Paragraph("2. Top Operational Performance Drivers", section_heading))
    driver_headers = [
        Paragraph("Rank", cell_bold),
        Paragraph("Operational Indicator", cell_bold),
        Paragraph("Department", cell_bold),
        Paragraph("Pearson r", cell_bold),
        Paragraph("Significance", cell_bold),
        Paragraph("Driver Score", cell_bold),
    ]
    driver_data = [driver_headers]
    
    for idx, d in enumerate(top_drivers[:5], 1):
        driver_data.append([
            Paragraph(f"#{idx}", cell_body),
            Paragraph(d.get("kpi_name", ""), cell_body),
            Paragraph(d.get("department", ""), cell_body),
            Paragraph(f"{d.get('pearson_r', 0):+.2f}", cell_body),
            Paragraph(d.get("significance", "Normal"), cell_body),
            Paragraph(f"{d.get('driver_score', 0)}/100", cell_body),
        ])

    t_driver = Table(driver_data, colWidths=[0.6 * inch, 2.3 * inch, 1.4 * inch, 0.9 * inch, 1.0 * inch, 0.8 * inch])
    t_driver.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_driver)
    story.append(Spacer(1, 14))

    # 4. Root-Cause Hypotheses
    story.append(Paragraph("3. Root-Cause Diagnostic Hypotheses", section_heading))
    for h in hypotheses[:3]:
        h_text = f"<b>{h.get('rank', 1)}. {h.get('hypothesis')}</b> (Confidence: <i>{h.get('evidence_strength', 'Medium')}</i>)<br/>"
        h_text += f"&bull; <b>Supporting Evidence:</b> {'; '.join(h.get('supporting_evidence', []))}<br/>"
        h_text += f"&bull; <b>Recommended Validation:</b> {h.get('suggested_validation', '')}"
        story.append(Paragraph(h_text, body_style))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))

    # 5. Prioritized Management Action Register
    story.append(Paragraph("4. Prioritized Executive Action Register", section_heading))
    action_headers = [
        Paragraph("Action ID", cell_bold),
        Paragraph("Proposed Strategic Action", cell_bold),
        Paragraph("Owner Role", cell_bold),
        Paragraph("Urgency", cell_bold),
        Paragraph("Priority", cell_bold),
    ]
    action_data = [action_headers]
    for act in actions[:4]:
        action_data.append([
            Paragraph(act.get("action_id", ""), cell_body),
            Paragraph(act.get("action_description", act.get("problem", "")), cell_body),
            Paragraph(act.get("owner", ""), cell_body),
            Paragraph(act.get("urgency", "Medium"), cell_body),
            Paragraph(f"{act.get('priority_score', 75)}/100", cell_body),
        ])

    t_actions = Table(action_data, colWidths=[1.1 * inch, 3.2 * inch, 1.4 * inch, 0.7 * inch, 0.6 * inch])
    t_actions.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_actions)
    story.append(Spacer(1, 14))

    # 6. Governance & Model Limitations Notice
    disclaimer = """<b>Model Governance & Analytical Disclaimer:</b> Correlation coefficients, regression weights, and driver rankings represent empirical statistical associations and do not assert isolated causal mechanisms. Modeled financial impacts are scenario approximations based on documented parameters and should be validated through internal audits prior to capital allocation."""
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceAfter=8))
    story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9, textColor=colors.HexColor("#64748B"))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
