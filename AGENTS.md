# Repository Guidelines

## Project Structure & Modules
- `backup.py`: Snapshot CLI (manifest + optional Git tag/push).
- `charlotte_core/`: Source persona, protocols, and knowledge base.
- `tools/`: Utilities (`ingest_chatgpt_export.py`, `charlotte_restore_builder.py`, `memory_card_scaffolder.py`).
- `archives/` + `imports/`: Processed ChatGPT exports and raw inputs.
- `snapshots/`: Timestamped backups (`YYYY-MM-DD_HHMMSSZ`).
- `tests/`: Pytest suite and a smoke script.
- `scripts/`: Shell wrappers (e.g., `scripts/backup.sh`).
- `out/`, `reports/`, `docs/`: Generated artifacts, reports, and docs.

## Build, Test, and Dev Commands
- Plan backup: `python3 backup.py plan -c config.yaml`
- Create snapshot: `python3 backup.py snapshot -c config.yaml` or `./scripts/backup.sh [plan]`
- Ingest export (dry-run): `python3 tools/ingest_chatgpt_export.py --zip tmp/export.zip --dry-run`
- Ingest export: `python3 tools/ingest_chatgpt_export.py --zip tmp/export.zip`
- Build restore package: `python3 tools/charlotte_restore_builder.py --profile full --dry-run`
- Tests (focused): `pytest tests/test_ingest_report.py -v`
- Smoke test: `bash tests/ingest_export_smoke.sh`

## Coding Style & Naming
- Language: Python 3.10+; follow PEP 8; 4-space indents.
- Names: `snake_case` for files/functions, `PascalCase` for classes, `UPPER_SNAKE` constants.
- CLI: use `argparse`, clear `--flags`, and `--dry-run` where applicable.
- Docs: include module docstrings and usage examples; keep functions small and pure.

## Testing Guidelines
- Framework: `pytest` (see `tests/test_ingest_report.py`).
- Conventions: test files `tests/test_*.py`; assert on structure, determinism, and manifest integrity.
- Setup: run an ingest (or the smoke script) before tests to create fixtures under `archives/chat_exports/`.
- Aim to cover new code paths; add focused tests near related modules.

## Commit & Pull Request Guidelines
- Style: Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`, `test:`) with optional scope (`fix(tools):`).
- Memory changes: include a `Mem-Intent:` trailer when altering persona/memory content.
- PRs: clear description, linked issues, before/after notes or sample output paths; checklist that plan/snapshot run and tests pass.
- Avoid unrelated refactors; keep changes atomic; update README/docs when commands or structure change.

## Security & Configuration
- Use a private repo; never commit secrets. Configure via `config.yaml` (copy from `config.example.yaml`).
- Optional encryption (e.g., git-crypt/age) is supported externally; keep manifests and archives intact.

