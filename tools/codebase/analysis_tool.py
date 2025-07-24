"""Codebase Analysis Tool

MCP wrapper exposing static analysis helpers under the `codebase_*` prefix.
Only lightweight operations are provided for now.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import analysis

from ...common.base_tool import BaseTool

logger = logging.getLogger(__name__)


class CodebaseAnalysisTool(BaseTool):
    """Expose analysis helpers as MCP Tools with `codebase_` prefix."""

    @property
    def name(self) -> str:
        return "codebase_analysis"

    @property
    def description(self) -> str:
        return "Static code analysis utilities (powered by analysis package)"

    def get_capabilities(self) -> List[str]:
        return [
            "codebase_parse_file",
            "codebase_analyse_repo",
            "codebase_query_hotspots",
        ]

    # ---------------------------------------------------------------------
    # Registration helpers
    # ---------------------------------------------------------------------

    def _parse_file(self, path: str):
        root = analysis.parse_file(path)
        return {
            "kind": root.kind,
            "name": root.name,
            "language": root.language,
            "cyclomatic_complexity": analysis.cyclomatic_complexity(root),
            "start_line": root.start_line,
            "end_line": root.end_line,
        }

    def _analyse_repo(self, directory: str):
        metrics = analysis.analyse_repo(directory)
        return metrics

    def _query_hotspots(self, directory: str, threshold: int = 10):
        metrics = analysis.analyse_repo(directory)
        return analysis.query_hotspots(metrics, threshold)

    # ------------------------------------------------------------------
    # MCP registration
    # ------------------------------------------------------------------

    def register(self, mcp):
        @mcp.tool(
            name="codebase_parse_file",
            description="Parse a single source file and return basic metrics including complexity, lines of code, and structure analysis",
            tags={"codebase", "analysis", "file", "metrics", "parsing"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def codebase_parse_file(path: str, ctx: object = None) -> dict:  # noqa: D401
            """Parse a single source file and return basic metrics."""
            try:
                return self._parse_file(path)
            except Exception as e:  # pragma: no cover
                logger.error("codebase_parse_file error: %s", e)
                return {"error": str(e)}

        @mcp.tool(
            name="codebase_analyse_repo",
            description="Analyse all supported files inside a directory recursively to provide comprehensive codebase metrics and insights",
            tags={"codebase", "analysis", "repository", "comprehensive", "recursive"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def codebase_analyse_repo(directory: str, ctx: object = None) -> list:  # noqa: D401
            """Analyse all supported files inside *directory* recursively."""
            try:
                return self._analyse_repo(directory)
            except Exception as e:  # pragma: no cover
                logger.error("codebase_analyse_repo error: %s", e)
                return [{"error": str(e)}]

        @mcp.tool(
            name="codebase_query_hotspots",
            description="Return high-complexity hotspots within a directory that may need refactoring or special attention",
            tags={"codebase", "analysis", "hotspots", "complexity", "refactoring"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def codebase_query_hotspots(directory: str, threshold: int = 10, ctx: object = None) -> list:  # noqa: D401
            """Return high-complexity hotspots within *directory*."""
            try:
                return self._query_hotspots(directory, threshold)
            except Exception as e:  # pragma: no cover
                logger.error("codebase_query_hotspots error: %s", e)
                return [{"error": str(e)}] 