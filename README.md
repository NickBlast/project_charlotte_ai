# Memory Cards System (MCS) Quickstart

This repository manages a collection of YAML-based "memory cards" via a Python CLI.

## CLI Usage (`tools/cards_cli.py`)

- **New Card**: Create a new card from the template.
  `python tools/cards_cli.py new --title "My New Idea" --category "projects" --tags "idea,planning"`

- **Update Card**: Modify an existing card.
  `python tools/cards_cli.py update "charlotte_ai/memory/cards/projects/my-new-idea.yaml" --status dormant`

- **List Cards**: Display active cards in a table.
  `python tools/cards_cli.py list --category "projects"`

- **Validate**: Check all cards for schema errors, checksum integrity, and PII in headers.
  `python tools/cards_cli.py validate`

- **Build Pack**: Package active cards into distributable text chunks.
  `python tools/cards_cli.py build-pack --filter "tag:idea" --max-bytes 8000`

- **Remember Snippet**: Generate a git commit message trailer.
  `python tools/cards_cli.py remember-snippet "path/to/card.yaml"`

## Security Rails

1.  **Secrets Ignored**: `.gitignore` prevents common secret file patterns from being committed.
2.  **Public Repo Tripwire**: On public repos, write/build commands require a `--yes` flag to proceed.
3.  **PII Scan**: `validate` warns if potential PII (emails, phones) is found in card headers.
