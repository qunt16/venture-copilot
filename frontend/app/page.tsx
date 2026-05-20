"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  BarChart3,
  CheckCircle2,
  ChevronUp,
  Copy,
  Download,
  FileText,
  FlaskConical,
  Languages,
  LineChart,
  Loader2,
  MessageSquare,
  PenLine,
  RotateCcw,
  RotateCw,
  Search,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const API_BASE = "http://127.0.0.1:18000";

type Envelope<T> = { success: boolean; data: T; message: string | null };
type Project = { id: string; title: string; idea_summary: string };
type Block = { id?: string; section_key: string; heading: string; block_type: string; content: string; order_index: number; metadata_json?: any };
type ExportResult = { file_name: string; download_url: string };
type Comment = { id: string; section_id: string; body: string; status: string; mention?: string | null };

const starterBlocks: Block[] = [
  "项目概述", "痛点与需求", "研究", "市场分析", "竞品分析", "SWOT分析", "财务分析", "融资计划", "风险分析", "社会价值", "附录",
].map((heading, index) => ({
  section_key: ["project_overview", "pain_point_analysis", "research", "market_analysis", "competitor_analysis", "swot_analysis", "financial_forecast", "funding_plan", "risk_analysis", "social_value", "appendix"][index],
  heading,
  block_type: heading === "财务分析" ? "finance" : "text",
  content: "",
  order_index: index,
}));

const defaultAssumptions = {
  price: 199,
  unit_cost: 65,
  first_month_units: 80,
  growth_rate: 0.08,
  startup_funds: 60000,
  fixed_costs: 7000,
  marketing_budget: 3000,
  employee_costs: 12000,
  forecast_months: 36,
  financing_amount: 0,
  r_and_d_costs: 2000,
  repeat_purchase_rate: 0.25,
  conversion_rate: 0.08,
  ltv: 1200,
  cac: 180,
  channel_costs: 1000,
  confirmed: true,
  ai_suggested: false,
};

