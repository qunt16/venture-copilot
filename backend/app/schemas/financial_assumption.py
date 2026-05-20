from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FinancialAssumptionPayload(BaseModel):
    price: float = Field(ge=0, description="售价")
    unit_cost: float = Field(ge=0, description="单位成本")
    first_month_units: float = Field(ge=0, description="预计首月销量")
    growth_rate: float = Field(ge=0, description="增长率")
    startup_funds: float = Field(ge=0, description="启动资金")
    fixed_costs: float = Field(ge=0, description="固定成本")
    marketing_budget: float = Field(ge=0, description="营销预算")
    employee_costs: float = Field(ge=0, description="员工成本")
    forecast_months: int = Field(ge=1, le=60, description="预测周期")
    financing_amount: float = Field(default=0, ge=0)
    r_and_d_costs: float = Field(default=0, ge=0)
    repeat_purchase_rate: Optional[float] = Field(default=None, ge=0, le=1)
    conversion_rate: Optional[float] = Field(default=None, ge=0, le=1)
    ltv: Optional[float] = Field(default=None, ge=0)
    cac: Optional[float] = Field(default=None, ge=0)
    channel_costs: float = Field(default=0, ge=0)
    confirmed: bool = True
    ai_suggested: bool = False


class FinancialAssumptionRead(BaseModel):
    id: str
    project_id: str
    assumptions: dict
    warnings: list[str]
    confirmed: bool
    forecast: dict | None = None
    interpretation: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
