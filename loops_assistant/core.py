from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_REPORT_STATUSES = {"continue", "stop", "needs_human", "rollback"}
REQUIRED_STEP_IDS = {"inspect", "act", "verify", "decide"}
EXTERNAL_EFFECT_WORDS = {
    "commit",
    "push",
    "publish",
    "release",
    "deploy",
    "send",
    "delete",
    "payment",
    "付款",
    "删除",
    "发送",
    "发布",
    "推送",
}


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
    title = _clean_text(snapshot.get("title")) or "Untitled task"
    goal = _clean_text(snapshot.get("goal")) or f"Move {title} to a verifiably complete state"
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
            "current_state": current_state or "No current state was provided. Inspect real context before acting.",
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
                "proves": f"This turn satisfies: {verifier}",
            }
            for index, verifier in enumerate(verifier_inputs, start=1)
        ],
        "stop_rules": _build_stop_rules(external_effects),
        "rollback": {
            "trigger": "Any verifier fails, evidence is missing, or an action crosses a constraint",
            "action": "Revert this turn's output or keep the prior state, record the failing evidence, then return to inspect with a narrower scope.",
        },
        "memory": {
            "read": "At the start of each turn, read prior state, failures, passed verifiers, and human approvals.",
            "write": "At the end of each turn, write action_id, evidence, verifier results, stop decision, and next step.",
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
  "next_step": "the next concrete action",
  "passed_verifiers": ["gate ids that passed in this turn"],
  "failed_verifiers": ["gate ids that failed in this turn"]
}}
```
"""


def write_loop(snapshot: dict[str, Any]) -> dict[str, Any]:
    loop = build_loop(snapshot)
    clarity = _score_loop_clarity(loop, snapshot)
    return {
        "loop": loop,
        "clarity": clarity,
        "patterns": _design_patterns(loop),
        "tightened_brief": _tightened_brief(loop),
        "agent_packet": render_agent_packet(loop),
    }


def render_loop_writing_report(package: dict[str, Any]) -> str:
    loop = package["loop"]
    clarity = package["clarity"]
    prompt = package["patterns"]["prompt"]
    harness = package["patterns"]["harness"]
    eval_pattern = package["patterns"]["eval"]

    missing = clarity.get("missing_inputs", [])
    missing_lines = _markdown_list(missing) if missing else "- None"
    dimension_lines = "\n".join(
        f"- {name}: {value}" for name, value in clarity["dimensions"].items()
    )
    assertions = "\n".join(f"- {item}" for item in eval_pattern["assertions"])

    return f"""# Ariadne Loop Report

## Clear Loop
- Name: {loop['name']}
- Goal: {loop['goal']}
- Current State: {loop['context']['current_state']}
- Tightened Brief: {package['tightened_brief']}

## Clarity Score
- Score: {clarity['score']}/100
{dimension_lines}

## Missing Inputs
{missing_lines}

## Borrowed Structures
- Prompt pattern: {', '.join(prompt['sections'])}
- Harness pattern: {', '.join(harness['requires'])}
- Eval pattern:
{assertions}

## Agent Packet
{package['agent_packet']}
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


def supervise_loop(
    loop: dict[str, Any], reports: list[dict[str, Any]]
) -> dict[str, Any]:
    errors = validate_loop(loop)
    if errors:
        return {
            "decision": "needs_human",
            "next_action_id": "inspect",
            "reasons": ["invalid loop: " + "; ".join(errors)],
            "iteration": len(reports),
        }

    if not reports:
        return {
            "decision": "continue",
            "next_action_id": "inspect",
            "reasons": ["no reports yet; start with inspect"],
            "iteration": 0,
            "covered_verifiers": [],
            "failed_verifiers": [],
        }

    normalized_reports = [_normalize_report(report) for report in reports]
    latest = normalized_reports[-1]
    iteration = len(normalized_reports)
    covered = _unique_items(
        item for report in normalized_reports for item in report["passed_verifiers"]
    )
    failed = _unique_items(
        item for report in normalized_reports for item in report["failed_verifiers"]
    )

    latest_status = latest["status"]
    if latest_status in {"stop", "needs_human", "rollback"}:
        return {
            "decision": latest_status,
            "next_action_id": "decide" if latest_status == "needs_human" else "inspect",
            "reasons": [f"agent reported {latest_status}"],
            "iteration": iteration,
            "covered_verifiers": covered,
            "failed_verifiers": failed,
        }

    repeated_failure = _first_repeated_failure(normalized_reports, threshold=2)
    if repeated_failure:
        return {
            "decision": "rollback",
            "next_action_id": "inspect",
            "reasons": [
                f"{repeated_failure} failed in two consecutive reports; rollback and narrow scope"
            ],
            "iteration": iteration,
            "covered_verifiers": covered,
            "failed_verifiers": failed,
        }

    if _has_external_effect_request(loop, latest["next_step"]):
        return {
            "decision": "needs_human",
            "next_action_id": "decide",
            "reasons": ["external effect requested; human confirmation required"],
            "iteration": iteration,
            "covered_verifiers": covered,
            "failed_verifiers": failed,
        }

    max_iterations = int(loop.get("budget", {}).get("max_iterations", 0))
    if max_iterations and iteration >= max_iterations:
        return {
            "decision": "stop",
            "next_action_id": "decide",
            "reasons": [f"budget exhausted at {iteration} iterations"],
            "iteration": iteration,
            "covered_verifiers": covered,
            "failed_verifiers": failed,
        }

    verifier_ids = [gate["id"] for gate in loop.get("verifiers", [])]
    if verifier_ids and set(verifier_ids).issubset(set(covered)):
        return {
            "decision": "stop",
            "next_action_id": "decide",
            "reasons": ["all verifiers passed"],
            "iteration": iteration,
            "covered_verifiers": covered,
            "failed_verifiers": failed,
        }

    reasons = []
    if _evidence_is_weak(latest["evidence"]):
        reasons.append("latest report evidence is weak; require concrete readback evidence")

    return {
        "decision": "continue",
        "next_action_id": _next_action_id(latest["action_id"]),
        "reasons": reasons or ["guardrails clear for next iteration"],
        "iteration": iteration,
        "covered_verifiers": covered,
        "failed_verifiers": failed,
    }


def _score_loop_clarity(
    loop: dict[str, Any], original_snapshot: dict[str, Any]
) -> dict[str, Any]:
    missing: list[str] = []
    score = 100

    goal = _clean_text(original_snapshot.get("goal"))
    current_state = _clean_text(
        original_snapshot.get("current_state") or original_snapshot.get("status")
    )
    constraints = _string_list(original_snapshot.get("constraints"))
    verifiers = _string_list(original_snapshot.get("verifiers"))
    external_effects = _string_list(original_snapshot.get("external_effects"))

    goal_specificity = "strong"
    if not goal or goal.lower() in {"let ai finish it", "do it well", "continue"} or goal in {"让 AI 帮我做完", "做好", "继续推进"} or len(goal) < 12:
        goal_specificity = "weak"
        score -= 20
        missing.append("goal: specify the final state, target object, and completion standard")

    state_grounding = "strong"
    if not current_state:
        state_grounding = "weak"
        score -= 15
        missing.append("current_state: add current progress, existing artifacts, and unresolved gaps")

    verifier_strength = "strong"
    if not verifiers:
        verifier_strength = "weak"
        score -= 25
        missing.append("verifier: add at least one verifier that produces observable evidence")

    constraint_quality = "strong"
    if not constraints:
        constraint_quality = "weak"
        score -= 10
        missing.append("constraints: state non-goals, permission boundaries, and risky actions")

    stop_safety = "strong" if loop.get("stop_rules") and loop.get("rollback") else "weak"
    if stop_safety == "weak":
        score -= 20
        missing.append("stop_rules: define when to stop, rollback, or ask for confirmation")

    ai_contract = "strong" if loop.get("agent_contract") else "weak"
    if ai_contract == "weak":
        score -= 10
        missing.append("agent_contract: require structured agent reports")

    if external_effects and not loop.get("human_gates"):
        score -= 10
        missing.append("human_gate: require confirmation before external-impact actions")

    return {
        "score": max(0, score),
        "dimensions": {
            "goal_specificity": goal_specificity,
            "state_grounding": state_grounding,
            "verifier_strength": verifier_strength,
            "constraint_quality": constraint_quality,
            "stop_safety": stop_safety,
            "ai_contract": ai_contract,
        },
        "missing_inputs": missing,
    }


def _normalize_report(report: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(report)
    normalized["passed_verifiers"] = _string_list(normalized.get("passed_verifiers"))
    normalized["failed_verifiers"] = _string_list(normalized.get("failed_verifiers"))
    normalized["evidence"] = _string_list(normalized.get("evidence"))
    normalized["next_step"] = _clean_text(normalized.get("next_step"))
    normalized["action_id"] = _clean_text(normalized.get("action_id")) or "inspect"
    normalized["status"] = _clean_text(normalized.get("status")) or "continue"
    return normalized


def _first_repeated_failure(reports: list[dict[str, Any]], threshold: int) -> str:
    if len(reports) < threshold:
        return ""
    recent = reports[-threshold:]
    common = set(recent[0]["failed_verifiers"])
    for report in recent[1:]:
        common &= set(report["failed_verifiers"])
    return sorted(common)[0] if common else ""


def _has_external_effect_request(loop: dict[str, Any], next_step: str) -> bool:
    lowered = next_step.lower()
    configured = [
        str(item).lower()
        for item in loop.get("context", {}).get("external_effects", [])
    ]
    words = set(configured) | EXTERNAL_EFFECT_WORDS
    return any(word and word in lowered for word in words)


def _evidence_is_weak(evidence: list[str]) -> bool:
    if not evidence:
        return True
    weak_terms = {"done", "ok", "looks good", "完成", "好了", "通过"}
    return all(item.strip().lower() in weak_terms for item in evidence)


def _next_action_id(action_id: str) -> str:
    order = ["inspect", "act", "verify", "decide"]
    if action_id not in order:
        return "inspect"
    return order[(order.index(action_id) + 1) % len(order)]


def _unique_items(values: Any) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            output.append(text)
            seen.add(text)
    return output


def _design_patterns(loop: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt": {
            "source": "high-star prompt libraries",
            "sections": [
                "role",
                "task",
                "context",
                "constraints",
                "output_contract",
            ],
            "instruction": "Write the loop as an executable task contract, not a wish.",
        },
        "harness": {
            "source": "agent harness projects",
            "requires": ["state", "tools", "memory", "checkpoints", "budget"],
            "instruction": "Put context, tools, state, budget, and checkpoints into the execution environment.",
        },
        "eval": {
            "source": "LLM eval harnesses",
            "assertions": [
                "loop has inspect/act/verify/decide cycle",
                "each verifier has observable evidence",
                "stop and rollback are explicit",
                "agent report is machine-checkable JSON",
            ],
        },
    }


def _tightened_brief(loop: dict[str, Any]) -> str:
    return (
        f"Run a stateful loop around \"{loop['goal']}\": inspect real context, "
        "take the smallest useful action, verify each gate, then stop, continue, "
        "rollback, or ask for human confirmation before changing external state."
    )


def _build_cycle(goal: str, verifier_inputs: list[str]) -> list[dict[str, str]]:
    verifier_summary = "；".join(verifier_inputs)
    return [
        {
            "id": "inspect",
            "instruction": "Read real context, existing artifacts, and previous state. Confirm this turn has one verifiable target.",
            "expected_output": "Turn scope, known evidence, gaps, and explicit non-goals",
        },
        {
            "id": "act",
            "instruction": f"Take the smallest useful action toward the goal: {goal}",
            "expected_output": "This turn's artifact or change list",
        },
        {
            "id": "verify",
            "instruction": f"Run or perform these verifiers: {verifier_summary}",
            "expected_output": "Pass, fail, or missing-evidence status for each verifier",
        },
        {
            "id": "decide",
            "instruction": "Decide whether to continue, stop, rollback, or ask for human confirmation based on verifier results.",
            "expected_output": "Next action and stop decision",
        },
    ]


def _build_stop_rules(external_effects: list[str]) -> list[str]:
    rules = [
        "Stop when every verifier has current evidence and passes.",
        "Stop and narrow the problem after the same verifier fails twice.",
        "Stop and ask for confirmation when the goal, input, or permissions do not match the current context.",
    ]
    if external_effects:
        joined = "、".join(external_effects)
        rules.append(f"Ask for confirmation before external-impact actions: {joined}")
    return rules


def _build_human_gates(risk: str, external_effects: list[str]) -> list[str]:
    gates = ["Ask for human confirmation before changing external state, publishing, sending, deleting, or paying."]
    if risk in {"medium", "high", "critical"}:
        gates.append(f"Risk is {risk}; do not expand scope after failure.")
    if external_effects:
        gates.append("After an external-impact action, read back the real target before reporting success.")
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
        inferred.append("Read back the external target and verify the effect")
    if not inferred:
        inferred.append("Read back the real artifact and verify the goal, key fields, and constraints")
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
