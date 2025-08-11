#!/usr/bin/env python3
"""
Ingest OpenAI account export → structured Markdown → intake candidates.
"""
import argparse
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import re

# Add the tools directory to the path so we can import utils
sys.path.append(str(Path(__file__).parent))

from utils import (
    utc_ts, 
    as_posix_sorted, 
    sanitize_filename, 
    redact_sensitive_content,
    safe_extract_path,
    exit_with_error,
    EXIT_BAD_INPUT,
    EXIT_NOTHING_TO_DO,
    EXIT_WRITE_ERROR
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ingest OpenAI ChatGPT export")
    parser.add_argument("--zip", help="Path to export ZIP file")
    parser.add_argument("--dir", help="Path to extracted export directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files")
    return parser.parse_args()


def safe_extract_zip(zip_path: Path, extract_to: Path, max_size_mb: int = 25):
    """Safely extract ZIP file with size and path traversal protection."""
    if not zip_path.exists():
        exit_with_error(EXIT_BAD_INPUT, f"ZIP file not found: {zip_path}", 
                       "Check the file path and ensure the ZIP file exists.")
    
    extract_to.mkdir(parents=True, exist_ok=True)
    
    try:
        from utils import BYTES_PER_MB
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Check file size
                if member.file_size > max_size_mb * BYTES_PER_MB:
                    print(f"[WARN] Skipping large file: {member.filename} ({member.file_size} bytes)")
                    continue
                # Skip directories
                if member.is_dir():
                    continue
                # Safely resolve path to prevent Zip-Slip
                try:
                    target_path = safe_extract_path(extract_to, member.filename)
                except ValueError as e:
                    print(f"[WARN] Skipping unsafe path: {member.filename} - {e}")
                    continue
                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)
                # Extract file
                with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
    except zipfile.BadZipFile:
        exit_with_error(EXIT_BAD_INPUT, f"Invalid ZIP file: {zip_path}", 
                       "Ensure the file is a valid ZIP archive.")


def detect_export_format(export_dir: Path):
    """Detect export format (JSON or HTML) and return the main file."""
    # Prefer JSON if present
    conversations_json = export_dir / "conversations.json"
    if conversations_json.exists():
        return "json", conversations_json
    
    # Look for HTML files
    html_files = list(export_dir.glob("*.html"))
    if html_files:
        return "html", html_files[0]
    
    # No recognized format found
    return None, None


def parse_conversations_json(json_path: Path) -> list:
    """Parse conversations.json file and return structured data."""
    try:
        with open(json_path, 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        exit_with_error(EXIT_BAD_INPUT, f"Invalid JSON in {json_path}: {e}", 
                       "Ensure the file is valid JSON format.")
    except Exception as e:
        exit_with_error(EXIT_BAD_INPUT, f"Error reading {json_path}: {e}", 
                       "Check file permissions and format.")
    return []  # This line ensures we always return a list

    return []  # This line ensures we always return a list
def html_to_text(html_content: str) -> str:
    """Convert HTML content to plain text with conservative parsing."""
    # Remove script and style elements
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    
    # Replace common HTML elements with text equivalents
    html_content = re.sub(r'<br\s*/?>', '\n', html_content)
    html_content = re.sub(r'<p[^>]*>', '\n', html_content)
    html_content = re.sub(r'</p>', '\n', html_content)
    html_content = re.sub(r'<div[^>]*>', '\n', html_content)
    html_content = re.sub(r'</div>', '\n', html_content)
    
    # Remove remaining HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up extra whitespace
    html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
    html_content = html_content.strip()
    
    return html_content


def normalize_timestamp(timestamp: str) -> str:
    """Normalize timestamp to UTC YYYY-MM-DD_HHMMSSZ format."""
    try:
        # Parse various timestamp formats
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If all else fails, use current time
                dt = datetime.now(timezone.utc)
        
        # Ensure UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
            
        return dt.strftime("%Y-%m-%d_%H%M%SZ")
    except Exception:
        # Fallback to current UTC time
        return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")


def create_chat_export_markdown(conversation, export_date: str) -> str:
    """Create structured Markdown for a conversation."""
    title = conversation.get('title', 'Untitled Conversation')
    create_time = normalize_timestamp(conversation.get('create_time', ''))
    
    markdown = f"# {title}\n\n"
    markdown += f"Exported: {export_date}\n"
    markdown += f"Created: {create_time}\n"
    if 'update_time' in conversation:
        update_time = normalize_timestamp(conversation.get('update_time', ''))
        markdown += f"Updated: {update_time}\n"
    markdown += "\n"
    
    # Process messages
    for msg in conversation.get('mapping', {}).values():
        message_data = msg.get('message', {})
        if not message_data:
            continue
            
        role = message_data.get('author', {}).get('role', 'unknown')
        content_parts = message_data.get('content', {}).get('parts', [])
        
        if not content_parts:
            continue
            
        content = '\n\n'.join(str(part) for part in content_parts if part)
        if not content.strip():
            continue
            
        # Format message
        markdown += f"## {role.capitalize()}\n\n"
        markdown += f"{content}\n\n"
        markdown += "---\n\n"
    
    return markdown


def process_conversations(conversations, export_date: str, archives_dir: Path, dry_run: bool = False):
    """Process conversations and create individual Markdown files."""
    thread_files = []
    
    for conv in conversations:
        title = conv.get('title', 'Untitled')
        create_time = normalize_timestamp(conv.get('create_time', ''))
        slug = sanitize_filename(title)
        
        # Create filename with timestamp
        filename = f"{create_time}_{slug}.md"
        file_path = archives_dir / filename
        
        # Generate Markdown content
        content = create_chat_export_markdown(conv, export_date)
        
        # Write file (or preview in dry-run mode)
        if not dry_run:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"[WARN] Failed to write {file_path}: {e}")
                continue
        
        thread_files.append(file_path)
        print(f" - {file_path.relative_to(archives_dir.parent)}")
    
    return thread_files


