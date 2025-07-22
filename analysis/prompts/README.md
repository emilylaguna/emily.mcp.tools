# Analysis Implementation Prompts

This directory hosts inspiration prompts and design outlines that guide the incremental
implementation of the *analysis* package.  Each sub-folder corresponds to a logical
phase in the roadmap (foundation, metrics, semantic, …).  Maintaining the prompts
close to the code keeps context loading efficient for AI agents because they can
fetch only the phase they currently work on rather than the full spec.

```
analysis/prompts/
├── phase1_foundation.md
├── phase2_metrics.md
└── progress_tracker.json
```

* **phaseX_*.md** – Natural-language instructions / acceptance criteria for that
  milestone.
* **progress_tracker.json** – Lightweight Kanban board consumed by agents & tests
  to verify milestone completion status.

## Why Tree-sitter?
Tree-sitter provides a fast, incremental parser with grammar coverage for dozens of
languages.  Our roadmap leverages it to achieve multi-language parity without
re-implementing parsers.  The *analysis* package ships a **thin adapter layer**
that will lazily compile/initialize grammars on-demand and convert them to the
`UniversalNode` hierarchy.

**Initial target grammars**:  
• Swift (`.swift`)  
• Kotlin (`.kt`, `.kts`)  
More languages can be enabled by adding entries to the `suffix_map` in
`analysis.__init__.py`.

> NOTE: Grammar compilation happens inside `analysis/_ts_build/` so subsequent
> runs are instant.  If `tree_sitter` is not installed the analysis gracefully
> falls back to Python-only support while alerting the caller. 