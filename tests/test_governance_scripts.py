from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "speckit-agent-governance"
SCRIPTS_DIR = SKILL_DIR / "scripts"


class GovernanceScriptCLITests(unittest.TestCase):
    maxDiff = None

    def _write(self, directory: Path, relative_path: str, content: str) -> Path:
        path = directory / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).strip() + "\n")
        return path

    def _run_json(self, script_name: str, *args: str) -> tuple[subprocess.CompletedProcess[str], object | None]:
        script_path = SCRIPTS_DIR / script_name
        completed = subprocess.run(
            ["python3", str(script_path), *args],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        payload = None
        if completed.returncode == 0:
            payload = json.loads(completed.stdout)
        return completed, payload

    def test_extract_rules_reads_headings_bullets_and_norm_strength(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agents = self._write(
                workspace,
                "AGENTS.md",
                """
                # AGENTS

                ## Workflow

                - Inspect files before editing.
                - Run relevant tests before finalizing changes.

                ## Communication

                Ask for clarification when a rule is ambiguous.
                """,
            )
            constitution = self._write(
                workspace,
                ".specify/memory/constitution.md",
                """
                # Constitution

                ## Compatibility

                - API changes MUST preserve backward compatibility.
                - Secrets MUST NEVER be exposed.
                """,
            )

            completed, payload = self._run_json(
                "governance_extract_rules.py",
                str(agents),
                str(constitution),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertGreaterEqual(len(payload), 5)
            texts = {rule["text"] for rule in payload}
            self.assertIn("Inspect files before editing.", texts)
            self.assertIn("API changes MUST preserve backward compatibility.", texts)
            compatibility_rule = next(
                rule for rule in payload if "backward compatibility" in rule["text"]
            )
            self.assertEqual(compatibility_rule["norm_strength"], "MUST")
            self.assertEqual(compatibility_rule["heading"], "Compatibility")

    def test_classify_rules_prefers_constitution_for_security_and_agents_for_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config = self._write(
                workspace,
                "governance.yml",
                """
                precedence:
                  - constitution
                  - agents
                  - task
                ownership:
                  constitution:
                    - security
                    - compatibility
                    - governance
                  agents:
                    - workflow
                    - communication
                    - tool-usage
                    - validation
                operationalization:
                  constitution_topics_requiring_agents:
                    - validation
                    - security
                runtime:
                  max_constraints: 5
                  max_workflow: 5
                """,
            )
            rules = self._write(
                workspace,
                "rules.json",
                json.dumps(
                    [
                        {
                            "id": "constitution-1",
                            "source": "constitution",
                            "source_file": ".specify/memory/constitution.md",
                            "heading": "Security",
                            "text": "Secrets MUST NEVER be exposed.",
                            "topic": "security",
                            "norm_strength": "MUST",
                            "actionability": False,
                        },
                        {
                            "id": "agents-1",
                            "source": "agents",
                            "source_file": "AGENTS.md",
                            "heading": "Workflow",
                            "text": "Inspect files before editing.",
                            "topic": "workflow",
                            "norm_strength": "UNSPECIFIED",
                            "actionability": True,
                        },
                    ],
                    indent=2,
                ),
            )

            completed, payload = self._run_json(
                "governance_classify_rules.py",
                "--input",
                str(rules),
                "--config",
                str(config),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            by_id = {rule["id"]: rule for rule in payload}
            self.assertEqual(by_id["constitution-1"]["owner"], "constitution")
            self.assertEqual(by_id["agents-1"]["owner"], "agents")
            self.assertEqual(by_id["constitution-1"]["confidence"], "high")

    def test_detect_conflicts_reports_duplicate_conflict_overreach_and_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config = self._write(
                workspace,
                "governance.yml",
                """
                precedence:
                  - constitution
                  - agents
                  - task
                ownership:
                  constitution:
                    - security
                    - compatibility
                    - governance
                    - quality-bar
                  agents:
                    - workflow
                    - communication
                    - tool-usage
                    - validation
                operationalization:
                  constitution_topics_requiring_agents:
                    - security
                    - quality-bar
                runtime:
                  max_constraints: 5
                  max_workflow: 5
                """,
            )
            classified = self._write(
                workspace,
                "classified.json",
                json.dumps(
                    [
                        {
                            "id": "constitution-compat",
                            "source": "constitution",
                            "source_file": ".specify/memory/constitution.md",
                            "heading": "Compatibility",
                            "text": "API changes MUST preserve backward compatibility.",
                            "topic": "compatibility",
                            "norm_strength": "MUST",
                            "actionability": False,
                            "owner": "constitution",
                        },
                        {
                            "id": "agents-compat-duplicate",
                            "source": "agents",
                            "source_file": "AGENTS.md",
                            "heading": "Compatibility",
                            "text": "API changes MUST preserve backward compatibility.",
                            "topic": "compatibility",
                            "norm_strength": "MUST",
                            "actionability": True,
                            "owner": "constitution",
                        },
                        {
                            "id": "constitution-security",
                            "source": "constitution",
                            "source_file": ".specify/memory/constitution.md",
                            "heading": "Security",
                            "text": "Secrets MUST NEVER be exposed.",
                            "topic": "security",
                            "norm_strength": "MUST",
                            "actionability": False,
                            "owner": "constitution",
                        },
                        {
                            "id": "agents-security-conflict",
                            "source": "agents",
                            "source_file": "AGENTS.md",
                            "heading": "Tooling",
                            "text": "Secrets MAY be printed in debug logs during local runs.",
                            "topic": "security",
                            "norm_strength": "MAY",
                            "actionability": True,
                            "owner": "agents",
                        },
                        {
                            "id": "constitution-quality",
                            "source": "constitution",
                            "source_file": ".specify/memory/constitution.md",
                            "heading": "Quality",
                            "text": "Relevant tests MUST be run before completion.",
                            "topic": "quality-bar",
                            "norm_strength": "MUST",
                            "actionability": False,
                            "owner": "constitution",
                        },
                    ],
                    indent=2,
                ),
            )

            completed, payload = self._run_json(
                "governance_detect_conflicts.py",
                "--input",
                str(classified),
                "--config",
                str(config),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            finding_types = {finding["kind"] for finding in payload["findings"]}
            self.assertEqual(payload["mode"], "double-source")
            self.assertIn("duplicate", finding_types)
            self.assertIn("conflict", finding_types)
            self.assertIn("overreach", finding_types)
            self.assertIn("gap", finding_types)

    def test_suggest_sync_plan_outputs_minimal_repair_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            findings = self._write(
                workspace,
                "findings.json",
                json.dumps(
                    {
                        "mode": "double-source",
                        "findings": [
                            {
                                "kind": "duplicate",
                                "winner": "constitution",
                                "loser": "agents",
                                "topic": "compatibility",
                                "source_rule_id": "constitution-1",
                                "related_rule_id": "agents-1",
                            },
                            {
                                "kind": "conflict",
                                "winner": "constitution",
                                "loser": "agents",
                                "topic": "security",
                                "source_rule_id": "constitution-2",
                                "related_rule_id": "agents-2",
                            },
                            {
                                "kind": "gap",
                                "winner": "constitution",
                                "loser": "agents",
                                "topic": "quality-bar",
                                "source_rule_id": "constitution-3",
                                "related_rule_id": None,
                            },
                        ],
                    },
                    indent=2,
                ),
            )

            completed, payload = self._run_json(
                "governance_suggest_sync.py",
                "--input",
                str(findings),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            actions = payload["actions"]
            action_kinds = {action["action"] for action in actions}
            self.assertIn("remove-lower-priority-duplicate", action_kinds)
            self.assertIn("update-lower-priority-rule", action_kinds)
            self.assertIn("add-operationalization", action_kinds)
            self.assertEqual(payload["summary"]["manual_review_required"], 1)

    def test_build_context_summarizes_governance_mode_constraints_and_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config = self._write(
                workspace,
                "governance.yml",
                """
                precedence:
                  - constitution
                  - agents
                  - task
                ownership:
                  constitution:
                    - security
                    - compatibility
                    - governance
                    - quality-bar
                  agents:
                    - workflow
                    - communication
                    - tool-usage
                    - validation
                operationalization:
                  constitution_topics_requiring_agents:
                    - security
                    - quality-bar
                runtime:
                  max_constraints: 3
                  max_workflow: 3
                """,
            )
            agents = self._write(
                workspace,
                "AGENTS.md",
                """
                # AGENTS

                ## Workflow

                - Inspect files before editing.
                - Ask for clarification when the boundary is ambiguous.
                - Run relevant tests before finalizing changes.
                """,
            )
            constitution = self._write(
                workspace,
                ".specify/memory/constitution.md",
                """
                # Constitution

                ## Security

                - Secrets MUST NEVER be exposed.

                ## Compatibility

                - API changes MUST preserve backward compatibility.
                """,
            )

            completed, payload = self._run_json(
                "governance_build_context.py",
                "--agents",
                str(agents),
                "--constitution",
                str(constitution),
                "--config",
                str(config),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(payload["mode"], "double-source")
            self.assertEqual(payload["precedence"], ["constitution", "agents", "task"])
            self.assertIn("Secrets MUST NEVER be exposed.", payload["constraints"])
            self.assertIn("Inspect files before editing.", payload["workflow"])


if __name__ == "__main__":
    unittest.main()
