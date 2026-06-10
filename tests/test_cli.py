import json
import subprocess
import sys


def test_cli_generates_json_and_markdown_packets(tmp_path):
    input_path = tmp_path / "thread.json"
    json_output = tmp_path / "loop.json"
    markdown_output = tmp_path / "agent.md"
    input_path.write_text(
        json.dumps(
            {
                "title": "术语提取",
                "goal": "从语言包和公告里提取有证据的术语",
                "current_state": "脚本本地提取后由 Codex 补充检查",
                "recent_progress": ["候选 packet 已生成"],
                "constraints": ["无证据项不写入主表"],
                "verifiers": ["每个新增术语可回溯到来源"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    json_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "make",
            "--input",
            str(input_path),
            "--output",
            str(json_output),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    markdown_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "make",
            "--input",
            str(input_path),
            "--output",
            str(markdown_output),
            "--format",
            "markdown",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert json_result.returncode == 0, json_result.stderr
    assert markdown_result.returncode == 0, markdown_result.stderr

    loop = json.loads(json_output.read_text(encoding="utf-8"))
    packet = markdown_output.read_text(encoding="utf-8")

    assert loop["name"] == "术语提取 Loop"
    assert loop["verifiers"]
    assert "Return JSON only" in packet
    assert "无证据项不写入主表" in packet


def test_cli_check_rejects_invalid_loop(tmp_path):
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(
        json.dumps({"version": "1.0", "goal": "缺少闭环"}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "check",
            "--input",
            str(invalid_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "verifier" in result.stderr


def test_cli_report_validates_agent_json_report(tmp_path):
    report_path = tmp_path / "agent-report.md"
    report_path.write_text(
        """```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": ["gate-1 passed"],
  "next_step": "run decide"
}
```""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "report",
            "--input",
            str(report_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "valid" in result.stdout


def test_cli_write_outputs_human_readable_loop_report(tmp_path):
    input_path = tmp_path / "rough.json"
    output_path = tmp_path / "loop-report.md"
    input_path.write_text(
        json.dumps(
            {
                "title": "当前线程",
                "goal": "继续增强 loops assistant，参考高星项目并发布",
                "current_state": "已有 make/check/report",
                "constraints": ["先写测试", "不只输出建议"],
                "verifiers": ["pytest", "AI smoke", "GitHub 远端读回"],
                "external_effects": ["commit", "push"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "write",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--format",
            "markdown",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = output_path.read_text(encoding="utf-8")
    assert "# Loop Writing Assistant" in report
    assert "当前线程 Loop" in report
    assert "Clarity Score" in report
    assert "Agent Packet" in report


def test_cli_supervise_outputs_guardrail_decision(tmp_path):
    loop_path = tmp_path / "loop.json"
    reports_path = tmp_path / "reports.jsonl"
    output_path = tmp_path / "decision.json"
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "title": "发布护航",
                "goal": "持续运行并发布结果",
                "current_state": "等待验证",
                "verifiers": ["pytest", "GitHub 远端读回"],
                "external_effects": ["push"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "make",
            "--input",
            str(snapshot_path),
            "--output",
            str(loop_path),
            "--format",
            "json",
        ],
        check=True,
    )
    reports_path.write_text(
        json.dumps(
            {
                "action_id": "decide",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "push to GitHub",
                "passed_verifiers": ["gate-1"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "supervise",
            "--loop",
            str(loop_path),
            "--reports",
            str(reports_path),
            "--output",
            str(output_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(output_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "needs_human"
    assert decision["next_action_id"] == "decide"


def test_cli_supervise_accepts_utf8_bom_jsonl(tmp_path):
    loop_path = tmp_path / "loop.json"
    reports_path = tmp_path / "reports.jsonl"
    output_path = tmp_path / "decision.json"
    loop_path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "name": "BOM Loop",
                "goal": "Handle Windows logs",
                "context": {"external_effects": []},
                "cycle": [
                    {"id": "inspect", "instruction": "inspect"},
                    {"id": "act", "instruction": "act"},
                    {"id": "verify", "instruction": "verify"},
                    {"id": "decide", "instruction": "decide"},
                ],
                "verifiers": [{"id": "gate-1", "instruction": "pytest"}],
                "stop_rules": ["stop when done"],
                "rollback": {"action": "rollback"},
                "budget": {"max_iterations": 3},
                "agent_contract": {
                    "required_fields": [
                        "action_id",
                        "status",
                        "evidence",
                        "next_step",
                    ]
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    reports_path.write_bytes(
        b"\xef\xbb\xbf"
        + json.dumps(
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "decide",
                "passed_verifiers": ["gate-1"],
                "failed_verifiers": [],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "supervise",
            "--loop",
            str(loop_path),
            "--reports",
            str(reports_path),
            "--output",
            str(output_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(output_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "stop"
