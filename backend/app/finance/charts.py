from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CHART_DIR = Path(__file__).resolve().parents[2] / "exports" / "charts"


def generate_finance_charts(project_id: str, forecast_data: dict) -> dict:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    rows = forecast_data.get("monthly_rows") or []
    sensitivity = forecast_data.get("sensitivity_analysis") or []
    if not rows:
        return {}
    charts = {}
    charts["revenue_trend"] = _line(project_id, "revenue_trend", "收入趋势", rows, "revenue")
    charts["cash_flow"] = _line(project_id, "cash_flow", "现金余额趋势", rows, "cash_balance")
    charts["cost_structure"] = _cost(project_id, rows)
    if sensitivity:
        charts["sensitivity"] = _sensitivity(project_id, sensitivity)
    return charts


def _line(project_id: str, name: str, title: str, rows: list[dict], key: str) -> str:
    path = CHART_DIR / f"{project_id}_{name}.png"
    plt.figure(figsize=(7, 3.2))
    plt.plot([r["month"] for r in rows], [r.get(key, 0) for r in rows], marker="o", linewidth=1.5)
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel(key)
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    return str(path)


def _cost(project_id: str, rows: list[dict]) -> str:
    path = CHART_DIR / f"{project_id}_cost_structure.png"
    plt.figure(figsize=(7, 3.2))
    months = [r["month"] for r in rows]
    plt.plot(months, [r.get("fixed_costs", 0) for r in rows], label="fixed")
    plt.plot(months, [r.get("variable_costs", 0) for r in rows], label="variable")
    plt.title("成本结构")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    return str(path)


def _sensitivity(project_id: str, rows: list[dict]) -> str:
    path = CHART_DIR / f"{project_id}_sensitivity.png"
    plt.figure(figsize=(7, 3.2))
    plt.bar([str(r.get("scenario")) for r in rows], [r.get("ending_cash", 0) for r in rows])
    plt.title("敏感性分析")
    plt.xticks(rotation=12)
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    return str(path)
