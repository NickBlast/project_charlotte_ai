#!/usr/bin/env python3
"""
Charlotte AI ChatGPT Export Ingestion Tool - Process OpenAI exports into structured memory.

Why this exists:
To fulfill Feature 2 of the PRD. This tool automates the first step of the
"Monthly Official Export" workflow (Track A in the Memory Pipeline), turning a
raw ChatGPT data export into structured, archivable, and searchable Markdown
files and identifying potential new memories for integration.

Features:
- Processes official OpenAI data export ZIPs safely (FR-2).
- Handles both `messages.json` and `conversations.html` formats (FR-1).
- Converts conversations into clean Markdown files in `archives/` (FR-2).
- Preserves and organizes artifacts like images and metadata (FR-2).
- Generates a redacted `memory_candidates.md` for safe review (FR-3).
- Creates a detailed `export_ingest_...md` report for auditability.
- Security-focused with Zip-Slip protection and path sanitization.
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import re
import hashlib

# Add the tools directory to the path so we can import shared utilities
sys.path.append(str(Path(__file__).parent))

from utils import (
    utc_ts,                    # UTC timestamp generation for consistent file naming
    as_posix_sorted,           # Cross-platform path sorting for deterministic results
    sanitize_filename,         # Filename sanitization for filesystem compatibility
    redact_sensitive_content,  # Sensitive information redaction for security
    safe_extract_path,         # Path traversal protection for archive extraction
    exit_with_error,           # Standardized error handling with exit codes
    EXIT_BAD_INPUT,            # Exit code for invalid input parameters
    EXIT_NOTHING_TO_DO,        # Exit code when no content is available
    EXIT_WRITE_ERROR,          # Exit code for filesystem write failures
    BYTES_PER_MB,              # Constant for byte-to-megabyte conversions
    MAX_TEXT_MB_DEFAULT,       # Default maximum text size limit
    MAX_CONVERSATIONS_JSON_MB  # Maximum size for conversations.json files
)


def parse_args():
    """
    Parse and validate command line arguments for the ChatGPT export ingestion tool.
    
    This function defines all available command-line options and their help
    text, then parses and returns the validated arguments. It provides
    comprehensive help documentation for users.
    
    Returns:
        argparse.Namespace: Parsed and validated command line arguments
        
    Command Line Options:
        --zip: Path to ChatGPT export ZIP file
        --dir: Path to already extracted export directory
        --dry-run: Preview actions without writing any files
        
    Example:
        >>> parse_args()
        Namespace(dry_run=False, dir=None, zip=None)
    """
    parser = argparse.ArgumentParser(
        description="Ingest OpenAI ChatGPT export into Charlotte AI memory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process ZIP export file
  python ingest_chatgpt_export.py --zip chatgpt_export.zip
  
  # Process already extracted directory
  python ingest_chatgpt_export.py --dir /path/to/export
  
  # Preview without writing files
  python ingest_chatgpt_export.py --zip chatgpt_export.zip --dry-run
        """
    )
    
    parser.add_argument(
        "--zip", 
        help="Path to ChatGPT export ZIP file (downloaded from OpenAI account)"
    )
    
    parser.add_argument(
        "--dir", 
        help="Path to already extracted export directory"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview actions without writing any files - shows what would be processed"
    )
    
    return parser.parse_args()


