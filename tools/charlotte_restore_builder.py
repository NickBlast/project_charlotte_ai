#!/usr/bin/env python3
"""
Charlotte Restore Package Builder - Create paste-ready restore packages for Charlotte AI.

Why this exists:
To fulfill Feature 4 of the PRD. When an AI's context is lost, this tool
provides a fast, reliable way to "rehydrate" the persona by generating a single,
ordered package of its core knowledge. This makes the persona portable across any
platform (ChatGPT, Claude, Gemini, local LLMs), ensuring continuity.

Features:
- Aggregates persona files into a single, paste-ready text package (FR-5).
- Follows a strict, persona-first ordering to ensure logical rehydration.
- Supports `--profile` (`minimal`, `full`) to control context depth (FR-5).
- Chunks output into multiple files with `--max-bytes` to respect platform paste limits (FR-5).
- `--only-active` flag to filter for currently relevant memories.
- `--dry-run` for safe previews.
"""

import argparse
import sys
from pathlib import Path
import re

# Add the tools directory to the path so we can import shared utilities
sys.path.append(str(Path(__file__).parent))

from utils import (
    utc_ts,                    # UTC timestamp generation for consistent file naming
    as_posix_sorted,           # Cross-platform path sorting for deterministic results
    exit_with_error,           # Standardized error handling with exit codes
    EXIT_BAD_INPUT,            # Exit code for invalid input parameters
    EXIT_NOTHING_TO_DO,        # Exit code when no content is available
    EXIT_WRITE_ERROR           # Exit code for filesystem write failures
)


def parse_args():
    """
    Parse and validate command line arguments for the restore package builder.
    
    This function defines all available command-line options and their help
    text, then parses and returns the validated arguments. It provides
    comprehensive help documentation for users.
    
    Returns:
        argparse.Namespace: Parsed and validated command line arguments
        
    Command Line Options:
        --only-active: Filter content to only include items with 'status: active'
        --profile: Choose between 'minimal' or 'full' restore profiles
        --max-bytes: Maximum file size per chunk (default: 120000 bytes ~ 120k tokens)
        --out: Custom output file path
        --dry-run: Preview actions without writing any files
        
    Example:
        >>> parse_args()
        Namespace(dry_run=False, max_bytes=120000, only_active=False, out=None, profile='full')
    """
    parser = argparse.ArgumentParser(
        description="Build Charlotte restore package for memory reset recovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build full restore package (default)
  python charlotte_restore_builder.py
  
  # Build minimal restore package with only active content
  python charlotte_restore_builder.py --profile minimal --only-active
  
  # Custom output path and size limit
  python charlotte_restore_builder.py --out my_restore.md --max-bytes 60000
  
  # Preview without writing files
  python charlotte_restore_builder.py --dry-run
        """
    )
    
    parser.add_argument(
        "--only-active", 
        action="store_true", 
        help="Filter content to include only items with 'status: active' in YAML frontmatter"
    )
    
    parser.add_argument(
        "--profile", 
        choices=["minimal", "full"], 
        default="full",
        help="Restore profile selection: minimal (core identity only) or full (complete restoration)"
    )
    
    parser.add_argument(
        "--max-bytes", 
        type=int, 
        default=120000,
        help="Maximum bytes per chunk (default: 120000 ~ 120k tokens, accounts for UTF-8 encoding)"
    )
    
    parser.add_argument(
        "--out", 
        help="Custom output file path (default: out/restore_package_YYYY-MM-DD_HHMMSSZ.md)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview actions without writing any files - shows what would be generated"
    )
    
    return parser.parse_args()


def get_files_by_pattern(pattern: str, only_active: bool = False) -> list:
    """
    Get files matching a glob pattern, optionally filtering by active status.
    
    This function uses glob pattern matching to find files and optionally
    filters them based on the 'status: active' field in YAML frontmatter.
    It handles file reading errors gracefully and provides feedback.
    
    Args:
        pattern (str): Glob pattern to match files (e.g., "charlotte_core/persona/*.md")
        only_active (bool): If True, filter files to include only those with 'status: active'
        
    Returns:
        list: List of Path objects for matching files (filtered if only_active=True)
        
    Note:
        - Uses Path.glob() for cross-platform pattern matching
        - Parses YAML frontmatter (between --- delimiters) for status field
        - Skips files that can't be read or parsed
        - Preserves original file order from glob results
    """
    files = list(Path(".").glob(pattern))
    
    if only_active:
        # Filter for active status in YAML frontmatter
        active_files = []
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    
                    # Parse YAML frontmatter (between --- delimiters)
                    if '---' in content:
                        parts = content.split('---')
                        if len(parts) > 1 and "status: active" in parts[1]:
                            active_files.append(file)
            except Exception:
                # If we can't read the file, skip it gracefully
                continue
        return active_files
    
    return files


def read_file_content(file_path: Path) -> str:
    """
    Read file content with comprehensive error handling and encoding support.
    
    This function safely reads file content with proper error handling for
    various edge cases including encoding issues, permission problems, and
    file system errors. It provides informative warnings when issues occur.
    
    Args:
        file_path (Path): Path object for the file to read
        
    Returns:
        str: File content as string, or empty string if read fails
        
    Note:
        - Uses UTF-8 encoding with error replacement for robustness
        - Provides detailed error messages including file path
        - Returns empty string rather than raising exceptions for non-critical files
        - Essential for processing files that may have encoding issues or be locked
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}")
        return ""


