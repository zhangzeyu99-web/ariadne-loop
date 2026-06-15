import json

import pytest

from loops_assistant import (
    build_loop,
    parse_agent_report,
    render_agent_packet,
    render_loop_writing_report,
    snapshot_from_issue,
    supervise_loop,
    validate_loop,
    write_loop,
)


def test_build_loop_creates_verifiable_ai_usable_loop():
    snapshot = {
        "title": "本地化工作台工程优化",
        "goal": "继续拆分 translation.py，并保持现有本地化行为不回归",
        "current_state": "已拆 workflow/main/provider/errors，下一步处理批次编排",
        "recent_progress": [
            "pytest 114 passed",
            "前端 build 通过",
            "禁外部机翻扫描无命中",
        ],
        "constraints": [
            "每轮只改一个小模块",
            "不引入 Google 翻译依赖",
        ],
        "verifiers": [
            "pytest",
            "ruff",
            "npm build",
            "禁外部机翻扫描",
        ],
        "external_effects": ["commit", "push"],
        "risk": "medium",
    }

    loop = build_loop(snapshot)
    errors = validate_loop(loop)

    assert errors == []
    assert loop["goal"] == snapshot["goal"]
    assert loop["context"]["source_title"] == snapshot["title"]
    assert len(loop["cycle"]) >= 4
    assert {step["id"] for step in loop["cycle"]} >= {
        "inspect",
        "act",
        "verify",
        "decide",
    }
    assert loop["verifiers"]
    assert any("pytest" in gate["instruction"] for gate in loop["verifiers"])
    assert loop["stop_rules"]
    assert loop["human_gates"]
    assert loop["budget"]["max_iterations"] >= 1


def test_validate_loop_rejects_prompt_only_plan():
    prompt_only_plan = {
        "version": "1.0",
        "name": "只写 Prompt",
        "goal": "让 AI 努力做好",
        "cycle": [{"id": "prompt", "instruction": "请认真完成"}],
        "verifiers": [],
        "stop_rules": [],
    }

    errors = validate_loop(prompt_only_plan)

    assert any("verifier" in error for error in errors)
    assert any("stop" in error for error in errors)
    assert any("rollback" in error for error in errors)


def test_render_agent_packet_contains_execution_contract_and_parseable_report():
    loop = build_loop(
        {
            "title": "OpenClaw 每日健康监控",
            "goal": "每天检查 Gateway、cron、备份和 doctor，只报告可操作异常",
            "current_state": "Gateway 自启动已修复，备份由 OpenClaw 自己执行",
            "verifiers": ["Gateway 端口", "cron ok", "backup verify", "doctor 无 error"],
            "constraints": ["SecretRefs 迁移单独开任务"],
        }
    )

    packet = render_agent_packet(loop)
    report = parse_agent_report(
        json.dumps(
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": ["doctor 无 error", "backup verify 通过"],
                "next_step": "整理异常摘要并决定是否停止",
            },
            ensure_ascii=False,
        )
    )

    assert "Return JSON only" in packet
    assert "action_id" in packet
    assert "passed_verifiers" in packet
    assert "failed_verifiers" in packet
    assert "Gateway 端口" in packet
    assert report["action_id"] == "verify"
    assert report["status"] == "continue"
    assert report["evidence"]


def test_build_loop_preserves_harness_and_agent_packet_renders_it():
    loop = build_loop(
        {
            "title": "Browser release loop",
            "goal": "Ship a static page only after visible browser checks pass",
            "current_state": "The builder exists, but release harness details are missing",
            "verifiers": ["desktop screenshot reviewed", "mobile screenshot reviewed"],
            "harness": {
                "tools": ["Browser", "pytest"],
                "official_sources": ["Python docs"],
                "browser_verification": ["check /playground.html at 390x844"],
                "forbidden_areas": ["do not edit GitHub Actions"],
                "local_secrets": "Do not read .env unless the user asks.",
                "source_priority": [
                    "official docs/API",
                    "repo/tests/current files",
                    "search",
                    "model inference",
                ],
                "cost_strategy": [
                    "strong model for hard repair",
                    "cheap model for formatting checks",
                ],
            },
        }
    )

    packet = render_agent_packet(loop)

    assert loop["harness"]["tools"] == ["Browser", "pytest"]
    assert "## Harness" in packet
    assert "Browser" in packet
    assert "official docs/API" in packet
    assert "Do not read .env" in packet


def test_generated_loop_has_persist_step_parts_and_cost_controls():
    loop = build_loop(
        {
            "title": "Morning triage",
            "goal": "Find one useful maintenance task and carry evidence across turns",
            "current_state": "The repo has prior reports and needs one bounded next action",
            "verifiers": ["pytest passes", "PROGRESS.md records the decision"],
        }
    )
    packet = render_agent_packet(loop)

    assert [step["id"] for step in loop["cycle"]] == [
        "inspect",
        "act",
        "verify",
        "persist",
        "decide",
    ]
    assert set(loop["loop_parts"]) >= {
        "automation",
        "isolation",
        "skills",
        "connectors",
        "evaluator",
        "memory",
    }
    assert set(loop["cost_controls"]) >= {
        "verification_debt",
        "comprehension_rot",
        "token_blowout",
        "cognitive_surrender",
    }
    assert "## Loop Parts" in packet
    assert "## Cost Controls" in packet
    assert "verification debt" in packet
    assert "persist" in packet


