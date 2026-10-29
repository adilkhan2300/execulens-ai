"""
ExecuLens AI - Synthetic Data Generator
Generates realistic, normalized 24-month executive demonstration datasets
with reproducible seeds, embedded business relationships, lead-lag effects,
seasonality, external shocks, and valid mathematical relationships.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from config.settings import (
    SYNTHETIC_DATA_DIR,
    BUSINESS_UNITS,
    REGIONS,
    DEPARTMENTS,
)

# Set deterministic seed for reproducibility
SEED = 42

KPI_DEFINITIONS_DATA = [
    # Sales
    {
        "kpi_name": "Sales Conversion Rate",
        "department": "Sales",
        "description": "Percentage of qualified sales opportunities converted into paying customers",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 4.5,
        "warning_threshold": 3.5,
        "critical_threshold": 2.8,
        "business_owner": "VP Sales",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Average Order Value",
        "department": "Sales",
        "description": "Average revenue generated per transaction or signed contract",
        "unit": "USD",
        "direction": "higher_is_better",
        "target_value": 4200.0,
        "warning_threshold": 3800.0,
        "critical_threshold": 3400.0,
        "business_owner": "VP Sales",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Sales Cycle Duration",
        "department": "Sales",
        "description": "Average number of days required to close a sales opportunity",
        "unit": "Days",
        "direction": "lower_is_better",
        "target_value": 45.0,
        "warning_threshold": 55.0,
        "critical_threshold": 65.0,
        "business_owner": "VP Sales",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "Sales Productivity",
        "department": "Sales",
        "description": "Average monthly revenue generated per quota-carrying sales representative",
        "unit": "USD",
        "direction": "higher_is_better",
        "target_value": 115000.0,
        "warning_threshold": 95000.0,
        "critical_threshold": 80000.0,
        "business_owner": "Head of Sales Ops",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Lead-to-Customer Conversion",
        "department": "Sales",
        "description": "Percentage of inbound and outbound marketing leads converted to customers",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 2.8,
        "warning_threshold": 2.0,
        "critical_threshold": 1.5,
        "business_owner": "Head of Demand Gen",
        "linked_financial_outcome": "customer_count",
        "expected_lag_days": 30,
    },
    # Marketing
    {
        "kpi_name": "Customer Acquisition Cost",
        "department": "Marketing",
        "description": "Total sales and marketing expenditure divided by new customers acquired",
        "unit": "USD",
        "direction": "lower_is_better",
        "target_value": 1250.0,
        "warning_threshold": 1600.0,
        "critical_threshold": 1950.0,
        "business_owner": "Chief Marketing Officer",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "Return on Advertising Spend",
        "department": "Marketing",
        "description": "Gross revenue generated per dollar spent on digital and print advertising",
        "unit": "x",
        "direction": "higher_is_better",
        "target_value": 4.2,
        "warning_threshold": 3.2,
        "critical_threshold": 2.5,
        "business_owner": "Director of Performance Mktg",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "Cost per Lead",
        "department": "Marketing",
        "description": "Average advertising and campaign spend required to acquire a raw marketing lead",
        "unit": "USD",
        "direction": "lower_is_better",
        "target_value": 75.0,
        "warning_threshold": 105.0,
        "critical_threshold": 135.0,
        "business_owner": "Head of Growth",
        "linked_financial_outcome": "operating_expenses",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Campaign Conversion Rate",
        "department": "Marketing",
        "description": "Percentage of campaign interactions that result in a high-intent marketing action",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 5.2,
        "warning_threshold": 4.0,
        "critical_threshold": 3.0,
        "business_owner": "Head of Growth",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "Marketing-Qualified Leads",
        "department": "Marketing",
        "description": "Total monthly volume of leads meeting ICP scoring criteria",
        "unit": "Count",
        "direction": "higher_is_better",
        "target_value": 1800.0,
        "warning_threshold": 1400.0,
        "critical_threshold": 1100.0,
        "business_owner": "VP Marketing",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 60,
    },
    # Operations
    {
        "kpi_name": "Order Fulfillment Time",
        "department": "Operations",
        "description": "Average hours elapsed between order confirmation and final fulfillment/delivery dispatch",
        "unit": "Hours",
        "direction": "lower_is_better",
        "target_value": 24.0,
        "warning_threshold": 32.0,
        "critical_threshold": 44.0,
        "business_owner": "Chief Operating Officer",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Capacity Utilization",
        "department": "Operations",
        "description": "Percentage of operational infrastructure and facility capacity actively utilized",
        "unit": "%",
        "direction": "target_range",
        "target_value": 82.0,
        "warning_threshold": 68.0,
        "critical_threshold": 55.0,
        "business_owner": "VP Operations",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Cost per Order",
        "department": "Operations",
        "description": "Average direct operational handling and dispatch cost per fulfilled order",
        "unit": "USD",
        "direction": "lower_is_better",
        "target_value": 14.5,
        "warning_threshold": 17.5,
        "critical_threshold": 21.0,
        "business_owner": "Director of Fulfillment",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Process Defect Rate",
        "department": "Operations",
        "description": "Percentage of completed jobs, batches, or dispatches with quality defects",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 1.2,
        "warning_threshold": 2.2,
        "critical_threshold": 3.5,
        "business_owner": "Head of Quality Assurance",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Employee Productivity",
        "department": "Operations",
        "description": "Completed work units or transactions per labor hour worked",
        "unit": "Units/Hr",
        "direction": "higher_is_better",
        "target_value": 18.5,
        "warning_threshold": 15.0,
        "critical_threshold": 12.0,
        "business_owner": "VP Operations",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 0,
    },
    # Customer Service
    {
        "kpi_name": "Customer Satisfaction Score",
        "department": "Customer Service",
        "description": "Average satisfaction rating expressed on a normalized 0-100 scale",
        "unit": "Score",
        "direction": "higher_is_better",
        "target_value": 88.0,
        "warning_threshold": 80.0,
        "critical_threshold": 72.0,
        "business_owner": "VP Customer Experience",
        "linked_financial_outcome": "customer_count",
        "expected_lag_days": 60,
    },
    {
        "kpi_name": "Net Promoter Score",
        "department": "Customer Service",
        "description": "Industry-standard net promoter score measuring customer loyalty (-100 to +100)",
        "unit": "NPS",
        "direction": "higher_is_better",
        "target_value": 52.0,
        "warning_threshold": 40.0,
        "critical_threshold": 28.0,
        "business_owner": "VP Customer Experience",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 60,
    },
    {
        "kpi_name": "First-Contact Resolution",
        "department": "Customer Service",
        "description": "Percentage of customer support inquiries resolved during the initial contact",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 78.0,
        "warning_threshold": 68.0,
        "critical_threshold": 58.0,
        "business_owner": "Head of Support Ops",
        "linked_financial_outcome": "operating_expenses",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Average Resolution Time",
        "department": "Customer Service",
        "description": "Average hours required to fully resolve a customer issue or complaint",
        "unit": "Hours",
        "direction": "lower_is_better",
        "target_value": 4.5,
        "warning_threshold": 7.0,
        "critical_threshold": 11.0,
        "business_owner": "Head of Support Ops",
        "linked_financial_outcome": "operating_expenses",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Complaint Rate",
        "department": "Customer Service",
        "description": "Formal customer complaints received per 1,000 completed orders",
        "unit": "Per 1k",
        "direction": "lower_is_better",
        "target_value": 4.0,
        "warning_threshold": 7.5,
        "critical_threshold": 12.0,
        "business_owner": "Customer Success Director",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 30,
    },
    # Supply Chain
    {
        "kpi_name": "Inventory Turnover",
        "department": "Supply Chain",
        "description": "Annualized frequency with which inventory stock is completely cycled and sold",
        "unit": "x/Year",
        "direction": "higher_is_better",
        "target_value": 7.5,
        "warning_threshold": 5.8,
        "critical_threshold": 4.5,
        "business_owner": "Head of Supply Chain",
        "linked_financial_outcome": "cash_flow",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Stockout Rate",
        "department": "Supply Chain",
        "description": "Percentage of customer orders that cannot be fulfilled immediately due to zero stock",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 1.8,
        "warning_threshold": 3.8,
        "critical_threshold": 6.5,
        "business_owner": "Inventory Manager",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Supplier Lead Time",
        "department": "Supply Chain",
        "description": "Average calendar days between procurement purchase order and warehouse receipt",
        "unit": "Days",
        "direction": "lower_is_better",
        "target_value": 21.0,
        "warning_threshold": 30.0,
        "critical_threshold": 42.0,
        "business_owner": "Procurement Director",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "On-Time Delivery",
        "department": "Supply Chain",
        "description": "Percentage of supplier and carrier shipments arriving on or before promise date",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 96.0,
        "warning_threshold": 91.0,
        "critical_threshold": 84.0,
        "business_owner": "Logistics Director",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Inventory Carrying Cost",
        "department": "Supply Chain",
        "description": "Carrying, warehousing, and insurance cost expressed as percentage of inventory value",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 14.0,
        "warning_threshold": 18.0,
        "critical_threshold": 22.0,
        "business_owner": "Supply Chain Controller",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
    # Human Resources
    {
        "kpi_name": "Employee Turnover",
        "department": "Human Resources",
        "description": "Annualized voluntary employee turnover percentage across business units",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 8.5,
        "warning_threshold": 12.5,
        "critical_threshold": 17.0,
        "business_owner": "Chief People Officer",
        "linked_financial_outcome": "operating_expenses",
        "expected_lag_days": 60,
    },
    {
        "kpi_name": "Absenteeism",
        "department": "Human Resources",
        "description": "Percentage of scheduled work days lost due to unplanned employee absence",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 2.4,
        "warning_threshold": 4.0,
        "critical_threshold": 5.8,
        "business_owner": "VP HR Operations",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Overtime Hours",
        "department": "Human Resources",
        "description": "Overtime hours expressed as a percentage of total standard worked hours",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 5.0,
        "warning_threshold": 8.5,
        "critical_threshold": 13.0,
        "business_owner": "VP HR Operations",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Training Completion",
        "department": "Human Resources",
        "description": "Percentage of operational staff who completed mandatory certification and skill training",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 92.0,
        "warning_threshold": 82.0,
        "critical_threshold": 70.0,
        "business_owner": "Director of L&D",
        "linked_financial_outcome": "revenue_per_employee",
        "expected_lag_days": 60,
    },
    {
        "kpi_name": "Revenue per Employee",
        "department": "Human Resources",
        "description": "Total company revenue divided by total full-time equivalent (FTE) headcount",
        "unit": "USD",
        "direction": "higher_is_better",
        "target_value": 310000.0,
        "warning_threshold": 260000.0,
        "critical_threshold": 220000.0,
        "business_owner": "Chief People Officer",
        "linked_financial_outcome": "revenue",
        "expected_lag_days": 0,
    },
    # Finance
    {
        "kpi_name": "Days Sales Outstanding",
        "department": "Finance",
        "description": "Average number of days required to collect invoice receivables from enterprise clients",
        "unit": "Days",
        "direction": "lower_is_better",
        "target_value": 42.0,
        "warning_threshold": 52.0,
        "critical_threshold": 65.0,
        "business_owner": "Chief Financial Officer",
        "linked_financial_outcome": "cash_flow",
        "expected_lag_days": 30,
    },
    {
        "kpi_name": "Working Capital Ratio",
        "department": "Finance",
        "description": "Ratio of current assets to current operational liabilities",
        "unit": "x",
        "direction": "target_range",
        "target_value": 1.75,
        "warning_threshold": 1.35,
        "critical_threshold": 1.10,
        "business_owner": "VP Corporate Finance",
        "linked_financial_outcome": "cash_flow",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Budget Variance",
        "department": "Finance",
        "description": "Percentage variance between actual operating profit and budgeted operating profit",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": 2.5,
        "warning_threshold": -4.0,
        "critical_threshold": -10.0,
        "business_owner": "VP FP&A",
        "linked_financial_outcome": "operating_profit",
        "expected_lag_days": 0,
    },
    {
        "kpi_name": "Expense-to-Revenue Ratio",
        "department": "Finance",
        "description": "Total operating expenses divided by total generated revenue",
        "unit": "%",
        "direction": "lower_is_better",
        "target_value": 34.0,
        "warning_threshold": 39.0,
        "critical_threshold": 45.0,
        "business_owner": "VP FP&A",
        "linked_financial_outcome": "operating_margin",
        "expected_lag_days": 0,
    },
]

BUSINESS_EVENTS_DATA = [
    {
        "event_id": "EVT-2024-001",
        "date": "2024-03-15",
        "business_unit": "Enterprise Solutions",
        "event_type": "Pricing Optimization",
        "description": "Implemented 8% price increase across enterprise tier subscriptions",
        "affected_department": "Sales",
        "estimated_impact": "+$1.8M ARR with minimal churn",
    },
    {
        "event_id": "EVT-2024-002",
        "date": "2024-07-10",
        "business_unit": "Global Logistics",
        "event_type": "Supply Chain Disruption",
        "description": "Red Sea shipping diversions and European port congestion caused 14-day transit delays",
        "affected_department": "Supply Chain",
        "estimated_impact": "+12 days supplier lead time, temporary stockouts",
    },
    {
        "event_id": "EVT-2024-003",
        "date": "2024-10-01",
        "business_unit": "Cloud & Digital Services",
        "event_type": "Product Launch",
        "description": "General availability launch of GenAI Decision Assist add-on module",
        "affected_department": "Marketing",
        "estimated_impact": "+22% MQL volume, +$2.4M new pipeline",
    },
    {
        "event_id": "EVT-2025-001",
        "date": "2025-02-15",
        "business_unit": "Consumer Products",
        "event_type": "Marketing Campaign",
        "description": "Global multi-channel brand campaign launch across Americas and Europe",
        "affected_department": "Marketing",
        "estimated_impact": "+35% website traffic, temporary surge in CAC",
    },
    {
        "event_id": "EVT-2025-002",
        "date": "2025-06-18",
        "business_unit": "Enterprise Solutions",
        "event_type": "System Outage",
        "description": "Cloud hosting provider latency outage impacting customer API workflows for 4 hours",
        "affected_department": "Customer Service",
        "estimated_impact": "Spike in complaint rate, $280K SLA credit provisions",
    },
    {
        "event_id": "EVT-2025-003",
        "date": "2025-09-01",
        "business_unit": "Global Logistics",
        "event_type": "Warehouse Automation",
        "description": "Commissioned automated sorter robotics across 3 major distribution hubs",
        "affected_department": "Operations",
        "estimated_impact": "-18% cost per order, +15% capacity utilization",
    },
]

MANAGEMENT_ACTIONS_DATA = [
    {
        "action_id": "ACT-2024-101",
        "date_created": "2024-08-01",
        "related_kpi": "Stockout Rate",
        "related_financial_outcome": "revenue",
        "action_description": "Diversify primary semiconductor and logistics suppliers with secondary regional backup agreements",
        "owner": "Director of Procurement",
        "priority": "High",
        "status": "Completed",
        "expected_impact": "Reduce stockout rate from 4.8% down to under 2.0%",
        "actual_impact": "Stockout rate improved to 1.9% by Q4 2024; recovered $650K estimated lost sales",
        "review_date": "2024-12-15",
    },
    {
        "action_id": "ACT-2024-102",
        "date_created": "2024-11-15",
        "related_kpi": "Sales Conversion Rate",
        "related_financial_outcome": "revenue",
        "action_description": "Revamp enterprise qualification criteria and roll out consultative sales playbook",
        "owner": "VP Sales",
        "priority": "High",
        "status": "In Progress",
        "expected_impact": "+0.6% uplift in sales conversion rate",
        "actual_impact": "+0.4% uplift observed across North America & Europe",
        "review_date": "2025-03-31",
    },
    {
        "action_id": "ACT-2025-103",
        "date_created": "2025-03-01",
        "related_kpi": "Customer Acquisition Cost",
        "related_financial_outcome": "operating_profit",
        "action_description": "Reallocate 25% of underperforming paid search budget into high-intent content syndication and partner referrals",
        "owner": "Chief Marketing Officer",
        "priority": "Medium",
        "status": "In Progress",
        "expected_impact": "Lower CAC by $250 while preserving deal volume",
        "actual_impact": "Early indicator shows CAC down by $180 in Consumer Products",
        "review_date": "2025-07-31",
    },
    {
        "action_id": "ACT-2025-104",
        "date_created": "2025-07-01",
        "related_kpi": "First-Contact Resolution",
        "related_financial_outcome": "operating_expenses",
        "action_description": "Deploy AI tiered deflection agent for tier-1 repetitive billing and status inquiries",
        "owner": "Head of Support Ops",
        "priority": "Medium",
        "status": "Proposed",
        "expected_impact": "Improve FCR by 8 percentage points, saving 600 agent hours/mo",
        "actual_impact": "Pending rollout in Q4 2025",
        "review_date": "2025-10-31",
    },
    {
        "action_id": "ACT-2025-105",
        "date_created": "2025-09-15",
        "related_kpi": "Employee Turnover",
        "related_financial_outcome": "operating_expenses",
        "action_description": "Benchmark engineering and operations compensation against tier-1 market percentiles to stem attrition",
        "owner": "Chief People Officer",
        "priority": "Critical",
        "status": "In Progress",
        "expected_impact": "Reduce voluntary turnover from 14% to below 9%",
        "actual_impact": "Early exit survey shows retention stabilized in Logistics",
        "review_date": "2026-01-31",
    },
]


def generate_all_synthetic_data(seed: int = SEED) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate comprehensive synthetic datasets with 24 monthly periods (2024-01 to 2025-12)
    across 4 business units and 5 regions, with realistic cross-variable couplings.
    """
    np.random.seed(seed)
    
    # 24 Months
    dates = pd.date_range(start="2024-01-01", end="2025-12-01", freq="MS")
    num_months = len(dates)
    
    # 1. KPI Definitions DataFrame
    df_kpi_defs = pd.DataFrame(KPI_DEFINITIONS_DATA)
    
    # 2. Business Events DataFrame
    df_events = pd.DataFrame(BUSINESS_EVENTS_DATA)
    
    # 3. Management Actions DataFrame
    df_actions = pd.DataFrame(MANAGEMENT_ACTIONS_DATA)
    
    # Product categories per BU
    bu_categories = {
        "Enterprise Solutions": ["Enterprise Core ERP", "Analytics Suite", "Custom Implementations"],
        "Consumer Products": ["Smart Home Devices", "Wearables", "Subscription Services"],
        "Cloud & Digital Services": ["Compute Instances", "Managed Storage", "AI API Services"],
        "Global Logistics": ["Freight Express", "Cold Chain Transport", "Warehousing Services"]
    }
    
    # Base revenue multipliers by Business Unit and Region
    bu_base = {
        "Enterprise Solutions": 3_200_000,
        "Consumer Products": 2_400_000,
        "Cloud & Digital Services": 2_800_000,
        "Global Logistics": 2_100_000,
    }
    region_multiplier = {
        "North America": 1.35,
        "Europe": 1.15,
        "Asia-Pacific": 1.05,
        "Latin America": 0.65,
        "Middle East & Africa": 0.55,
    }
    
    # 4. Financial Performance Generation
    fin_records = []
    
    # Track monthly trends with seasonality and intentional shocks
    for m_idx, dt in enumerate(dates):
        month_str = dt.strftime("%Y-%m-%d")
        cal_month = dt.month
        year = dt.year
        
        # Seasonality factor: Q4 peak (Oct, Nov, Dec), summer dip (Jul, Aug)
        seasonality = 1.0 + 0.12 * np.sin(2 * np.pi * (cal_month - 3) / 12) + (0.15 if cal_month in [11, 12] else 0.0)
        # 2-year secular growth trend (~8% annual growth)
        secular_trend = 1.0 + 0.007 * m_idx
        
        # Embedded macro events:
        # Event A: Q3 2024 Red Sea logistics bottleneck (months 6-8: July, Aug, Sep 2024)
        supply_chain_shock = -0.06 if (year == 2024 and cal_month in [7, 8, 9]) else 0.0
        # Event B: Q4 2024 GenAI product launch (months 9-11: Oct, Nov, Dec 2024)
        ai_launch_boost = 0.08 if (year == 2024 and cal_month >= 10) else 0.0
        # Event C: Q1 2025 Consumer Brand Campaign (Feb, Mar 2025)
        mktg_surge = 0.05 if (year == 2025 and cal_month in [2, 3]) else 0.0
        
        for bu_name, base_rev in bu_base.items():
            categories = bu_categories[bu_name]
            for reg_name, reg_mult in region_multiplier.items():
                for cat_name in categories:
                    # Random component
                    noise = np.random.normal(0, 0.035)
                    
                    # BU-specific shock adjustments
                    bu_shock = 0.0
                    if bu_name == "Global Logistics":
                        bu_shock += supply_chain_shock * 1.8
                    elif bu_name == "Cloud & Digital Services":
                        bu_shock += ai_launch_boost * 1.5
                    elif bu_name == "Consumer Products":
                        bu_shock += mktg_surge * 1.4
                    
                    # Composite revenue calculation
                    total_growth_factor = secular_trend * seasonality * (1.0 + bu_shock + noise)
                    cat_share = 1.0 / len(categories)
                    
                    rev = base_rev * reg_mult * cat_share * total_growth_factor
                    
                    # Cost structure
                    # COGS: typically 42% - 55% of revenue
                    cogs_base_pct = 0.48
                    if bu_name == "Global Logistics" and year == 2024 and cal_month in [7, 8, 9]:
                        cogs_base_pct += 0.07  # Shipping disruption inflated carrier costs
                    cogs_pct = cogs_base_pct + np.random.normal(0, 0.015)
                    cogs = rev * np.clip(cogs_pct, 0.35, 0.65)
                    
                    # Gross Profit exact identity
                    gross_profit = rev - cogs
                    
                    # Operating Expenses: ~30% - 38% of revenue
                    opex_pct = 0.33 + np.random.normal(0, 0.012)
                    if bu_name == "Consumer Products" and year == 2025 and cal_month in [2, 3]:
                        opex_pct += 0.05  # Marketing campaign surge
                    opex = rev * np.clip(opex_pct, 0.22, 0.45)
                    
                    # Operating Profit exact identity
                    operating_profit = gross_profit - opex
                    
                    # Cash flow: operating profit + working capital adjustments
                    working_cap_noise = np.random.normal(0, 0.08)
                    cash_flow = operating_profit * (0.85 + working_cap_noise)
                    
                    # Customer and orders counts
                    avg_order_size = 3800 if bu_name == "Enterprise Solutions" else (850 if bu_name == "Consumer Products" else 2200)
                    orders_count = max(10, int(rev / avg_order_size * (1 + np.random.normal(0, 0.05))))
                    customer_count = max(5, int(orders_count * 0.72))
                    
                    # Budget targets
                    budget_rev = base_rev * reg_mult * cat_share * secular_trend * seasonality * 1.02
                    budget_profit = budget_rev * 0.19
                    
                    # Previous period values (calculated or approximated for index 0)
                    if m_idx == 0:
                        prev_rev = rev * 0.98
                        prev_profit = operating_profit * 0.96
                    else:
                        prev_rev = rev * (1.0 - (0.01 + noise * 0.5))
                        prev_profit = operating_profit * (1.0 - (0.01 + noise * 0.6))
                        
                    fin_records.append({
                        "date": month_str,
                        "business_unit": bu_name,
                        "region": reg_name,
                        "product_category": cat_name,
                        "revenue": round(rev, 2),
                        "cost_of_goods_sold": round(cogs, 2),
                        "operating_expenses": round(opex, 2),
                        "gross_profit": round(gross_profit, 2),
                        "operating_profit": round(operating_profit, 2),
                        "cash_flow": round(cash_flow, 2),
                        "customer_count": customer_count,
                        "orders_count": orders_count,
                        "budget_revenue": round(budget_rev, 2),
                        "budget_operating_profit": round(budget_profit, 2),
                        "previous_period_revenue": round(prev_rev, 2),
                        "previous_period_profit": round(prev_profit, 2),
                    })
                    
    df_financial = pd.DataFrame(fin_records)
    
    # 5. Operational KPIs Generation
    kpi_records = []
    
    # Pre-map KPI definitions for fast lookup
    defs_lookup = {d["kpi_name"]: d for d in KPI_DEFINITIONS_DATA}
    
    for m_idx, dt in enumerate(dates):
        month_str = dt.strftime("%Y-%m-%d")
        cal_month = dt.month
        year = dt.year
        
        for bu_name in BUSINESS_UNITS:
            for reg_name in REGIONS:
                for kpi_meta in KPI_DEFINITIONS_DATA:
                    kpi_name = kpi_meta["kpi_name"]
                    dept = kpi_meta["department"]
                    unit = kpi_meta["unit"]
                    target = kpi_meta["target_value"]
                    owner = kpi_meta["business_owner"]
                    
                    # Generate value based on baseline target + natural variance + realistic shocks
                    noise = np.random.normal(0, 0.04)
                    val = target * (1.0 + noise)
                    
                    # Embedded Realistic Domain Behaviors:
                    if kpi_name == "Sales Conversion Rate":
                        # Improved gradually after Nov 2024 sales enablement training
                        if year == 2025:
                            val *= 1.08
                        if cal_month in [11, 12]:
                            val *= 1.12 # Q4 sales urgency
                    
                    elif kpi_name == "Stockout Rate":
                        # Spiked during Q3 2024 Red Sea event for Global Logistics & Consumer Products
                        if year == 2024 and cal_month in [7, 8, 9] and bu_name in ["Global Logistics", "Consumer Products"]:
                            val = target * 2.8 + np.random.uniform(0.5, 1.5)
                        elif year == 2025 and cal_month >= 9 and bu_name == "Global Logistics":
                            val = target * 0.7  # Post-automation improvement
                            
                    elif kpi_name == "Supplier Lead Time":
                        if year == 2024 and cal_month in [7, 8, 9]:
                            val = target * 1.6 + np.random.uniform(2, 6)
                            
                    elif kpi_name == "Customer Acquisition Cost":
                        # Rose during Q1 2025 consumer campaign
                        if year == 2025 and cal_month in [2, 3] and bu_name == "Consumer Products":
                            val = target * 1.35
                            
                    elif kpi_name == "Customer Satisfaction Score":
                        # Dipped slightly in Q3 2024 due to stockouts & delays
                        if year == 2024 and cal_month in [8, 9, 10]:
                            val = target * 0.91
                        # Dipped in June 2025 due to enterprise cloud outage
                        if year == 2025 and cal_month == 6 and bu_name == "Enterprise Solutions":
                            val = target * 0.88
                            
                    elif kpi_name == "Employee Turnover":
                        # Rose in late 2024 / early 2025 across tech & logistics
                        if (year == 2024 and cal_month >= 10) or (year == 2025 and cal_month <= 4):
                            val = target * 1.45
                        elif year == 2025 and cal_month >= 10:
                            val = target * 0.95 # Post-retention intervention
                            
                    elif kpi_name == "Cost per Order":
                        # Dropped in Q4 2025 post warehouse automation
                        if year == 2025 and cal_month >= 9 and bu_name == "Global Logistics":
                            val = target * 0.82
                    
                    # Rounding according to unit
                    if unit in ["%", "x", "Score", "NPS", "Units/Hr"]:
                        val_rounded = round(float(val), 2)
                    elif unit in ["Days", "Hours", "Count"]:
                        val_rounded = round(float(val), 1)
                    else: # USD
                        val_rounded = round(float(val), 2)
                    
                    # Previous period value
                    prev_val = round(val_rounded * (1.0 - np.random.normal(0, 0.03)), 2)
                    
                    kpi_records.append({
                        "date": month_str,
                        "department": dept,
                        "business_unit": bu_name,
                        "region": reg_name,
                        "kpi_name": kpi_name,
                        "kpi_value": val_rounded,
                        "kpi_unit": unit,
                        "target_value": target,
                        "previous_period_value": prev_val,
                        "data_source": "Enterprise Data Warehouse (EDW)",
                        "kpi_owner": owner,
                    })
                    
    df_operational = pd.DataFrame(kpi_records)
    
    return df_financial, df_operational, df_kpi_defs, df_events, df_actions