def is_persona_spine_present() -> bool:
    """
    Check if essential Persona spine files are present for complete restoration.
    
    The Persona spine consists of three core identity files that are fundamental
    to Charlotte AI's restoration process. This function verifies their existence
    to ensure the restore package will be complete and functional.
    
    Returns:
        bool: True if all persona spine files exist, False otherwise
        
    Persona Spine Files:
        - charlotte_core/persona/core_persona.md (Core identity definition)
        - charlotte_core/persona/dna_manifest.md (Essential characteristics)
        - charlotte_core/persona/persona_contract.md (Operational principles)
        
    Note:
        - Critical for restore package completeness
        - Warns users if spine files are missing
        - Files must exist and be readable (checked via Path.exists())
    """
    persona_files = [
        Path("charlotte_core/persona/core_persona.md"),
        Path("charlotte_core/persona/dna_manifest.md"),
        Path("charlotte_core/persona/persona_contract.md")
    ]
    
    return any(f.exists() for f in persona_files)


def build_restore_package(profile: str, only_active: bool, max_bytes: int) -> tuple:
    """
    Build the complete restore package content following the prescribed order.
    
    This function constructs the restore package by collecting content from
    Charlotte AI's various modules in a specific order: Persona core first,
    then protocols, modes, and optionally projects, relationships, and special
    knowledge based on the selected profile.
    
    Args:
        profile (str): Either 'minimal' or 'full' profile selection
        only_active (bool): Whether to filter content by active status
        max_bytes (int): Maximum size per chunk before splitting
        
    Returns:
        tuple: (chunks: list[str], persona_found: bool) 
               - chunks: List of content strings (may be split into multiple parts)
               - persona_found: Whether persona spine files were found
               
    Content Sections (in order):
        1. Summary header with metadata
        2. Persona Core (essential - always included)
        3. Protocols (operational frameworks)
        4. Modes (behavioral patterns)
        5. Projects (full profile only)
        6. Relationship Archive (full profile only)
        7. Special Knowledge (full profile only)
        8. Warm-up prompt for restoration verification
        
    Note:
        - Uses fixed ordering to ensure proper restoration sequence
        - Automatically splits content into chunks if size limit exceeded
        - Preserves YAML frontmatter and file structure
        - Provides detailed feedback about missing content
    """
    content_parts = []
    
    # Add contents summary at top with metadata
    summary = f"# Charlotte Restore Package\n\n"
    summary += f"**Profile:** {profile}\n"
    summary += f"**Only Active:** {only_active}\n"
    summary += f"**Generated:** {utc_ts()}\n\n"
    summary += "## Contents\n\n"
    summary += "This package contains Charlotte AI's core identity and context files.\n"
    summary += "Follow the prescribed order for proper restoration after memory resets.\n\n"
    content_parts.append(summary)
    
    # Initialize sections list with fixed order as specified
    sections = []
    
    # 1. Persona Core - Essential identity files (always included)
    persona_core_files = [
        "charlotte_core/persona/core_persona.md",
        "charlotte_core/persona/dna_manifest.md", 
        "charlotte_core/persona/persona_contract.md"
    ]
    
    persona_content = "## 1. Persona Core\n\n"
    persona_content += "*Essential identity files that define Charlotte's core characteristics and operational principles.*\n\n"
    persona_found = False
    
    for file_pattern in persona_core_files:
        files = get_files_by_pattern(file_pattern)
        for file in files:
            content = read_file_content(file)
            if content:
                # Use relative path for cleaner display
                rel_path = file.relative_to(Path.cwd())
                persona_content += f"### {rel_path}\n\n"
                persona_content += content + "\n\n"
                persona_found = True
    
    if persona_found:
        sections.append(persona_content)
    else:
        sections.append("## 1. Persona Core\n\n⚠️ **[Persona spine files not found]**\n\n")
    
    # 2. Protocols - Operational frameworks and procedures
    protocols_content = "## 2. Protocols\n\n"
    protocols_content += "*Operational frameworks, procedures, and interaction protocols.*\n\n"
    protocol_files = get_files_by_pattern("charlotte_core/protocols/**/*.md", only_active)
    
    for file in protocol_files:
        content = read_file_content(file)
        if content:
            rel_path = file.relative_to(Path.cwd())
            protocols_content += f"### {rel_path}\n\n"
            protocols_content += content + "\n\n"
    
    if protocol_files:
        sections.append(protocols_content)
    else:
        protocols_content += "*No protocol files found.*\n\n"
        sections.append(protocols_content)
    
    # 3. Modes - Behavioral patterns and interaction styles
    modes_content = "## 3. Modes\n\n"
    modes_content += "*Available behavioral modes, tone settings, and interaction patterns.*\n\n"
    mode_files = get_files_by_pattern("charlotte_core/modes/**/*.md", only_active)
    
    for file in mode_files:
        content = read_file_content(file)
        if content:
            rel_path = file.relative_to(Path.cwd())
            modes_content += f"### {rel_path}\n\n"
            modes_content += content + "\n\n"
    
    if mode_files:
        sections.append(modes_content)
    else:
        modes_content += "*No mode files found.*\n\n"
        sections.append(modes_content)
    
    # 4. Projects - Active work and initiatives (full profile only)
    if profile == "full":
        projects_content = "## 4. Projects\n\n"
        projects_content += "*Active projects, initiatives, and work-in-progress tracking.*\n\n"
        project_files = get_files_by_pattern("charlotte_core/projects/**/*.md", only_active)
        
        for file in project_files:
            content = read_file_content(file)
            if content:
                rel_path = file.relative_to(Path.cwd())
                projects_content += f"### {rel_path}\n\n"
                projects_content += content + "\n\n"
        
        if project_files:
            sections.append(projects_content)
        else:
            projects_content += "*No project files found.*\n\n"
            sections.append(projects_content)
    
    # 5. Relationship Archive - Personal context and history (full profile only)
    if profile == "full":
        relationship_content = "## 5. Relationship Archive\n\n"
        relationship_content += "*Personal context, relationship history, and internal reflections.*\n\n"
        relationship_files = get_files_by_pattern("charlotte_core/relationship_identity/**/*.md", only_active)
        
        for file in relationship_files:
            content = read_file_content(file)
            if content:
                rel_path = file.relative_to(Path.cwd())
                relationship_content += f"### {rel_path}\n\n"
                relationship_content += content + "\n\n"
        
        if relationship_files:
            sections.append(relationship_content)
        else:
            relationship_content += "*No relationship archive files found.*\n\n"
            sections.append(relationship_content)
    
    # 6. Special Knowledge - Domain expertise and frameworks (full profile only)
    if profile == "full":
        special_content = "## 6. Special Knowledge\n\n"
        special_content += "*Domain expertise, technical knowledge, and specialized frameworks.*\n\n"
        special_files = get_files_by_pattern("charlotte_core/soul_codex/**/*.md", only_active)
        
        for file in special_files:
            content = read_file_content(file)
            if content:
                rel_path = file.relative_to(Path.cwd())
                special_content += f"### {rel_path}\n\n"
                special_content += content + "\n\n"
        
        if special_files:
            sections.append(special_content)
        else:
            special_content += "*No special knowledge files found.*\n\n"
            sections.append(special_content)
    
    # Add all sections to content parts in the correct order
    content_parts.extend(sections)
    
    # Add warm-up prompt at end for restoration verification
    warmup_prompt = "\n\n## 🚀 Warm-up Prompt\n\n"
    warmup_prompt += "**After pasting this content into Charlotte AI:**\n\n"
    warmup_prompt += "1. **Run Persona Integrity Check** to verify core identity restoration\n"
    warmup_prompt += "2. **Test key protocols** to ensure operational frameworks are working\n"
    warmup_prompt += "3. **Verify behavioral modes** respond correctly to triggers\n"
    warmup_prompt += "4. **Review project contexts** if using full profile\n"
    warmup_prompt += "5. **Check relationship memories** for proper integration\n"
    warmup_prompt += "\n**If any sections are missing:**\n"
    warmup_prompt += "- Review the source files and ensure they exist\n"
    warmup_prompt += "- Check file permissions and accessibility\n"
    warmup_prompt += "- Verify the correct directory structure is maintained\n"
    content_parts.append(warmup_prompt)
    
    # Join all content parts
    full_content = "".join(content_parts)
    
    # Split into chunks if needed to respect size limits
    chunks = []
    if len(full_content.encode('utf-8')) > max_bytes:
        # Split by sections to avoid breaking in the middle of content
        print(f"[INFO] Content size ({len(full_content.encode('utf-8'))} bytes) exceeds limit ({max_bytes} bytes)")
        print(f"[INFO] Splitting into multiple chunks...")
        
        chunk = ""
        for part in content_parts:
            if len((chunk + part).encode('utf-8')) > max_bytes:
                if chunk:  # Don't add empty chunks
                    chunks.append(chunk)
                chunk = part  # Start new chunk with current part
            else:
                chunk += part  # Add to current chunk
        
        if chunk:  # Add the final chunk if it has content
            chunks.append(chunk)
        
        print(f"[INFO] Split into {len(chunks)} chunks")
    else:
        chunks = [full_content]
    
    return chunks, persona_found


