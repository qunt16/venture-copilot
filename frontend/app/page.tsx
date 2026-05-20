"use client";

import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, FileCheck2, LineChart, Loader2, Save, WalletCards } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const API_BASE = "http://127.0.0.1:18000";

type Envelope<T> = { success: boolean; data: T; message: string | null };
type BusinessModel = "saas" | "service";
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

const steps = ["Business Setup", "Revenue", "Costs", "Forecast", "Validation"];

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
  const [activeStep, setActiveStep] = useState(0);
  const [setup, setSetup] = useState(defaultSetup);
  const [saasRevenue, setSaasRevenue] = useState(defaultSaasRevenue);
  const [serviceRevenue, setServiceRevenue] = useState(defaultServiceRevenue);
  const [costs, setCosts] = useState(defaultCosts);
  const [project, setProject] = useState<Project | null>(null);
  const [forecast, setForecast] = useState<ForecastOutput | null>(null);
  const [validation, setValidation] = useState<ValidationReport | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

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
    if (!response.ok || payload.success === false) throw new Error(payload.message || `Request failed: ${response.status}`);
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
      setError(err instanceof Error ? err.message : "Unknown error");
      throw err;
    } finally {
      setBusy("");
    }
  }

  async function saveProject() {
    const data = await run(
      "project",
      () => call<Project>("/projects", { method: "POST", body: JSON.stringify({ ...setup, stage: "idea" }) }),
      "Project created. Continue with revenue inputs."
    );
    setProject(data);
    setForecast(null);
    setValidation(null);
    setActiveStep(1);
  }

  async function saveRevenue() {
    if (!project) return setError("Create a project first.");
    await run(
      "revenue",
      () => call(`/projects/${project.id}/finance/revenue`, { method: "PUT", body: JSON.stringify({ config: revenueConfig }) }),
      "Revenue config saved."
    );
    setActiveStep(2);
  }

  async function saveCosts() {
    if (!project) return setError("Create a project first.");
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
      "Cost config saved."
    );
    setActiveStep(3);
  }

  async function calculate() {
    if (!project) return setError("Create a project first.");
    const data = await run(
      "calculate",
      () => call<ForecastOutput>(`/projects/${project.id}/calculate`, { method: "POST" }),
      "Forecast calculated and saved."
    );
    setForecast(data);
  }

  async function validate() {
    if (!project) return setError("Create a project and calculate forecast first.");
    const data = await run(
      "validate",
      () => call<ValidationReport>(`/projects/${project.id}/validate`, { method: "POST" }),
      "Validation completed."
    );
    setValidation(data);
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <div className="mx-auto grid max-w-[1400px] gap-4 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Finance MVP Flow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {steps.map((step, index) => (
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
              <CardTitle>Current Project</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {project ? (
                <>
                  <p className="font-medium">{project.title}</p>
                  <p className="text-muted-foreground">{project.id}</p>
                </>
              ) : (
                <p className="text-muted-foreground">Create a project to enable finance inputs.</p>
              )}
            </CardContent>
          </Card>
        </aside>

        <section className="space-y-4">
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
                <CardTitle>Step 1 · Business Setup</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <Field label="Startup name">
                  <Input value={setup.title} onChange={(event) => setSetup({ ...setup, title: event.target.value })} />
                </Field>
                <Field label="Business model">
                  <select className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" value={setup.business_model} onChange={(event) => setSetup({ ...setup, business_model: event.target.value as BusinessModel })}>
                    <option value="saas">SaaS / Subscription</option>
                    <option value="service">Service / Consulting</option>
                  </select>
                </Field>
                <Field label="One-line description" className="md:col-span-2">
                  <Textarea value={setup.idea_summary} onChange={(event) => setSetup({ ...setup, idea_summary: event.target.value })} />
                </Field>
                <Field label="Industry">
                  <Input value={setup.industry} onChange={(event) => setSetup({ ...setup, industry: event.target.value })} />
                </Field>
                <Field label="Competition type">
                  <Input value={setup.competition_type} onChange={(event) => setSetup({ ...setup, competition_type: event.target.value })} />
                </Field>
                <Field label="Planning horizon">
                  <select className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" value={setup.planning_horizon} onChange={(event) => setSetup({ ...setup, planning_horizon: Number(event.target.value) })}>
                    <option value={12}>12 months</option>
                    <option value={24}>24 months</option>
                    <option value={36}>36 months</option>
                  </select>
                </Field>
                <div className="flex items-end">
                  <Button onClick={saveProject} disabled={Boolean(busy) || !setup.title.trim()} className="w-full">
                    {busy === "project" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    Create Project
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle>Step 2 · Revenue</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                {setup.business_model === "saas" ? (
                  <>
                    <NumberField label="Subscription price" value={saasRevenue.monthly_price} onChange={(value) => setSaasRevenue({ ...saasRevenue, monthly_price: value })} />
                    <NumberField label="Initial customers" value={saasRevenue.initial_customers} onChange={(value) => setSaasRevenue({ ...saasRevenue, initial_customers: value })} />
                    <NumberField label="Monthly growth rate" value={saasRevenue.monthly_growth_rate} step="0.01" onChange={(value) => setSaasRevenue({ ...saasRevenue, monthly_growth_rate: value })} />
                    <NumberField label="Monthly churn rate" value={saasRevenue.churn_rate} step="0.01" onChange={(value) => setSaasRevenue({ ...saasRevenue, churn_rate: value })} />
                  </>
                ) : (
                  <>
                    <NumberField label="Average monthly revenue per client" value={serviceRevenue.average_monthly_revenue_per_client} onChange={(value) => setServiceRevenue({ ...serviceRevenue, average_monthly_revenue_per_client: value })} />
                    <NumberField label="Initial clients" value={serviceRevenue.initial_clients} onChange={(value) => setServiceRevenue({ ...serviceRevenue, initial_clients: value })} />
                    <NumberField label="Monthly client growth rate" value={serviceRevenue.monthly_client_growth_rate} step="0.01" onChange={(value) => setServiceRevenue({ ...serviceRevenue, monthly_client_growth_rate: value })} />
                    <NumberField label="Churn / completion rate" value={serviceRevenue.completion_rate} step="0.01" onChange={(value) => setServiceRevenue({ ...serviceRevenue, completion_rate: value })} />
                  </>
                )}
                <div className="md:col-span-2">
                  <Button onClick={saveRevenue} disabled={!project || Boolean(busy)}>
                    {busy === "revenue" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    Save Revenue
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle>Step 3 · Costs</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <NumberField label="Starting cash" value={costs.starting_cash} onChange={(value) => setCosts({ ...costs, starting_cash: value })} />
                <NumberField label="Fixed monthly costs" value={costs.fixed_monthly_costs} onChange={(value) => setCosts({ ...costs, fixed_monthly_costs: value })} />
                <NumberField label="Variable cost rate" value={costs.variable_cost_rate} step="0.01" onChange={(value) => setCosts({ ...costs, variable_cost_rate: value })} />
                <NumberField label="API/server cost rate" value={costs.hosting_api_rate} step="0.01" onChange={(value) => setCosts({ ...costs, hosting_api_rate: value })} />
                <NumberField label="Marketing spend" value={costs.marketing_budget} onChange={(value) => setCosts({ ...costs, marketing_budget: value })} />
                <NumberField label="Payroll / team cost" value={costs.payroll_costs} onChange={(value) => setCosts({ ...costs, payroll_costs: value })} />
                <div className="md:col-span-2">
                  <Button onClick={saveCosts} disabled={!project || Boolean(busy)}>
                    {busy === "costs" ? <Loader2 className="h-4 w-4 animate-spin" /> : <WalletCards className="h-4 w-4" />}
                    Save Costs
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle>Step 4 · Forecast</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={calculate} disabled={!project || Boolean(busy)}>
                  {busy === "calculate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <LineChart className="h-4 w-4" />}
                  Calculate Forecast
                </Button>
                {forecast && <ForecastView forecast={forecast} />}
              </CardContent>
            </Card>
          )}

          {activeStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle>Step 5 · Validation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={validate} disabled={!project || Boolean(busy)}>
                  {busy === "validate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
                  Run Validation
                </Button>
                {validation && <ValidationView validation={validation} />}
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </main>
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

function ForecastView({ forecast }: { forecast: ForecastOutput }) {
  const output = forecast.output;
  const summary = output.summary || {};
  const annual = summary.annual || [];
  const rows = output.monthly_rows || [];
  const last = rows[rows.length - 1] || {};

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Cash balance" value={money(summary.ending_cash ?? last.cash_balance)} />
        <Metric label="Runway months" value={summary.runway_months ?? "--"} />
        <Metric label="Zero-cash month" value={summary.zero_cash_month ?? "Not reached"} />
        <Metric label="Break-even month" value={summary.break_even_month ?? "Not reached"} />
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
              <th className="px-3 py-2">Year</th>
              <th className="px-3 py-2">Annual revenue</th>
              <th className="px-3 py-2">Annual net profit / loss</th>
              <th className="px-3 py-2">Gross margin</th>
            </tr>
          </thead>
          <tbody>
            {annual.map((year: any) => (
              <tr key={year.year} className="border-t border-border">
                <td className="px-3 py-2">Year {year.year}</td>
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
              {["Month", "Customers/clients", "Revenue", "Costs", "Net profit", "Cash balance"].map((heading) => (
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

function ValidationView({ validation }: { validation: ValidationReport }) {
  const report = validation.report;
  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Errors" value={report.issue_count.errors} />
        <Metric label="Warnings" value={report.issue_count.warnings} />
        <Metric label="Suggestions" value={report.issue_count.suggestions} />
      </div>
      <div className="space-y-3">
        {report.issues.length === 0 && <p className="rounded-md bg-muted p-3 text-sm">No validation issues found.</p>}
        {report.issues.map((issue) => (
          <div key={`${issue.rule_id}-${issue.title}`} className="rounded-md border border-border p-3 text-sm">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-muted px-2 py-1 font-mono text-xs">{issue.rule_id}</span>
              <span className={severityClass(issue.severity)}>{issue.severity}</span>
              <b>{issue.title}</b>
            </div>
            <p>{issue.description}</p>
            <p className="mt-2 text-muted-foreground">{issue.fix_suggestion}</p>
            {issue.affected_fields?.length ? (
              <p className="mt-2 font-mono text-xs text-muted-foreground">{issue.affected_fields.join(", ")}</p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function money(value: any) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function pct(value: any) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function severityClass(severity: string) {
  if (severity === "error") return "rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700";
  if (severity === "warning") return "rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700";
  return "rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700";
}
