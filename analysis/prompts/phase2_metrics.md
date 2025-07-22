# Phase 2 – Extended Metrics

Goal: Expand metric extraction beyond basic cyclomatic complexity.

## Candidate Metrics
- Cognitive complexity
- NPath complexity
- Afferent/Efferent Coupling
- Instability metric (I = Ce / (Ca + Ce))

## Acceptance Criteria
1. Each metric extractor lives in `analysis/metrics.py` or a dedicated module.
2. Extractors are language-agnostic where possible.
3. Unit-tests validate formulas with contrived code samples.
4. Existing APIs (`analyse_repo`, `query_hotspots`) expose new metrics seamlessly. 