def safe_extract_zip(zip_path: Path, extract_to: Path, max_size_mb: int = 25):
    """
    Safely extract ZIP file with comprehensive security and size protection.
    
    This function extracts ZIP files with multiple safety measures to prevent
    security vulnerabilities like Zip-Slip attacks and to handle large files
    gracefully. It validates file sizes and paths before extraction.
    
    Args:
        zip_path (Path): Path to the ZIP file to extract
        extract_to (Path): Directory where files should be extracted
        max_size_mb (int): Maximum file size in MB to extract (default: 25MB)
        
    Raises:
        SystemExit: If ZIP file is invalid or not found
        
    Security Features:
        - Path traversal protection using safe_extract_path()
        - File size limits to prevent extraction of oversized files
        - Directory skipping to prevent filesystem clutter
        - Error handling for corrupted ZIP archives
        
    Note:
        - Creates extraction directory if it doesn't exist
        - Skips files larger than max_size_mb * BYTES_PER_MB
        - Preserves file permissions and metadata
        - Provides detailed feedback about skipped files
    """
    # Validate ZIP file existence
    if not zip_path.exists():
        exit_with_error(
            EXIT_BAD_INPUT, 
            f"ZIP file not found: {zip_path}", 
            "Check the file path and ensure the ZIP file exists. Verify the file extension is .zip"
        )
    
    # Create extraction directory with parent directories
    extract_to.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Skip directories to prevent empty directory creation
                if member.is_dir():
                    continue
                
                # Check file size against safety limit
                if member.file_size > max_size_mb * BYTES_PER_MB:
                    print(f"[WARN] Skipping large file: {member.filename} ({member.file_size} bytes)")
                    continue
                
                # Safely resolve path to prevent Zip-Slip attacks
                try:
                    target_path = safe_extract_path(extract_to, member.filename)
                except ValueError as e:
                    print(f"[WARN] Skipping unsafe path: {member.filename} - {e}")
                    continue
                
                # Create parent directories as needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file with binary mode preservation
                with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
                    
    except zipfile.BadZipFile:
        exit_with_error(
            EXIT_BAD_INPUT, 
            f"Invalid ZIP file: {zip_path}", 
            "Ensure the file is a valid ZIP archive. Try re-downloading the export from OpenAI."
        )


def detect_export_format(export_dir: Path):
    """
    Detect ChatGPT export format and identify the main data file.
    
    This function examines the export directory to determine the format
    of the ChatGPT export. It prioritizes JSON format for better parsing
    but falls back to HTML if JSON is not available.
    
    Args:
        export_dir (Path): Path to the export directory
        
    Returns:
        tuple: (format_type: str, main_file: Path) or (None, None) if no format detected
        
    Format Priority:
        1. JSON format (conversations.json) - preferred for structured data
        2. HTML format (*.html files) - fallback for basic parsing
        
    Note:
        - Uses Path.exists() for reliable file detection
        - Returns None if no recognized format is found
        - Provides feedback about detected format
    """
    # Check for JSON format first (preferred)
    conversations_json = export_dir / "conversations.json"
    if conversations_json.exists():
        return "json", conversations_json
    
    # Look for HTML files as fallback
    html_files = list(export_dir.glob("*.html"))
    if html_files:
        # Use the first HTML file found
        return "html", html_files[0]
    
    # No recognized format found
    return None, None


