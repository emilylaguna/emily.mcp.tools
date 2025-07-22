# Phase 3 – Multi-Language Support via Tree-sitter

This phase equips the *analysis* package with **incremental, multi-language**
parsing using [Tree-sitter](https://tree-sitter.github.io/).

## Deliverables
1. **Tree-sitter Adapter Layer**  
   – `analysis.tree_sitter_adapter` module that wraps the `Parser` API and
     exposes `parse_bytes(language_id, bytes) -> UniversalNode`.
2. **Grammar Registry**  
   – Lazy compilation & caching of grammars under `analysis/_ts_build/`.
3. **Swift + Kotlin Support**  
   – Parsing capable of returning a valid `UniversalNode` root for `.swift`,
     `.kt`, and `.kts` files.  
   – Smoke-tests asserting that a trivial `print("hello")` snippet produces a
     root node with language field set appropriately.
4. **Language Extension Guide**  
   – Inline docstring / README snippet explaining how to add more grammars by
     editing the registry map.

## Acceptance Criteria
- `analysis.parse_file("hello.swift")` returns without raising when the
  `tree_sitter` package is available.
- The cyclomatic complexity function gracefully returns `1` for unsupported
  granular metrics on non-Python languages.
- New pytest module `test_tree_sitter_support.py` covers:
  * Swift & Kotlin happy-path parsing.
  * Error raised when suffix is unknown.
- Documentation updated (`analysis/prompts/README.md`).

**Stretch**: Detect control-flow node kinds in Swift/Kotlin and integrate the
complexity metric into the generic visitor (optional for this phase). 