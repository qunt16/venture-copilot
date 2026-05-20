"use client";

import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, Download, FileCheck2, Languages, LineChart, Loader2, Save, WalletCards } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const API_BASE = "http://127.0.0.1:18000";

type Envelope<T> = { success: boolean; data: T; message: string | null };
type BusinessModel = "saas" | "service";
type Lang = "zh" | "en";
type Project = {
  id: string;
  title: string;
  idea_summary: string | null;
  industry?: string | null;
  competition_type?: string | null;
  business_model?: BusinessModel | null;
  planning_horizon?: number | null;
};
type ForecastOutput = {
  id: string;
  project_id: string;
  output: {
    business_model: string;
    planning_horizon: number;
    monthly_rows: Array<Record<string, any>>;
    summary: Record<string, any>;
  };
};
type ValidationReport = {
  id: string;
  project_id: string;
  report: {
    summary_narrative?: string | null;
    judge_perspective?: string | null;
    overall_score?: number | null;
    risk_level?: string | null;
    why_this_matters?: string | null;
    top_risks?: string[];
    next_actions?: string[];
    issue_count: { errors: number; warnings: number; suggestions: number };
    issues: Array<{
      rule_id: string;
      severity: string;
      title: string;
      description: string;
      fix_suggestion: string;
      affected_fields?: string[];
    }>;
  };
};
type ProjectSummary = {
  project: Project;
  forecast_metrics: Record<string, any>;
  validation_issue_counts: { errors: number; warnings: number; suggestions: number };
  summary_narrative?: string | null;
  judge_perspective?: string | null;
};

