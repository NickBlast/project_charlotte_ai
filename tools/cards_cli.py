
import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import yaml

# --- Constants ---
CARDS_DIR = Path("charlotte_ai/memory/cards")
INDEX_PATH = Path("charlotte_ai/memory/index.json")
TEMPLATE_PATH = Path("templates/memory_card.yaml")
DIST_DIR = Path("dist")

# PII Regex (naive, for warnings)
PII_PATTERNS = {
    "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    "phone": re.compile(r"\+?\d[\d\s().-]{7,}", re.IGNORECASE),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "address": re.compile(r"\b\d{1,5}\s+\w+(?:\s+\w+){0,3}\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Lane|Ln)\b", re.IGNORECASE),
}
HEADER_FIELDS_TO_SCAN = ["title", "tags", "category", "mode", "source"]

# --- Utility Functions ---

def is_repo_public(args):
    """Check if the repo is public, requiring --yes for sensitive ops."""
    if hasattr(args, 'yes') and args.yes:
        return False # User has already consented

    try:
        result = subprocess.run(["gh", "repo", "view", "--json", "isPrivate"], capture_output=True, text=True, check=True)
        is_private = json.loads(result.stdout).get("isPrivate", False)
        if not is_private:
            print("\033[91mWARNING: This repository is public. Operations that write files or build artifacts require the --yes flag.\033[0m", file=sys.stderr)
            return True
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        # If gh fails or isn't installed, assume public as a fallback
        print("\033[91mWARNING: Could not determine repository privacy. Assuming public. Operations that write files or build artifacts require the --yes flag.\033[0m", file=sys.stderr)
        return True
    return False

def update_index():
    """Rebuilds the index.json from active cards, sorted deterministically."""
    active_cards = []
    for card_path in sorted(CARDS_DIR.glob("**/*.yaml")):
        with open(card_path, "r", encoding="utf-8") as f:
            card = yaml.safe_load(f)
        if card.get("status") == "active":
            active_cards.append({
                "id": card.get("id"),
                "title": card.get("title"),
                "category": card.get("category"),
                "tags": card.get("tags"),
                "mode": card.get("mode"),
                "status": card.get("status"),
                "updated_utc": card.get("updated_utc"),
            })

    # Deterministic sort
    active_cards.sort(key=lambda x: (x["title"] or "", x["id"] or ""))

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(active_cards, f, indent=2, ensure_ascii=False)
        f.write("\n")

def calculate_checksum(body_md):
    """Calculates the SHA256 checksum of the card body."""
    return sha256(body_md.encode("utf-8")).hexdigest()

def slugify(title):
    """Creates a filesystem-friendly slug from a title."""
    s = title.lower().strip()
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"[^a-z0-9- ]", "", s)
    return s

# --- CLI Subcommands ---

def new_card(args):
    """Create a new memory card."""
    if is_repo_public(args):
        sys.exit(1)

    title = args.title
    category = args.category
    slug = slugify(title)
    now_utc = datetime.now(timezone.utc).isoformat()

    card_dir = CARDS_DIR / category
    card_dir.mkdir(parents=True, exist_ok=True)
    card_path = card_dir / f"{slug}.yaml"

    if card_path.exists():
        print(f"ERROR: Card already exists at {card_path}", file=sys.stderr)
        sys.exit(1)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        card = yaml.safe_load(f)

    body_content = ""
    if args.body:
        try:
            with open(args.body, "r", encoding="utf-8") as f:
                body_content = f.read()
        except FileNotFoundError:
            print(f"ERROR: Body file not found at {args.body}", file=sys.stderr)
            sys.exit(1)

    card.update({
        "id": str(uuid.uuid4()),
        "title": title,
        "category": category,
        "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
        "mode": args.mode or "",
        "scope": args.scope or "",
        "status": args.status,
        "created_utc": now_utc,
        "updated_utc": now_utc,
        "source": args.source or "",
        "body_md": body_content,
        "checksum": calculate_checksum(body_content),
        "mem_intent": f"New memory about {title}."
    })

    with open(card_path, "w", encoding="utf-8", newline="\n") as f:
        yaml.dump(card, f, sort_keys=False, allow_unicode=True)

    print(f"Created new card: {card_path}")
    update_index()

