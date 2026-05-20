from pathlib import Path


def validate_export(context: dict) -> dict:
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []
    sections = context.get("business_plan_sections") or []
    exports = context.get("exports") or []

    empty = [section.get("heading") or section.get("key") for section in sections if not (section.get("content") or "").strip()]
    if empty:
        critical.append("导出内容存在空章节")
        suggestions.append("重新生成业务计划，补齐空章节后再导出。")
    if not exports:
        warnings.append("尚未发现已生成的 PDF/DOCX 导出文件。")
    elif not {Path(item.get("file_name", "")).suffix for item in exports}.intersection({".pdf", ".docx"}):
        warnings.append("导出文件格式不完整。")

    score = 100 - len(warnings) * 8 - len(critical) * 25
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