const copy = {
  zh: {
    appTitle: "竞赛财务 Copilot",
    flowTitle: "五步财务建模",
    currentProject: "当前项目",
    createHint: "先创建项目，再填写收入和成本假设。",
    steps: ["项目设置", "收入预测", "成本结构", "财务预测", "风险检查"],
    stepTitles: ["第 1 步 · 项目设置", "第 2 步 · 收入预测", "第 3 步 · 成本结构", "第 4 步 · 财务预测", "第 5 步 · 风险检查"],
    startupName: "项目名称",
    businessModel: "商业模式",
    saas: "SaaS / 订阅制",
    service: "服务 / 咨询",
    description: "一句话描述",
    industry: "所属行业",
    competitionType: "竞赛类型",
    planningHorizon: "预测周期",
    months12: "12 个月",
    months24: "24 个月",
    months36: "36 个月",
    createProject: "创建项目",
    projectCreated: "项目已创建，请继续填写收入假设。",
    createFirst: "请先创建项目。",
    forecastFirst: "请先创建项目并完成财务预测。",
    subscriptionPrice: "订阅价格",
    initialCustomers: "首月客户数",
    monthlyGrowthRate: "月增长率",
    monthlyChurnRate: "月流失率",
    avgClientRevenue: "单客户月收入",
    initialClients: "初始客户数",
    clientGrowthRate: "客户月增长率",
    completionRate: "流失 / 项目完成率",
    saveRevenue: "保存收入假设",
    revenueSaved: "收入假设已保存。",
    startingCash: "启动资金",
    fixedCosts: "固定月成本",
    variableCostRate: "变动成本率",
    apiCostRate: "API / 服务器成本率",
    marketingSpend: "营销预算",
    payrollCost: "团队 / 人员成本",
    saveCosts: "保存成本结构",
    costsSaved: "成本结构已保存。",
    calculateForecast: "开始预测",
    forecastDone: "财务预测已生成并保存。",
    runValidation: "风险检查",
    validationDone: "风险检查已完成。",
    downloadCsv: "导出 CSV",
    loadSummary: "加载一页摘要",
    summaryLoaded: "一页摘要已加载。",
    cashBalance: "现金余额",
    runway: "现金续航月数",
    zeroCashMonth: "现金耗尽月份",
    notReached: "未触发",
    breakEven: "盈亏平衡点",
    annualRevenue: "年度收入",
    annualNetProfit: "年度净利润 / 亏损",
    grossMargin: "毛利率",
    year: "年份",
    month: "月份",
    customers: "客户数",
    revenue: "收入",
    costs: "成本",
    netProfit: "净利润",
    score: "综合评分",
    riskLevel: "风险等级",
    topRisks: "主要问题",
    nextActions: "下一步建议",
    whyMatters: "为什么重要",
    judgePerspective: "评委视角",
    issueList: "规则检查明细",
    noIssues: "暂未发现规则风险，请继续准备假设依据和答辩材料。",
    affectedFields: "相关字段",
    onePageSummary: "一页摘要",
    totalRevenue: "总收入",
    endingCash: "期末现金",
    highRisk: "高风险",
    watch: "需关注",
    healthy: "健康",
    suggestions: "建议优化",
    unknownError: "未知错误",
    requestFailed: "请求失败",
    language: "语言",
  },
  en: {
    appTitle: "Competition Finance Copilot",
    flowTitle: "Five-step Finance Flow",
    currentProject: "Current Project",
    createHint: "Create a project to enable revenue and cost assumptions.",
    steps: ["Business Setup", "Revenue", "Costs", "Forecast", "Validation"],
    stepTitles: ["Step 1 · Business Setup", "Step 2 · Revenue", "Step 3 · Costs", "Step 4 · Forecast", "Step 5 · Validation"],
    startupName: "Startup name",
    businessModel: "Business model",
    saas: "SaaS / Subscription",
    service: "Service / Consulting",
    description: "One-line description",
    industry: "Industry",
    competitionType: "Competition type",
    planningHorizon: "Planning horizon",
    months12: "12 months",
    months24: "24 months",
    months36: "36 months",
    createProject: "Create Project",
    projectCreated: "Project created. Continue with revenue inputs.",
    createFirst: "Create a project first.",
    forecastFirst: "Create a project and calculate forecast first.",
    subscriptionPrice: "Subscription price",
    initialCustomers: "Initial customers",
    monthlyGrowthRate: "Monthly growth rate",
    monthlyChurnRate: "Monthly churn rate",
    avgClientRevenue: "Average monthly revenue per client",
    initialClients: "Initial clients",
    clientGrowthRate: "Monthly client growth rate",
    completionRate: "Churn / completion rate",
    saveRevenue: "Save Revenue",
    revenueSaved: "Revenue config saved.",
    startingCash: "Starting cash",
    fixedCosts: "Fixed monthly costs",
    variableCostRate: "Variable cost rate",
    apiCostRate: "API/server cost rate",
    marketingSpend: "Marketing spend",
    payrollCost: "Payroll / team cost",
    saveCosts: "Save Costs",
    costsSaved: "Cost config saved.",
    calculateForecast: "Calculate Forecast",
    forecastDone: "Forecast calculated and saved.",
    runValidation: "Run Validation",
    validationDone: "Validation completed.",
    downloadCsv: "Download CSV",
    loadSummary: "Load One-page Summary",
    summaryLoaded: "One-page summary loaded.",
    cashBalance: "Cash balance",
    runway: "Runway months",
    zeroCashMonth: "Zero-cash month",
    notReached: "Not reached",
    breakEven: "Break-even",
    annualRevenue: "Annual revenue",
    annualNetProfit: "Annual net profit / loss",
    grossMargin: "Gross margin",
    year: "Year",
    month: "Month",
    customers: "Customers/clients",
    revenue: "Revenue",
    costs: "Costs",
    netProfit: "Net profit",
    score: "Overall score",
    riskLevel: "Risk level",
    topRisks: "Top risks",
    nextActions: "Next actions",
    whyMatters: "Why this matters",
    judgePerspective: "Judge perspective",
    issueList: "Validation details",
    noIssues: "No validation issues found. Keep evidence ready for your assumptions.",
    affectedFields: "Affected fields",
    onePageSummary: "One-page summary",
    totalRevenue: "Total revenue",
    endingCash: "Ending cash",
    highRisk: "High risk",
    watch: "Needs attention",
    healthy: "Healthy",
    suggestions: "Suggestions",
    unknownError: "Unknown error",
    requestFailed: "Request failed",
    language: "Language",
  },
} as const;

const defaultSetup = {
  title: "Campus Finance Copilot",
  idea_summary: "A guided finance planning tool for university startup competitions.",
  industry: "education technology",
  competition_type: "challenge_cup",
  business_model: "saas" as BusinessModel,
  planning_horizon: 36,
};

const defaultSaasRevenue = {
  monthly_price: 99,
  initial_customers: 20,
  monthly_growth_rate: 0.1,
  churn_rate: 0.03,
};