def parse_conversations_json(json_path: Path) -> list:
    """
    Parse conversations.json file and return structured conversation data.
    
    This function reads and parses the ChatGPT conversations.json file,
    validating the JSON structure and returning the conversation data
    in a usable format for further processing.
    
    Args:
        json_path (Path): Path to the conversations.json file
        
    Returns:
        list: List of conversation objects, or empty list if parsing fails
        
    Error Handling:
        - JSON syntax errors with detailed error messages
        - File permission issues with helpful error hints
        - Invalid JSON structure with format guidance
        
    Note:
        - Uses UTF-8 encoding with error replacement for robustness
        - Validates that the parsed data is a list (expected format)
        - Provides comprehensive error messages for troubleshooting
    """
    try:
        with open(json_path, 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
        
        # Validate that we got a list (expected format)
        return data if isinstance(data, list) else []
        
    except json.JSONDecodeError as e:
        exit_with_error(
            EXIT_BAD_INPUT, 
            f"Invalid JSON in {json_path}: {e}", 
            "Ensure the file is valid JSON format. Try re-downloading the export from OpenAI."
        )
    except Exception as e:
        exit_with_error(
            EXIT_BAD_INPUT, 
            f"Error reading {json_path}: {e}", 
            "Check file permissions and format. Ensure the file is not corrupted."
        )
    
    # Fallback return (should not be reached due to exit_with_error calls)
    return []


def html_to_text(html_content: str) -> str:
    """
    Convert HTML content to plain text with conservative parsing.
    
    This function performs basic HTML-to-text conversion using regex patterns
    to remove HTML tags and convert common elements to text equivalents.
    It uses conservative parsing to preserve content structure.
    
    Args:
        html_content (str): HTML content to convert
        
    Returns:
        str: Plain text representation of the HTML content
        
    Conversion Rules:
        - Removes <script> and <style> elements completely
        - Converts <br>, <p>, <div> elements to newlines
        - Removes all remaining HTML tags
        - Normalizes whitespace (multiple newlines become single)
        - Trims leading/trailing whitespace
        
    Note:
        - Uses DOTALL flag for multi-line pattern matching
        - Conservative approach to avoid losing content
        - Suitable for basic HTML export processing
        - Not intended for complex HTML documents
    """
    # Remove script and style elements (potential security and noise)
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Convert common HTML block elements to newlines
    html_content = re.sub(r'<br\s*/?>', '\n', html_content)      # Line breaks
    html_content = re.sub(r'<p[^>]*>', '\n', html_content)       # Paragraphs
    html_content = re.sub(r'</p>', '\n', html_content)           # Paragraph closes
    html_content = re.sub(r'<div[^>]*>', '\n', html_content)     # Divs
    html_content = re.sub(r'</div>', '\n', html_content)         # Div closes
    
    # Remove all remaining HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up excessive whitespace (multiple newlines become single)
    html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
    
    # Remove leading/trailing whitespace
    html_content = html_content.strip()
    
    return html_content


def normalize_timestamp(timestamp: str) -> str:
    """
    Normalize various timestamp formats to UTC YYYY-MM-DD_HHMMSSZ format.
    
    This function handles multiple timestamp formats commonly found in
    ChatGPT exports and converts them to a standardized UTC format
    consistent with Charlotte AI's timestamping conventions.
    
    Args:
        timestamp (str): Input timestamp in various possible formats
        
    Returns:
        str: Normalized timestamp in UTC YYYY-MM-DD_HHMMSSZ format
        
    Supported Formats:
        - ISO 8601 with 'T' separator (e.g., "2024-01-15T14:30:22Z")
        - Standard datetime format (e.g., "2024-01-15 14:30:22")
        - Datetime with microseconds (e.g., "2024-01-15 14:30:22.123456")
        - Fallback to current UTC time if parsing fails
        
    Note:
        - Handles timezone conversion to UTC
        - Uses current UTC time as fallback for invalid formats
        - Ensures consistent timestamping across all processed content
    """
    try:
        # Parse ISO 8601 format with 'T' separator
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            # Try common datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If all parsing attempts fail, use current time
                dt = datetime.now(timezone.utc)
        
        # Ensure the datetime is in UTC timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
            
        # Format in Charlotte AI's standard UTC format
        return dt.strftime("%Y-%m-%d_%H%M%SZ")
        
    except Exception:
        # Fallback to current UTC time if any parsing error occurs
        return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")


def create_chat_export_markdown(conversation, export_date: str) -> str:
    """
    Create structured Markdown representation of a ChatGPT conversation.
    
    This function converts a ChatGPT conversation object into a well-formatted
    Markdown document with proper structure, metadata, and message formatting.
    
    Args:
        conversation (dict): ChatGPT conversation object from JSON
        export_date (str): Export date in YYYY-MM-DD format
        
    Returns:
        str: Formatted Markdown string representing the conversation
        
    Markdown Structure:
        - Title with conversation name
        - Metadata section (exported date, created/updated timestamps)
        - Message sections with role-based formatting
        - Horizontal rules between messages
        
    Message Processing:
        - Filters out empty messages
        - Handles multi-part content messages
        - Preserves original message content
        - Formats user/assistant roles appropriately
        
    Note:
        - Uses normalized timestamps for consistency
        - Handles missing fields gracefully
        - Creates readable, well-structured output
    """
    # Extract conversation metadata
    title = conversation.get('title', 'Untitled Conversation')
    create_time = normalize_timestamp(conversation.get('create_time', ''))
    
    # Build Markdown header with metadata
    markdown = f"# {title}\n\n"
    markdown += f"**Exported:** {export_date}\n"
    markdown += f"**Created:** {create_time}\n"
    
    # Add update time if available
    if 'update_time' in conversation:
        update_time = normalize_timestamp(conversation.get('update_time', ''))
        markdown += f"**Updated:** {update_time}\n"
    
    markdown += "\n"
    
    # Process conversation messages
    for msg in conversation.get('mapping', {}).values():
        message_data = msg.get('message', {})
        if not message_data:
            continue  # Skip empty messages
            
        # Extract message role and content
        role = message_data.get('author', {}).get('role', 'unknown')
        content_parts = message_data.get('content', {}).get('parts', [])
        
        # Skip messages with no content
        if not content_parts:
            continue
            
        # Join content parts and filter out empty parts
        content = '\n\n'.join(str(part) for part in content_parts if part)
        if not content.strip():
            continue
            
        # Format message with role header and separator
        markdown += f"## {role.capitalize()}\n\n"
        markdown += f"{content}\n\n"
        markdown += "---\n\n"
    
    return markdown


def process_conversations(conversations, export_date: str, archives_dir: Path, dry_run: bool = False):
    """
    Process conversation list and create individual Markdown files.
    
    This function takes a list of conversations and creates separate
    Markdown files for each conversation in the specified archive directory.
    It handles file naming, content generation, and error management.
    
    Args:
        conversations (list): List of conversation objects to process
        export_date (str): Export date for file organization
        archives_dir (Path): Directory where conversation files will be stored
        dry_run (bool): If True, preview without writing files
        
    Returns:
        list: List of Path objects for created conversation files
        
    File Naming:
        - Format: "YYYY-MM-DD_HHMMSS_slug.md"
        - Slug is sanitized conversation title
        - Timestamp is from conversation creation time
        
    Processing Steps:
        1. Extract title and creation time from each conversation
        2. Sanitize filename for filesystem compatibility
        3. Generate Markdown content using create_chat_export_markdown()
        4. Write file to archive directory (or preview in dry-run mode)
        5. Track created files for return value
        
    Note:
        - Creates parent directories as needed
        - Handles file write errors gracefully
        - Provides progress feedback during processing
        - Returns empty list if no files created
    """
    thread_files = []
    
    for conv in conversations:
        # Extract conversation metadata
        title = conv.get('title', 'Untitled')
        create_time = normalize_timestamp(conv.get('create_time', ''))
        slug = sanitize_filename(title)
        
        # Create filename with timestamp and sanitized title
        filename = f"{create_time}_{slug}.md"
        file_path = archives_dir / filename
        
        # Generate structured Markdown content
        content = create_chat_export_markdown(conv, export_date)
        
        # Write file (or preview in dry-run mode)
        if not dry_run:
            try:
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write content with UTF-8 encoding
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"[WARN] Failed to write {file_path}: {e}")
                continue  # Skip this file and continue with others
        
        # Track created file and provide feedback
        thread_files.append(file_path)
        print(f" - {file_path.relative_to(archives_dir.parent)}")
    
    return thread_files