def create_memory_candidates(thread_files: list, intake_dir: Path, dry_run: bool = False) -> str:
    """Create consolidated memory candidates file."""
    candidates_content = "# Memory Candidates\n\n"
    candidates_content += "Generated from ChatGPT export. Review and refine before processing.\n\n"
    
    for thread_file in thread_files:
        if not thread_file.exists():
            continue
            
        try:
            with open(thread_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                # Redact sensitive information for candidates file
                content = redact_sensitive_content(content)
                candidates_content += f"## From: {thread_file.name}\n\n"
                candidates_content += content
                candidates_content += "\n\n"
        except Exception as e:
            print(f"[WARN] Failed to read {thread_file}: {e}")
            continue
    
    # Write file (or preview in dry-run mode)
    candidates_file = intake_dir / "memory_candidates.md"
    if not dry_run:
        try:
            candidates_file.parent.mkdir(parents=True, exist_ok=True)
            with open(candidates_file, 'w', encoding='utf-8') as f:
                f.write(candidates_content)
        except Exception as e:
            exit_with_error(EXIT_WRITE_ERROR, f"Failed to write {candidates_file}: {e}", 
                           "Check directory permissions and available disk space.")
    
    return candidates_content


def create_ingest_report(export_date: str, thread_count: int, thread_files: list, 
                        reports_dir: Path, dry_run: bool = False):
    """Create ingestion report."""
    report_content = f"# ChatGPT Export Ingest Report\n\n"
    report_content += f"Date: {export_date}\n"
    report_content += f"Threads Processed: {thread_count}\n\n"
    
    report_content += "## Processed Threads\n\n"
    for thread_file in thread_files:
        report_content += f"- {thread_file.name}\n"
    
    report_content += "\n## Summary\n\n"
    report_content += f"Successfully processed {thread_count} conversation threads.\n"
    
    # Write report (or preview in dry-run mode)
    report_file = reports_dir / f"export_ingest_{export_date}.md"
    if not dry_run:
        try:
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
        except Exception as e:
            print(f"[WARN] Failed to write report {report_file}: {e}")
    
    return report_content


def main():
    """Main entry point."""
    args = parse_args()
    
    # Validate inputs
    if not args.zip and not args.dir:
        exit_with_error(EXIT_BAD_INPUT, "Either --zip or --dir must be specified", 
                       "Provide either --zip <export.zip> or --dir <extracted_dir>")
    
    if args.zip and args.dir:
        exit_with_error(EXIT_BAD_INPUT, "Only one of --zip or --dir can be specified", 
                       "Choose either --zip <export.zip> or --dir <extracted_dir>")
    
    # Generate timestamp for this run
    export_date = utc_ts().split('_')[0]  # YYYY-MM-DD part
    
    # Set up directories
    imports_dir = Path("imports") / "chatgpt_export" / export_date
    archives_dir = Path("archives") / "chat_exports" / export_date
    intake_dir = Path("charlotte_ai") / "_intake"
    reports_dir = Path("reports")
    
    if not args.dry_run:
        # Create directories
        for directory in [imports_dir, archives_dir, intake_dir, reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Handle ZIP extraction
    if args.zip:
        zip_path = Path(args.zip).resolve()
        if not args.dry_run:
            print(f"[INFO] Extracting {zip_path} to {imports_dir}")
            safe_extract_zip(zip_path, imports_dir)
        else:
            print(f"[DRY-RUN] Would extract {zip_path} to {imports_dir}")
        export_dir = imports_dir
    else:
        export_dir = Path(args.dir).resolve()
        if not export_dir.exists():
            exit_with_error(EXIT_BAD_INPUT, f"Directory not found: {export_dir}", 
                           "Check the directory path and ensure it exists.")
    
    # Detect export format
    format_type, main_file = detect_export_format(export_dir)
    if not format_type or not main_file:
        exit_with_error(EXIT_BAD_INPUT, "No recognized export format found", 
                       "Ensure the export contains conversations.json or HTML files.")
    print(f"[INFO] Detected export format: {format_type.upper() if format_type else 'UNKNOWN'}")
    # Process export based on format
    conversations: list = []
    if format_type == "json" and main_file is not None:
        conversations = parse_conversations_json(main_file)
    elif format_type == "html" and main_file is not None:
        try:
            with open(str(main_file), 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            # Convert HTML to a simple text format for processing
            text_content = html_to_text(html_content)
            # For now, we'll create a simple structure
            conversations = [{
                "title": "HTML Export",
                "create_time": datetime.now(timezone.utc).isoformat(),
                "mapping": {
                    "1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": [text_content]}
                        }
                    }
                }
            }]
            print("[WARN] HTML export detected - limited parsing applied")
        except Exception as e:
            exit_with_error(EXIT_BAD_INPUT, f"Error processing HTML file: {e}", 
                           "Ensure the HTML file is readable.")
    if not conversations:
        exit_with_error(EXIT_NOTHING_TO_DO, "No conversations found in export", 
                       "Check that the export contains conversation data.")
    print(f"[INFO] Found {len(conversations)} conversations")
    # Process conversations into Markdown files
    if not args.dry_run:
        print(f"[INFO] Creating Markdown files in {archives_dir}")
    else:
        print(f"[DRY-RUN] Would create Markdown files in {archives_dir}")
    thread_files = process_conversations(conversations, export_date, archives_dir, args.dry_run)
    if not thread_files:
        exit_with_error(EXIT_NOTHING_TO_DO, "No threads were processed successfully", 
                       "Check the export format and file permissions.")
    # Create memory candidates file
    if not args.dry_run:
        print(f"[INFO] Creating memory candidates in {intake_dir}")
    else:
        print(f"[DRY-RUN] Would create memory candidates in {intake_dir}")
    candidates_content = create_memory_candidates(thread_files, intake_dir, args.dry_run)
    # Create ingest report
    if not args.dry_run:
        print(f"[INFO] Creating ingest report in {reports_dir}")
    else:
        print(f"[DRY-RUN] Would create ingest report in {reports_dir}")
    report_content = create_ingest_report(export_date, len(thread_files), thread_files, 
                                         reports_dir, args.dry_run)
    # Print summary
    print(f"\n[SUMMARY] ChatGPT Export Ingest")
    print(f"  Format: {format_type.upper() if format_type else 'UNKNOWN'}")
    print(f"  Date: {export_date}")
    print(f"  Threads: {len(thread_files)}")
    print(f"  Candidates: {'Generated' if not args.dry_run else 'Would generate'}")
    print(f"  Report: {'Generated' if not args.dry_run else 'Would generate'}")
    if args.dry_run:
        print(f"\n[DRY-RUN] No files were actually written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