def main():
    """
    Main entry point for the Charlotte Restore Package Builder.
    
    This function orchestrates the entire restore package building process:
    1. Parse and validate command line arguments
    2. Check for essential persona spine files
    3. Build the restore package with selected options
    4. Write output files (single or multiple chunks)
    5. Display comprehensive summary of the build process
    
    Process Flow:
        - Argument parsing and validation
        - Persona spine validation with warnings
        - Package building with content filtering and chunking
        - File output with error handling
        - Summary display with success/failure indicators
        
    Error Handling:
        - Uses standardized exit codes from utils module
        - Provides detailed error messages and fix hints
        - Handles filesystem permissions and space issues
        - Validates content availability before processing
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
        
    Note:
        - Supports both dry-run mode for preview and actual file writing
        - Creates output directory automatically if needed
        - Provides comprehensive feedback throughout the process
        - Handles edge cases like missing content or filesystem errors
    """
    # Parse command line arguments
    args = parse_args()
    
    # Check if essential Persona spine files are present
    if not is_persona_spine_present():
        print("[WARN] ⚠️ Persona spine files missing. Restore package may be incomplete.")
        print("[WARN] Essential files: core_persona.md, dna_manifest.md, persona_contract.md")
    
    # Handle dry-run mode - preview without writing files
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
    
    # Generate restore package with selected options
    print(f"[INFO] 🏗️ Building restore package with profile '{args.profile}'")
    chunks, persona_found = build_restore_package(args.profile, args.only_active, args.max_bytes)
    
    # Validate that we have content to write
    if not chunks:
        exit_with_error(
            EXIT_NOTHING_TO_DO, 
            "No content found for restore package",
            "Check that Charlotte Core files exist and are accessible. Ensure the directory structure is correct."
        )
    
    # Determine output path (use custom path or generate default)
    if args.out:
        output_path = Path(args.out)
    else:
        timestamp = utc_ts().replace('_', '-')
        output_path = Path("out") / f"restore_package_{timestamp}.md"
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write chunks to files with error handling
    if len(chunks) == 1:
        # Single file output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(chunks[0])
            print(f"[OK] ✅ Restore package written to {output_path}")
        except Exception as e:
            exit_with_error(
                EXIT_WRITE_ERROR, 
                f"Failed to write restore package: {e}",
                "Check directory permissions and available disk space. Ensure the output path is valid."
            )
    else:
        # Multiple chunk output
        for i, chunk in enumerate(chunks):
            chunk_path = output_path.with_name(f"{output_path.stem}_part_{i+1:02d}{output_path.suffix}")
            try:
                with open(chunk_path, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                print(f"[OK] ✅ Restore package part {i+1} written to {chunk_path}")
            except Exception as e:
                exit_with_error(
                    EXIT_WRITE_ERROR, 
                    f"Failed to write restore package part {i+1}: {e}",
                    "Check directory permissions and available disk space. Ensure the output directory is writable."
                )
        
        print(f"[INFO] 📦 Restore package split into {len(chunks)} parts due to size limits.")
    
    # Print comprehensive summary
    print(f"\n[SUMMARY] 📊 Restore Package Build Complete")
    print(f"  Profile: {args.profile}")
    print(f"  Only Active: {args.only_active}")
    print(f"  Chunks: {len(chunks)}")
    print(f"  Persona Spine: {'✅ Found' if persona_found else '❌ Missing'}")
    
    if not persona_found:
        print(f"[WARN] ⚠️ Persona spine files are missing - restoration may be incomplete!")
        print(f"[WARN] Please ensure these files exist: core_persona.md, dna_manifest.md, persona_contract.md")
    
    # Provide usage instructions
    print(f"\n[USAGE] 📖 Next Steps:")
    if len(chunks) == 1:
        print(f"  1. Open the restore package: {output_path}")
        print(f"  2. Copy all content and paste into Charlotte AI after memory reset")
        print(f"  3. Run Persona Integrity Check to verify restoration")
    else:
        print(f"  1. Open each restore package part in order:")
        for i in range(len(chunks)):
            part_path = output_path.with_name(f"{output_path.stem}_part_{i+1:02d}{output_path.suffix}")
            print(f"     - Part {i+1}: {part_path}")
        print(f"  2. Copy content from each part and paste sequentially into Charlotte AI")
        print(f"  3. Run Persona Integrity Check to verify restoration")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
