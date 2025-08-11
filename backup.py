#!/usr/bin/env python3
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
    import yaml  # PyYAML
except Exception:
    yaml = None

def sha256_file(path):
    """Compute SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_str(s):
    """Compute SHA-256 hash of string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_config(path):
    """Load configuration from YAML file."""
    if not os.path.exists(path):
        print(f"[!] Config not found: {path}. Copy config.example.yaml to config.yaml and edit.", file=sys.stderr)
        sys.exit(2)
    if yaml is None:
        print("[!] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def pre_store_bytes(path: str, data: bytes) -> bytes:
    """Hook: Process bytes before storing (no-op stub for future encryption/compression)."""
    return data

def post_restore_bytes(path: str, data: bytes) -> bytes:
    """Hook: Process bytes after restoring (no-op stub for future decryption/decompression)."""
    return data

def matches_any_glob(path, globs):
    """Check if path matches any of the glob patterns."""
    path_posix = path.as_posix()
    return any(path.match(glob) for glob in globs)

def collect_files(source_dirs, include_exts, exclude_globs, follow_symlinks=False, repo_root="."):
    """Collect files with robust filtering using Path.match() for glob support."""
    files = []
    repo_path = Path(repo_root).resolve()
    
    for src in source_dirs:
        src_path = Path(src)
        if not src_path.exists():
            print(f"[!] Source directory not found: {src}", file=sys.stderr)
            continue
        if not src_path.is_dir():
            continue
            
        # Use rglob for better cross-platform support
        for item in src_path.rglob("*"):
            # Check if item is a file (handle symlinks based on follow_symlinks setting)
            if follow_symlinks:
                if not item.is_file():
                    continue
            else:
                # Don't follow symlinks - check if it's a file and not a symlink
                if not item.is_file() or item.is_symlink():
                    continue
                
            # Skip if matches exclude patterns
            try:
                rel_path = item.relative_to(repo_path)
                if matches_any_glob(rel_path, exclude_globs):
                    continue
            except ValueError:
                # If item is not under repo_root, use its direct path
                if matches_any_glob(item, exclude_globs):
                    continue
            
            # Check extension filter
            if include_exts:
                ext = item.suffix.lower()
                if ext not in include_exts:
                    continue
                    
            files.append(item)
    
    # Sort by normalized forward-slash paths for deterministic order
    return sorted(files, key=lambda p: p.relative_to(repo_path).as_posix())

def preflight_checks(repo_root):
    """Run non-blocking preflight checks and return results."""
    repo_path = Path(repo_root)
    checks = []
    
    # Persona activation cues
    persona_cues = repo_path / "charlotte_ai" / "persona" / "activation_block.md"
    if persona_cues.exists() and persona_cues.stat().st_size > 0:
        checks.append(("Persona activation cues", "PASS", ""))
    else:
        checks.append(("Persona activation cues", "WARN", "missing or empty"))
    
    # Soul Codex recency (≤14 days)
    soul_codex = repo_path / "charlotte_ai" / "soul_codex" / "codex_index.md"
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
    
    # Projects legacy vision tags
    projects_index = repo_path / "charlotte_ai" / "projects" / "index.md"
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
    
    # Compliance folder
    compliance_dir = repo_path / "charlotte_ai" / "compliance"
    if compliance_dir.exists() and compliance_dir.is_dir():
        checks.append(("Compliance folder", "PASS", ""))
    else:
        checks.append(("Compliance folder", "WARN", "missing"))
    
    return checks

def print_preflight_results(checks):
    """Print preflight check results in compact table format."""
    print("[Preflight]")
    for name, status, detail in checks:
        detail_str = f" ({detail})" if detail else ""
        print(f"- {name}: {status}{detail_str}")

def build_manifest(files, repo_root, snapshot_rel):
    """Build deterministic manifest with compact JSON format."""
    repo_path = Path(repo_root)
    snapshot_path = Path(snapshot_rel)
    entries = []
    
    # Process files in deterministic order
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
    """Write files to snapshot with hook processing."""
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
            
            # Apply pre-store hook
            processed_data = pre_store_bytes(str(rel_path), file_data)
            
            # Write to snapshot
            dest.write_bytes(processed_data)
        except Exception as e:
            print(f"[!] Error copying file {f}: {e}", file=sys.stderr)
            raise

def get_unique_snapshot_dir(base_snapshot_dir):
    """Ensure snapshot directory name is unique by appending suffix if needed."""
    snapshot_path = Path(base_snapshot_dir)
    counter = 1
    unique_path = snapshot_path
    
    while unique_path.exists():
        unique_path = snapshot_path.parent / f"{snapshot_path.name}-{counter}"
        counter += 1
    
    return str(unique_path)

def git(*args, allow_fail=False):
    """Execute git command with error handling."""
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
    """Check if git is in detached HEAD state."""
    import subprocess
    try:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                              capture_output=True, text=True)
        return result.stdout.strip() == "HEAD"
    except:
        return False

def get_origin_url():
    """Get the origin remote URL."""
    import subprocess
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

def do_plan(cfg):
    """Plan mode: list files that would be included."""
    repo_root = cfg["repo_root"]
    include_exts = set([e.lower() for e in cfg.get("include_exts", [".md", ".markdown", ".yml", ".yaml", ".json", ".txt"])])
    exclude_globs = cfg.get("exclude_globs", [])
    source_dirs = [os.path.join(repo_root, p) for p in cfg.get("source_dirs", ["charlotte_ai"])]
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
    """Snapshot mode: create backup with manifest and git operations."""
    repo_root = cfg["repo_root"]
    include_exts = set([e.lower() for e in cfg.get("include_exts", [".md", ".markdown", ".yml", ".yaml", ".json", ".txt"])])
    exclude_globs = cfg.get("exclude_globs", [])
    source_dirs = [os.path.join(repo_root, p) for p in cfg.get("source_dirs", ["charlotte_ai"])]
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
                    if tag_enabled:
                        git("push", "origin", tag, allow_fail=True)
                    print("[OK] Git: Pushed to origin")
                except subprocess.CalledProcessError:
                    print("[!] Git: No origin remote found - push skipped")
                except FileNotFoundError:
                    print("[!] Git: Git not found - push skipped")

def main():
    """Main entry point."""
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
