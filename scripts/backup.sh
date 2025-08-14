#!/usr/bin/env bash
#
# Wrapper script for executing the main backup.py tool in a Linux/macOS/WSL environment.
#
# Why this exists:
# Provides a simple, conventional interface for running backups, abstracting the
# direct Python call and ensuring consistent flags are used. This aligns with the
# goal of streamlined operations (Goal 3 of PRD).
#
# Usage:
#   ./scripts/backup.sh          - Runs a full snapshot.
#   ./scripts/backup.sh plan     - Runs a dry-run plan.
#
set -euo pipefail
CMD="snapshot"
[[ "${1:-}" == "plan" ]] && CMD="plan"
python3 ./backup.py "$CMD" -c config.yaml
