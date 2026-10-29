"""
Unit tests for LLM fallback, Executive QA routing, and PDF report generation.
"""

import pytest
from src.llm_service import generate_deterministic_briefing, generate_executive_briefing
from src.reporting import generate_pdf_executive_report
from src.executive_qa import answer_executive_question

def test_generate_deterministic_briefing():
    evidence = {
        "scorecard": {
            "current_period": "2025-12-01",
            "previous_period": "2025-11-01",
            "revenue": {"value": 5000000.0, "change_pct": 4.5, "favorable": True},
            "operating_profit": {"value": 900000.0, "change_pct": -3.2, "favorable": False},
            "operating_margin": {"value": 18.0, "change_pts": -1.2, "favorable": False},
            "performance_score": 78.5,
        },
        "financial_decomposition": {
            "total_profit_change": -30000.0,
            "cogs_variance": 120000.0,
            "opex_variance": 50000.0
        },
        "adverse_kpis": [
            {"kpi_name": "Stockout Rate", "current_value": 4.2, "unit": "%", "pct_delta": 45.0, "linked_outcome": "revenue"}
        ],
        "top_drivers": [
            {"kpi_name": "Sales Conversion Rate", "department": "Sales", "driver_score": 85.0, "pearson_r": 0.82, "significance": "High"}
        ],
        "root_cause": {
            "hypotheses": [
                {
                    "rank": 1,
                    "hypothesis": "Supply chain congestion bottlenecked fulfillment",
                    "evidence_strength": "High",
                    "supporting_evidence": ["Stockout rate rose 45%"],
                    "contradicting_evidence": "Demand remained high",
                    "suggested_validation": "Check warehouse backlog"
                }
            ]
        },
        "recommendations": [
            {"action_description": "Activate backup suppliers", "owner": "VP Supply Chain", "urgency": "High", "priority_score": 90}
        ]
    }

    text = generate_deterministic_briefing(evidence)
    # Check that all 8 required sections are present
    assert "### 1. Executive Summary" in text
    assert "### 2. What Changed?" in text
    assert "### 3. What May Explain the Change?" in text
    assert "### 4. Financial Implications" in text
    assert "### 5. Key Risks" in text
    assert "### 6. Recommended Actions" in text
    assert "### 7. What Management Should Validate" in text
    assert "### 8. Decisions Required" in text

def test_generate_pdf_executive_report():
    scorecard = {
        "current_period": "2025-12-01",
        "revenue": {"value": 5000000.0, "prev_value": 4800000.0, "change_pct": 4.1, "favorable": True},
        "operating_profit": {"value": 900000.0, "prev_value": 950000.0, "change_pct": -5.2, "favorable": False},
        "operating_margin": {"value": 18.0, "prev_value": 19.8, "change_pts": -1.8, "favorable": False},
        "cash_flow": {"value": 800000.0, "prev_value": 750000.0, "change_pct": 6.6, "favorable": True},
    }
    drivers = [
        {"kpi_name": "Sales Conversion Rate", "department": "Sales", "pearson_r": 0.85, "significance": "High", "driver_score": 88.0}
    ]
    hypotheses = [
        {"rank": 1, "hypothesis": "Fulfillment cost inflation", "evidence_strength": "High", "supporting_evidence": ["Cost/order +15%"], "suggested_validation": "Audit invoices"}
    ]
    actions = [
        {"action_id": "ACT-001", "action_description": "Renegotiate freight", "owner": "Logistics Director", "urgency": "High", "priority_score": 92}
    ]

    pdf_bytes = generate_pdf_executive_report(scorecard, drivers, hypotheses, actions)
    assert len(pdf_bytes) > 1000
    # PDF Magic bytes
    assert pdf_bytes.startswith(b"%PDF-")
