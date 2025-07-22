"""Tests for CodebaseAnalysisTool registration and local helpers."""

from pathlib import Path

import analysis
from tools.codebase.analysis_tool import CodebaseAnalysisTool


class DummyMCP:
    """Minimal stub to capture tool registration."""

    def __init__(self):
        self.registered = {}

    def tool(self):
        def decorator(func):
            self.registered[func.__name__] = func
            return func
        return decorator


def test_codebase_tool_registration(tmp_path: Path):
    tool = CodebaseAnalysisTool(tmp_path)
    mcp = DummyMCP()
    tool.register(mcp)

    assert "codebase_parse_file" in mcp.registered
    assert "codebase_analyse_repo" in mcp.registered
    assert "codebase_query_hotspots" in mcp.registered

    # Sanity call parse helper directly
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n")
    res = tool._parse_file(str(sample))
    assert res["language"] == "python" 