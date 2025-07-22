"""analysis package
Static code analysis utilities for the Emily.Tools project.

This first milestone focuses on Python source files. It provides:
1. A language-agnostic `UniversalNode` tree representation.
2. Parsers that convert concrete syntax to UniversalNode trees.
3. Basic metric extractors (currently cyclomatic complexity).
4. Convenience helpers (`analyse_repo`, `query_hotspots`) that higher-level
   AI components can call programmatically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from dataclasses import dataclass, field

# Re-export key helpers so `import analysis` feels ergonomic

__all__ = [
    "UniversalNode",
    "parse_file",
    "cyclomatic_complexity",
    "analyse_repo",
    "query_hotspots",
]


@dataclass
class UniversalNode:
    """Language-agnostic AST node used by analysis routines."""

    kind: str
    name: str | None
    start_line: int
    end_line: int
    language: str
    children: List["UniversalNode"] = field(default_factory=list)

    # Utility helpers -----------------------------------------------------
    def walk(self):
        """Depth-first traversal yielding *self* and all descendants."""
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def add_child(self, child: "UniversalNode") -> None:
        self.children.append(child)


# ---------------------------------------------------------------------------
# Imports (std-lib & optional deps)
# ---------------------------------------------------------------------------

import ast
# Optional import – analysis still works without tree-sitter so test suite passes
try:
    from tree_sitter import Language, Parser  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – optional dep
    Language = Parser = None  # type: ignore


_CONTROL_FLOW_NODES: tuple[type[ast.AST], ...] = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.BoolOp,
)


def _convert_ast(node: ast.AST) -> UniversalNode:
    """Convert a CPython `ast.AST` node into a `UniversalNode`."""

    # Determine human-friendly name & kind
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        kind = "Function"
        name = node.name
    elif isinstance(node, ast.ClassDef):
        kind = "Class"
        name = node.name
    elif isinstance(node, ast.Module):
        kind = "Module"
        name = None
    else:
        kind = node.__class__.__name__
        name = getattr(node, "name", None)

    # Fallback for missing position info (e.g. generated nodes)
    start_line = getattr(node, "lineno", 0)
    end_line = getattr(node, "end_lineno", start_line)

    universal = UniversalNode(
        kind=kind,
        name=name,
        start_line=start_line,
        end_line=end_line,
        language="python",
    )

    for child in ast.iter_child_nodes(node):
        universal.add_child(_convert_ast(child))

    return universal


def _parse_python_file(path: Path) -> UniversalNode:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    return _convert_ast(tree)


def parse_file(path: str | Path) -> UniversalNode:
    """Parse *path* into a `UniversalNode` tree.

    Currently supports only Python files. Other languages will be added in
    future milestones via Tree-sitter adapters.
    """
    path = Path(path)
    if path.suffix != ".py":
        raise ValueError(f"Unsupported file type: {path.suffix}. Only .py is supported for now.")
    return _parse_python_file(path)

    # ------------------------------------------------------------------
    # Experimental Tree-sitter branch for multi-language support
    # ------------------------------------------------------------------

    if Parser is None:
        raise RuntimeError(
            "tree_sitter package is not installed. Install via `pip install tree_sitter` "
            "to enable multi-language parsing."
        )

    # Lazy static registry of compiled languages
    global _TS_LANGUAGES  # type: ignore  # noqa: SLF001
    if "_TS_LANGUAGES" not in globals():
        _TS_LANGUAGES = {}

    def _ensure_language(lang_name: str, repo: str, so_name: str):
        if lang_name in _TS_LANGUAGES:
            return _TS_LANGUAGES[lang_name]

        build_dir = Path(__file__).parent / "_ts_build"
        build_dir.mkdir(exist_ok=True)
        so_path = build_dir / so_name
        if not so_path.exists():
            try:
                Language.build_library(
                    str(so_path),
                    [repo],
                )
            except Exception as e:  # pragma: no cover
                raise RuntimeError(f"Failed to build tree-sitter grammar for {lang_name}: {e}")

        _TS_LANGUAGES[lang_name] = Language(str(so_path), lang_name)
        return _TS_LANGUAGES[lang_name]

    suffix_map = {
        ".swift": ("swift", "tree-sitter-swift"),
        ".kt": ("kotlin", "tree-sitter-kotlin"),
        ".kts": ("kotlin", "tree-sitter-kotlin"),
    }

    if path.suffix.lower() in suffix_map:
        lang_name, repo_slug = suffix_map[path.suffix.lower()]
        language = _ensure_language(lang_name, repo_slug, f"{lang_name}.so")
        parser = Parser()
        parser.set_language(language)

        source_bytes = path.read_bytes()
        tree = parser.parse(source_bytes)

        # Very thin conversion: just return Module-level node
        return UniversalNode(
            kind="Module",
            name=path.name,
            start_line=1,
            end_line=len(source_bytes.splitlines()),
            language=lang_name,
            children=[],
        )

    raise ValueError(
        "Unsupported file type. Supported: .py (built-in) plus .swift/.kt with tree-sitter installed."
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def cyclomatic_complexity(node: UniversalNode) -> int:
    """Calculate cyclomatic complexity for *node* (and its descendants).

    The implementation is a simplified formula: start with 1 and add 1 for
    every control-flow node encountered in the Python AST.
    """
    complexity = 1
    for descendant in node.walk():
        if descendant.kind in {
            "If",
            "For",
            "AsyncFor",
            "While",
            "With",
            "AsyncWith",
            "Try",
            "BoolOp",
        }:
            complexity += 1
    return complexity


# ---------------------------------------------------------------------------
# Public helper APIs
# ---------------------------------------------------------------------------

def analyse_repo(repo_path: str | Path) -> List[Dict[str, int]]:
    """Analyse every Python file in *repo_path* and return metric records.

    Records are dictionaries with keys: `path`, `cyclomatic_complexity`.
    """
    repo_path = Path(repo_path)
    results: List[Dict[str, int]] = []
    for file in repo_path.rglob("*.py"):
        try:
            root = parse_file(file)
            complexity = cyclomatic_complexity(root)
            results.append({"path": str(file), "cyclomatic_complexity": complexity})
        except Exception:
            # Skip problematic files rather than failing the whole analysis run.
            continue
    return results


def query_hotspots(metrics: List[Dict[str, int]], threshold: int = 10) -> List[Dict[str, int]]:
    """Return subset of *metrics* whose cyclomatic complexity ≥ *threshold*.
    The list is sorted in descending order of complexity.
    """
    hotspots = [m for m in metrics if m["cyclomatic_complexity"] >= threshold]
    return sorted(hotspots, key=lambda m: m["cyclomatic_complexity"], reverse=True) 