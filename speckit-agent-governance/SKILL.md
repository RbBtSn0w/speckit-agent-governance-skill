---
name: speckit-agent-governance
description: Use when Codex needs to govern or reconcile the boundary between `AGENTS.md` and `.specify/memory/constitution.md`, check for duplicate or conflicting rules, detect overreach or missing operationalization, or build a runtime governance summary without introducing new long-lived governance markdown.
---

# Speckit Agent Governance

## Overview

Maintain a two-document governance model for `AGENTS.md` and `.specify/memory/constitution.md`. Keep durable principles in the constitution, keep executable agent behavior in `AGENTS.md`, and use scripts for repeatable analysis instead of creating more long-lived governance markdown.

## Governed Files

Read and update only these governed files:

- `AGENTS.md`
- `.specify/memory/constitution.md`

Do not introduce another durable governance markdown file in the target project.

## Workflow

1. Read `AGENTS.md`.
2. Read `.specify/memory/constitution.md` when it exists. If it does not exist, switch to single-source mode and report that state.
3. Read [references/governance.md](references/governance.md) before deciding ownership or precedence.
4. Run `scripts/governance_extract_rules.py` on the governed files.
5. Run `scripts/governance_classify_rules.py` with `assets/governance.yml` to assign ownership.
6. Run `scripts/governance_detect_conflicts.py` to find `duplicate`, `conflict`, `overreach`, and `gap` issues.
7. Run `scripts/governance_suggest_sync.py` to produce the minimal repair plan.
8. Present the repair plan and wait for explicit user confirmation before editing governed files.
9. If the user confirms, apply only the minimal changes needed to `AGENTS.md` and `.specify/memory/constitution.md`.
10. Run `scripts/governance_build_context.py` to emit the runtime summary.

## Boundary Rules

- Keep principles, hard constraints, safety, compliance, compatibility, and governance authority in the constitution.
- Keep workflow, communication, tool usage, editing discipline, and validation procedures in `AGENTS.md`.
- For `validation` and `quality-bar`, keep the requirement in the constitution and the executable step in `AGENTS.md` when both are needed.
- Apply precedence in this order: constitution, then `AGENTS.md`, then current task input.
- Stop and ask the user when ownership is ambiguous or when a proposed repair would materially change project policy.

## Resources

- Read [references/governance.md](references/governance.md) for ownership taxonomy, precedence, finding definitions, and single-source behavior.
- Read `assets/governance.yml` when topic ownership or precedence needs machine-readable defaults.
- Use `scripts/governance_extract_rules.py` to parse markdown into rule units.
- Use `scripts/governance_classify_rules.py` to assign rules to `constitution` or `agents`.
- Use `scripts/governance_detect_conflicts.py` to emit governance findings.
- Use `scripts/governance_suggest_sync.py` to generate the repair plan.
- Use `scripts/governance_build_context.py` to build the runtime memory summary.
