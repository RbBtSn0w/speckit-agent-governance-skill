#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from governance_utils import GovernanceError, classify_rules, load_config, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify extracted governance rules by owner.")
    parser.add_argument("--input", required=True, help="Path to extracted rules JSON")
    parser.add_argument("--config", help="Optional governance config YAML")
    args = parser.parse_args()

    try:
        rules = load_json(args.input)
        config = load_config(args.config)
        classified = classify_rules(rules, config)
    except GovernanceError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(classified, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
