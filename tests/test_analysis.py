"""Unit tests for the `analysis` package (Phase 1 foundation)."""

import tempfile
from pathlib import Path

import pytest

import analysis


def _make_sample_file(tmp_path: Path) -> Path:
    """Create a Python file with known cyclomatic complexity in *tmp_path*."""
    code = """

def foo(x):
    if x > 0:
        return 1
    else:
        return -1


def bar(n):
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i
    return total
    """
    file_path = tmp_path / "sample.py"
    file_path.write_text(code)
    return file_path


class TestParsers:
    def test_parse_python_file(self, tmp_path: Path):
        sample = _make_sample_file(tmp_path)
        root = analysis.parse_file(sample)
        # Root should be a Module with children
        assert root.kind == "Module"
        assert len(root.children) > 0


class TestMetrics:
    def test_cyclomatic_complexity(self, tmp_path: Path):
        sample = _make_sample_file(tmp_path)
        root = analysis.parse_file(sample)
        complexity = analysis.cyclomatic_complexity(root)
        # Manual reasoning: Module baseline 1 + if + for + if  = 4
        assert complexity == 4


class TestEndToEnd:
    def test_analyse_repo_and_hotspots(self, tmp_path: Path):
        # Set up a tiny repo with two python files
        file1 = _make_sample_file(tmp_path)
        file2 = tmp_path / "empty.py"
        file2.write_text("pass\n")

        metrics = analysis.analyse_repo(tmp_path)
        # Expect two records (order not guaranteed)
        assert len(metrics) == 2
        paths = {m["path"] for m in metrics}
        assert str(file1) in paths and str(file2) in paths

        hotspots = analysis.query_hotspots(metrics, threshold=2)
        # Only sample.py crosses threshold (complexity 4)
        assert len(hotspots) == 1
        assert hotspots[0]["path"] == str(file1)


class TestPromptsFolder:
    def test_prompts_structure_exists(self):
        base = Path("analysis/prompts")
        assert base.exists()
        assert (base / "phase1_foundation.md").exists()
        tracker = base / "progress_tracker.json"
        assert tracker.exists()

        import json
        data = json.loads(tracker.read_text())
        assert data["phase1_foundation"]["status"] == "completed"
        assert "phase3_language_support" in data 