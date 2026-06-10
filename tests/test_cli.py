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