const defaultServiceRevenue = {
  average_monthly_revenue_per_client: 3000,
  initial_clients: 3,
  monthly_client_growth_rate: 0.08,
  completion_rate: 0.05,
};

const defaultCosts = {
  starting_cash: 50000,
  fixed_monthly_costs: 2500,
  variable_cost_rate: 0,
  hosting_api_rate: 0.08,
  marketing_budget: 1000,
  payroll_costs: 8000,
};

export default function Home() {
  const [lang, setLang] = useState<Lang>("zh");
  const [activeStep, setActiveStep] = useState(0);
  const [setup, setSetup] = useState(defaultSetup);
  const [saasRevenue, setSaasRevenue] = useState(defaultSaasRevenue);
  const [serviceRevenue, setServiceRevenue] = useState(defaultServiceRevenue);
  const [costs, setCosts] = useState(defaultCosts);
  const [project, setProject] = useState<Project | null>(null);
  const [forecast, setForecast] = useState<ForecastOutput | null>(null);
  const [validation, setValidation] = useState<ValidationReport | null>(null);
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const t = copy[lang];

  const revenueConfig = useMemo(() => {
    if (setup.business_model === "service") return serviceRevenue;
    return saasRevenue;
  }, [setup.business_model, serviceRevenue, saasRevenue]);

  async function call<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "content-type": "application/json", ...(options?.headers || {}) },
    });
    const payload = (await response.json()) as Envelope<T>;
    if (!response.ok || payload.success === false) throw new Error(payload.message || `${t.requestFailed}: ${response.status}`);
    return payload.data;
  }

  async function run<T>(label: string, fn: () => Promise<T>, success?: string) {
    setBusy(label);
    setError("");
    setMessage("");
    try {
      const result = await fn();
      if (success) setMessage(success);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : t.unknownError);
      throw err;
    } finally {
      setBusy("");
    }
  }

  async function saveProject() {
    const data = await run(
      "project",
      () => call<Project>("/projects", { method: "POST", body: JSON.stringify({ ...setup, stage: "idea" }) }),
      t.projectCreated
    );
    setProject(data);
    setForecast(null);
    setValidation(null);
    setSummary(null);
    setActiveStep(1);
  }

  async function saveRevenue() {
    if (!project) return setError(t.createFirst);
    await run(
      "revenue",
      () => call(`/projects/${project.id}/finance/revenue`, { method: "PUT", body: JSON.stringify({ config: revenueConfig }) }),
      t.revenueSaved
    );
    setActiveStep(2);
  }

  async function saveCosts() {
    if (!project) return setError(t.createFirst);
    const config = {
      starting_cash: costs.starting_cash,
      fixed_monthly_costs: costs.fixed_monthly_costs,
      variable_cost_rate: costs.variable_cost_rate,
      marketing_budget: costs.marketing_budget,
      payroll_costs: costs.payroll_costs,
      variable_costs: [
        { category: "hosting", label: "API/server costs", basis: "percent_of_revenue", rate: costs.hosting_api_rate },
      ],
    };
    await run(
      "costs",
      () => call(`/projects/${project.id}/finance/costs`, { method: "PUT", body: JSON.stringify({ config }) }),
      t.costsSaved
    );
    setActiveStep(3);
  }

  async function calculate() {
    if (!project) return setError(t.createFirst);
    const data = await run(
      "calculate",
      () => call<ForecastOutput>(`/projects/${project.id}/calculate`, { method: "POST" }),
      t.forecastDone
    );
    setForecast(data);
  }

  async function validate() {
    if (!project) return setError(t.forecastFirst);
    const data = await run(
      "validate",
      () => call<ValidationReport>(`/projects/${project.id}/validate`, { method: "POST" }),
      t.validationDone
    );
    setValidation(data);
    const latestSummary = await call<ProjectSummary>(`/projects/${project.id}/summary`);
    setSummary(latestSummary);
  }

  async function loadSummary() {
    if (!project) return setError(t.createFirst);
    const data = await run(
      "summary",
      () => call<ProjectSummary>(`/projects/${project.id}/summary`),
      t.summaryLoaded
    );
    setSummary(data);
  }

  function downloadCsv() {
    if (!project) return setError(t.createFirst);
    window.open(`${API_BASE}/projects/${project.id}/export/csv`, "_blank");
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <div className="mx-auto grid max-w-[1400px] gap-4 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-4">
          <Card>
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <CardTitle>{t.flowTitle}</CardTitle>
                <LanguageToggle lang={lang} setLang={setLang} />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {t.steps.map((step, index) => (
                <button
                  key={step}
                  onClick={() => setActiveStep(index)}
                  className={`flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm ${
                    activeStep === index ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <span>{index + 1}. {step}</span>
                  {isStepDone(index, project, forecast, validation) && <CheckCircle2 className="h-4 w-4" />}
                </button>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t.currentProject}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {project ? (
                <>
                  <p className="font-medium">{project.title}</p>
                  <p className="text-muted-foreground">{project.id}</p>
                </>
              ) : (
                <p className="text-muted-foreground">{t.createHint}</p>
              )}
            </CardContent>
          </Card>
        </aside>

        <section className="space-y-4">
          <div>
            <h1 className="text-2xl font-semibold">{t.appTitle}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {lang === "zh" ? "把财务模型从数字表变成能被评委听懂的商业判断。" : "Turn finance numbers into judge-ready business reasoning."}
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4" />
              <span>{error}</span>
            </div>
          )}
          {message && (
            <div className="flex items-start gap-2 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
              <CheckCircle2 className="mt-0.5 h-4 w-4" />
              <span>{message}</span>
            </div>
          )}

          {activeStep === 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.stepTitles[0]}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <Field label={t.startupName}>
                  <Input value={setup.title} onChange={(event) => setSetup({ ...setup, title: event.target.value })} />
                </Field>
                <Field label={t.businessModel}>
                  <select className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" value={setup.business_model} onChange={(event) => setSetup({ ...setup, business_model: event.target.value as BusinessModel })}>
                    <option value="saas">{t.saas}</option>
                    <option value="service">{t.service}</option>
                  </select>
                </Field>
                <Field label={t.description} className="md:col-span-2">
                  <Textarea value={setup.idea_summary} onChange={(event) => setSetup({ ...setup, idea_summary: event.target.value })} />
                </Field>
                <Field label={t.industry}>
                  <Input value={setup.industry} onChange={(event) => setSetup({ ...setup, industry: event.target.value })} />
                </Field>
                <Field label={t.competitionType}>
                  <Input value={setup.competition_type} onChange={(event) => setSetup({ ...setup, competition_type: event.target.value })} />
                </Field>
                <Field label={t.planningHorizon}>
                  <select className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" value={setup.planning_horizon} onChange={(event) => setSetup({ ...setup, planning_horizon: Number(event.target.value) })}>
                    <option value={12}>{t.months12}</option>
                    <option value={24}>{t.months24}</option>
                    <option value={36}>{t.months36}</option>
                  </select>
                </Field>
                <div className="flex items-end">
                  <Button onClick={saveProject} disabled={Boolean(busy) || !setup.title.trim()} className="w-full">
                    {busy === "project" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    {t.createProject}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.stepTitles[1]}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                {setup.business_model === "saas" ? (
                  <>
                    <NumberField label={t.subscriptionPrice} value={saasRevenue.monthly_price} onChange={(value) => setSaasRevenue({ ...saasRevenue, monthly_price: value })} />
                    <NumberField label={t.initialCustomers} value={saasRevenue.initial_customers} onChange={(value) => setSaasRevenue({ ...saasRevenue, initial_customers: value })} />
                    <NumberField label={t.monthlyGrowthRate} value={saasRevenue.monthly_growth_rate} step="0.01" onChange={(value) => setSaasRevenue({ ...saasRevenue, monthly_growth_rate: value })} />
                    <NumberField label={t.monthlyChurnRate} value={saasRevenue.churn_rate} step="0.01" onChange={(value) => setSaasRevenue({ ...saasRevenue, churn_rate: value })} />
                  </>
                ) : (
                  <>
                    <NumberField label={t.avgClientRevenue} value={serviceRevenue.average_monthly_revenue_per_client} onChange={(value) => setServiceRevenue({ ...serviceRevenue, average_monthly_revenue_per_client: value })} />
                    <NumberField label={t.initialClients} value={serviceRevenue.initial_clients} onChange={(value) => setServiceRevenue({ ...serviceRevenue, initial_clients: value })} />
                    <NumberField label={t.clientGrowthRate} value={serviceRevenue.monthly_client_growth_rate} step="0.01" onChange={(value) => setServiceRevenue({ ...serviceRevenue, monthly_client_growth_rate: value })} />
                    <NumberField label={t.completionRate} value={serviceRevenue.completion_rate} step="0.01" onChange={(value) => setServiceRevenue({ ...serviceRevenue, completion_rate: value })} />
                  </>
                )}
                <div className="md:col-span-2">
                  <Button onClick={saveRevenue} disabled={!project || Boolean(busy)}>
                    {busy === "revenue" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    {t.saveRevenue}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.stepTitles[2]}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <NumberField label={t.startingCash} value={costs.starting_cash} onChange={(value) => setCosts({ ...costs, starting_cash: value })} />
                <NumberField label={t.fixedCosts} value={costs.fixed_monthly_costs} onChange={(value) => setCosts({ ...costs, fixed_monthly_costs: value })} />
                <NumberField label={t.variableCostRate} value={costs.variable_cost_rate} step="0.01" onChange={(value) => setCosts({ ...costs, variable_cost_rate: value })} />
                <NumberField label={t.apiCostRate} value={costs.hosting_api_rate} step="0.01" onChange={(value) => setCosts({ ...costs, hosting_api_rate: value })} />
                <NumberField label={t.marketingSpend} value={costs.marketing_budget} onChange={(value) => setCosts({ ...costs, marketing_budget: value })} />
                <NumberField label={t.payrollCost} value={costs.payroll_costs} onChange={(value) => setCosts({ ...costs, payroll_costs: value })} />
                <div className="md:col-span-2">
                  <Button onClick={saveCosts} disabled={!project || Boolean(busy)}>
                    {busy === "costs" ? <Loader2 className="h-4 w-4 animate-spin" /> : <WalletCards className="h-4 w-4" />}
                    {t.saveCosts}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.stepTitles[3]}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={calculate} disabled={!project || Boolean(busy)}>
                  {busy === "calculate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <LineChart className="h-4 w-4" />}
                  {t.calculateForecast}
                </Button>
                {forecast && <ForecastView forecast={forecast} labels={t} />}
              </CardContent>
            </Card>
          )}

          {activeStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.stepTitles[4]}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Button onClick={validate} disabled={!project || Boolean(busy)}>
                    {busy === "validate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
                    {t.runValidation}
                  </Button>
                  <Button variant="outline" onClick={downloadCsv} disabled={!project || !forecast}>
                    <Download className="h-4 w-4" />
                    {t.downloadCsv}
                  </Button>
                  <Button variant="outline" onClick={loadSummary} disabled={!project || Boolean(busy)}>
                    {busy === "summary" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
                    {t.loadSummary}
                  </Button>
                </div>
                {validation && <ValidationView validation={validation} labels={t} />}
                {summary && <SummaryView summary={summary} labels={t} />}
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </main>
  );
}

function LanguageToggle({ lang, setLang }: { lang: Lang; setLang: (lang: Lang) => void }) {
  return (
    <div className="flex items-center gap-1 rounded-md border border-border p-1 text-xs" aria-label={copy[lang].language}>
      <Languages className="h-3.5 w-3.5 text-muted-foreground" />
      {(["zh", "en"] as const).map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => setLang(option)}
          className={`rounded px-2 py-1 ${lang === option ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"}`}
        >
          {option === "zh" ? "中文" : "English"}
        </button>
      ))}
    </div>
  );
}

function isStepDone(index: number, project: Project | null, forecast: ForecastOutput | null, validation: ValidationReport | null) {
  if (index === 0) return Boolean(project);
  if (index === 3) return Boolean(forecast);
  if (index === 4) return Boolean(validation);
  return Boolean(project);
}

function Field({ label, className = "", children }: { label: string; className?: string; children: ReactNode }) {
  return (
    <label className={`space-y-1 text-sm font-medium ${className}`}>
      <span>{label}</span>
      {children}
    </label>
  );
}

function NumberField({ label, value, step = "1", onChange }: { label: string; value: number; step?: string; onChange: (value: number) => void }) {
  return (
    <Field label={label}>
      <Input type="number" step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </Field>
  );
}

function ForecastView({ forecast, labels }: { forecast: ForecastOutput; labels: typeof copy[Lang] }) {
  const output = forecast.output;
  const summary = output.summary || {};
  const annual = summary.annual || [];
  const rows = output.monthly_rows || [];
  const last = rows[rows.length - 1] || {};

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label={labels.cashBalance} value={money(summary.ending_cash ?? last.cash_balance)} />
        <Metric label={labels.runway} value={summary.runway_months ?? "--"} />
        <Metric label={labels.zeroCashMonth} value={summary.zero_cash_month ?? labels.notReached} />
        <Metric label={labels.breakEven} value={summary.break_even_month ?? labels.notReached} />
        <Metric label="MRR" value={money(summary.mrr)} />
        <Metric label="ARR" value={money(summary.arr)} />
        <Metric label="LTV" value={money(summary.ltv)} />
        <Metric label="CAC" value={money(summary.cac)} />
        <Metric label="LTV:CAC" value={summary.ltv_cac_ratio ?? "--"} />
      </div>

      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-3 py-2">{labels.year}</th>
              <th className="px-3 py-2">{labels.annualRevenue}</th>
              <th className="px-3 py-2">{labels.annualNetProfit}</th>
              <th className="px-3 py-2">{labels.grossMargin}</th>
            </tr>
          </thead>
          <tbody>
            {annual.map((year: any) => (
              <tr key={year.year} className="border-t border-border">
                <td className="px-3 py-2">{labels.year} {year.year}</td>
                <td className="px-3 py-2">{money(year.revenue)}</td>
                <td className="px-3 py-2">{money(year.net_profit)}</td>
                <td className="px-3 py-2">{pct(year.gross_margin_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="bg-muted">
            <tr>
              {[labels.month, labels.customers, labels.revenue, labels.costs, labels.netProfit, labels.cashBalance].map((heading) => (
                <th key={heading} className="px-3 py-2">{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 12).map((row: any) => (
              <tr key={row.month} className="border-t border-border">
                <td className="px-3 py-2">{row.month}</td>
                <td className="px-3 py-2">{row.active_customers ?? row.active_clients ?? "--"}</td>
                <td className="px-3 py-2">{money(row.monthly_revenue)}</td>
                <td className="px-3 py-2">{money(row.total_costs)}</td>
                <td className="px-3 py-2">{money(row.net_profit)}</td>
                <td className="px-3 py-2">{money(row.cash_balance)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ValidationView({ validation, labels }: { validation: ValidationReport; labels: typeof copy[Lang] }) {
  const report = validation.report;
  const topRisks = report.top_risks?.length ? report.top_risks : report.issues.slice(0, 3).map((issue) => issue.title);
  const nextActions = report.next_actions?.length ? report.next_actions : report.issues.slice(0, 3).map((issue) => issue.fix_suggestion);
  const riskLevel = report.risk_level || fallbackRiskLevel(report.issue_count, labels);
  const score = report.overall_score ?? fallbackScore(report.issue_count);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-4">
        <Metric label={labels.score} value={`${score} / 100`} tone={score < 60 ? "danger" : score < 85 ? "warning" : "success"} />
        <Metric label={labels.riskLevel} value={translateRiskLevel(riskLevel, labels)} tone={riskTone(riskLevel)} />
        <Metric label={labels.topRisks} value={topRisks[0] || labels.noIssues} />
        <Metric label={labels.nextActions} value={nextActions[0] || "OK"} />
      </div>

      {(report.why_this_matters || report.judge_perspective || report.summary_narrative) && (
        <div className="grid gap-3 md:grid-cols-2">
          {(report.why_this_matters || report.summary_narrative) && (
            <div className="rounded-md border border-border p-3 text-sm">
              <p className="mb-1 font-semibold">{labels.whyMatters}</p>
              <p>{report.why_this_matters || report.summary_narrative}</p>
            </div>
          )}
          {report.judge_perspective && (
            <div className="rounded-md border border-border p-3 text-sm">
              <p className="mb-1 font-semibold">{labels.judgePerspective}</p>
              <p>{report.judge_perspective}</p>
            </div>
          )}
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        <ListCard title={labels.topRisks} items={topRisks} empty={labels.noIssues} />
        <ListCard title={labels.nextActions} items={nextActions} empty="OK" />
      </div>

      <div className="space-y-3">
        <p className="font-semibold">{labels.issueList}</p>
        {report.issues.length === 0 && <p className="rounded-md bg-muted p-3 text-sm">{labels.noIssues}</p>}
        {report.issues.map((issue) => (
          <div key={`${issue.rule_id}-${issue.title}`} className="rounded-md border border-border p-3 text-sm">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-muted px-2 py-1 font-mono text-xs">{issue.rule_id}</span>
              <span className={severityClass(issue.severity)}>{translateSeverity(issue.severity, labels)}</span>
              <b>{issue.title}</b>
            </div>
            <p>{issue.description}</p>
            <p className="mt-2 text-muted-foreground">{issue.fix_suggestion}</p>
            {issue.affected_fields?.length ? (
              <p className="mt-2 font-mono text-xs text-muted-foreground">{labels.affectedFields}: {issue.affected_fields.join(", ")}</p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function SummaryView({ summary, labels }: { summary: ProjectSummary; labels: typeof copy[Lang] }) {
  return (
    <div className="space-y-3 rounded-md border border-border p-3 text-sm">
      <div>
        <p className="font-semibold">{labels.onePageSummary}</p>
        <p className="text-muted-foreground">{summary.project.title}</p>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label={labels.totalRevenue} value={money(summary.forecast_metrics.total_revenue)} />
        <Metric label={labels.endingCash} value={money(summary.forecast_metrics.ending_cash)} />
        <Metric label={labels.runway} value={summary.forecast_metrics.runway_months ?? "--"} />
      </div>
      {summary.summary_narrative && <p>{summary.summary_narrative}</p>}
      {summary.judge_perspective && <p className="text-muted-foreground">{summary.judge_perspective}</p>}
    </div>
  );
}

function ListCard({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div className="rounded-md border border-border p-3 text-sm">
      <p className="mb-2 font-semibold">{title}</p>
      {items.length ? (
        <ul className="space-y-1">
          {items.slice(0, 4).map((item, index) => (
            <li key={`${title}-${index}`} className="text-muted-foreground">{index + 1}. {item}</li>
          ))}
        </ul>
      ) : (
        <p className="text-muted-foreground">{empty}</p>
      )}
    </div>
  );
}

function Metric({ label, value, tone = "neutral" }: { label: string; value: ReactNode; tone?: "neutral" | "success" | "warning" | "danger" }) {
  const toneClass = {
    neutral: "",
    success: "border-emerald-200 bg-emerald-50",
    warning: "border-amber-200 bg-amber-50",
    danger: "border-red-200 bg-red-50",
  }[tone];
  return (
    <div className={`rounded-md border border-border p-3 ${toneClass}`}>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function fallbackScore(issueCount: { errors: number; warnings: number; suggestions: number }) {
  return Math.max(0, Math.min(100, 100 - issueCount.errors * 25 - issueCount.warnings * 10 - issueCount.suggestions * 3));
}

function fallbackRiskLevel(issueCount: { errors: number; warnings: number; suggestions: number }, labels: typeof copy[Lang]) {
  const score = fallbackScore(issueCount);
  if (issueCount.errors > 0 || score < 60) return labels.highRisk;
  if (issueCount.warnings > 0 || score < 85) return labels.watch;
  return labels.healthy;
}

function translateRiskLevel(riskLevel: string, labels: typeof copy[Lang]) {
  if (riskLevel === "高风险" || riskLevel === "High risk") return labels.highRisk;
  if (riskLevel === "需关注" || riskLevel === "Needs attention") return labels.watch;
  if (riskLevel === "健康" || riskLevel === "Healthy") return labels.healthy;
  return riskLevel;
}

function riskTone(riskLevel: string): "neutral" | "success" | "warning" | "danger" {
  if (riskLevel === "高风险" || riskLevel === "High risk") return "danger";
  if (riskLevel === "需关注" || riskLevel === "Needs attention") return "warning";
  if (riskLevel === "健康" || riskLevel === "Healthy") return "success";
  return "neutral";
}

function money(value: any) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function pct(value: any) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function translateSeverity(severity: string, labels: typeof copy[Lang]) {
  if (severity === "error") return labels.highRisk;
  if (severity === "warning") return labels.watch;
  return labels.suggestions;
}

function severityClass(severity: string) {
  if (severity === "error") return "rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700";
  if (severity === "warning") return "rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700";
  return "rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700";
}