export default function Home() {
  const [title, setTitle] = useState("校园低碳智能回收平台");
  const [idea, setIdea] = useState("面向高校宿舍和教学楼的智能回收箱与积分激励系统，帮助学生分类回收并为学校提供低碳数据。");
  const [project, setProject] = useState<Project | null>(null);
  const [assumptions, setAssumptions] = useState<Record<string, any>>(defaultAssumptions);
  const [assumptionWarnings, setAssumptionWarnings] = useState<string[]>([]);
  const [financeSummary, setFinanceSummary] = useState<any>(null);
  const [blocks, setBlocks] = useState<Block[]>(starterBlocks);
  const [activeIndex, setActiveIndex] = useState(0);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [score, setScore] = useState<any>(null);
  const [exports, setExports] = useState<ExportResult[]>([]);
  const [search, setSearch] = useState("");
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState("");
  const [suggestion, setSuggestion] = useState("");
  const [history, setHistory] = useState<Block[][]>([]);
  const [future, setFuture] = useState<Block[][]>([]);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const active = blocks[activeIndex] || blocks[0];
  const visibleBlocks = useMemo(
    () => blocks.filter((block) => !search || `${block.heading}\n${block.content}`.includes(search)),
    [blocks, search]
  );
  const checklist = [
    ["财务假设完整", Boolean(financeSummary)],
    ["引用已生成", blocks.some((b) => b.content.includes("http"))],
    ["无明显中英混杂", !blocks.some((b) => /Summary:|This page markets|Key features:/i.test(b.content))],
    ["章节非空", blocks.filter((b) => !b.content.trim()).length === 0],
    ["评分已生成", Boolean(score)],
    ["DOCX/PDF 已导出", exports.length >= 2],
  ];

  async function call<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "content-type": "application/json", ...(options?.headers || {}) },
    });
    const payload = (await response.json()) as Envelope<T>;
    if (!response.ok || payload.success === false) throw new Error(payload.message || `请求失败：${response.status}`);
    return payload.data;
  }

  async function run<T>(label: string, fn: () => Promise<T>) {
    setBusy(label);
    setError("");
    try {
      return await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "未知错误");
      throw err;
    } finally {
      setBusy("");
    }
  }

  function pushHistory(next: Block[]) {
    setHistory((prev) => [...prev.slice(-20), blocks]);
    setFuture([]);
    setBlocks(next);
  }

  function updateBlock(index: number, content: string) {
    pushHistory(blocks.map((block, i) => (i === index ? { ...block, content } : block)));
  }

  async function createProject() {
    const data = await run("创建项目", () =>
      call<Project>("/projects", { method: "POST", body: JSON.stringify({ title, idea_summary: idea, stage: "prototype" }) })
    );
    setProject(data);
  }

  async function saveAssumptions() {
    if (!project) return;
    const data = await run("保存假设并重算", () =>
      call<any>(`/projects/${project.id}/finance/assumptions`, { method: "POST", body: JSON.stringify(assumptions) })
    );
    setAssumptionWarnings(data.warnings || []);
    setFinanceSummary(data.forecast?.summary || null);
    upsertBlock("financial_forecast", "财务分析", [
      "财务假设已确认并完成实时重算。",
      data.interpretation?.summary || "",
      `总收入：${data.forecast?.summary?.total_revenue ?? "--"}`,
      `期末现金：${data.forecast?.summary?.ending_cash ?? "--"}`,
      `资金缺口：${data.forecast?.summary?.funding_needed ?? "--"}`,
    ].join("\n"));
  }

  async function generateResearch() {
    if (!project) return;
    const data = await run("生成 Exa 研究", () =>
      call<any>(`/projects/${project.id}/research`, { method: "POST", body: JSON.stringify({ language: "zh-CN", research_config: { provider: "exa", type: "auto", num_results: 8, fallback_to_mock: false } }) })
    );
    upsertBlock("research", "研究", `${data.summary}\n\n${data.market_size}\n\n引用：\n${(data.citations || []).map((c: any) => `${c.title}\n${c.url}`).join("\n")}`);
  }

  async function generateFrameworks() {
    if (!project) return;
    const data = await run("生成 SWOT/框架", () =>
      call<any>(`/projects/${project.id}/frameworks/analyze`, { method: "POST", body: JSON.stringify({ language: "zh-CN", frameworks: ["swot", "pest", "porter_five_forces", "business_model_canvas", "tam_sam_som", "competitor_matrix"] }) })
    );
    upsertBlock("swot_analysis", "SWOT分析", JSON.stringify(data.frameworks?.swot || data.frameworks || {}, null, 2));
    upsertBlock("competitor_analysis", "竞品分析", JSON.stringify(data.frameworks?.competitor_matrix || data.frameworks?.porter_five_forces || {}, null, 2));
  }

  async function generateFinalBP() {
    if (!project) return;
    const data = await run("生成最终商业计划书", () =>
      call<any>(`/projects/${project.id}/business-plan`, {
        method: "POST",
        body: JSON.stringify({ language: "zh-CN", template_type: "challenge_cup", sections: ["project_overview", "pain_point_analysis", "product_service", "market_analysis", "tam_sam_som", "competitor_analysis", "swot_analysis", "business_model", "marketing_strategy", "operation_plan", "financial_forecast", "funding_plan", "risk_analysis", "social_value", "references", "appendix"], ai_config: { provider: "openrouter", model: "deepseek/deepseek-chat", fallback_to_mock: false } }),
      })
    );
    const next = data.sections.map((s: any, index: number) => ({ section_key: s.key, heading: s.heading, block_type: s.key === "financial_forecast" ? "finance" : "text", content: s.content, order_index: index }));
    pushHistory(next);
  }

  async function review() {
    if (!project) return;
    const data = await run("运行评分", () => call<any>(`/projects/${project.id}/review`, { method: "POST" }));
    setScore(data);
  }

  async function polish(mode: string) {
    if (!project || !active?.content) return;
    const data = await run("AI 修改", () =>
      call<any>(`/projects/${project.id}/sections/polish`, { method: "POST", body: JSON.stringify({ language: "zh-CN", section_key: active.section_key, text: active.content, mode }) })
    );
    setSuggestion(data.revised_text);
  }

  async function saveNow() {
    if (!project) return;
    await call(`/projects/${project.id}/document/autosave`, { method: "PATCH", body: JSON.stringify({ blocks }) });
  }

  async function exportFiles() {
    if (!project) return;
    if (score?.overall_score < 70 && !confirm("评分低于 70，仍要导出吗？")) return;
    const data = await run("导出", async () => {
      await saveNow();
      const docx = await call<ExportResult>(`/projects/${project.id}/export/docx`, { method: "POST", body: JSON.stringify({ include_review: true }) });
      const pdf = await call<ExportResult>(`/projects/${project.id}/export/pdf`, { method: "POST", body: JSON.stringify({ include_review: true }) });
      return [docx, pdf];
    });
    setExports(data);
  }

  async function loadComments() {
    if (!project || !active) return;
    const data = await call<Comment[]>(`/projects/${project.id}/sections/${active.section_key}/comments`);
    setComments(data);
  }

  async function addComment() {
    if (!project || !active || !commentText.trim()) return;
    await call(`/projects/${project.id}/sections/${active.section_key}/comment`, { method: "POST", body: JSON.stringify({ body: commentText }) });
    setCommentText("");
    await loadComments();
  }

  async function resolveComment(id: string) {
    if (!project) return;
    await call(`/projects/${project.id}/comments/${id}/resolve`, { method: "PATCH", body: JSON.stringify({ status: "resolved" }) });
    await loadComments();
  }

  function upsertBlock(key: string, heading: string, content: string) {
    const exists = blocks.findIndex((b) => b.section_key === key);
    if (exists >= 0) updateBlock(exists, content);
    else pushHistory([...blocks, { section_key: key, heading, block_type: "text", content, order_index: blocks.length }]);
  }

  function duplicateBlock() {
    pushHistory([...blocks.slice(0, activeIndex + 1), { ...active, id: undefined, heading: `${active.heading} 副本`, order_index: activeIndex + 1 }, ...blocks.slice(activeIndex + 1)].map((b, i) => ({ ...b, order_index: i })));
  }

  function moveActive(delta: number) {
    const target = activeIndex + delta;
    if (target < 0 || target >= blocks.length) return;
    const next = [...blocks];
    [next[activeIndex], next[target]] = [next[target], next[activeIndex]];
    pushHistory(next.map((b, i) => ({ ...b, order_index: i })));
    setActiveIndex(target);
  }

  useEffect(() => {
    if (!project) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => saveNow().catch(() => null), 5000);
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [blocks, project]);

  useEffect(() => { loadComments().catch(() => null); }, [activeIndex, project]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        saveNow().catch((err) => setError(String(err)));
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        document.getElementById("doc-search")?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  return (
    <main className="min-h-screen px-4 py-5 md:px-6">
      <div className="mx-auto grid max-w-[1600px] gap-4 xl:grid-cols-[330px_1fr_340px]">
        <aside className="space-y-4">
          <Card>
            <CardHeader><CardTitle>项目与财务假设</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="项目名称" />
              <Textarea value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="项目简介" />
              <Button onClick={createProject} disabled={Boolean(busy)} className="w-full">{busy === "创建项目" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}创建项目</Button>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries({ price: "售价", unit_cost: "单位成本", first_month_units: "首月销量", growth_rate: "增长率", startup_funds: "启动资金", fixed_costs: "固定成本", marketing_budget: "营销预算", employee_costs: "员工成本", forecast_months: "周期" }).map(([key, label]) => (
                  <label key={key} className="text-xs text-muted-foreground">{label}<Input type="number" value={assumptions[key]} onChange={(e) => setAssumptions({ ...assumptions, [key]: Number(e.target.value) })} /></label>
                ))}
              </div>
              <Button variant="secondary" onClick={saveAssumptions} disabled={!project || Boolean(busy)} className="w-full"><LineChart className="h-4 w-4" />保存假设并实时重算</Button>
              {assumptionWarnings.map((warning) => <p key={warning} className="text-xs text-red-700">{warning}</p>)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>文档导航</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <Input id="doc-search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="搜索文档 Cmd+K" />
              {visibleBlocks.map((block) => {
                const realIndex = blocks.findIndex((b) => b === block);
                return (
                  <button key={`${block.section_key}-${realIndex}`} onClick={() => setActiveIndex(realIndex)} className={`flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm ${activeIndex === realIndex ? "bg-primary text-primary-foreground" : "hover:bg-muted"}`}>
                    <span>{block.heading}</span>{block.content.trim() && <CheckCircle2 className="h-4 w-4" />}
                  </button>
                );
              })}
            </CardContent>
          </Card>
        </aside>

        <section className="space-y-4">
          {error && <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>{active?.heading}</CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setCollapsed({ ...collapsed, [active.section_key]: !collapsed[active.section_key] })}><ChevronUp className="h-4 w-4" /></Button>
                  <Button variant="outline" onClick={duplicateBlock}><Copy className="h-4 w-4" /></Button>
                  <Button variant="outline" onClick={() => moveActive(-1)}>上移</Button>
                  <Button variant="outline" onClick={() => moveActive(1)}>下移</Button>
                  <Button variant="outline" onClick={() => { if (history.length) { setFuture([blocks, ...future]); setBlocks(history[history.length - 1]); setHistory(history.slice(0, -1)); } }}><RotateCcw className="h-4 w-4" /></Button>
                  <Button variant="outline" onClick={() => { if (future.length) { setHistory([...history, blocks]); setBlocks(future[0]); setFuture(future.slice(1)); } }}><RotateCw className="h-4 w-4" /></Button>
                </div>
              </div>
            </CardHeader>
            {!collapsed[active.section_key] && <CardContent className="space-y-3"><Textarea className="min-h-[620px] leading-7" value={active?.content || ""} onChange={(e) => updateBlock(activeIndex, e.target.value)} /></CardContent>}
          </Card>

          {suggestion && <Card><CardHeader><CardTitle>AI 建议</CardTitle></CardHeader><CardContent className="space-y-3"><Textarea className="min-h-40" value={suggestion} onChange={(e) => setSuggestion(e.target.value)} /><Button onClick={() => updateBlock(activeIndex, suggestion)}>替换</Button><Button variant="secondary" onClick={() => updateBlock(activeIndex, `${active.content}\n\n${suggestion}`)}>追加</Button></CardContent></Card>}
        </section>

        <aside className="space-y-4">
          <Card>
            <CardHeader><CardTitle>协作与生成</CardTitle></CardHeader>
            <CardContent className="grid gap-2">
              <Action label="生成 Exa 研究" icon={Search} busy={busy === "生成 Exa 研究"} disabled={!project || Boolean(busy)} onClick={generateResearch} />
              <Action label="生成 SWOT/竞品" icon={BarChart3} busy={busy === "生成 SWOT/框架"} disabled={!project || Boolean(busy)} onClick={generateFrameworks} />
              <Action label="生成最终 BP" icon={FileText} busy={busy === "生成最终商业计划书"} disabled={!project || Boolean(busy)} onClick={generateFinalBP} />
              <Action label="运行动态评分" icon={FlaskConical} busy={busy === "运行评分"} disabled={!project || Boolean(busy)} onClick={review} />
              <Action label="导出 DOCX/PDF" icon={Download} busy={busy === "导出"} disabled={!project || Boolean(busy)} onClick={exportFiles} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>AI 编辑</CardTitle></CardHeader>
            <CardContent className="grid gap-2">
              {[
                ["polish", "AI润色", PenLine],
                ["expand", "AI扩写", Sparkles],
                ["shorten", "AI精简", FileText],
                ["challenge_cup_style", "挑战杯风格", BarChart3],
                ["internet_plus_style", "互联网+风格", LineChart],
                ["fix_language_mixing", "清洗中英混杂", Languages],
              ].map(([mode, label, Icon]: any) => <Action key={mode} label={label} icon={Icon} busy={busy === "AI 修改"} disabled={!project || Boolean(busy)} onClick={() => polish(mode)} />)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>评论线程</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <Textarea value={commentText} onChange={(e) => setCommentText(e.target.value)} placeholder="@队友 这里需要补数据" />
              <Button onClick={addComment} disabled={!project || !commentText.trim()}><MessageSquare className="h-4 w-4" />添加评论</Button>
              {comments.map((comment) => <div key={comment.id} className="rounded-md border border-border p-2 text-sm"><p>{comment.body}</p><p className="text-xs text-muted-foreground">{comment.status}</p>{comment.status === "open" && <Button variant="secondary" onClick={() => resolveComment(comment.id)}>Resolve</Button>}</div>)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>最终导出检查</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {checklist.map(([label, ok]) => <div key={String(label)} className="flex items-center gap-2 text-sm"><CheckCircle2 className={`h-4 w-4 ${ok ? "text-primary" : "text-muted-foreground"}`} />{label}</div>)}
              {score && <div className="rounded-md bg-muted p-3 text-sm">评分：<b>{score.overall_score}</b><div>{(score.deductions || []).slice(0, 4).map((d: any) => <p key={d.reason}>{d.reason} ({d.points})</p>)}</div></div>}
              {exports.map((item) => <a key={item.file_name} className="block rounded-md border border-border p-2 text-sm" href={`${API_BASE}${item.download_url}`} target="_blank">{item.file_name}</a>)}
            </CardContent>
          </Card>
        </aside>
      </div>
    </main>
  );
}

function Action({ label, icon: Icon, busy, disabled, onClick }: { label: string; icon: any; busy: boolean; disabled: boolean; onClick: () => void }) {
  return <Button variant="outline" className="justify-start" disabled={disabled} onClick={onClick}>{busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Icon className="h-4 w-4" />}{label}</Button>;
}
