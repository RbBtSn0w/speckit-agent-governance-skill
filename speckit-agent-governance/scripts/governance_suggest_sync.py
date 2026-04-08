#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from governance_utils import GovernanceError, load_json, suggest_sync_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a minimal sync plan from governance findings.")
    parser.add_argument("--input", required=True, help="Path to findings JSON")
    args = parser.parse_args()

    try:
        findings = load_json(args.input)
        precedence = findings.get("precedence", ["constitution", "agents", "task"])
        plan = suggest_sync_plan(findings, precedence)
    except GovernanceError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
