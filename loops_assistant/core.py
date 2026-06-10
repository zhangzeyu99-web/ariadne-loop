from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_REPORT_STATUSES = {"continue", "stop", "needs_human", "rollback"}
REQUIRED_STEP_IDS = {"inspect", "act", "verify", "decide"}


def load_snapshot(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".json":
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("snapshot JSON must be an object")
        return value
    return _snapshot_from_text(text, source.stem)


def build_loop(snapshot: dict[str, Any]) -> dict[str, Any]:
    title = _clean_text(snapshot.get("title")) or "未命名任务"
    goal = _clean_text(snapshot.get("goal")) or f"把 {title} 推进到可验证完成状态"
    current_state = _clean_text(snapshot.get("current_state") or snapshot.get("status"))
    recent_progress = _string_list(snapshot.get("recent_progress") or snapshot.get("evidence"))
    constraints = _string_list(snapshot.get("constraints"))
    external_effects = _string_list(snapshot.get("external_effects"))
    risk = (_clean_text(snapshot.get("risk")) or "low").lower()
    verifier_inputs = _string_list(snapshot.get("verifiers")) or _infer_verifiers(
        recent_progress, external_effects
    )

    loop = {
        "version": "1.0",
        "name": f"{title} Loop",
        "goal": goal,
        "context": {
            "source_title": title,
            "current_state": current_state or "未提供当前状态，先读取真实上下文再行动",
            "evidence": recent_progress,
            "constraints": constraints,
            "external_effects": external_effects,
            "risk": risk,
        },
        "state": {
            "status": "ready",
            "progress": recent_progress,
            "open_questions": _string_list(snapshot.get("open_questions")),
        },
        "cycle": _build_cycle(goal, verifier_inputs),
        "verifiers": [
            {
                "id": f"gate-{index}",
                "kind": _verifier_kind(verifier),
                "instruction": verifier,
                "proves": f"本轮结果满足：{verifier}",
            }
            for index, verifier in enumerate(verifier_inputs, start=1)
        ],
        "stop_rules": _build_stop_rules(external_effects),
        "rollback": {
            "trigger": "任一 verifier 失败、输出缺证据、或动作越过约束",
            "action": "撤销本轮产物或保持原状态，记录失败证据，回到 inspect 步骤重新收窄范围",
        },
        "memory": {
            "read": "每轮开始读取上一轮状态、失败原因、通过的 verifier 和用户确认项",
            "write": "每轮结束写入 action_id、证据、验证结果、停止判断和下一步",
        },
        "budget": _build_budget(risk),
        "human_gates": _build_human_gates(risk, external_effects),
        "agent_contract": {
            "output_format": "json",
            "required_fields": ["action_id", "status", "evidence", "next_step"],
            "allowed_statuses": sorted(ALLOWED_REPORT_STATUSES),
        },
    }
    return loop


def validate_loop(loop: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["version", "name", "goal", "context", "cycle", "verifiers"]:
        if field not in loop:
            errors.append(f"missing {field}")

    cycle = loop.get("cycle")
    if not isinstance(cycle, list) or not cycle:
        errors.append("missing cycle")
    else:
        step_ids = {str(step.get("id")) for step in cycle if isinstance(step, dict)}
        missing_steps = REQUIRED_STEP_IDS - step_ids
        if missing_steps:
            errors.append(f"cycle missing required steps: {', '.join(sorted(missing_steps))}")
        for step in cycle:
            if not isinstance(step, dict) or not step.get("instruction"):
                errors.append("cycle step missing instruction")
                break

    verifiers = loop.get("verifiers")
    if not isinstance(verifiers, list) or not verifiers:
        errors.append("missing verifier list")
    else:
        for verifier in verifiers:
            if not isinstance(verifier, dict) or not verifier.get("instruction"):
                errors.append("verifier missing instruction")
                break

    stop_rules = loop.get("stop_rules")
    if not isinstance(stop_rules, list) or not stop_rules:
        errors.append("missing stop rules")

    rollback = loop.get("rollback")
    if not isinstance(rollback, dict) or not rollback.get("action"):
        errors.append("missing rollback action")

    budget = loop.get("budget")
    if not isinstance(budget, dict) or int(budget.get("max_iterations", 0)) < 1:
        errors.append("budget must set max_iterations >= 1")

    agent_contract = loop.get("agent_contract")
    if not isinstance(agent_contract, dict):
        errors.append("missing agent contract")
    else:
        required_fields = set(agent_contract.get("required_fields", []))
        if {"action_id", "status", "evidence", "next_step"} - required_fields:
            errors.append("agent contract missing report fields")

    return errors


def render_agent_packet(loop: dict[str, Any]) -> str:
    errors = validate_loop(loop)
    if errors:
        raise ValueError("invalid loop: " + "; ".join(errors))

    action_lines = "\n".join(
        f"- `{step['id']}`: {step['instruction']} -> {step['expected_output']}"
        for step in loop["cycle"]
    )
    verifier_lines = "\n".join(
        f"- `{gate['id']}` ({gate['kind']}): {gate['instruction']}"
        for gate in loop["verifiers"]
    )
    stop_lines = "\n".join(f"- {rule}" for rule in loop["stop_rules"])
    human_lines = "\n".join(f"- {gate}" for gate in loop.get("human_gates", []))

    return f"""# {loop['name']} Agent Packet

## Goal
{loop['goal']}

## Current State
{loop['context']['current_state']}

## Constraints
{_markdown_list(loop['context'].get('constraints'))}

## Cycle
{action_lines}

## Verifiers
{verifier_lines}

## Stop Rules
{stop_lines}

## Rollback
{loop['rollback']['action']}

## Human Gates
{human_lines or "- No extra human gate beyond the stop rules."}

## Budget
- max_iterations: {loop['budget']['max_iterations']}
- max_minutes: {loop['budget']['max_minutes']}

## Report Contract
Return JSON only. Do not add prose outside the JSON.

```json
{{
  "action_id": "inspect|act|verify|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action"
}}
```
"""


def parse_agent_report(text: str) -> dict[str, Any]:
    payload = _extract_json_object(text)
    report = json.loads(payload)
    if not isinstance(report, dict):
        raise ValueError("agent report must be a JSON object")
    missing = {"action_id", "status", "evidence", "next_step"} - set(report)
    if missing:
        raise ValueError(f"agent report missing fields: {', '.join(sorted(missing))}")
    if report["status"] not in ALLOWED_REPORT_STATUSES:
        raise ValueError(f"invalid status: {report['status']}")
    if not isinstance(report["evidence"], list) or not report["evidence"]:
        raise ValueError("agent report evidence must be a non-empty list")
    return report


def _build_cycle(goal: str, verifier_inputs: list[str]) -> list[dict[str, str]]:
    verifier_summary = "；".join(verifier_inputs)
    return [
        {
            "id": "inspect",
            "instruction": "读取真实上下文、现有产物和上一轮状态，确认本轮只处理一个可验证目标",
            "expected_output": "本轮范围、已知证据、缺口和不做事项",
        },
        {
            "id": "act",
            "instruction": f"围绕目标执行最小必要动作：{goal}",
            "expected_output": "本轮产物或改动清单",
        },
        {
            "id": "verify",
            "instruction": f"运行或执行这些验证：{verifier_summary}",
            "expected_output": "逐项 verifier 的通过、失败或缺证据状态",
        },
        {
            "id": "decide",
            "instruction": "根据验证结果决定继续、停止、回滚或请求人工确认",
            "expected_output": "下一步动作和停止判断",
        },
    ]


def _build_stop_rules(external_effects: list[str]) -> list[str]:
    rules = [
        "所有 verifier 都有当前证据且通过时停止",
        "同一 verifier 连续失败 2 次时停止并收窄问题",
        "发现目标、输入或权限与当前上下文不一致时停止并请求确认",
    ]
    if external_effects:
        joined = "、".join(external_effects)
        rules.append(f"执行外部影响动作前停止并确认：{joined}")
    return rules


def _build_human_gates(risk: str, external_effects: list[str]) -> list[str]:
    gates = ["需要改变外部状态、发布、发送、删除或付款前必须人工确认"]
    if risk in {"medium", "high", "critical"}:
        gates.append(f"风险等级为 {risk}，失败后不可直接扩大范围")
    if external_effects:
        gates.append("外部影响动作完成后必须读回真实载体再报告")
    return gates


def _build_budget(risk: str) -> dict[str, int]:
    if risk in {"high", "critical"}:
        return {"max_iterations": 2, "max_minutes": 30}
    if risk == "medium":
        return {"max_iterations": 3, "max_minutes": 60}
    return {"max_iterations": 4, "max_minutes": 90}


def _infer_verifiers(recent_progress: list[str], external_effects: list[str]) -> list[str]:
    inferred = [item for item in recent_progress if _looks_like_verifier(item)]
    if external_effects:
        inferred.append("外部载体读回验证")
    if not inferred:
        inferred.append("读回真实产物并核对目标、关键字段和约束")
    return list(dict.fromkeys(inferred))


def _verifier_kind(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["pytest", "ruff", "build", "test", "npm"]):
        return "command"
    if any(token in text for token in ["读回", "端口", "扫描", "verify", "doctor"]):
        return "readback"
    return "checklist"


def _looks_like_verifier(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in ["passed", "pytest", "ruff", "build", "verify", "扫描", "读回", "qa"]
    )


def _snapshot_from_text(text: str, fallback_title: str) -> dict[str, Any]:
    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    title = lines[0].lstrip("# ").strip() if lines else fallback_title
    goal = _find_prefixed(lines, ["goal", "目标"]) or title
    current_state = _find_prefixed(lines, ["state", "status", "当前状态", "进度"])
    constraints = [
        line
        for line in lines
        if any(token in line for token in ["不要", "不能", "必须", "只", "停止", "确认"])
    ]
    verifiers = [
        line
        for line in lines
        if _looks_like_verifier(line)
        or any(token in line for token in ["验证", "测试", "读回", "检查"])
    ]
    return {
        "title": title,
        "goal": goal,
        "current_state": current_state,
        "constraints": constraints,
        "verifiers": verifiers,
        "recent_progress": lines[1:],
    }


def _find_prefixed(lines: list[str], prefixes: list[str]) -> str:
    for line in lines:
        normalized = line.lower()
        for prefix in prefixes:
            if normalized.startswith(prefix.lower()):
                return line.split(":", 1)[-1].split("：", 1)[-1].strip()
    return ""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _markdown_list(values: Any) -> str:
    items = _string_list(values)
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{"):
        return stripped
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    raise ValueError("agent report must contain a JSON object")

