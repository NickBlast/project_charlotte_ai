#!/usr/bin/env python3
"""
Scaffold a Memory Card, update the relevant index, and print a ready-made "Remember" prompt.
"""
import argparse
import sys
from pathlib import Path
import re

# Add the tools directory to the path so we can import utils
sys.path.append(str(Path(__file__).parent))

from utils import (
    utc_ts, 
    sanitize_filename,
    exit_with_error,
    EXIT_BAD_INPUT,
    EXIT_NOTHING_TO_DO,
    EXIT_WRITE_ERROR
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Scaffold a Memory Card for Charlotte AI")
    parser.add_argument("--category", choices=["persona", "protocol", "project", "relationship", "special"], 
                        required=True, help="Memory card category")
    parser.add_argument("--title", required=True, help="Short active title")
    parser.add_argument("--scope", required=True, help="Scope (global, <project>, <mode>)")
    parser.add_argument("--project", help="Project name (when category=project)")
    parser.add_argument("--mode", help="Mode name (when category=protocol or modes)")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files")
    return parser.parse_args()


def validate_args(args):
    """Validate command line arguments."""
    if args.category == "project" and not args.project:
        exit_with_error(EXIT_BAD_INPUT, "--project is required when category is project",
                       "Provide the project name with --project <name>")
    
    if args.category in ["protocol"] and not args.mode:
        # Note: For modes, --mode is not strictly required as it might be global
        pass
    
    if args.category == "special" and args.project:
        exit_with_error(EXIT_BAD_INPUT, "--project is not valid for special category",
                       "Remove --project or choose a different category")
    
    if args.category == "special" and args.mode:
        exit_with_error(EXIT_BAD_INPUT, "--mode is not valid for special category",
                       "Remove --mode or choose a different category")


def get_module_path(category: str, project: str = None, mode: str = None) -> Path:
    """Get the module path for the given category."""
    base_path = Path("charlotte_ai")
    
    if category == "persona":
        return base_path / "persona"
    elif category == "protocol":
        return base_path / "protocols"
    elif category == "project":
        if not project:
            exit_with_error(EXIT_BAD_INPUT, "Project name required for project category",
                           "Provide project name with --project <name>")
        return base_path / "projects" / sanitize_filename(project)
    elif category == "relationship":
        return base_path / "relationship_identity"
    elif category == "special":
        return base_path / "special_knowledge"
    else:
        exit_with_error(EXIT_BAD_INPUT, f"Unknown category: {category}",
                       "Use one of: persona, protocol, project, relationship, special")
    
    # This should never be reached
    return base_path  # type: ignore


def generate_intent_id() -> str:
    """Generate a unique intent ID in the format YYYY-MM-DD-NN."""
    # For simplicity, we'll use 01 as the sequence number
    # In a real implementation, you'd want to check existing files to find the next number
    date_part = utc_ts().split('_')[0]  # YYYY-MM-DD part
    return f"{date_part}-01"


def ensure_unique_slug(base_slug: str, module_path: Path) -> str:
    """Ensure the slug is unique by appending a number if needed."""
    slug = sanitize_filename(base_slug)
    counter = 1
    unique_slug = slug
    
    while (module_path / "memory_cards" / f"{unique_slug}.md").exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    
    return unique_slug


def create_memory_card_content(title: str, intent_id: str, category: str, scope: str, 
                              project: str = None, mode: str = None) -> str:
    """Create the content for a memory card."""
    # Generate tags based on category
    tags = [category]
    if project:
        tags.append(f"project:{project}")
    if mode:
        tags.append(f"mode:{mode}")
    
    # Create YAML header
    yaml_header = f"""---
title: {title}
intent_id: {intent_id}
type: memory_card
scope: {scope}
tags: [{', '.join(tags)}]
updated: {utc_ts().split('_')[0]}
status: active
---"""

    # Create card content
    content = f"""{yaml_header}

# {title}

## Canonical Truth

[State the core truth or fact here. Be precise and unambiguous.]

## Why This Matters

[Explain why this truth is important to remember and how it should influence behavior.]

## Verification

[Describe how to verify this truth or when it might need updating.]

## Links

[Related memory cards, documents, or external references.]

---
*Intent ID: {intent_id}*
*Last Updated: {utc_ts().split('_')[0]}*
*Status: active*
"""
    
    return content


def update_index_file(module_path: Path, intent_id: str, title: str, dry_run: bool = False):
    """Update the category index file with the new memory card."""
    index_file = module_path / "memory_index.md"
    
    # Create index file if it doesn't exist
    if not dry_run and not index_file.exists():
        try:
            index_file.parent.mkdir(parents=True, exist_ok=True)
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write("# Memory Index\n\n")
                f.write("This file tracks all memory cards in this module.\n\n")
        except Exception as e:
            print(f"[WARN] Failed to create index file {index_file}: {e}")
            return
    
    # Read existing content
    existing_content = ""
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            print(f"[WARN] Failed to read index file {index_file}: {e}")
            return
    
    # Check if entry already exists
    entry_line = f"- [{intent_id}] {title} — status: active"
    if entry_line in existing_content:
        print(f"[INFO] Memory card already indexed: {intent_id}")
        return
    
    # Add new entry
    if "- [intent_id] title — status:" in existing_content or "Memory Index" in existing_content:
        # Append to existing index section
        updated_content = existing_content.rstrip() + f"\n{entry_line}\n"
    else:
        # Create new index section
        updated_content = existing_content.rstrip() + f"\n\n## Memory Cards\n\n{entry_line}\n"
    
    # Write updated content
    if not dry_run:
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        except Exception as e:
            print(f"[WARN] Failed to update index file {index_file}: {e}")


def main():
    """Main entry point."""
    args = parse_args()
    validate_args(args)
    
    # Generate intent ID and slug
    intent_id = generate_intent_id()
    base_slug = args.title.lower().replace(' ', '_')
    module_path = get_module_path(args.category, args.project, args.mode)
    slug = ensure_unique_slug(base_slug, module_path)
    
    # Create memory card content
    card_content = create_memory_card_content(
        title=args.title,
        intent_id=intent_id,
        category=args.category,
        scope=args.scope,
        project=args.project,
        mode=args.mode
    )
    
    # Determine file path
    memory_cards_dir = module_path / "memory_cards"
    card_file = memory_cards_dir / f"{slug}.md"
    
    # Print what would be done
    if args.dry_run:
        print(f"[DRY-RUN] Would create memory card:")
        print(f"  Path: {card_file}")
        print(f"  Intent ID: {intent_id}")
        print(f"  Category: {args.category}")
        print(f"  Title: {args.title}")
        print(f"  Scope: {args.scope}")
        if args.project:
            print(f"  Project: {args.project}")
        if args.mode:
            print(f"  Mode: {args.mode}")
        print(f"\n[DRY-RUN] Card content preview:")
        print(card_content[:500] + "..." if len(card_content) > 500 else card_content)
        return 0
    
    # Create directories and write file
    try:
        memory_cards_dir.mkdir(parents=True, exist_ok=True)
        with open(card_file, 'w', encoding='utf-8') as f:
            f.write(card_content)
        print(f"[INFO] Created memory card: {card_file}")
    except Exception as e:
        exit_with_error(EXIT_WRITE_ERROR, f"Failed to create memory card: {e}",
                       "Check directory permissions and available disk space.")
    
    # Update index file
    update_index_file(module_path, intent_id, args.title, args.dry_run)
    
    # Print remember prompt
    print(f"\n[SUCCESS] Memory card created successfully!")
    print(f"Intent ID: {intent_id}")
    print(f"File: {card_file}")
    print(f"\nRemember prompt:")
    print(f"---")
    print(f"Remember this truth: {args.title} (ID: {intent_id})")
    print(f"---")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
