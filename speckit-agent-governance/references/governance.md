# Governance Reference

Use this reference when deciding whether a rule belongs in `AGENTS.md` or `.specify/memory/constitution.md`.

## Ownership

Put rules in `.specify/memory/constitution.md` when they define:

- project principles
- architectural constraints
- safety or compliance requirements
- compatibility requirements
- quality bars
- governance authority

Put rules in `AGENTS.md` when they define:

- execution workflow
- tool usage
- communication behavior
- editing discipline
- validation steps
- handoff format

For `validation` and `quality-bar`, split the rule across both documents when needed:

- keep the durable requirement in the constitution
- keep the concrete operational step in `AGENTS.md`

## Precedence

Apply this order whenever documents disagree:

1. `.specify/memory/constitution.md`
2. `AGENTS.md`
3. current task input

Do not let `AGENTS.md` redefine a constitutional rule.

## Findings

Use these finding types:

- `duplicate`: the same rule appears in both documents
- `conflict`: the two documents express incompatible policies
- `overreach`: a rule appears in the wrong document
- `gap`: a constitutional requirement lacks an executable step in `AGENTS.md`

## Workflow

1. Read `AGENTS.md`
2. Read `.specify/memory/constitution.md` when it exists
3. Run `scripts/governance_extract_rules.py`
4. Run `scripts/governance_classify_rules.py`
5. Run `scripts/governance_detect_conflicts.py`
6. Run `scripts/governance_suggest_sync.py`
7. Present the repair plan
8. Wait for explicit user confirmation before writing governed files
9. Run `scripts/governance_build_context.py` to emit the runtime summary

## Single-Source Mode

If `.specify/memory/constitution.md` is absent:

- operate in single-source mode
- analyze only `AGENTS.md`
- report that constitutional governance is not enabled for this project

## Output Discipline

- Prefer minimal edits to governed files
- Surface ambiguity instead of guessing
- Emit temporary summaries or JSON artifacts instead of new durable governance markdown
