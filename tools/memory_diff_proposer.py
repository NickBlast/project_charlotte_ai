#!/usr/bin/env python3
"""
Turn _intake/memory_candidates.md and/or latest _intake/memory_self_dump/YYYY-MM-DD.md 
into proposed patches for the correct modules.
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import tempfile
import shutil

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
    parser = argparse.ArgumentParser(description="Propose memory diffs for Charlotte AI")
    parser.add_argument("--source", choices=["candidates", "self_dump"], required=True,
                        help="Source of memory content")
    parser.add_argument("--date", help="Date for self_dump (YYYY-MM-DD)")
    parser.add_argument("--open-pr", action="store_true", 
                        help="Open a PR with gh CLI (requires gh)")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Preview actions without writing files")
    return parser.parse_args()


def load_source_content(source: str, date: str = None) -> str:
    """Load content from the specified source."""
    source_file: Path = None  # type: ignore
    if source == "candidates":
        source_file = Path("charlotte_ai") / "_intake" / "memory_candidates.md"
        if not source_file.exists():
            exit_with_error(EXIT_BAD_INPUT, f"Memory candidates file not found: {source_file}",
                           "Run ingest_chatgpt_export.py first to generate candidates.")
    else:  # self_dump
        if not date:
            # Find the latest self_dump file
            intake_dir = Path("charlotte_ai") / "_intake" / "memory_self_dump"
            if not intake_dir.exists():
                exit_with_error(EXIT_BAD_INPUT, f"Self dump directory not found: {intake_dir}",
                               "Create the directory and add self dump files.")
            
            # Find the latest file
            dump_files = list(intake_dir.glob("*.md"))
            if not dump_files:
                exit_with_error(EXIT_BAD_INPUT, "No self dump files found",
                               "Add self dump files to charlotte_ai/_intake/memory_self_dump/")
            
            # Sort by date in filename (assuming format includes date)
            dump_files.sort(key=lambda x: x.name, reverse=True)
            source_file = dump_files[0]
        else:
            source_file = Path("charlotte_ai") / "_intake" / "memory_self_dump" / f"{date}.md"
            if not source_file.exists():
                exit_with_error(EXIT_BAD_INPUT, f"Self dump file not found: {source_file}",
                               "Check the date and ensure the file exists.")
    
    if source_file is None:
        return ""  # This should never happen due to the logic above, but satisfies the type checker
    
    try:
        with open(source_file, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        exit_with_error(EXIT_BAD_INPUT, f"Error reading {source_file}: {e}",
                       "Check file permissions and format.")
    return ""  # This line ensures we always return a string


def score_routing_confidence(line: str, target_dir: str) -> float:
    """Score confidence (0-1) for routing a line to a target directory."""
    line_lower = line.lower()
    
    # High confidence keywords for each category
    scores = {
        "persona": 0.0,
        "modes": 0.0,
        "protocols": 0.0,
        "projects": 0.0,
        "relationship_identity": 0.0,
        "soul_codex": 0.0
    }
    
    # Persona related keywords
    if any(keyword in line_lower for keyword in [
        "persona", "character", "identity", "behavior", "tone", "voice", 
        "response", "personality", "traits", "values", "beliefs"]):
        scores["persona"] += 0.4
    
    # Modes related keywords
    if any(keyword in line_lower for keyword in [
        "mode", "mood", "context", "situation", "scenario", "setting"]):
        scores["modes"] += 0.3
    
    # Protocols related keywords
    if any(keyword in line_lower for keyword in [
        "protocol", "procedure", "process", "workflow", "step", "method", 
        "approach", "technique", "framework", "guideline"]):
        scores["protocols"] += 0.4
    
    # Projects related keywords
    if any(keyword in line_lower for keyword in [
        "project", "task", "goal", "objective", "milestone", "deliverable", 
        "plan", "schedule", "timeline", "resource"]):
        scores["projects"] += 0.3
    
    # Relationship related keywords
    if any(keyword in line_lower for keyword in [
        "relationship", "friend", "connection", "bond", "interaction", 
        "communication", "understanding", "empathy", "trust"]):
        scores["relationship_identity"] += 0.4
    
    # Soul Codex related keywords
    if any(keyword in line_lower for keyword in [
        "philosophy", "wisdom", "knowledge", "insight", "principle", 
        "concept", "theory", "idea", "thought", "reflection"]):
        scores["soul_codex"] += 0.3
    
    # Return score for the target directory
    return scores.get(target_dir, 0.0)


def route_content_line(line: str) -> tuple:
    """Route a content line to the most appropriate module with confidence score."""
    # Score each possible target
    targets = ["persona", "modes", "protocols", "projects", "relationship_identity", "soul_codex"]
    scores = {target: score_routing_confidence(line, target) for target in targets}
    
    # Find the best match
    if not scores:
        return None, 0.0
        
    best_target = max(scores.keys(), key=lambda x: scores[x])
    best_score = scores[best_target]
    
    # If confidence is too low, return None to park in unclassified
    if best_score < 0.6:
        return None, 0.0
    
    # Map targets to actual directories
    target_map = {
        "persona": "charlotte_ai/persona",
        "modes": "charlotte_ai/modes",
        "protocols": "charlotte_ai/protocols",
        "projects": "charlotte_ai/projects",
        "relationship_identity": "charlotte_ai/relationship_identity",
        "soul_codex": "charlotte_ai/soul_codex"
    }
    
    return target_map.get(best_target), best_score


def normalize_line_endings(text: str) -> str:
    """Normalize line endings to LF for consistent patch application."""
    return text.replace('\r\n', '\n').replace('\r', '\n')


def create_patch_for_target(target_path: Path, content: str, date: str, dry_run: bool = False) -> str:
    """Create a unified diff patch for a target file."""
    # For this implementation, we'll create a simple patch format
    # In a real implementation, you'd want to do a more sophisticated diff
    
    patch_content = f"--- a/{target_path}\n"
    patch_content += f"+++ b/{target_path}\n"
    patch_content += f"@@ -0,0 +1 @@\n"
    patch_content += f"+# {target_path.name} - Memory Update {date}\n"
    patch_content += f"+\n"
    patch_content += f"+{content}\n"
    
    return normalize_line_endings(patch_content)


def process_content(content: str, date: str, reports_dir: Path, dry_run: bool = False) -> tuple:
    """Process content and create proposed patches."""
    lines = content.split('\n')
    
    # Categorize lines by target
    categorized = {
        "persona": [],
        "modes": [],
        "protocols": [],
        "projects": [],
        "relationship_identity": [],
        "soul_codex": [],
        "unclassified": []
    }
    
    # Process each line
    for line in lines:
        if not line.strip():
            continue
            
        target, confidence = route_content_line(line)
        if target is None:
            categorized["unclassified"].append(line)
        else:
            # Extract the directory name from the target path
            target_dir = Path(target).name
            categorized[target_dir].append((line, confidence))
    
    # Create patches for each category
    patches = {}
    summary_data = []
    
    for category, items in categorized.items():
        if not items:
            continue
            
        if category == "unclassified":
            # Write unclassified content to a file
            unclassified_file = reports_dir / "unclassified.md"
            if not dry_run:
                try:
                    unclassified_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(unclassified_file, 'w', encoding='utf-8') as f:
                        f.write("# Unclassified Memory Content\n\n")
                        for line in items:
                            f.write(f"{line}\n")
                except Exception as e:
                    print(f"[WARN] Failed to write unclassified content: {e}")
            continue
        
        # For classified content, create a patch
        target_path = Path(f"charlotte_ai/{category}/memory_updates.md")
        content_lines = [item[0] for item in items]  # Extract just the lines
        content_text = "\n".join(content_lines)
        
        if content_text.strip():
            patch_content = create_patch_for_target(target_path, content_text, date, dry_run)
            patches[str(target_path)] = patch_content
            
            # Add to summary
            summary_data.append({
                "target": str(target_path),
                "lines": len(content_lines),
                "confidence": sum(item[1] for item in items) / len(items) if items else 0
            })
    
    return patches, summary_data


def write_patches(patches: dict, reports_dir: Path, date: str, dry_run: bool = False):
    """Write patches to files."""
    patches_dir = reports_dir / "proposed_patches"
    
    if not dry_run:
        patches_dir.mkdir(parents=True, exist_ok=True)
    
    written_patches = []
    
    for target_path, patch_content in patches.items():
        # Create a filename based on the target
        filename = f"{Path(target_path).parent.name}_{Path(target_path).stem}.patch"
        patch_file = patches_dir / filename
        
        if not dry_run:
            try:
                with open(patch_file, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(patch_content)
                written_patches.append(patch_file)
            except Exception as e:
                print(f"[WARN] Failed to write patch {patch_file}: {e}")
        else:
            written_patches.append(patch_file)
    
    return written_patches


def create_summary_report(summary_data: list, reports_dir: Path, date: str, dry_run: bool = False):
    """Create a summary report of proposed changes."""
    summary_content = f"# Memory Diff Proposal Summary\n\n"
    summary_content += f"Date: {date}\n\n"
    
    summary_content += "## Proposed Changes\n\n"
    summary_content += "| Target | Lines | Avg Confidence |\n"
    summary_content += "|--------|-------|----------------|\n"
    
    total_lines = 0
    for item in summary_data:
        summary_content += f"| {item['target']} | {item['lines']} | {item['confidence']:.2f} |\n"
        total_lines += item['lines']
    
    summary_content += f"\n## Summary\n\n"
    summary_content += f"Total proposed changes: {total_lines} lines across {len(summary_data)} files.\n"
    
    summary_file = reports_dir / "summary.md"
    if not dry_run:
        try:
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
        except Exception as e:
            print(f"[WARN] Failed to write summary report: {e}")
    
    return summary_content


def open_pr_with_gh(summary_file: Path, patches_dir: Path):
    """Open a PR with gh CLI."""
    try:
        # Create a new branch
        branch_name = f"memory-update-{utc_ts().replace('_', '-')}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        
        # Commit the changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: memory update {utc_ts()}"], check=True)
        
        # Push the branch
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        
        # Create PR with gh
        pr_title = f"Memory Update {utc_ts()}"
        pr_body = f"Proposed memory updates from {summary_file.name}"
        subprocess.run(["gh", "pr", "create", "--title", pr_title, "--body", pr_body], check=True)
        
        print(f"[INFO] PR created successfully on branch {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Failed to create PR: {e}")
        print("You may need to manually create the PR.")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Generate timestamp for this run
    run_date = utc_ts().split('_')[0]  # YYYY-MM-DD part
    reports_dir = Path("reports") / "memory_diff" / run_date
    
    if not args.dry_run:
        reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Load source content
    print(f"[INFO] Loading {args.source} content")
    content = load_source_content(args.source, args.date)
    
    if not content.strip():
        exit_with_error(EXIT_NOTHING_TO_DO, "No content found in source",
                       "Check the source file for content.")
    
    print(f"[INFO] Processing {len(content.splitlines())} lines of content")
    
    # Process content into patches
    if not args.dry_run:
        print(f"[INFO] Creating proposed patches in {reports_dir}")
    else:
        print(f"[DRY-RUN] Would create proposed patches in {reports_dir}")
    
    patches, summary_data = process_content(content, run_date, reports_dir, args.dry_run)
    
    if not patches and not summary_data:
        exit_with_error(EXIT_NOTHING_TO_DO, "No content could be routed to targets",
                       "Check the content and routing rules.")
    
    # Write patches
    written_patches = write_patches(patches, reports_dir, run_date, args.dry_run)
    
    # Create summary report
    if not args.dry_run:
        print(f"[INFO] Creating summary report in {reports_dir}")
    else:
        print(f"[DRY-RUN] Would create summary report in {reports_dir}")
    
    summary_content = create_summary_report(summary_data, reports_dir, run_date, args.dry_run)
    
    # Print summary
    print(f"\n[SUMMARY] Memory Diff Proposal")
    print(f"  Source: {args.source}")
    print(f"  Date: {run_date}")
    print(f"  Patches: {len(written_patches)}")
    print(f"  Targets: {len(summary_data)}")
    
    # Open PR if requested
    if args.open_pr and not args.dry_run:
        print(f"[INFO] Opening PR with gh CLI")
        patches_dir = reports_dir / "proposed_patches"
        summary_file = reports_dir / "summary.md"
        open_pr_with_gh(summary_file, patches_dir)
    elif args.open_pr and args.dry_run:
        print(f"[DRY-RUN] Would open PR with gh CLI")
    
    if args.dry_run:
        print(f"\n[DRY-RUN] No files were actually written.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