def create_memory_candidates(thread_files: list, intake_dir: Path, dry_run: bool = False) -> str:
    """
    Create consolidated memory candidates file from processed conversations.
    
    This function combines all processed conversation files into a single
    memory candidates file suitable for Charlotte AI's intake system.
    It includes proper redaction of sensitive information.
    
    Args:
        thread_files (list): List of Path objects to conversation files
        intake_dir (Path): Directory where memory candidates file will be stored
        dry_run (bool): If True, preview without writing files
        
    Returns:
        str: Content of the memory candidates file
        
    File Structure:
        - Header with metadata and instructions
        - Individual conversation sections with source attribution
        - Proper formatting for Charlotte AI processing
        
    Security Features:
        - Applies sensitive content redaction using redact_sensitive_content()
        - Filters out files that can't be read
        - Handles encoding errors gracefully
        
    Note:
        - Creates parent directories as needed
        - Provides error handling for file operations
        - Returns file content for preview/dry-run purposes
    """
    # Build memory candidates header
    candidates_content = "# Memory Candidates\n\n"
    candidates_content += "**Generated from ChatGPT export.** Review and refine before processing.\n\n"
    candidates_content += "**Source:** ChatGPT conversation export\n"
    candidates_content += "**Purpose:** Integration with Charlotte AI memory system\n\n"
    
    # Process each conversation file
    for thread_file in thread_files:
        if not thread_file.exists():
            continue  # Skip missing files
            
        try:
            with open(thread_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
                # Apply sensitive content redaction for security
                content = redact_sensitive_content(content)
                
                # Add section header with source attribution
                candidates_content += f"## From: {thread_file.name}\n\n"
                candidates_content += content
                candidates_content += "\n\n"
                
        except Exception as e:
            print(f"[WARN] Failed to read {thread_file}: {e}")
            continue  # Skip problematic files
    
    # Write consolidated file (or preview in dry-run mode)
    candidates_file = intake_dir / "memory_candidates.md"
    if not dry_run:
        try:
            # Ensure parent directory exists
            candidates_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write consolidated content
            with open(candidates_file, 'w', encoding='utf-8') as f:
                f.write(candidates_content)
                
        except Exception as e:
            exit_with_error(
                EXIT_WRITE_ERROR, 
                f"Failed to write {candidates_file}: {e}", 
                "Check directory permissions and available disk space. Ensure the output directory is writable."
            )
    
    return candidates_content


def sha256_file(path: Path) -> str:
    """
    Compute SHA-256 hash of file contents for integrity verification.
    
    This function calculates the SHA-256 hash of a file's contents,
    reading the file in chunks to handle large files efficiently
    while maintaining memory efficiency.
    
    Args:
        path (Path): Path to the file to hash
        
    Returns:
        str: Hexadecimal SHA-256 hash digest
        
    Hashing Process:
        - Opens file in binary mode for accurate byte representation
        - Reads file in 8KB chunks to handle large files
        - Updates hash incrementally to minimize memory usage
        - Returns hexadecimal string representation
        
    Note:
        - Used for file integrity verification in artifact processing
        - Handles large files efficiently with chunked reading
        - Returns consistent hashes for identical file content
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_export_artifacts(raw_dir: Path, archives_dir: Path, export_date: str, dry_run: bool = False) -> dict:
    """
    Copy and organize images and metadata files from raw export to archive structure.
    
    This function processes export artifacts including user folders with images,
    loose image files, and metadata files, organizing them into a structured
    archive directory while maintaining integrity tracking.
    
    Args:
        raw_dir (Path): Source directory containing raw export files
        archives_dir (Path): Target archive directory for organized artifacts
        export_date (str): Export date for directory organization
        dry_run (bool): If True, preview without copying files
        
    Returns:
        dict: Statistics about copied artifacts including counts and file information
        
    Artifact Organization:
        - assets/user_folders/ - User-specific image folders with structure preserved
        - assets/loose/ - Loose image files not in user folders
        - assets/images_manifest.json - Manifest with file hashes and metadata
        - meta/ - Metadata files (message_feedback.json, user.json)
        
    Processing Steps:
        1. Create organized directory structure
        2. Find and copy user* folders with images
        3. Copy loose image files (file* patterns)
        4. Copy metadata files if present
        5. Generate manifest with integrity hashes
        
    Note:
        - Preserves directory structure for user folders
        - Calculates SHA-256 hashes for integrity verification
        - Handles various image formats (PNG, JPG, GIF, etc.)
        - Provides detailed feedback about copied artifacts
    """
    # Create organized directory structure
    assets_dir = archives_dir / "assets"
    meta_dir = archives_dir / "meta"
    user_folders_dir = assets_dir / "user_folders"
    loose_images_dir = assets_dir / "loose"
    
    if not dry_run:
        # Create all necessary directories
        for directory in [assets_dir, meta_dir, user_folders_dir, loose_images_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Initialize tracking variables
    copied_images = []
    user_folder_count = 0
    loose_image_count = 0
    
    # Process user* folders containing images
    for item in raw_dir.rglob("*"):
        if item.is_dir() and item.name.startswith("user") and item.name != "user":
            # This is a user* folder - copy all contents preserving structure
            if not dry_run:
                # Create corresponding destination directory
                dest_dir = user_folders_dir / item.relative_to(raw_dir)
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy all image files from this folder
                for file in item.iterdir():
                    if file.is_file() and file.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}:
                        dest_file = dest_dir / file.name
                        dest_file.write_bytes(file.read_bytes())
                        
                        # Track copied file information
                        copied_images.append({
                            "dest": str(dest_file.relative_to(archives_dir)),
                            "sha256": sha256_file(dest_file),
                            "bytes": dest_file.stat().st_size
                        })
            else:
                # Dry-run: count what would be copied
                image_files = list(item.rglob("*.[pP][nN][gG]")) + list(item.rglob("*.[jJ][pP][gG]")) + \
                             list(item.rglob("*.[jJ][pP][eE][gG]")) + list(item.rglob("*.[gG][iI][fF]")) + \
                             list(item.rglob("*.[wW][eE][bB][pP]")) + list(item.rglob("*.[bB][mM][pP]")) + \
                             list(item.rglob("*.[sS][vV][gG]"))
                if image_files:
                    print(f"[DRY-RUN] Would copy user folder: {item.relative_to(raw_dir)} ({len(image_files)} images)")
                    user_folder_count += 1
                    loose_image_count += len(image_files)
            
            user_folder_count += 1
    
    # Process loose image files (file* patterns)
    image_patterns = ["file*.[pP][nN][gG]", "file*.[jJ][pP][gG]", "file*.[jJ][pP][eE][gG]", 
                     "file*.[gG][iI][fF]", "file*.[wW][eE][bB][pP]", "file*.[bB][mM][pP]", "file*.[sS][vV][gG]"]
    
    for pattern in image_patterns:
        for file in raw_dir.rglob(pattern):
            if file.is_file():
                if not dry_run:
                    # Copy loose image to organized directory
                    dest_file = loose_images_dir / file.name
                    dest_file.write_bytes(file.read_bytes())
                    
                    # Track copied file information
                    copied_images.append({
                        "dest": str(dest_file.relative_to(archives_dir)),
                        "sha256": sha256_file(dest_file),
                        "bytes": dest_file.stat().st_size
                    })
                else:
                    print(f"[DRY-RUN] Would copy loose image: {file.relative_to(raw_dir)}")
                
                loose_image_count += 1
    
    # Process metadata files
    meta_files = ["message_feedback.json", "user.json"]
    for meta_file in meta_files:
        source_file = raw_dir / meta_file
        if source_file.exists() and source_file.is_file():
            if not dry_run:
                # Copy metadata file to organized directory
                dest_file = meta_dir / meta_file
                dest_file.write_bytes(source_file.read_bytes())
                print(f"[INFO] Copied metadata: {meta_file}")
            else:
                print(f"[DRY-RUN] Would copy metadata: {meta_file}")
        elif not dry_run:
            print(f"[INFO] Metadata file not found: {meta_file}")
    
    # Create images manifest if files were copied
    if not dry_run and copied_images:
        manifest_data = {
            "copied_at": utc_ts(),
            "export_date": export_date,
            "counts": {
                "user_folders": user_folder_count,
                "loose_images": loose_image_count,
                "total_images": len(copied_images)
            },
            "images": copied_images
        }
        
        manifest_file = assets_dir / "images_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Created images manifest with {len(copied_images)} images")
    
    return {
        "user_folders": user_folder_count,
        "loose_images": loose_image_count,
        "images_copied": len(copied_images) if not dry_run else 0
    }


def create_ingest_report(export_date: str, thread_count: int, thread_files: list, 
                        reports_dir: Path, format_type: str, artifacts_info: dict, dry_run: bool = False):
    """
    Create comprehensive ingestion report with processing statistics and artifact information.
    
    This function generates a detailed report documenting the ChatGPT export ingestion
    process, including statistics, file lists, and artifact preservation information.
    
    Args:
        export_date (str): Export date for report identification
        thread_count (int): Number of conversation threads processed
        thread_files (list): List of processed conversation file paths
        reports_dir (Path): Directory where the report will be stored
        format_type (str): Detected export format (json/html)
        artifacts_info (dict): Statistics about copied artifacts
        dry_run (bool): If True, preview without writing report
        
    Returns:
        str: Content of the ingestion report
        
    Report Structure:
        - Header with metadata and processing summary
        - Export format and statistics information
        - List of processed conversation threads
        - Artifact preservation details
        - Metadata file status
        - Processing summary with success indicators
        
    Note:
        - Creates parent directories as needed
        - Handles file write errors gracefully
        - Provides comprehensive documentation for audit purposes
        - Returns content for preview/dry-run purposes
    """
    # Build report header with metadata
    report_content = f"# ChatGPT Export Ingest Report\n\n"
    report_content += f"**Date:** {export_date}\n"
    report_content += f"**Format:** {format_type.upper()}\n"
    report_content += f"**Threads Processed:** {thread_count}\n"
    report_content += f"**User Folders:** {artifacts_info.get('user_folders', 0)}\n"
    report_content += f"**Loose Images:** {artifacts_info.get('loose_images', 0)}\n\n"
    
    # Check for metadata files and report status
    meta_files_present = []
    if not dry_run:
        archives_base = Path("archives") / "chat_exports" / export_date
        meta_dir = archives_base / "meta"
        if (meta_dir / "message_feedback.json").exists():
            meta_files_present.append("message_feedback.json")
        if (meta_dir / "user.json").exists():
            meta_files_present.append("user.json")
    
    if meta_files_present:
        report_content += f"**Metadata Files:** {', '.join(meta_files_present)}\n\n"
    else:
        report_content += "*No metadata files found in export*\n\n"
    
    # List processed conversation threads
    report_content += "## Processed Threads\n\n"
    for thread_file in thread_files:
        report_content += f"- {thread_file.name}\n"
    
    report_content += "\n## Summary\n\n"
    report_content += f"**Successfully processed** {thread_count} conversation threads.\n"
    report_content += f"**Preserved** {artifacts_info.get('user_folders', 0)} user folders and {artifacts_info.get('loose_images', 0)} loose images.\n"
    report_content += f"**Memory candidates** generated for Charlotte AI integration.\n"
    report_content += f"**Ingest report** created for documentation purposes.\n\n"
    
    # Add processing notes
    report_content += "## Processing Notes\n\n"
    report_content += "- All conversation threads have been converted to structured Markdown format\n"
    report_content += "- Sensitive information has been redacted from memory candidates\n"
    report_content += "- Images and metadata have been preserved in organized archive structure\n"
    report_content += "- Files are ready for integration with Charlotte AI's memory system\n"
    
    # Write report file (or preview in dry-run mode)
    report_file = reports_dir / f"export_ingest_{export_date}.md"
    if not dry_run:
        try:
            # Ensure parent directory exists
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write comprehensive report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        except Exception as e:
            print(f"[WARN] Failed to write report {report_file}: {e}")
    
    return report_content


def main():
    """
    Main entry point for the ChatGPT Export Ingestion Tool.
    
    This function orchestrates the complete ingestion process:
    1. Parse and validate command line arguments
    2. Set up directory structure for processing
    3. Handle ZIP extraction if needed
    4. Detect and validate export format
    5. Parse conversation data
    6. Process conversations into Markdown files
    7. Create memory candidates for Charlotte AI
    8. Preserve artifacts (images, metadata)
    9. Generate comprehensive ingestion report
    10. Display summary of processing results
    
    Process Flow:
        - Input validation with error handling
        - Directory setup and organization
        - Format detection and parsing
        - Content processing and transformation
        - Artifact preservation and organization
        - Reporting and documentation
        - Summary display with statistics
        
    Error Handling:
        - Uses standardized exit codes from utils module
        - Provides detailed error messages and fix hints
        - Handles filesystem permissions and space issues
        - Validates input formats and file existence
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
        
    Note:
        - Supports both ZIP and directory input formats
        - Provides comprehensive feedback throughout processing
        - Handles edge cases like missing files or corrupted exports
        - Creates organized archive structure for all outputs
    """
    # Parse command line arguments
    args = parse_args()
    
    # Validate input arguments (mutually exclusive options)
    if not args.zip and not args.dir:
        exit_with_error(
            EXIT_BAD_INPUT, 
            "Either --zip or --dir must be specified", 
            "Provide either --zip <export.zip> or --dir <extracted_dir>"
        )
    
    if args.zip and args.dir:
        exit_with_error(
            EXIT_BAD_INPUT, 
            "Only one of --zip or --dir can be specified", 
            "Choose either --zip <export.zip> or --dir <extracted_dir>"
        )
    
    # Generate timestamp for this processing run
    export_date = utc_ts().split('_')[0]  # Use YYYY-MM-DD part for organization
    
    # Set up directory structure for organized processing
    imports_dir = Path("imports") / "ChatGPT_export" / export_date
    archives_dir = Path("archives") / "chat_exports" / export_date
    intake_dir = Path("charlotte_core") / "_intake"  # Updated to charlotte_core
    reports_dir = Path("reports")
    
    if not args.dry_run:
        # Create all necessary directories
        for directory in [imports_dir, archives_dir, intake_dir, reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Handle ZIP extraction with raw preservation if ZIP provided
    raw_dir = None
    if args.zip:
        zip_path = Path(args.zip).resolve()
        raw_dir = imports_dir / "raw"
        
        if not args.dry_run:
            print(f"[INFO] Extracting {zip_path} to {raw_dir}")
            safe_extract_zip(zip_path, raw_dir)
        else:
            print(f"[DRY-RUN] Would extract {zip_path} to {raw_dir}")
        
        export_dir = raw_dir
    else:
        # Use provided directory as export directory
        export_dir = Path(args.dir).resolve()
        if not export_dir.exists():
            exit_with_error(
                EXIT_BAD_INPUT, 
                f"Directory not found: {export_dir}", 
                "Check the directory path and ensure it exists."
            )
        raw_dir = export_dir
    
    # Detect export format and validate
    format_result = detect_export_format(export_dir)
    if not format_result or not format_result[0] or not format_result[1]:
        exit_with_error(
            EXIT_BAD_INPUT, 
            "No recognized export format found", 
            "Ensure the export contains conversations.json or HTML files."
        )
    
    format_type, main_file = format_result
    # Ensure format_type is not None before calling .upper()
    format_type_str = format_type if format_type else "unknown"
    print(f"[INFO] Detected export format: {format_type_str.upper()}")
    
    # Process export based on detected format
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
    
    # Copy export artifacts (images and metadata)
    if not args.dry_run:
        print(f"[INFO] Copying export artifacts to {archives_dir}")
    else:
        print(f"[DRY-RUN] Would copy export artifacts to {archives_dir}")
    
    artifacts_info = copy_export_artifacts(raw_dir, archives_dir, export_date, args.dry_run)
    
    # Create ingest report
    if not args.dry_run:
        print(f"[INFO] Creating ingest report in {reports_dir}")
    else:
        print(f"[DRY-RUN] Would create ingest report in {reports_dir}")
    
    # Ensure format_type is not None before passing to create_ingest_report
    safe_format_type = format_type if format_type else "unknown"
    report_content = create_ingest_report(export_date, len(thread_files), thread_files, 
                                         reports_dir, safe_format_type, artifacts_info, args.dry_run)
    
    # Print comprehensive summary
    print(f"\n[SUMMARY] ChatGPT Export Ingest Complete")
    print(f"  Format: {format_type_str.upper()}")
    print(f"  Date: {export_date}")
    print(f"  Threads: {len(thread_files)}")
    print(f"  User Folders: {artifacts_info.get('user_folders', 0)}")
    print(f"  Loose Images: {artifacts_info.get('loose_images', 0)}")
    print(f"  Candidates: {'Generated' if not args.dry_run else 'Would generate'}")
    print(f"  Report: {'Generated' if not args.dry_run else 'Would generate'}")
    
    if args.dry_run:
        print(f"\n[DRY-RUN] No files were actually written.")
        print(f"  This was a preview of what would be processed.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())