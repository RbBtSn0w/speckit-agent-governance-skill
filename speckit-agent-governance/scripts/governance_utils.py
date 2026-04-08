#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "precedence": ["constitution", "agents", "task"],
    "ownership": {
        "constitution": [
            "principle",
            "constraint",
            "security",
            "compliance",
            "architecture",
            "compatibility",
            "quality-bar",
            "governance",
        ],
        "agents": [
            "workflow",
            "communication",
            "tool-usage",
            "planning",
            "editing",
            "validation",
            "handoff",
        ],
    },
    "operationalization": {
        "constitution_topics_requiring_agents": [
            "security",
            "compatibility",
            "quality-bar",
            "validation",
        ],
        "allow_constitution_to_agents_projection": True,
        "allow_agents_to_redefine_constitution": False,
    },
    "runtime": {
        "max_constraints": 8,
        "max_workflow": 8,
        "include_risk_flags": True,
    },
}

TOPIC_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("security", ("secret", "credential", "token", "security", "auth", "sensitive")),
    ("compliance", ("compliance", "regulation", "regulatory", "privacy", "legal")),
    ("architecture", ("architecture", "boundary", "layer", "module", "dependency")),
    ("compatibility", ("compatibility", "backward", "backwards", "api", "contract")),
    ("quality-bar", ("quality", "reliable", "reliability", "coverage", "test bar")),
    ("governance", ("governance", "precedence", "authority", "source of truth", "constitution")),
    ("workflow", ("workflow", "inspect", "analyze", "implement", "sequence", "step")),
    ("communication", ("clarify", "communication", "communicate", "respond", "output")),
    ("tool-usage", ("tool", "command", "script", "git", "rg", "browser")),
    ("planning", ("plan", "design", "spec", "proposal")),
    ("editing", ("edit", "modify", "patch", "write file", "minimal diff")),
    ("validation", ("validate", "verification", "verify", "test", "lint", "build")),
    ("handoff", ("handoff", "handover", "summary", "next step", "report back")),
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "before",
    "by",
    "can",
    "do",
    "for",
    "in",
    "is",
    "it",
    "local",
    "may",
    "must",
    "never",
    "not",
    "of",
    "on",
    "or",
    "should",
    "the",
    "to",
    "when",
    "with",
}


class GovernanceError(RuntimeError):
    pass


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(config_path: str | None = None) -> dict[str, Any]:
    if config_path is None:
        return copy.deepcopy(DEFAULT_CONFIG)

    path = Path(config_path)
    if not path.exists():
        raise GovernanceError(f"Config file not found: {path}")

    loaded = yaml.safe_load(path.read_text())
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise GovernanceError("Governance config must be a YAML mapping.")
    return deep_merge(DEFAULT_CONFIG, loaded)


def load_json(path: str) -> Any:
    source = Path(path)
    if not source.exists():
        raise GovernanceError(f"JSON input file not found: {source}")
    try:
        return json.loads(source.read_text())
    except json.JSONDecodeError as exc:
        raise GovernanceError(f"Invalid JSON in {source}: {exc}") from exc


def infer_source_kind(source_file: str) -> str:
    lowered = source_file.lower()
    if "constitution" in lowered:
        return "constitution"
    if lowered.endswith("agents.md") or "/agents" in lowered or "\\agents" in lowered:
        return "agents"
    return "unknown"


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def determine_norm_strength(text: str) -> str:
    lowered = text.lower()
    if any(pattern in lowered for pattern in ("must not", "must never", "never", "required", "shall", "must")):
        return "MUST"
    if "should" in lowered:
        return "SHOULD"
    if any(pattern in lowered for pattern in (" may ", " can ", "allow", "permit")):
        return "MAY"
    return "UNSPECIFIED"


