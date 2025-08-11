#!/usr/bin/env bash
set -euo pipefail
CMD="snapshot"
[[ "${1:-}" == "plan" ]] && CMD="plan"
python3 ./backup.py "$CMD" -c config.yaml
