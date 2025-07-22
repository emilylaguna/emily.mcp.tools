# Phase 1 – Foundation

Goal: Set up the minimal viable *analysis* infrastructure.

## Acceptance Criteria
1. Universal AST (`UniversalNode`) dataclass exists.
2. Python parser converts `ast.AST` → `UniversalNode`.
3. Cyclomatic complexity metric computed for Python files.
4. `analyse_repo` helper analyses an entire repo directory.
5. Unit-tests cover ≥90 % of added lines.

---
_Note: This file is intentionally lightweight to keep token footprint low
for context-restricted AI agents._ 