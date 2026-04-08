# Speckit Agent Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repository-local governance skill that analyzes and reconciles `AGENTS.md` and `.specify/memory/constitution.md`, then produces a repair plan and runtime summary.

**Architecture:** The skill lives in `speckit-agent-governance/`. `SKILL.md` and `references/governance.md` define the workflow and ownership rules. Python scripts perform extraction, classification, conflict detection, sync planning, and runtime summary generation. A small YAML config file drives precedence and ownership defaults.

**Tech Stack:** Markdown, YAML, Python 3 stdlib plus PyYAML, `unittest`

---

### Task 1: Scaffold The Skill Folder

**Files:**
- Create: `speckit-agent-governance/`
- Create: `speckit-agent-governance/SKILL.md`
- Create: `speckit-agent-governance/agents/openai.yaml`
- Create: `speckit-agent-governance/scripts/`
- Create: `speckit-agent-governance/references/`
- Create: `speckit-agent-governance/assets/`

- [ ] **Step 1: Initialize the skill scaffold**

```bash
python3 /Users/snow/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  speckit-agent-governance \
  --path /Users/snow/Documents/GitHub/speckit-agent-governance \
  --resources scripts,references,assets \
  --interface display_name="Speckit Agent Governance" \
  --interface short_description="Govern AGENTS and constitution boundaries" \
  --interface default_prompt="Use $speckit-agent-governance to reconcile AGENTS.md and .specify/memory/constitution.md."
```

- [ ] **Step 2: Verify the scaffold exists**

Run: `rg --files /Users/snow/Documents/GitHub/speckit-agent-governance/speckit-agent-governance`
Expected: `SKILL.md`, `agents/openai.yaml`, and requested resource directories appear.

### Task 2: Add Red Tests For Governance Logic

**Files:**
- Create: `tests/test_governance_scripts.py`

- [ ] **Step 1: Write failing tests for rule extraction, classification, reconciliation, and context building**

```python
def test_extract_rules_reads_bullets_and_norm_strength(self):
    ...

def test_classify_rules_prefers_constitution_for_security(self):
    ...

def test_detect_findings_reports_duplicate_conflict_overreach_and_gap(self):
    ...
```

- [ ] **Step 2: Run the tests and confirm they fail before implementation**

Run: `python3 -m unittest tests.test_governance_scripts -v`
Expected: failures or missing behavior for governance script logic.

### Task 3: Implement Shared Governance Logic

**Files:**
- Create: `speckit-agent-governance/scripts/governance_utils.py`

- [ ] **Step 1: Add data-shaping helpers and markdown parsing utilities**

```python
def extract_rules_from_text(source: str, text: str) -> list[dict]:
    ...

def classify_rules(rules: list[dict], config: dict) -> list[dict]:
    ...
```

- [ ] **Step 2: Add conflict detection, sync suggestions, and runtime summary helpers**

```python
def detect_findings(classified_rules: list[dict], config: dict) -> dict:
    ...

def suggest_sync_plan(findings: dict, precedence: list[str]) -> dict:
    ...

def build_runtime_context(classified_rules: list[dict], config: dict) -> dict:
    ...
```

- [ ] **Step 3: Run the tests and confirm the shared logic now passes**

Run: `python3 -m unittest tests.test_governance_scripts -v`
Expected: all governance logic tests pass.

### Task 4: Wire The CLI Scripts And Skill Resources

**Files:**
- Create: `speckit-agent-governance/scripts/governance_extract_rules.py`
- Create: `speckit-agent-governance/scripts/governance_classify_rules.py`
- Create: `speckit-agent-governance/scripts/governance_detect_conflicts.py`
- Create: `speckit-agent-governance/scripts/governance_suggest_sync.py`
- Create: `speckit-agent-governance/scripts/governance_build_context.py`
- Create: `speckit-agent-governance/references/governance.md`
- Create: `speckit-agent-governance/assets/governance.yml`
- Modify: `speckit-agent-governance/SKILL.md`

- [ ] **Step 1: Add CLI entrypoints that expose the shared logic as JSON-producing commands**

```python
def main() -> int:
    parser = argparse.ArgumentParser(...)
    ...
    print(json.dumps(result, indent=2))
    return 0
```

- [ ] **Step 2: Author the governance reference and skill instructions**

```markdown
## Workflow
1. Read governed files
2. Extract and classify rules
3. Detect duplicate, conflict, overreach, and gap findings
4. Produce a repair plan
5. Wait for explicit confirmation before writing governed files
```

- [ ] **Step 3: Define the machine-readable governance policy**

```yaml
precedence:
  - constitution
  - agents
  - task
```

### Task 5: Validate The Skill And Clean Templates

**Files:**
- Modify: `speckit-agent-governance/agents/openai.yaml`
- Modify: `speckit-agent-governance/` resource files as needed

- [ ] **Step 1: Remove generated placeholders and ensure the resource set matches the final design**

```text
Delete template text and keep only the required governance materials.
```

- [ ] **Step 2: Run the skill validator**

Run: `python3 /Users/snow/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/snow/Documents/GitHub/speckit-agent-governance/speckit-agent-governance`
Expected: `Skill is valid!`

- [ ] **Step 3: Re-run repository tests as final verification**

Run: `python3 -m unittest tests.test_governance_scripts -v`
Expected: all tests pass.