def save_synthetic_datasets(target_dir: Path = SYNTHETIC_DATA_DIR) -> Dict[str, str]:
    """Generate and write all 5 CSV files to the synthetic data directory."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    df_fin, df_ops, df_defs, df_events, df_actions = generate_all_synthetic_data()
    
    paths = {
        "financial_performance": str(target_dir / "financial_performance.csv"),
        "operational_kpis": str(target_dir / "operational_kpis.csv"),
        "kpi_definitions": str(target_dir / "kpi_definitions.csv"),
        "business_events": str(target_dir / "business_events.csv"),
        "management_actions": str(target_dir / "management_actions.csv"),
    }
    
    df_fin.to_csv(paths["financial_performance"], index=False)
    df_ops.to_csv(paths["operational_kpis"], index=False)
    df_defs.to_csv(paths["kpi_definitions"], index=False)
    df_events.to_csv(paths["business_events"], index=False)
    df_actions.to_csv(paths["management_actions"], index=False)
    
    print(f"Synthetic datasets generated successfully in {target_dir}:")
    print(f" - financial_performance.csv: {len(df_fin)} rows")
    print(f" - operational_kpis.csv: {len(df_ops)} rows")
    print(f" - kpi_definitions.csv: {len(df_defs)} rows")
    print(f" - business_events.csv: {len(df_events)} rows")
    print(f" - management_actions.csv: {len(df_actions)} rows")
    
    return paths

if __name__ == "__main__":
    save_synthetic_datasets()
