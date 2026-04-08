# Speckit Agent Governance Design

**Goal:** Create a governance skill that maintains the boundary between `AGENTS.md` and `.specify/memory/constitution.md` without introducing additional long-lived governance markdown in the target project.

## Scope

The skill governs only two durable project documents:

- `AGENTS.md`
- `.specify/memory/constitution.md`

The skill itself may include reusable operational resources:

- `SKILL.md`
- `references/governance.md`
- `scripts/*.py`
- `assets/governance.yml`
- `agents/openai.yaml`

Those resources live inside the skill folder and are not additional project governance sources.

## Ownership Model

### Constitution

`constitution.md` is the durable principle source. It may define:

- long-lived project principles
- architectural constraints
- safety, compliance, and compatibility rules
- quality bars
- governance and change-control principles

It must not define agent-specific workflows or tool procedures.

### AGENTS

`AGENTS.md` is the execution source. It may define:

- workflow order
- communication behavior
- tool usage habits
- editing and validation procedures
- how constitutional rules are operationalized

It must not redefine project principles that belong in the constitution.

### Precedence

The skill enforces this precedence order:

1. `.specify/memory/constitution.md`
2. `AGENTS.md`
3. Current task input

Task input may refine execution details but may not override constitutional constraints.

## Skill Behavior

The skill supports these intents:

- update constitution
- update AGENTS
- align both files
- check conflicts
- generate runtime memory summary

Execution is split into explicit phases:

1. Read target files
2. Extract rule units
3. Classify ownership and topic
4. Detect duplicates, conflicts, overreach, and gaps
5. Produce a minimal repair plan
6. Wait for user confirmation before modifying governed files
7. Build a temporary runtime summary

The skill must never silently rewrite governed files.

## Architecture

The implementation uses a mixed prompt-plus-scripts design:

- `SKILL.md` orchestrates the workflow and user interaction
- `references/governance.md` captures the stable governance boundary rules
- Python scripts perform repeatable extraction, classification, comparison, and summary generation
- `assets/governance.yml` provides machine-readable defaults for precedence and topic ownership

This balances determinism with low maintenance cost.

## Script Responsibilities

### `governance_extract_rules.py`

Parse markdown into structured rule units with fields such as source, heading, text, norm strength, topic, actionability, and candidate owner.

### `governance_classify_rules.py`

Use topic rules and actionability to classify each rule into `constitution` or `agents`, with confidence and reasoning.

### `governance_detect_conflicts.py`

Compare classified rules and emit findings for:

- duplicate
- conflict
- overreach
- gap

### `governance_suggest_sync.py`

Turn findings into a minimal sync plan that preserves constitutional authority and highlights manual decisions when ambiguity remains.

### `governance_build_context.py`

Build a compact runtime summary from both governed files without creating a new durable governance markdown file.

## Config

`assets/governance.yml` stores the minimum machine-readable policy surface:

- precedence
- ownership topics
- operationalization rules
- runtime summary limits

## Validation

The implementation should include repository tests for the shared governance logic and run the skill validator against the generated skill folder.

Forward-testing with subagents is intentionally skipped in this repository because the current session is not authorized to delegate.

## Risks And Controls

- Ambiguous rules cannot be auto-resolved; the skill must stop and request human confirmation.
- Missing constitution files must degrade cleanly to single-source governance mode.
- Similarity-based conflict detection is heuristic; the skill should surface uncertainty rather than silently choosing a repair.

## Repository Constraints

- The current workspace is not a git repository, so the design doc cannot be committed here.
- The skill is created inside this repository as source material, not installed into `~/.codex/skills`.
