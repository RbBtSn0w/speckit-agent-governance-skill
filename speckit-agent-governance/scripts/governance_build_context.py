#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from governance_utils import (
    GovernanceError,
    build_runtime_context,
    classify_rules,
    extract_rules_from_files,
    load_config,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a runtime governance context summary.")
    parser.add_argument("--agents", required=True, help="Path to AGENTS.md")
    parser.add_argument("--constitution", help="Path to constitution.md")
    parser.add_argument("--config", help="Optional governance config YAML")
    args = parser.parse_args()

    paths = [args.agents]
    if args.constitution:
        paths.append(args.constitution)

    try:
        config = load_config(args.config)
        extracted = extract_rules_from_files(paths)
        classified = classify_rules(extracted, config)
        context = build_runtime_context(classified, config)
    except GovernanceError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(context, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
