from typing import Optional
from pydantic import BaseModel, Field


class FinanceForecastCreate(BaseModel):
    starting_revenue: float = Field(default=0.0, ge=0)
    monthly_growth_rate: float = Field(default=0.08, ge=0, le=1)
    gross_margin: float = Field(default=0.7, ge=0, le=1)
    fixed_monthly_costs: float = Field(default=3000.0, ge=0)
    variable_cost_rate: float = Field(default=0.2, ge=0, le=1)
    starting_cash: float = Field(default=10000.0, ge=0)
    months: int = Field(default=36, ge=1, le=60)
    discount_rate: float = Field(default=0.1, ge=0, le=1)
    tax_rate: float = Field(default=0.0, ge=0, le=1)
    initial_investment: float = Field(default=0.0, ge=0)
    financing_amount: float = Field(default=0.0, ge=0)


class MonthRow(BaseModel):
    month: int
    revenue: float
    variable_costs: float
    fixed_costs: float
    total_costs: float
    gross_profit: float
    net_profit: float
    cash_balance: float


class ForecastSummary(BaseModel):
    total_revenue: float
    total_net_profit: float
    ending_cash: float
    breakeven_month: Optional[int]
    funding_needed: float


class FinanceForecastRead(BaseModel):
    id: str
    project_id: str
    assumptions: dict
    summary: dict
    months: list[dict]
    forecast_data: dict
    markdown_tables: dict
    csv_exports: dict
    charts: dict

    model_config = {"from_attributes": True}
