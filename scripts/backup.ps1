param([switch]$Plan, [string]$Config="config.yaml")
$cmd = if ($Plan) { "plan" } else { "snapshot" }
python ".\backup.py" $cmd -c $Config
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
