<!--
  Superseded for Sprint 3 by:
  - lint_contradiction_detect.md (Pass 1 — candidate pairs, titles/summaries only)
  - lint_contradiction_plan.md (Pass 2 — full page compare + merge plan JSON)

  This file is kept for backward compatibility and tooling references.
-->

# Lint Contradiction — legacy scaffold

**Loop:** Lint (on-demand).

**Purpose:** Compare candidate Wiki pages or excerpts and report structured contradictions for human or HITL review — expensive; run only when explicitly triggered.

Use **lint_contradiction_detect.md** and **lint_contradiction_plan.md** for the 3-pass gated pipeline (`contradiction_checker.py` + `lint_graph.py`).
