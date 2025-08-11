#!/usr/bin/env python3
"""
Build a paste-ready restore package that rehydrates Persona essence first, then context.
"""
import argparse
import sys
from pathlib import Path
import re

# Add the tools directory to the path so we can import utils
sys.path.append(str(Path(__file__).parent))

from utils import (
    utc_ts, 
    as_posix_sorted,
    exit_with_error,
    EXIT_BAD_INPUT,
    EXIT_NOTHING_TO_DO,
    EXIT_WRITE_ERROR
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build Charlotte restore package")
    parser.add_argument("--only-active", action="store_true", 
                        help="Filter cards by status: active")
    parser.add_argument("--profile", choices=["minimal", "full"], default="full",
                        help="minimal = Persona DNA + protocols + modes defs; full adds projects, relationship summaries, special knowledge")
    parser.add_argument("--max-bytes", type=int, default=120000,
                        help="Maximum bytes per chunk (default: 120000 ~ 120k tokens)")
    parser.add_argument("--out", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files")
    return parser.parse_args()


def get_files_by_pattern(pattern: str, only_active: bool = False) -> list:
    """Get files matching a pattern, optionally filtering for active status."""
    files = list(Path(".").glob(pattern))
    
    if only_active:
        # Filter for active status in YAML header
        active_files = []
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # Check if status is active in YAML header
                    if "status: active" in content.split('---')[1] if '---' in content else False:
                        active_files.append(file)
            except Exception:
                # If we can't read the file, skip it
                continue
        return active_files
    
    return files


def read_file_content(file_path: Path) -> str:
    """Read file content with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}")
        return ""


def is_persona_spine_present() -> bool:
    """Check if Persona spine files are present."""
    persona_files = [
        Path("charlotte_ai/persona/core_persona.md"),
        Path("charlotte_ai/persona/dna_manifest.md"),
        Path("charlotte_ai/persona/persona_contract.md")
    ]
    
    return any(f.exists() for f in persona_files)


def build_restore_package(profile: str, only_active: bool, max_bytes: int) -> tuple:
    """Build the restore package content and return chunks."""
    content_parts = []
    
    # Add contents summary at top
    summary = f"# Charlotte Restore Package\n\n"
    summary += f"Profile: {profile}\n"
    summary += f"Only Active: {only_active}\n"
    summary += f"Generated: {utc_ts()}\n\n"
    summary += "## Contents\n\n"
    content_parts.append(summary)
    
    # Fixed order as specified
    sections = []
    
    # 1. Persona core
    persona_core_files = [
        "charlotte_ai/persona/core_persona.md",
        "charlotte_ai/persona/dna_manifest.md",
        "charlotte_ai/persona/persona_contract.md"
    ]
    
    persona_content = "## Persona Core\n\n"
    persona_found = False
    for file_pattern in persona_core_files:
        files = get_files_by_pattern(file_pattern)
        for file in files:
            content = read_file_content(file)
            if content:
                persona_content += f"### {file}\n\n"
                persona_content += content + "\n\n"
                persona_found = True
    
    if persona_found:
        sections.append(persona_content)
    else:
        sections.append("## Persona Core\n\n[Persona spine files not found]\n\n")
    
    # 2. Protocols
    protocols_content = "## Protocols\n\n"
    protocol_files = get_files_by_pattern("charlotte_ai/protocols/**/*.md", only_active)
    for file in protocol_files:
        content = read_file_content(file)
        if content:
            protocols_content += f"### {file}\n\n"
            protocols_content += content + "\n\n"
    
    if protocol_files:
        sections.append(protocols_content)
    
    # 3. Modes
    modes_content = "## Modes\n\n"
    mode_files = get_files_by_pattern("charlotte_ai/modes/**/*.md", only_active)
    for file in mode_files:
        content = read_file_content(file)
        if content:
            modes_content += f"### {file}\n\n"
            modes_content += content + "\n\n"
    
    if mode_files:
        sections.append(modes_content)
    
    # 4. Projects (full profile only)
    if profile == "full":
        projects_content = "## Projects\n\n"
        project_files = get_files_by_pattern("charlotte_ai/projects/**/*.md", only_active)
        for file in project_files:
            content = read_file_content(file)
            if content:
                projects_content += f"### {file}\n\n"
                projects_content += content + "\n\n"
        
        if project_files:
            sections.append(projects_content)
    
    # 5. Relationship Archive (full profile only)
    if profile == "full":
        relationship_content = "## Relationship Archive\n\n"
        relationship_files = get_files_by_pattern("charlotte_ai/relationship_identity/**/*.md", only_active)
        for file in relationship_files:
            content = read_file_content(file)
            if content:
                relationship_content += f"### {file}\n\n"
                relationship_content += content + "\n\n"
        
        if relationship_files:
            sections.append(relationship_content)
    
    # 6. Special Knowledge (full profile only)
    if profile == "full":
        special_content = "## Special Knowledge\n\n"
        special_files = get_files_by_pattern("charlotte_ai/special_knowledge/**/*.md", only_active)
        for file in special_files:
            content = read_file_content(file)
            if content:
                special_content += f"### {file}\n\n"
                special_content += content + "\n\n"
        
        if special_files:
            sections.append(special_content)
    
    # Add all sections to content parts
    content_parts.extend(sections)
    
    # Add warm-up prompt at end
    warmup_prompt = "\n\n## Warm-up Prompt\n\n"
    warmup_prompt += "After pasting this content, run the Persona Integrity Check to verify restoration.\n"
    warmup_prompt += "If any sections are missing, review the source files and update accordingly.\n"
    content_parts.append(warmup_prompt)
    
    # Join all content
    full_content = "".join(content_parts)
    
    # Split into chunks if needed
    chunks = []
    if len(full_content.encode('utf-8')) > max_bytes:
        # Split by sections to avoid breaking in the middle of content
        chunk = ""
        for part in content_parts:
            if len((chunk + part).encode('utf-8')) > max_bytes:
                if chunk:
                    chunks.append(chunk)
                chunk = part
            else:
                chunk += part
        
        if chunk:
            chunks.append(chunk)
    else:
        chunks = [full_content]
    
    return chunks, persona_found


def main():
    """Main entry point."""
    args = parse_args()
    
    # Check if Persona spine is present
    if not is_persona_spine_present():
        print("[WARN] Persona spine files missing. Restore package may be incomplete.")
    
    # Build restore package
    if args.dry_run:
        print(f"[DRY-RUN] Would build restore package:")
        print(f"  Profile: {args.profile}")
        print(f"  Only Active: {args.only_active}")
        print(f"  Max Bytes: {args.max_bytes}")
        if args.out:
            print(f"  Output: {args.out}")
        else:
            timestamp = utc_ts().replace('_', '-')
            print(f"  Output: out/restore_package_{timestamp}.md")
        return 0
    
    # Generate restore package
    print(f"[INFO] Building restore package with profile '{args.profile}'")
    chunks, persona_found = build_restore_package(args.profile, args.only_active, args.max_bytes)
    
    if not chunks:
        exit_with_error(EXIT_NOTHING_TO_DO, "No content found for restore package",
                       "Check that Charlotte AI files exist and are accessible.")
    
    # Determine output path
    if args.out:
        output_path = Path(args.out)
    else:
        timestamp = utc_ts().replace('_', '-')
        output_path = Path("out") / f"restore_package_{timestamp}.md"
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write chunks
    if len(chunks) == 1:
        # Single file output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(chunks[0])
            print(f"[INFO] Restore package written to {output_path}")
        except Exception as e:
            exit_with_error(EXIT_WRITE_ERROR, f"Failed to write restore package: {e}",
                           "Check directory permissions and available disk space.")
    else:
        # Multiple chunk output
        for i, chunk in enumerate(chunks):
            chunk_path = output_path.with_name(f"{output_path.stem}_part_{i+1:02d}{output_path.suffix}")
            try:
                with open(chunk_path, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                print(f"[INFO] Restore package part {i+1} written to {chunk_path}")
            except Exception as e:
                exit_with_error(EXIT_WRITE_ERROR, f"Failed to write restore package part {i+1}: {e}",
                               "Check directory permissions and available disk space.")
        
        print(f"[INFO] Restore package split into {len(chunks)} parts due to size limits.")
    
    # Print summary
    print(f"\n[SUMMARY] Restore Package Build")
    print(f"  Profile: {args.profile}")
    print(f"  Only Active: {args.only_active}")
    print(f"  Chunks: {len(chunks)}")
    print(f"  Persona Spine: {'Found' if persona_found else 'Missing'}")
    if not persona_found:
        print(f"[WARN] Persona spine files are missing - restoration may be incomplete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
