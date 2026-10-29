# ExecuLens AI — Executive Decision Intelligence & Business Performance Insights

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> **Core Business Mission:**  
> *"What is driving our business performance, what has changed, why did it change, what is the financial impact, and what should management do next?"*

ExecuLens AI is an enterprise-grade Decision Intelligence System engineered to bridge operational KPIs across Sales, Marketing, Operations, Customer Service, Supply Chain, and HR directly to financial outcomes (Revenue, Gross Profit, Operating Margin, and Cash Flow). It functions as a virtual business performance analyst for CEOs, CFOs, COOs, and Business Unit Leaders.

---

## 🌟 Key Features

1. **Executive Command Center:**
   - Consolidated scorecard displaying Total Revenue, Operating Profit, Operating Margin, and Overall Business Performance Score.
   - Dual-axis revenue and profit trend charts with actual vs. budget tracking.
   - Active threshold alert detection (Warning and Critical breaches) plus multi-indicator cluster risk detection.

2. **KPI Intelligence:**
   - 34 standardized enterprise operational indicators across 6 corporate departments.
   - Target deviation tracking and directional health evaluation (`higher_is_better`, `lower_is_better`, `target_range`).
   - Interactive time-series trajectories across business units.

3. **KPI-to-Financial Driver Analysis:**
   - Pearson (linear) and Spearman (rank) correlation analysis with p-values and sample sizes.
   - Explainable composite **Driver Score** ($0-100$) factoring association strength, reliability, temporal stability, target deviation, and financial relevance.
   - Multivariable Ordinary Least Squares (OLS) regression with $R^2$, standard errors, and 95% confidence intervals.
   - Lagged correlation screening ($0-90$ days / $1-3$ months) to uncover delayed operational effects.

4. **Root-Cause Diagnostic Engine:**
   - 10-step comparative diagnostic workflow between any two time horizons.
   - Operating profit variance waterfall decomposition (Volume Effect, Price/Mix Effect, COGS Impact, OpEx Impact).
   - Ranked diagnostic hypotheses with supporting and contradicting evidence, confidence levels, and recommended validation checks.

5. **Financial Impact Modeling Center:**
   - Quantified P&L variance translations for operational shifts:
     - Sales conversion variance on top-line revenue
     - Customer Acquisition Cost (CAC) impact on marketing spend
     - Inventory stockout rates and lost sales
     - Employee turnover and recruitment replacement costs
     - Order fulfillment cost impact on operating margin
   - Documented formulas, explicit business assumptions, and Low / Base / High uncertainty bounds.

6. **AI-Powered Executive Briefing:**
   - Synthesizes complex analytics into a standard 8-part executive briefing:
     1. Executive Summary
     2. What Changed?
     3. What May Explain the Change?
     4. Financial Implications
     5. Key Risks
     6. Recommended Actions
     7. What Management Should Validate
     8. Decisions Required
   - Powered by OpenAI API with a 100% deterministic, rule-based fallback when no API key is configured (Zero-API mode).

7. **Ask ExecuLens (Executive QA):**
   - Natural language conversational assistant interpreting management queries.
   - Routes queries to validated Python calculation engines without code hallucination.

8. **Scenario Simulator & Performance Forecasting:**
   - Chronological holdout backtesting forecasting (Exponential Smoothing / Trend Decomposition) with widening 95% prediction intervals.
   - Interactive what-if simulator with multi-lever adjustments.
   - Standard 5-way scenario comparison (BAU, Cost Reduction, Revenue Acceleration, Operational Excellence, Combined Transformation).
   - 2D sensitivity matrix for margin optimization.

9. **Action Tracker & Workflow Register:**
   - Prioritized action register with transparent Priority Scores ($0-100$).
   - Status tracking (Proposed, Approved, In Progress, Completed), executive ownership, and post-action outcome review.

10. **Data Center & Validation:**
    - Support for CSV and Excel uploads.
    - Mathematical identity validation (e.g., Gross Profit = Revenue - COGS).
    - Synthetic demonstration data generator with reproducible seed ($42$).

11. **Methodology & Audit Governance:**
    - Documented mathematical formulas and scoring algorithms.
    - Model governance, statistical assumptions, and limitations.
    - Immutable SQLite system audit trail tracking all actions and briefings.

12. **Executive PDF Export:**
    - One-click publication-grade PDF report generation using ReportLab.

---

## 🏗️ Architecture & Project Structure

