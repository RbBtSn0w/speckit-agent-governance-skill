# Speckit Agent Governance Skill

[![release](https://github.com/RbBtSn0w/speckit-agent-governance-skill/actions/workflows/release.yml/badge.svg)](https://github.com/RbBtSn0w/speckit-agent-governance-skill/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional governance skill for managing the boundary between `AGENTS.md` and `.specify/memory/constitution.md` in AI-agent collaborative projects.

## Overview

In complex AI-agent workflows, maintaining clear boundaries between **Principles** (Constitution) and **Execution** (Agents) is critical. This skill provides the tools and scripts necessary to:

-   **Reconcile** the relationship between `constitution.md` and `AGENTS.md`.
-   **Detect Conflicts** and overlaps between durable principles and executable behaviors.
-   **Enforce Precedence**: Constitution > Agents > Task.
-   **Optimize Runtime Memory**: Generate minimal, high-signal summaries for agent context.

## Core Architecture

The skill operates on a "professional maintenance layer" philosophy, avoiding the introduction of new long-lived governance documents. It relies on:

1.  **Fixed Boundaries**: Prinicples stay in the constitution; operational steps stay in `AGENTS.md`.
2.  **Automated Analysis**: Scripts for rule extraction, classification, and conflict detection.
3.  **Minimal Repair Plans**: Suggesting the smallest necessary changes to maintain alignment.

## Installation

Add this skill to your agent environment:

```bash
npx skills add https://github.com/RbBtSn0w/speckit-agent-governance-skill --skill speckit-agent-governance
```

## Quick Start

The skill provides several scripts in `speckit-agent-governance/scripts/`:

-   `governance_extract_rules.py`: Parse markdown files into rule units.
-   `governance_classify_rules.py`: Assign ownership based on `assets/governance.yml`.
-   `governance_detect_conflicts.py`: Identify duplicates, conflicts, and missing operationalization.
-   `governance_suggest_sync.py`: Generate a repair plan.
-   `governance_build_context.py`: Emit a runtime governance summary for AI memory.

## Configuration

Custom ownership and precedence rules can be configured in `speckit-agent-governance/assets/governance.yml`.

## License

MIT