def detect_topic(heading: str, text: str) -> str:
    haystack = f"{heading} {text}".lower()
    scores: dict[str, int] = {}
    for topic, keywords in TOPIC_KEYWORDS:
        score = sum(1 for keyword in keywords if keyword in haystack)
        if score:
            scores[topic] = score
    if scores:
        return max(scores.items(), key=lambda item: (item[1], -TOPIC_KEYWORDS.index((item[0], next(keywords for topic, keywords in TOPIC_KEYWORDS if topic == item[0])))))[0]
    return "governance"


def detect_actionability(source: str, text: str) -> bool:
    lowered = text.lower()
    if source == "constitution":
        return False
    return bool(
        re.search(
            r"\b(ask|inspect|run|use|update|remove|add|write|read|check|analyze|align|build|generate|stop|wait|prompt|verify)\b",
            lowered,
        )
        or determine_norm_strength(text) != "UNSPECIFIED"
    )


def extract_rules_from_text(source_file: str, text: str) -> list[dict[str, Any]]:
    source = infer_source_kind(source_file)
    rules: list[dict[str, Any]] = []
    current_heading = Path(source_file).name
    paragraph_buffer: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if not paragraph_buffer:
            return
        paragraph = normalize_whitespace(" ".join(paragraph_buffer))
        paragraph_buffer.clear()
        if paragraph:
            rules.append(make_rule(source, source_file, current_heading, paragraph, len(rules) + 1))

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            flush_paragraph()
            continue
        if in_code_block:
            continue
        if not stripped:
            flush_paragraph()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            current_heading = normalize_whitespace(heading_match.group(2))
            continue

        bullet_match = re.match(r"^([-*+]|\d+\.)\s+(.*)$", stripped)
        if bullet_match:
            flush_paragraph()
            bullet_text = normalize_whitespace(bullet_match.group(2))
            if bullet_text:
                rules.append(make_rule(source, source_file, current_heading, bullet_text, len(rules) + 1))
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    return rules


def make_rule(source: str, source_file: str, heading: str, text: str, index: int) -> dict[str, Any]:
    topic = detect_topic(heading, text)
    return {
        "id": f"{source}-{index}",
        "source": source,
        "source_file": source_file,
        "heading": heading,
        "text": text,
        "norm_strength": determine_norm_strength(text),
        "topic": topic,
        "actionability": detect_actionability(source, text),
        "candidate_owner": source if source in {"constitution", "agents"} else None,
    }


def extract_rules_from_files(paths: list[str]) -> list[dict[str, Any]]:
    if not paths:
        raise GovernanceError("At least one markdown file is required.")
    rules: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise GovernanceError(f"Markdown file not found: {path}")
        rules.extend(extract_rules_from_text(str(path), path.read_text()))
    return rules


