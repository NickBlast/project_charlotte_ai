#
# Wrapper script for executing the main backup.py tool in a Windows/PowerShell environment.
#
# Why this exists:
# Provides a simple, conventional interface for running backups, abstracting the
# direct Python call and ensuring consistent flags are used. This aligns with the
# goal of streamlined operations (Goal 3 of PRD) and provides Windows ergonomics.
#
# Usage:
#   .\scripts\backup.ps1          - Runs a full snapshot.
#   .\scripts\backup.ps1 -Plan     - Runs a dry-run plan.
#
param([switch]$Plan, [string]$Config="config.yaml")
$cmd = if ($Plan) { "plan" } else { "snapshot" }
python ".\backup.py" $cmd -c $Config
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