def test_write_loop_adds_clarity_review_and_design_patterns():
    draft = {
        "title": "当前线程",
        "goal": "继续增强 loops assistant，参考高星 prompt 和 harness 项目并发布",
        "current_state": "已有 make/check/report，下一步要把 Loop 写清楚",
        "constraints": ["先写测试", "不把建议停在文档"],
        "verifiers": ["pytest", "AI smoke", "GitHub 远端读回"],
        "external_effects": ["commit", "push"],
        "risk": "medium",
    }

    package = write_loop(draft)

    assert validate_loop(package["loop"]) == []
    assert package["clarity"]["score"] >= 80
    assert package["clarity"]["dimensions"]["verifier_strength"] == "strong"
    assert package["patterns"]["prompt"]["sections"] == [
        "role",
        "task",
        "context",
        "constraints",
        "output_contract",
    ]
    assert package["patterns"]["harness"]["requires"] == [
        "state",
        "tools",
        "memory",
        "checkpoints",
        "budget",
    ]
    assert package["patterns"]["eval"]["assertions"]
    assert "Return JSON only" in package["agent_packet"]


def test_snapshot_from_issue_extracts_markdown_sections():
    snapshot = snapshot_from_issue(
        "Fix report validation for empty verifier arrays",
        """
## Context
The report validator accepts reports that omit failed verifier ids.

## Constraints
- Do not change the JSON report field names.
- Keep backward-compatible CLI behavior.

## Acceptance Criteria
- [ ] Reports with missing failed_verifiers are normalized.
- [ ] Existing report command tests still pass.

## Open Questions
- Should empty verifier arrays be allowed?
""",
    )

    loop = build_loop(snapshot)

    assert snapshot["goal"] == "Fix report validation for empty verifier arrays"
    assert "validator accepts reports" in snapshot["current_state"]
    assert "Do not change the JSON report field names." in snapshot["constraints"]
    assert "Reports with missing failed_verifiers are normalized." in snapshot["verifiers"]
    assert "Should empty verifier arrays be allowed?" in snapshot["open_questions"]
    assert validate_loop(loop) == []


def test_render_loop_writing_report_surfaces_missing_inputs():
    package = write_loop(
        {
            "title": "粗略想法",
            "goal": "让 AI 帮我做完",
        }
    )

    report = render_loop_writing_report(package)

    assert "# Ariadne Loop Report" in report
    assert "Clarity Score" in report
    assert "Missing Inputs" in report
    assert "verifier" in report.lower()
    assert "Agent Packet" in report


def test_supervise_loop_starts_and_blocks_external_effects():
    loop = build_loop(
        {
            "title": "发布护航",
            "goal": "持续运行并发布结果",
            "current_state": "等待第一轮",
            "verifiers": ["pytest", "GitHub 远端读回"],
            "external_effects": ["push"],
            "risk": "medium",
        }
    )

    first_decision = supervise_loop(loop, [])
    push_decision = supervise_loop(
        loop,
        [
            {
                "action_id": "decide",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "push to GitHub",
                "passed_verifiers": ["gate-1"],
            }
        ],
    )

    assert first_decision["decision"] == "continue"
    assert first_decision["next_action_id"] == "inspect"
    assert push_decision["decision"] == "needs_human"
    assert any("external effect" in reason for reason in push_decision["reasons"])


def test_supervise_loop_stops_on_repeated_failed_verifier():
    loop = build_loop(
        {
            "title": "测试护航",
            "goal": "修复测试直到通过",
            "current_state": "pytest 失败",
            "verifiers": ["pytest", "AI smoke"],
        }
    )
    reports = [
        {
            "action_id": "verify",
            "status": "continue",
            "evidence": ["pytest failed: assertion error"],
            "next_step": "retry pytest",
            "failed_verifiers": ["gate-1"],
        },
        {
            "action_id": "verify",
            "status": "continue",
            "evidence": ["pytest failed: same assertion error"],
            "next_step": "retry pytest again",
            "failed_verifiers": ["gate-1"],
        },
    ]

    decision = supervise_loop(loop, reports)

    assert decision["decision"] == "rollback"
    assert decision["next_action_id"] == "inspect"
    assert "gate-1" in decision["reasons"][0]


def test_supervise_loop_routes_verify_to_persist_before_decide():
    loop = build_loop(
        {
            "title": "Partial verification",
            "goal": "Persist partial verifier evidence before deciding the next turn",
            "current_state": "One verifier has passed and another still needs evidence",
            "verifiers": ["pytest", "browser smoke"],
        }
    )

    decision = supervise_loop(
        loop,
        [
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "record evidence in PROGRESS.md",
                "passed_verifiers": ["gate-1"],
                "failed_verifiers": [],
            }
        ],
    )

    assert decision["decision"] == "continue"
    assert decision["next_action_id"] == "persist"


def test_supervise_loop_stops_when_all_verifiers_pass():
    loop = build_loop(
        {
            "title": "完成护航",
            "goal": "所有验证通过后停止",
            "current_state": "验证中",
            "verifiers": ["pytest", "AI smoke"],
        }
    )

    decision = supervise_loop(
        loop,
        [
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": ["pytest passed", "AI smoke valid"],
                "next_step": "summarize",
                "passed_verifiers": ["gate-1", "gate-2"],
            }
        ],
    )

    assert decision["decision"] == "stop"
    assert any("all verifiers passed" in reason for reason in decision["reasons"])
