from app.ai.base import AIProviderError
from app.finance import ai_narrative


def _report():
    return {
        "summary_narrative": None,
        "judge_perspective": None,
        "issue_count": {"errors": 0, "warnings": 1, "suggestions": 0},
        "issues": [
            {
                "rule_id": "CF-003",
                "severity": "warning",
                "title": "Runway under 6 months",
                "description": "Runway is under 6 months.",
                "fix_suggestion": "Increase runway.",
                "affected_fields": ["forecast.summary.runway_months"],
            }
        ],
    }


def test_validation_works_when_openrouter_missing(monkeypatch):
    def fail_provider(_config):
        raise AIProviderError("missing key")

    monkeypatch.setattr(ai_narrative, "get_provider", fail_provider)

    report = ai_narrative.add_ai_narrative(
        _report(),
        project={"title": "Test", "idea_summary": "Idea", "competition_type": "challenge_cup"},
        forecast_summary={"runway_months": 4},
        business_model="saas",
    )

    assert report["overall_score"] == 90
    assert report["risk_level"] == "需关注"
    assert report["why_this_matters"]
    assert report["judge_perspective"]
    assert [issue["rule_id"] for issue in report["issues"]] == ["CF-003"]


def test_ai_prompt_only_receives_existing_validation_issues():
    report = _report()

    payload = ai_narrative.build_ai_payload(
        report=report,
        project={"title": "Test", "idea_summary": "Idea", "competition_type": "internet_plus"},
        forecast_summary={"runway_months": 4},
        business_model="saas",
    )

    assert [issue["rule_id"] for issue in payload["issues"]] == ["CF-003"]
    assert "strict_rules" in payload
    assert "Do not add new issues." in payload["strict_rules"]
    assert payload["competition_focus"] == "商业化路径、增长证据和落地能力"
    assert "why_this_matters" in payload["output_schema"]


def test_ai_result_cannot_add_new_issues():
    report = _report()

    updated = ai_narrative.apply_ai_result(
        report,
        {
            "summary_narrative": "The model has a short runway and needs a clearer cash plan.",
            "why_this_matters": "现金续航较短会影响项目持续验证能力。",
            "top_risks": ["现金续航不足"],
            "judge_perspective": "Judges will focus on whether the team can survive long enough to validate demand.",
            "next_actions": ["补充融资或降低早期支出。"],
            "issues": [
                {"rule_id": "CF-003", "fix_suggestion": "Add a realistic funding event or reduce early monthly burn."},
                {"rule_id": "REV-999", "fix_suggestion": "This should be ignored."},
            ],
        },
    )

    assert len(updated["issues"]) == 1
    assert updated["issues"][0]["rule_id"] == "CF-003"
    assert updated["issues"][0]["fix_suggestion"] == "Add a realistic funding event or reduce early monthly burn."
    assert updated["summary_narrative"]
    assert updated["why_this_matters"]
    assert updated["top_risks"] == ["现金续航不足"]
    assert updated["judge_perspective"]
    assert updated["next_actions"] == ["补充融资或降低早期支出。"]
