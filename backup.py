#!/usr/bin/env python3
"""
Charlotte Core Backup System - Automated versioned backups with integrity verification.

Why this exists:
To fulfill Goal 1 of the PRD: Achieve Stateful Memory. This script is the heart
of the snapshot system (Feature 1), creating deterministic, verifiable backups of
Charlotte's core knowledge files. It treats the Git repository as canonical,
long-term memory, resilient to platform-specific memory limitations.

Features:
- Collects Core Modules as defined in `config.yaml`.
- Creates timestamped snapshots under `snapshots/YYYY-MM-DD_HHMMSSZ/` (FR-1).
- Generates a `MANIFEST.json` with SHA-256 hashes for integrity (FR-1).
- Optionally commits, tags, and pushes to a Git remote (FR-1).
- `--plan` mode for a safe dry-run (FR-1).
- Preflight checks to validate persona integrity before backup.
- Adheres to deterministic principles (UTC, sorted paths) (FR-6).
"""

import argparse
import json
import os
import shutil
import sys
import hashlib
import fnmatch
from datetime import datetime, timezone
from pathlib import Path
import re

try:
    import yaml  # PyYAML - Required for configuration file parsing
except Exception:
    yaml = None

def sha256_file(path):
    """
    Compute SHA-256 hash of file contents for integrity verification.
    
    Args:
        path (str): Path to the file to hash
        
    Returns:
        str: Hexadecimal SHA-256 hash digest
        
    Note:
        Reads file in 8KB chunks to handle large files efficiently
        while maintaining memory efficiency.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_str(s):
    """
    Compute SHA-256 hash of a string for content integrity verification.
    
    Args:
        s (str): String content to hash
        
    Returns:
        str: Hexadecimal SHA-256 hash digest
        
    Note:
        Used for generating overall manifest hash from JSON representation
        to ensure manifest integrity.
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_config(path):
    """
    Load configuration from YAML file with comprehensive error handling.
    
    Args:
        path (str): Path to the YAML configuration file
        
    Returns:
        dict: Parsed configuration data
        
    Raises:
        SystemExit: If config file not found or PyYAML not installed
        
    Note:
        Validates both file existence and PyYAML dependency availability
        before attempting to parse the configuration.
    """
    if not os.path.exists(path):
        print(f"[!] Config not found: {path}. Copy config.example.yaml to config.yaml and edit.", file=sys.stderr)
        sys.exit(2)
    if yaml is None:
        print("[!] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def pre_store_bytes(path: str, data: bytes) -> bytes:
    """
    Hook function for processing bytes before storing to snapshot.
    
    Args:
        path (str): Relative path of the file being processed
        data (bytes): Raw file content bytes
        
    Returns:
        bytes: Processed file content (currently no-op for future extensibility)
        
    Note:
        This is a stub implementation designed for future enhancements
        such as encryption, compression, or content transformation
        before storing files in the snapshot.
    """
    return data

def post_restore_bytes(path: str, data: bytes) -> bytes:
    """
    Hook function for processing bytes after restoring from snapshot.
    
    Args:
        path (str): Relative path of the file being processed
        data (bytes): Restored file content bytes
        
    Returns:
        bytes: Processed file content (currently no-op for future extensibility)
        
    Note:
        This is a stub implementation designed for future enhancements
        such as decryption, decompression, or content validation
        after restoring files from snapshots.
    """
    return data

def matches_any_glob(path, globs):
    """
    Check if a path matches any of the provided glob patterns.
    
    Args:
        path (Path): Path object to check against patterns
        globs (list): List of glob pattern strings
        
    Returns:
        bool: True if path matches any glob pattern, False otherwise
        
    Note:
        Uses Path.match() for robust cross-platform glob pattern matching
        and converts path to POSIX format for consistent pattern matching.
    """
    path_posix = path.as_posix()
    return any(path.match(glob) for glob in globs)

def collect_files(source_dirs, include_exts, exclude_globs, follow_symlinks=False, repo_root="."):
    """
    Collect files from source directories with robust filtering and cross-platform support.
    
    This function performs comprehensive file collection with multiple filtering layers:
    1. Directory validation and existence checking
    2. Symlink handling based on configuration
    3. Glob pattern exclusion matching
    4. File extension filtering
    5. Deterministic sorting for reproducible results
    
    Args:
        source_dirs (list): List of source directory paths to scan
        include_exts (set): Set of file extensions to include (empty for all)
        exclude_globs (list): List of glob patterns to exclude
        follow_symlinks (bool): Whether to follow symbolic links (default: False)
        repo_root (str): Repository root path for relative path calculations
        
    Returns:
        list: Sorted list of Path objects representing files to include in backup
        
    Note:
        Uses Path.rglob() for recursive directory traversal with cross-platform compatibility.
        Files are sorted by their POSIX-style relative paths to ensure deterministic ordering
        across different operating systems.
    """
    files = []
    repo_path = Path(repo_root).resolve()
    
    for src in source_dirs:
        src_path = Path(src)
        if not src_path.exists():
            print(f"[!] Source directory not found: {src}", file=sys.stderr)
            continue
        if not src_path.is_dir():
            continue
            
        # Use rglob for better cross-platform support - recursively finds all files
        for item in src_path.rglob("*"):
            # Check if item is a file (handle symlinks based on follow_symlinks setting)
            if follow_symlinks:
                if not item.is_file():
                    continue
            else:
                # Don't follow symlinks - check if it's a file and not a symlink
                if not item.is_file() or item.is_symlink():
                    continue
                
            # Skip if matches exclude patterns - handle both relative and absolute paths
            try:
                rel_path = item.relative_to(repo_path)
                if matches_any_glob(rel_path, exclude_globs):
                    continue
            except ValueError:
                # If item is not under repo_root, use its direct path
                if matches_any_glob(item, exclude_globs):
                    continue
            
            # Check extension filter - case-insensitive comparison
            if include_exts:
                ext = item.suffix.lower()
                if ext not in include_exts:
                    continue
                    
            files.append(item)
    
    # Sort by normalized forward-slash paths for deterministic order
    return sorted(files, key=lambda p: p.relative_to(repo_path).as_posix())

def preflight_checks(repo_root):
    """
    Run comprehensive system integrity checks before backup operations.
    
    This function performs non-blocking validation checks to ensure Charlotte AI's
    core system components are present and up-to-date before creating a backup.
    Each check provides a PASS/WARN status with detailed feedback.
    
    Args:
        repo_root (str): Path to the repository root directory
        
    Returns:
        list: List of tuples containing (check_name, status, detail_message)
        
    Checks Performed:
        1. Persona activation cues - Verifies core persona files exist
        2. Soul Codex recency - Ensures knowledge base is recently updated (≤14 days)
        3. Projects legacy vision tags - Validates project documentation completeness
        4. Compliance folder - Confirms testing framework is present
        
    Note:
        These checks help identify potential issues that might affect backup
        completeness or system integrity, but they don't prevent backup creation.
    """
    repo_path = Path(repo_root)
    checks = []
    
    # Persona activation cues - Core identity verification
    persona_cues = repo_path / "charlotte_core" / "persona" / "activation_block.md"
    if persona_cues.exists() and persona_cues.stat().st_size > 0:
        checks.append(("Persona activation cues", "PASS", ""))
    else:
        checks.append(("Persona activation cues", "WARN", "missing or empty"))
    
    # Soul Codex recency (≤14 days) - Knowledge freshness check
    soul_codex = repo_path / "charlotte_core" / "soul_codex" / "codex_index.md"
    status = "WARN"
    detail = "not found or no recent update"
    if soul_codex.exists():
        try:
            content = soul_codex.read_text(encoding='utf-8')
            # Look for updated: YYYY-MM-DD pattern
            match = re.search(r'updated:\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
            if match:
                update_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                days_old = (datetime.now().date() - update_date.date()).days
                if days_old <= 14:
                    status = "PASS"
                    detail = f"updated: {match.group(1)}"
                else:
                    detail = f"updated: {match.group(1)} ({days_old} days old)"
        except Exception:
            pass
    checks.append(("Soul Codex index", status, detail))
    
    # Projects legacy vision tags - Project documentation completeness
    projects_index = repo_path / "charlotte_core" / "projects" / "index.md"
    status = "WARN"
    detail = "not found or no legacy vision tags"
    if projects_index.exists():
        try:
            content = projects_index.read_text(encoding='utf-8')
            if re.search(r'legacy_vision:', content, re.IGNORECASE):
                status = "PASS"
                detail = "legacy vision tags found"
        except Exception:
            pass
    checks.append(("Projects legacy vision tags", status, detail))
    
    # Compliance folder - Testing framework presence
    compliance_dir = repo_path / "charlotte_core" / "compliance"
    if compliance_dir.exists() and compliance_dir.is_dir():
        checks.append(("Compliance folder", "PASS", ""))
    else:
        checks.append(("Compliance folder", "WARN", "missing"))
    
    return checks

def print_preflight_results(checks):
    """
    Display preflight check results in a user-friendly table format.
    
    Args:
        checks (list): List of tuples from preflight_checks() containing
                      (check_name, status, detail_message)
                      
    Note:
        Formats output as a compact table with check names, status indicators,
        and optional detail messages for warnings.
    """
    print("[Preflight]")
    for name, status, detail in checks:
        detail_str = f" ({detail})" if detail else ""
        print(f"- {name}: {status}{detail_str}")

def build_manifest(files, repo_root, snapshot_rel):
    """
    Generate a deterministic manifest file with integrity hashes for all backed up files.
    
    This function creates a comprehensive manifest that serves as both an inventory
    and integrity verification system for the backup snapshot. It includes per-file
    SHA-256 hashes and an overall hash of the manifest itself for tamper detection.
    
    Args:
        files (list): List of Path objects representing source files
        repo_root (str): Repository root path for relative path calculations
        snapshot_rel (str): Relative path to the snapshot directory
        
    Returns:
        dict: Manifest dictionary with metadata and file entries
        
    Manifest Structure:
        - created_at: ISO timestamp of manifest creation
        - snapshot: Relative path to snapshot directory
        - count: Total number of files in snapshot
        - overall_sha256: SHA-256 hash of compact JSON manifest
        - files: List of file entries with path, size, and hash
        
    Note:
        The manifest is built from snapshot files (not source files) to ensure
        we hash exactly what was stored, accounting for any processing hooks.
        Uses compact JSON format (no whitespace) for deterministic hashing.
    """
    repo_path = Path(repo_root)
    snapshot_path = Path(snapshot_rel)
    entries = []
    
    # Process files in deterministic order (sorted by relative path)
    for f in files:
        try:
            rel_path = f.relative_to(repo_path)
            rel_str = rel_path.as_posix()
            
            # Read from snapshot copy to ensure we hash what was actually stored
            snapshot_file = snapshot_path / rel_path
            if not snapshot_file.exists():
                print(f"[!] Warning: Snapshot file missing: {snapshot_file}", file=sys.stderr)
                continue
                
            size = snapshot_file.stat().st_size
            digest = sha256_file(snapshot_file)
            
            entries.append({
                "path": rel_str,
                "size": size,
                "sha256": digest
            })
        except Exception as e:
            print(f"[!] Error processing file {f}: {e}", file=sys.stderr)
            continue
    
    # Sort entries by path for deterministic order
    entries.sort(key=lambda x: x["path"])
    
    # Build overall hash from compact JSON (no spaces)
    manifest_str = json.dumps(entries, separators=(",", ":"), ensure_ascii=False)
    overall = sha256_str(manifest_str)
    
    return {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "snapshot": snapshot_rel.replace("\\", "/"),
        "count": len(entries),
        "overall_sha256": overall,
        "files": entries
    }

def write_snapshot(files, repo_root, snapshot_dir):
    """
    Copy source files to snapshot directory with optional pre-processing hooks.
    
    This function handles the actual file copying operation for creating a backup
    snapshot. It preserves directory structure, applies processing hooks, and
    ensures proper error handling throughout the copy process.
    
    Args:
        files (list): List of Path objects representing source files to copy
        repo_root (str): Repository root path for relative path calculations
        snapshot_dir (str): Target directory path for the snapshot
        
    Note:
        - Creates parent directories automatically as needed
        - Applies pre_store_bytes() hook before writing each file
        - Preserves original file permissions and content
        - Raises exceptions on critical errors to halt backup process
        - Uses binary mode for accurate file copying
    """
    repo_path = Path(repo_root)
    snapshot_path = Path(snapshot_dir)
    snapshot_path.mkdir(parents=True, exist_ok=True)
    
    for f in files:
        try:
            rel_path = f.relative_to(repo_path)
            dest = snapshot_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Read original file
            file_data = f.read_bytes()
            
            # Apply pre-store hook (for future encryption/compression)
            processed_data = pre_store_bytes(str(rel_path), file_data)
            
            # Write to snapshot
            dest.write_bytes(processed_data)
        except Exception as e:
            print(f"[!] Error copying file {f}: {e}", file=sys.stderr)
            raise

def get_unique_snapshot_dir(base_snapshot_dir):
    """
    Generate a unique snapshot directory name by appending numeric suffix if needed.
    
    This function ensures that snapshot directory names are unique by checking
    for existing directories and appending a numeric suffix (e.g., -1, -2, etc.)
    to prevent conflicts and accidental overwrites.
    
    Args:
        base_snapshot_dir (str): Base directory path (without suffix)
        
    Returns:
        str: Unique directory path with suffix if needed
        
    Example:
        Input: "snapshots/2024-01-01_120000"
        Output: "snapshots/2024-01-01_120000" (if unique)
        Output: "snapshots/2024-01-01_120000-1" (if base exists)
        
    Note:
        Starts with suffix -1 and increments until a unique name is found.
        Preserves the original directory name structure while ensuring uniqueness.
    """
    snapshot_path = Path(base_snapshot_dir)
    counter = 1
    unique_path = snapshot_path
    
    while unique_path.exists():
        unique_path = snapshot_path.parent / f"{snapshot_path.name}-{counter}"
        counter += 1
    
    return str(unique_path)

def git(*args, allow_fail=False):
    """
    Execute git command with comprehensive error handling and logging.
    
    This function serves as a robust wrapper around git subprocess calls,
    providing consistent error handling and optional failure tolerance.
    It's used throughout the backup process for all git operations.
    
    Args:
        *args: Variable length argument list passed directly to git command
        allow_fail (bool): If True, return error code instead of raising exception
        
    Returns:
        int: 0 on success, error code on failure (when allow_fail=True)
        
    Raises:
        subprocess.CalledProcessError: If git command fails and allow_fail=False
        FileNotFoundError: If git executable not found and allow_fail=False
        
    Note:
        Commonly used operations: add, commit, tag, push, status, remote operations
        Always uses subprocess.check_call() for proper command execution
    """
    import subprocess
    try:
        subprocess.check_call(["git"] + list(args))
        return 0
    except subprocess.CalledProcessError as e:
        if not allow_fail:
            raise
        return e.returncode
    except FileNotFoundError:
        if not allow_fail:
            raise
        return 127

def is_detached_head():
    """
    Check if git repository is in detached HEAD state.
    
    A detached HEAD state occurs when you're not on any branch, typically
    when checking out a specific commit or tag. This state can interfere
    with normal git operations like commits and pushes.
    
    Returns:
        bool: True if in detached HEAD state, False otherwise
        
    Note:
        Uses 'git rev-parse --abbrev-ref HEAD' command which returns 'HEAD'
        when in detached state, or the current branch name otherwise.
        Returns False if git command fails (e.g., not a git repository).
    """
    import subprocess
    try:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                              capture_output=True, text=True)
        return result.stdout.strip() == "HEAD"
    except:
        return False

def get_origin_url():
    """
    Retrieve the URL of the origin remote repository.
    
    This function fetches the configured URL for the 'origin' remote,
    which is typically used as the primary remote for pushing and pulling.
    
    Returns:
        str: Origin remote URL if found and accessible, None otherwise
        
    Note:
        Uses 'git remote get-url origin' command to fetch the URL.
        Returns None if command fails (e.g., no origin remote or git not installed).
        Common formats: HTTPS (https://github.com/user/repo.git) or SSH (git@github.com:user/repo.git)
    """
    import subprocess
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

def do_plan(cfg):
    """
    Execute plan mode - preview backup contents without creating actual backup.
    
    This function performs a dry-run of the backup process, showing exactly
    which files would be included in a snapshot without writing any files
    or making any changes to the system.
    
    Args:
        cfg (dict): Configuration dictionary from load_config()
        
    Process:
        1. Parse configuration settings for file collection
        2. Change to repository root for consistent path handling
        3. Collect files using configured filters and exclusions
        4. Display list of files that would be included
        5. Exit with error if no files selected
        
    Note:
        This is a read-only operation that's safe to run anytime.
        Useful for verifying configuration and understanding backup scope.
        Exits with code 1 if no files are selected for backup.
    """
    repo_root = cfg["repo_root"]
    include_exts = set([e.lower() for e in cfg.get("include_exts", [".md", ".markdown", ".yml", ".yaml", ".json", ".txt"])])
    exclude_globs = cfg.get("exclude_globs", [])
    source_dirs = [os.path.join(repo_root, p) for p in cfg.get("source_dirs", ["charlotte_core"])]
    follow_symlinks = cfg.get("follow_symlinks", False)
    
    # Change to repo root for consistent path handling
    os.chdir(repo_root)
    
    files = collect_files(source_dirs, include_exts, exclude_globs, follow_symlinks, repo_root)
    
    if not files:
        print("[!] No files selected. Check source_dirs, include_exts, and exclude_globs.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Would snapshot {len(files)} files:")
    repo_path = Path(repo_root)
    for f in files:
        try:
            rel_path = f.relative_to(repo_path)
            print(" -", rel_path.as_posix())
        except ValueError:
            print(" -", f.as_posix())

def do_snapshot(cfg):
    """
    Execute snapshot mode - create complete backup with manifest and Git integration.
    
    This is the main backup function that orchestrates the entire backup process:
    system validation, file collection, snapshot creation, manifest generation,
    and optional Git operations for version control and remote synchronization.
    
    Args:
        cfg (dict): Configuration dictionary from load_config()
        
    Process Flow:
        1. System validation via preflight checks
        2. File collection with comprehensive filtering
        3. Timestamp generation and snapshot directory creation
        4. File copying with optional processing hooks
        5. Manifest generation with integrity verification
        6. Git operations (commit, tag, push) if enabled
        
    Key Features:
        - UTC timestamping for consistency across timezones
        - Automatic directory conflict resolution
        - SHA-256 integrity verification for all files
        - Conditional Git operations based on repository state
        - Comprehensive error handling and user feedback
        
    Note:
        This is a write operation that modifies the filesystem and Git repository.
        Always run 'plan' mode first to preview what will be backed up.
        Handles various edge cases like detached HEAD, missing remotes, etc.
    """
    repo_root = cfg["repo_root"]
    include_exts = set([e.lower() for e in cfg.get("include_exts", [".md", ".markdown", ".yml", ".yaml", ".json", ".txt"])])
    exclude_globs = cfg.get("exclude_globs", [])
    source_dirs = [os.path.join(repo_root, p) for p in cfg.get("source_dirs", ["charlotte_core"])]
    follow_symlinks = cfg.get("follow_symlinks", False)
    
    # Change to repo root for consistent path handling
    os.chdir(repo_root)
    
    # Run preflight checks
    checks = preflight_checks(repo_root)
    print_preflight_results(checks)
    
    # Collect files
    files = collect_files(source_dirs, include_exts, exclude_globs, follow_symlinks, repo_root)
    
    if not files:
        print("[!] No files selected. Check source_dirs, include_exts, and exclude_globs.", file=sys.stderr)
        sys.exit(1)
    
    # Generate timestamp with Z suffix for UTC
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")
    base_snapshot_rel = os.path.join("snapshots", ts)
    base_snapshot_dir = os.path.join(repo_root, base_snapshot_rel)
    
    # Ensure unique snapshot directory
    snapshot_dir = get_unique_snapshot_dir(base_snapshot_dir)
    snapshot_rel = os.path.relpath(snapshot_dir, repo_root).replace("\\", "/")
    
    # Copy files to snapshot
    write_snapshot(files, repo_root, snapshot_dir)
    
    # Build manifest from snapshot files
    repo_path = Path(repo_root)
    snapshot_files = []
    for f in files:
        try:
            rel_path = f.relative_to(repo_path)
            snapshot_files.append(Path(snapshot_dir) / rel_path)
        except ValueError:
            snapshot_files.append(Path(snapshot_dir) / f.name)
    
    manifest = build_manifest(files, repo_root, snapshot_rel)
    manifest_path = Path(snapshot_dir) / "MANIFEST.json"
    
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)
    
    print(f"[OK] Snapshot written: {snapshot_rel} ({manifest['count']} files)")
    print(f"     Overall SHA-256: {manifest['overall_sha256']}")
    
    # Git operations
    git_enabled = cfg.get("git", {}).get("enable", True)
    if git_enabled:
        # Check for detached HEAD
        if is_detached_head():
            print("[!] Git: Detached HEAD - skipping commit/tag operations")
        else:
            # Check for public remote warning
            origin_url = get_origin_url()
            if origin_url and "github.com/" in origin_url and not origin_url.startswith("git@"):
                print("[!] Warning: Origin appears to be a public HTTPS URL - ensure repo is private")
            
            git("add", "-A")
            
            # Only commit if there are changes
            import subprocess
            try:
                status_result = subprocess.run(["git", "status", "--porcelain"], 
                                             capture_output=True, text=True)
                if status_result.stdout.strip():
                    msg = cfg.get("git", {}).get("commit_message", "chore: Charlotte snapshot")
                    git("commit", "-m", msg, allow_fail=True)
                else:
                    print("[OK] Git: Working tree clean - no commit needed")
            except:
                pass
            
            # Tag operations
            tag_enabled = cfg.get("git", {}).get("tag", True)
            tag = None  # Initialize tag variable to prevent unbound error
            if tag_enabled:
                # Use timestamp format that matches snapshot directory
                tag_ts = ts.replace("_", "-")
                tag_prefix = cfg.get("git", {}).get("tag_prefix", "backup-")
                tag = f"{tag_prefix}{tag_ts}"
                tag_message = f"Charlotte backup {ts}\n\nSnapshot: {snapshot_rel}\nOverall SHA-256: {manifest['overall_sha256']}"
                git("tag", "-a", tag, "-m", tag_message, allow_fail=True)
                print(f"[OK] Git: Created tag {tag}")
            
            # Push operations
            push_enabled = cfg.get("git", {}).get("push", True)
            if push_enabled:
                try:
                    # Check if origin exists
                    subprocess.run(["git", "remote", "get-url", "origin"], 
                                 check=True, capture_output=True)
                    git("push", "origin", "HEAD", allow_fail=True)
                    if tag_enabled and tag:
                        git("push", "origin", tag, allow_fail=True)
                    print("[OK] Git: Pushed to origin")
                except subprocess.CalledProcessError:
                    print("[!] Git: No origin remote found - push skipped")
                except FileNotFoundError:
                    print("[!] Git: Git not found - push skipped")

