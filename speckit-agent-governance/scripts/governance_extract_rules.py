#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from governance_utils import GovernanceError, extract_rules_from_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract governance rules from markdown files.")
    parser.add_argument("paths", nargs="+", help="Markdown files to analyze")
    args = parser.parse_args()

    try:
        rules = extract_rules_from_files(args.paths)
    except GovernanceError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(rules, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