def update_card(args):
    """Update an existing memory card."""
    if is_repo_public(args):
        sys.exit(1)

    card_path = Path(args.card_path)
    if not card_path.exists():
        print(f"ERROR: Card not found at {card_path}", file=sys.stderr)
        sys.exit(1)

    with open(card_path, "r", encoding="utf-8") as f:
        card = yaml.safe_load(f)

    updated = False
    fields_to_update = ["title", "category", "tags", "mode", "scope", "status", "source"]
    for field in fields_to_update:
        new_value = getattr(args, field)
        if new_value is not None:
            if field == "tags":
                new_value = [t.strip() for t in new_value.split(",")]
            if card.get(field) != new_value:
                card[field] = new_value
                updated = True

    if args.body:
        try:
            with open(args.body, "r", encoding="utf-8") as f:
                new_body = f.read()
            if card.get("body_md") != new_body:
                card["body_md"] = new_body
                card["checksum"] = calculate_checksum(new_body)
                updated = True
        except FileNotFoundError:
            print(f"ERROR: Body file not found at {args.body}", file=sys.stderr)
            sys.exit(1)

    if updated:
        card["updated_utc"] = datetime.now(timezone.utc).isoformat()
        with open(card_path, "w", encoding="utf-8", newline="\n") as f:
            yaml.dump(card, f, sort_keys=False, allow_unicode=True)
        print(f"Updated card: {card_path}")
        update_index()
    else:
        print("No changes detected.")

def list_cards(args):
    """List memory cards."""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    if not args.all: # Default to active
        cards = [c for c in cards if c.get("status") == "active"]

    if args.tag:
        cards = [c for c in cards if args.tag in c.get("tags", [])]

    if args.category:
        cards = [c for c in cards if c.get("category") == args.category]

    # Print table
    headers = ["Title", "Category", "Tags", "Status", "Updated UTC"]
    rows = [
        [
            c.get("title", "N/A"),
            c.get("category", "N/A"),
            ",".join(c.get("tags", [])),
            c.get("status", "N/A"),
            c.get("updated_utc", "N/A"),
        ]
        for c in cards
    ]

    if not rows:
        print("No cards found.")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))