def classify_rules(rules: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    constitution_topics = set(config["ownership"]["constitution"])
    agents_topics = set(config["ownership"]["agents"])
    dual_topics = {"validation", "quality-bar"}
    classified: list[dict[str, Any]] = []

    for rule in rules:
        topic = rule["topic"]
        source = rule["source"]
        actionability = bool(rule.get("actionability"))

        if topic in constitution_topics and topic not in agents_topics:
            owner = "constitution"
            confidence = "high" if source == "constitution" else "medium"
            reason = f"Topic '{topic}' is constitution-owned."
        elif topic in agents_topics and topic not in constitution_topics:
            owner = "agents"
            confidence = "high" if source == "agents" else "medium"
            reason = f"Topic '{topic}' is agent-owned."
        elif topic in dual_topics:
            if source == "constitution" and not actionability:
                owner = "constitution"
                confidence = "medium"
                reason = f"Topic '{topic}' stays in constitution when stated as a requirement."
            else:
                owner = "agents"
                confidence = "medium"
                reason = f"Topic '{topic}' belongs in AGENTS when stated as an execution step."
        elif source in {"constitution", "agents"}:
            owner = source
            confidence = "medium"
            reason = "Fell back to the source document because topic ownership is ambiguous."
        else:
            owner = rule.get("candidate_owner") or "agents"
            confidence = "low"
            reason = "Fell back to candidate owner because the source file is unknown."

        classified.append(
            {
                **rule,
                "owner": owner,
                "confidence": confidence,
                "reason": reason,
            }
        )

    return classified


def normalize_rule_text(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return normalize_whitespace(text)


def content_tokens(text: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        if token not in STOPWORDS:
            tokens.add(token)
    return tokens


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_rule_text(a), normalize_rule_text(b)).ratio()


def policy_direction(text: str) -> str:
    lowered = text.lower()
    if any(pattern in lowered for pattern in ("must not", "must never", "never", "cannot", "forbid")):
        return "forbid"
    if any(pattern in lowered for pattern in ("may", "can", "allow", "permit")):
        return "allow"
    if any(pattern in lowered for pattern in ("must", "required", "shall", "should")):
        return "require"
    return "neutral"


def precedence_map(config: dict[str, Any]) -> dict[str, int]:
    return {item: index for index, item in enumerate(config["precedence"])}


def winning_source(left: str, right: str, config: dict[str, Any]) -> tuple[str, str]:
    ranks = precedence_map(config)
    left_rank = ranks.get(left, 999)
    right_rank = ranks.get(right, 999)
    return (left, right) if left_rank <= right_rank else (right, left)


def make_finding(kind: str, left: dict[str, Any], right: dict[str, Any] | None, config: dict[str, Any], note: str) -> dict[str, Any]:
    winner, loser = winning_source(left["source"], right["source"] if right else "agents", config)
    return {
        "kind": kind,
        "winner": winner,
        "loser": loser,
        "topic": left["topic"],
        "source_rule_id": left["id"],
        "related_rule_id": right["id"] if right else None,
        "note": note,
    }


def are_duplicate(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["topic"] != right["topic"]:
        return False
    left_text = normalize_rule_text(left["text"])
    right_text = normalize_rule_text(right["text"])
    return left_text == right_text or similarity(left["text"], right["text"]) >= 0.94


def are_conflicting(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["topic"] != right["topic"]:
        return False
    left_direction = policy_direction(left["text"])
    right_direction = policy_direction(right["text"])
    if {left_direction, right_direction} not in ({"forbid", "allow"}, {"forbid", "require"}):
        return False
    shared_tokens = content_tokens(left["text"]) & content_tokens(right["text"])
    return bool(shared_tokens) or similarity(left["text"], right["text"]) >= 0.45


def group_by_source(classified_rules: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    constitution_rules = [rule for rule in classified_rules if rule["source"] == "constitution"]
    agent_rules = [rule for rule in classified_rules if rule["source"] == "agents"]
    return constitution_rules, agent_rules


def has_agents_operationalization(rule: dict[str, Any], agent_rules: list[dict[str, Any]]) -> bool:
    for candidate in agent_rules:
        if candidate["topic"] == rule["topic"] and bool(candidate.get("actionability")):
            return True
    return False


def detect_findings(classified_rules: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    constitution_rules, agent_rules = group_by_source(classified_rules)
    mode = "double-source" if constitution_rules else "single-source"
    findings: list[dict[str, Any]] = []

    for rule in classified_rules:
        if rule["source"] in {"constitution", "agents"} and rule["owner"] != rule["source"]:
            findings.append(
                {
                    "kind": "overreach",
                    "winner": rule["owner"],
                    "loser": rule["source"],
                    "topic": rule["topic"],
                    "source_rule_id": rule["id"],
                    "related_rule_id": None,
                    "note": f"Rule appears in {rule['source']} but belongs to {rule['owner']}.",
                }
            )

    seen_pairs: set[tuple[str, str]] = set()
    for constitution_rule in constitution_rules:
        for agent_rule in agent_rules:
            pair_key = tuple(sorted((constitution_rule["id"], agent_rule["id"])))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            if are_duplicate(constitution_rule, agent_rule):
                findings.append(
                    make_finding(
                        "duplicate",
                        constitution_rule,
                        agent_rule,
                        config,
                        "Rules are materially identical across both documents.",
                    )
                )
            elif are_conflicting(constitution_rule, agent_rule):
                findings.append(
                    make_finding(
                        "conflict",
                        constitution_rule,
                        agent_rule,
                        config,
                        "Rules describe incompatible policy directions.",
                    )
                )

    required_topics = set(
        config.get("operationalization", {}).get("constitution_topics_requiring_agents", [])
    )
    for constitution_rule in constitution_rules:
        if constitution_rule["topic"] not in required_topics:
            continue
        if has_agents_operationalization(constitution_rule, agent_rules):
            continue
        findings.append(
            make_finding(
                "gap",
                constitution_rule,
                None,
                config,
                "Constitutional requirement has no operational step in AGENTS.",
            )
        )

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["kind"]] = counts.get(finding["kind"], 0) + 1

    return {
        "mode": mode,
        "findings": findings,
        "counts": counts,
    }


def suggest_sync_plan(findings: dict[str, Any], precedence: list[str]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []

    for finding in findings.get("findings", []):
        kind = finding["kind"]
        if kind == "duplicate":
            actions.append(
                {
                    "action": "remove-lower-priority-duplicate",
                    "target": finding["loser"],
                    "topic": finding["topic"],
                    "source_rule_id": finding["source_rule_id"],
                    "related_rule_id": finding["related_rule_id"],
                    "manual_review": False,
                }
            )
        elif kind == "conflict":
            actions.append(
                {
                    "action": "update-lower-priority-rule",
                    "target": finding["loser"],
                    "topic": finding["topic"],
                    "source_rule_id": finding["source_rule_id"],
                    "related_rule_id": finding["related_rule_id"],
                    "manual_review": True,
                }
            )
        elif kind == "overreach":
            actions.append(
                {
                    "action": "move-rule-to-authoritative-document",
                    "target": finding["winner"],
                    "topic": finding["topic"],
                    "source_rule_id": finding["source_rule_id"],
                    "related_rule_id": finding["related_rule_id"],
                    "manual_review": False,
                }
            )
        elif kind == "gap":
            actions.append(
                {
                    "action": "add-operationalization",
                    "target": "agents",
                    "topic": finding["topic"],
                    "source_rule_id": finding["source_rule_id"],
                    "related_rule_id": finding["related_rule_id"],
                    "manual_review": False,
                }
            )

    manual_review_required = sum(1 for action in actions if action["manual_review"])
    return {
        "precedence": precedence,
        "actions": actions,
        "summary": {
            "total_actions": len(actions),
            "manual_review_required": manual_review_required,
        },
    }


def unique_texts(rules: list[dict[str, Any]], limit: int) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for rule in rules:
        text = rule["text"]
        if text in seen:
            continue
        values.append(text)
        seen.add(text)
        if len(values) >= limit:
            break
    return values


def build_runtime_context(classified_rules: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    findings = detect_findings(classified_rules, config)
    mode = findings["mode"]
    runtime = config["runtime"]
    max_constraints = int(runtime.get("max_constraints", 8))
    max_workflow = int(runtime.get("max_workflow", 8))
    constitution_topics = set(config["ownership"]["constitution"])
    agent_topics = set(config["ownership"]["agents"])

    constraints = [
        rule
        for rule in classified_rules
        if rule["source"] == "constitution" or rule["owner"] == "constitution" or rule["topic"] in constitution_topics
    ]
    workflow = [
        rule
        for rule in classified_rules
        if rule["source"] == "agents"
        and (rule["owner"] == "agents" or rule["topic"] in agent_topics or rule["actionability"])
    ]

    risk_flags = [finding["kind"] for finding in findings["findings"]]

    return {
        "mode": mode,
        "precedence": config["precedence"],
        "constraints": unique_texts(constraints, max_constraints),
        "workflow": unique_texts(workflow, max_workflow),
        "risk_flags": risk_flags,
    }
