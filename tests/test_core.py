import json

import pytest

from loops_assistant import (
    build_loop,
    parse_agent_report,
    render_agent_packet,
    validate_loop,
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
    assert "Gateway 端口" in packet
    assert report["action_id"] == "verify"
    assert report["status"] == "continue"
    assert report["evidence"]