def validate_cards(args):
    """Validate all memory cards for schema, checksums, and PII."""
    errors = 0
    warnings = 0
    all_ids = set()

    for card_path in sorted(CARDS_DIR.glob("**/*.yaml")):
        with open(card_path, "r", encoding="utf-8") as f:
            try:
                card = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"ERROR: Invalid YAML in {card_path}: {e}", file=sys.stderr)
                errors += 1
                continue

        # 1. Schema conformity
        required_fields = ["id", "title", "category", "status", "created_utc", "updated_utc", "body_md", "checksum"]
        missing_fields = [f for f in required_fields if f not in card]
        if missing_fields:
            print(f"ERROR: {card_path} missing required fields: {missing_fields}", file=sys.stderr)
            errors += 1

        # 2. UUID uniqueness
        card_id = card.get("id")
        if card_id in all_ids:
            print(f"ERROR: {card_path} has duplicate UUID: {card_id}", file=sys.stderr)
            errors += 1
        if card_id:
            all_ids.add(card_id)

        # 3. Checksum validation
        body = card.get("body_md", "")
        expected_checksum = calculate_checksum(body)
        if card.get("checksum") != expected_checksum:
            print(f"ERROR: {card_path} has incorrect checksum.", file=sys.stderr)
            errors += 1

        # 4. Header PII scan
        for field in HEADER_FIELDS_TO_SCAN:
            value = card.get(field)
            if not value:
                continue
            # For tags list, join them into a string
            value_str = ", ".join(value) if isinstance(value, list) else str(value)
            for pii_type, pattern in PII_PATTERNS.items():
                if pattern.search(value_str):
                    print(f"WARN: {card_path} has potential PII ({pii_type}) in header field '{field}'.", file=sys.stderr)
                    warnings += 1

    if errors > 0:
        print(f"\nValidation failed with {errors} error(s).", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Validation successful with {warnings} warning(s).")


def build_pack(args):
    """Build a distributable pack of memory cards."""
    if is_repo_public(args):
        sys.exit(1)

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        all_cards = json.load(f)

    # Filter for active cards first
    cards_to_pack = [c for c in all_cards if c.get("status") == "active"]

    # Apply filters
    if args.filter:
        filter_parts = [p.strip() for p in args.filter.split("|")]
        filtered_set = set()
        for part in filter_parts:
            key, value = part.split(":", 1)
            for card_info in cards_to_pack:
                if key == "tag" and value in card_info.get("tags", []):
                    filtered_set.add(card_info["id"])
                elif key == "category" and value == card_info.get("category"):
                    filtered_set.add(card_info["id"])
        cards_to_pack = [c for c in cards_to_pack if c["id"] in filtered_set]

    # Load full card content for selected cards
    full_cards = []
    for card_info in cards_to_pack:
        # Find the card file
        card_path = next(CARDS_DIR.glob(f"**/{slugify(card_info['title'])}.yaml"), None)
        if not card_path:
             # Fallback for titles that might have changed
            for p in CARDS_DIR.glob("**/*.yaml"):
                with open(p, 'r', encoding='utf-8') as f:
                    c = yaml.safe_load(f)
                    if c.get('id') == card_info['id']:
                        card_path = p
                        break
        
        if card_path:
            with open(card_path, "r", encoding="utf-8") as f:
                full_cards.append(yaml.safe_load(f))

    # Deterministic sort
    full_cards.sort(key=lambda x: (x["title"] or "", x["id"] or ""))

    # Create chunks
    pack_dir = DIST_DIR / f"pack_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}"
    pack_dir.mkdir(parents=True, exist_ok=True)
    chunk_num = 1
    current_chunk_size = 0
    current_chunk_content = ""

    for card in full_cards:
        card_block = f"### {card['title']} [{card['id']}]\n\n{card['body_md']}\n\n---\n"
        card_block_size = len(card_block.encode("utf-8"))

        if current_chunk_size + card_block_size > args.max_bytes and current_chunk_size > 0:
            chunk_path = pack_dir / f"chunk_{chunk_num:03d}.txt"
            with open(chunk_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(current_chunk_content)
            print(f"Wrote {chunk_path}")
            chunk_num += 1
            current_chunk_content = ""
            current_chunk_size = 0

        current_chunk_content += card_block
        current_chunk_size += card_block_size

    if current_chunk_content:
        chunk_path = pack_dir / f"chunk_{chunk_num:03d}.txt"
        with open(chunk_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(current_chunk_content)
        print(f"Wrote {chunk_path}")

def remember_snippet(args):
    """Generate a commit message snippet for a card."""
    card_path = Path(args.card_path)
    if not card_path.exists():
        print(f"ERROR: Card not found at {card_path}", file=sys.stderr)
        sys.exit(1)

    with open(card_path, "r", encoding="utf-8") as f:
        card = yaml.safe_load(f)

    print(f'Remember (Mem-Intent: "{card.get("mem_intent", "")}") — {card.get("title", "N/A")} [{card.get("id", "N/A")}]')


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Memory Cards System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- 'new' command ---
    p_new = subparsers.add_parser("new", help="Create a new memory card.")
    p_new.add_argument("--title", required=True, help="Card title.")
    p_new.add_argument("--category", required=True, help="Card category.")
    p_new.add_argument("--tags", help="Comma-separated tags.")
    p_new.add_argument("--mode", help="Card mode.")
    p_new.add_argument("--scope", help="Card scope.")
    p_new.add_argument("--status", choices=["active", "dormant"], default="active", help="Card status.")
    p_new.add_argument("--source", help="Card source.")
    p_new.add_argument("--body", help="Path to a markdown file for the body content (e.g., @file.md).")
    p_new.add_argument("--yes", action="store_true", help="Consent to write/build on a public repo.")
    p_new.set_defaults(func=new_card)

    # --- 'update' command ---
    p_update = subparsers.add_parser("update", help="Update an existing card.")
    p_update.add_argument("card_path", help="Path to the card YAML file.")
    p_update.add_argument("--title", help="New card title.")
    p_update.add_argument("--category", help="New card category.")
    p_update.add_argument("--tags", help="New comma-separated tags.")
    p_update.add_argument("--mode", help="New card mode.")
    p_update.add_argument("--scope", help="New card scope.")
    p_update.add_argument("--status", choices=["active", "dormant"], help="New card status.")
    p_update.add_argument("--source", help="New card source.")
    p_update.add_argument("--body", help="Path to a new markdown file for the body content.")
    p_update.add_argument("--yes", action="store_true", help="Consent to write on a public repo.")
    p_update.set_defaults(func=update_card)

    # --- 'list' command ---
    p_list = subparsers.add_parser("list", help="List cards.")
    p_list.add_argument("--all", action="store_true", help="Show all cards (default is active only).")
    p_list.add_argument("--tag", help="Filter by tag.")
    p_list.add_argument("--category", help="Filter by category.")
    p_list.set_defaults(func=list_cards)

    # --- 'validate' command ---
    p_validate = subparsers.add_parser("validate", help="Validate all cards.")
    p_validate.set_defaults(func=validate_cards)

    # --- 'build-pack' command ---
    p_build = subparsers.add_parser("build-pack", help="Build a distributable pack of cards.")
    p_build.add_argument("--filter", help="Filter cards to include, e.g., 'tag:foo|category:bar'.")
    p_build.add_argument("--max-bytes", type=int, default=110000, help="Max bytes per chunk.")
    p_build.add_argument("--yes", action="store_true", help="Consent to build on a public repo.")
    p_build.set_defaults(func=build_pack)

    # --- 'remember-snippet' command ---
    p_remember = subparsers.add_parser("remember-snippet", help="Generate a commit message snippet.")
    p_remember.add_argument("card_path", help="Path to the card YAML file.")
    p_remember.set_defaults(func=remember_snippet)

    # --- Initial setup ---
    if not INDEX_PATH.exists():
        INDEX_PATH.touch()
        with open(INDEX_PATH, "w") as f:
            json.dump([], f)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