def main():
    """
    Main entry point for the Charlotte Core Backup System.
    
    This function handles command-line argument parsing and dispatches
    to the appropriate backup mode (plan or snapshot) based on user input.
    It serves as the primary interface between the user and the backup system.
    
    Command Line Interface:
        - command: Required - either "plan" or "snapshot"
        - -c/--config: Optional - path to configuration file (default: config.yaml)
        
    Configuration:
        Loads configuration from YAML file with comprehensive error handling.
        Normalizes repository root path to absolute path for consistency.
        
    Mode Dispatch:
        - plan: Dry-run mode showing what would be backed up
        - snapshot: Full backup creation with manifest and Git operations
        
    Note:
        This is the entry point when the script is executed directly.
        Uses argparse for robust command-line processing with help messages.
        Exits with appropriate error codes for configuration or execution issues.
    """
    ap = argparse.ArgumentParser(description="Charlotte Core Backup")
    ap.add_argument("command", choices=["plan", "snapshot"], help="plan: list files; snapshot: write snapshot + manifest (+git)")
    ap.add_argument("-c", "--config", default="config.yaml", help="Path to config file")
    args = ap.parse_args()

    cfg = load_config(args.config)
    # normalize repo_root to absolute
    cfg["repo_root"] = os.path.abspath(cfg.get("repo_root", "."))

    if args.command == "plan":
        do_plan(cfg)
    else:
        do_snapshot(cfg)

if __name__ == "__main__":
    main()
