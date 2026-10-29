"""
ExecuLens AI - Configuration & Settings
Contains application-wide constants, file paths, formatting utilities, and UI style tokens.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
UPLOADS_DATA_DIR = DATA_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
DATABASE_PATH = BASE_DIR / "execulens.db"

# Ensure runtime directories exist
SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# App Metadata
APP_NAME = "ExecuLens AI"
APP_SUBTITLE = "Executive Decision Intelligence & Business Performance Insights"
APP_VERSION = "1.0.0"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Formatting & Display
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "$")
DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"

# Standard Financial Outcomes
FINANCIAL_OUTCOMES = [
    "revenue",
    "gross_profit",
    "operating_profit",
    "operating_margin",
    "cash_flow",
    "revenue_per_employee",
    "customer_count",
]

FINANCIAL_OUTCOME_LABELS = {
    "revenue": "Revenue",
    "gross_profit": "Gross Profit",
    "operating_profit": "Operating Profit",
    "operating_margin": "Operating Margin (%)",
    "cash_flow": "Operating Cash Flow",
    "revenue_per_employee": "Revenue per Employee",
    "customer_count": "Customer Count",
}

# Standard Departments
DEPARTMENTS = [
    "Sales",
    "Marketing",
    "Operations",
    "Customer Service",
    "Supply Chain",
    "Human Resources",
    "Finance",
]

# Standard Business Units
BUSINESS_UNITS = [
    "Enterprise Solutions",
    "Consumer Products",
    "Cloud & Digital Services",
    "Global Logistics",
]

# Standard Regions
REGIONS = [
    "North America",
    "Europe",
    "Asia-Pacific",
    "Latin America",
    "Middle East & Africa",
]

# KPI Direction Enums
KPI_DIRECTIONS = {
    "higher_is_better": "Higher is Better",
    "lower_is_better": "Lower is Better",
    "target_range": "Target Range",
}

# Driver Score Weights (default)
DRIVER_SCORE_WEIGHTS = {
    "association_strength": 0.35,  # Abs correlation / feature importance
    "statistical_reliability": 0.20,  # 1 - p_value
    "stability": 0.15,  # Cross-period consistency
    "target_deviation": 0.15,  # Deviation magnitude
    "financial_relevance": 0.15,  # Domain/business weighting
}

# Action Prioritization Weights
ACTION_PRIORITY_WEIGHTS = {
    "urgency": 0.30,
    "financial_impact": 0.35,
    "feasibility": 0.20,
    "evidence_strength": 0.15,
}

# Executive UI Color Palette
PALETTE = {
    "primary": "#1E3A8A",      # Deep Executive Navy
    "secondary": "#0284C7",    # Corporate Slate Blue
    "accent": "#0D9488",       # Deep Teal
    "success": "#16A34A",      # Emerald Green
    "warning": "#D97706",      # Rich Amber
    "danger": "#DC2626",       # Crimson
    "info": "#2563EB",         # Royal Blue
    "neutral_dark": "#0F172A", # Slate 900
    "neutral_light": "#F8FAFC",# Slate 50
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "chart_series": [
        "#1E3A8A", "#0D9488", "#F59E0B", "#DC2626",
        "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"
    ]
}

def format_currency(val: float, currency_symbol: str = None) -> str:
    """Format currency values into concise executive numbers ($1.2M, $450K)."""
    if val is None or not (isinstance(val, (int, float))):
        return "N/A"
    sym = currency_symbol if currency_symbol is not None else DEFAULT_CURRENCY
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{sign}{sym}{abs_val / 1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}{sym}{abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}{sym}{abs_val / 1_000:.1f}K"
    else:
        return f"{sign}{sym}{abs_val:.2f}"

def format_percentage(val: float, decimals: int = 1, show_sign: bool = False) -> str:
    """Format decimal percentage values (e.g. 0.052 -> +5.2%)."""
    if val is None or not (isinstance(val, (int, float))):
        return "N/A"
    sign = "+" if show_sign and val > 0 else ""
    return f"{sign}{val:.{decimals}f}%"

def format_number(val: float, decimals: int = 1) -> str:
    """Format general numbers concisely."""
    if val is None or not (isinstance(val, (int, float))):
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.1f}K"
    else:
        return f"{sign}{abs_val:.{decimals}f}"