```text
PB12/
├── app.py                            # Streamlit main entrypoint & executive dashboard
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── pytest.ini                        # Pytest configuration
├── README.md                         # Documentation
├── config/
│   ├── __init__.py
│   └── settings.py                   # Paths, thresholds, palettes, and formatters
├── data/
│   ├── synthetic/                    # 24-month demonstration CSV datasets
│   │   ├── financial_performance.csv # 1,440 records
│   │   ├── operational_kpis.csv      # 16,320 records
│   │   ├── kpi_definitions.csv       # 34 KPI definitions
│   │   ├── business_events.csv       # Documented business shocks
│   │   └── management_actions.csv    # Initial actions
│   └── uploads/                      # Uploaded user datasets
├── src/
│   ├── __init__.py
│   ├── database.py                   # SQLite storage for actions, audit logs, scenarios
│   ├── synthetic_generator.py        # Seeded realistic demonstration data generator
│   ├── data_validation.py            # Integrity and math consistency checks
│   ├── data_ingestion.py             # Caching, filtering, and schema harmonization
│   ├── kpi_engine.py                 # KPI status, scorecards, MoM/QoQ calculations
│   ├── financial_analysis.py         # Variance waterfall & budget decompositions
│   ├── driver_analysis.py            # Pearson, Spearman, OLS, and Driver Scores
│   ├── lag_analysis.py               # 0-90 days lag screening & peak lead-times
│   ├── anomaly_detection.py          # Z-score and threshold breach alerts
│   ├── root_cause.py                 # 10-step diagnostic hypothesis synthesizer
│   ├── financial_impact.py           # Quantified operational-to-financial impact models
│   ├── forecasting.py                # Chronological holdout forecasting & intervals
│   ├── scenario_engine.py            # What-if simulator, 2D sensitivity & comparisons
│   ├── recommendation_engine.py      # Automated weighted action recommendations
│   ├── llm_service.py                # OpenAI API with zero-API deterministic fallback
│   ├── executive_qa.py               # Safe natural language question router
│   ├── reporting.py                  # ReportLab PDF executive briefing generator
│   └── ui_components.py              # Corporate CSS and Plotly visualization builders
├── pages/
│   ├── 01_Executive_Command_Center.py
│   ├── 02_KPI_Intelligence.py
│   ├── 03_Driver_Analysis.py
│   ├── 04_Root_Cause_Investigation.py
│   ├── 05_Financial_Impact.py
│   ├── 06_AI_Executive_Briefing.py
│   ├── 07_Ask_ExecuLens.py
│   ├── 08_Scenario_Simulator.py
│   ├── 09_Action_Tracker.py
│   ├── 10_Data_Center.py
│   └── 11_Methodology_Model_Quality.py
└── tests/
    ├── __init__.py
    ├── test_kpi_engine.py
    ├── test_financial_analysis.py
    ├── test_driver_analysis.py
    ├── test_scenario_engine.py
    ├── test_data_validation.py
    ├── test_financial_impact.py
    └── test_llm_and_reporting.py
```

---

## 📊 Embedded Synthetic Dataset Scenarios

The synthetic generator (`seed=42`) generates 24 monthly periods (January 2024 to December 2025) across 4 Business Units and 5 Global Regions. It embeds realistic business relationships:
1. **Commercial Funnel:** Sales Conversion Rate and Average Order Value directly drive revenue.
2. **Delayed Marketing Effects:** CAC and digital ad spend lead revenue and margin changes by ~30 days.
3. **Q3 2024 Supply Chain Disruption:** A simulated external shipping route disruption increases Supplier Lead Time and Stockout Rate in Global Logistics and Consumer Products, causing COGS inflation and delayed fulfillment.
4. **Q4 2024 GenAI Product Launch:** Cloud & Digital Services experiences a 22% surge in MQLs and an ARR uplift.
5. **Q1 2025 Consumer Brand Campaign:** A marketing surge elevates lead inflow but temporarily raises CAC and OpEx.
6. **Q4 2025 Warehouse Automation:** Robotic sorter commissioning in Global Logistics reduces Cost per Order by 18% and expands margins.

---

## 🚀 Quickstart & Execution

### 1. Prerequisites
- Python 3.11 or higher
- pip package manager

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
To enable live OpenAI LLM synthesis, create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Add your OpenAI key:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DEFAULT_CURRENCY=$
```
> **Note:** If no API key is provided, ExecuLens AI automatically runs in **Deterministic Zero-API Mode**, delivering full analytical summaries without external network calls.

### 4. Running the Application
Launch the Streamlit executive dashboard:
```bash
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`.

### 5. Running the Test Suite
Execute the test suite covering data validation, KPI calculations, variance decomposition, regressions, financial impact models, and PDF generation:
```bash
python -m pytest tests/ -v
```

---

## ⚖️ Methodology & Governance Notice

- **Association vs. Causation:** Statistical correlation coefficients ($r$) and regression weights indicate observed historical co-movements. They do not constitute proof of isolated causal mechanisms.
- **Modeled Estimates:** Financial impacts (e.g., conversion losses, turnover replacement costs) are modeled approximations derived from explicit documented business assumptions and industry benchmarks.
- **Decision Support:** ExecuLens AI is designed for senior management decision support and scenario evaluation, not autonomous decision execution.

---

## 📄 License
This project is licensed under the MIT License.
