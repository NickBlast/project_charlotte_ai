#!/usr/bin/env python3
"""
Shared utilities for Charlotte AI memory tools.

This module provides common utility functions used across various Charlotte AI
memory processing tools. It includes functions for timestamp generation,
path handling, filename sanitization, sensitive content redaction, and
error handling with standardized exit codes.

Why this exists:
To avoid code duplication and ensure consistent behavior across the toolchain for
critical operations like timestamping, path normalization, and error handling,
which are essential for the deterministic and reliable functioning of the memory
pipeline as defined in the PRD.

Features:
- UTC timestamp generation for consistent file naming (FR-6)
- Cross-platform path handling and sorting for deterministic outputs (FR-6)
- Filename sanitization for filesystem compatibility
- Sensitive content redaction for security and privacy (FR-3, NFR-Security)
- Path traversal protection (Zip-Slip prevention) for safe archive handling
- Standardized error handling and exit codes for observability (NFR-Observability)
"""

# Constants for file size calculations and thresholds
BYTES_PER_MB = 1024 * 1024
ROUTING_CONFIDENCE_THRESHOLD = 0.6
INVALID_FILENAME_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1f]'
MAX_TEXT_MB_DEFAULT = 25
MAX_CONVERSATIONS_JSON_MB = 500
FILENAME_LENGTH_LIMIT = 200

# Standard library imports
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Union, Optional


def utc_ts() -> str:
    """
    Generate UTC timestamp in standardized YYYY-MM-DD_HHMMSSZ format.
    
    This function creates consistent timestamps across all Charlotte AI tools
    using UTC time to avoid timezone-related issues. The format follows
    ISO 8601 conventions with a 'Z' suffix indicating UTC timezone.
    
    Returns:
        str: Formatted timestamp string in format 'YYYY-MM-DD_HHMMSSZ'
        
    Example:
        >>> utc_ts()
        '2024-01-15_143022Z'
        
    Note:
        Used consistently across all tools for file naming, logging,
        and creating unique identifiers that are chronologically sortable.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")


def as_posix_sorted(paths: List[Union[str, Path]]) -> List[str]:
    """
    Sort paths by their forward-slash representation for deterministic ordering.
    
    This function ensures consistent path ordering across different operating
    systems by converting all paths to POSIX format before sorting. This is
    crucial for reproducible results in backup and processing operations.
    
    Args:
        paths (List[Union[str, Path]]): List of path strings or Path objects
        
    Returns:
        List[str]: Sorted list of path strings in POSIX format
        
    Example:
        >>> as_posix_sorted(['/path/b', '/path/a'])
        ['/path/a', '/path/b']
        
    Note:
        - Converts all paths to string representation using Path.as_posix()
        - Uses Python's built-in sorted() for consistent ordering
        - Essential for deterministic backup manifests and processing results
    """
    return sorted(str(Path(p).as_posix()) for p in paths)


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename by replacing invalid characters and limiting length.
    
    This function creates filesystem-safe filenames by removing or replacing
    characters that are invalid across different operating systems. It also
    enforces a maximum filename length to prevent filesystem compatibility issues.
    
    Args:
        name (str): Original filename to sanitize
        
    Returns:
        str: Sanitized filename safe for use across filesystems
        
    Example:
        >>> sanitize_filename("My*File<>.txt")
        'My_File_.txt'
        
    Note:
        - Uses regex pattern to replace invalid characters with underscores
        - Limits filename length to FILENAME_LENGTH_LIMIT (200 characters)
        - Preserves alphanumeric characters, hyphens, and underscores
        - Important for cross-platform compatibility and security
    """
    # Replace invalid characters with underscores using predefined pattern
    sanitized = re.sub(INVALID_FILENAME_CHARS_PATTERN, '_', name)
    # Limit length to prevent filesystem issues across different platforms
    return sanitized[:FILENAME_LENGTH_LIMIT] if len(sanitized) > FILENAME_LENGTH_LIMIT else sanitized


def redact_sensitive_content(text: str) -> str:
    """
    Redact sensitive information from text for security and privacy.
    
    This function identifies and redacts various types of sensitive information
    including API keys, private keys, and environment variables. It's used
    specifically for memory candidates and reports, while preserving audit
    trails in their original form.
    
    Args:
        text (str): Input text potentially containing sensitive information
        
    Returns:
        str: Text with sensitive information redacted
        
    Example:
        >>> redact_sensitive_content("API_KEY=sk-1234567890abcdef")
        'API_KEY=[REDACTED]'
        
    Note:
        - Redacts OpenAI API keys (sk- prefix followed by 48 alphanumeric chars)
        - Redacts generic API_KEY patterns with various formats
        - Redacts PEM-formatted private keys (BEGIN/END PRIVATE KEY)
        - Redacts .env file patterns and environment variable assignments
        - NOT used for audit trail preservation - only for user-facing content
    """
    # Redact OpenAI API keys (48-character alphanumeric after sk- prefix)
    text = re.sub(r'sk-[a-zA-Z0-9]{48}', '[REDACTED]', text)
    # Redact generic API key patterns with various assignment formats
    text = re.sub(r'API_KEY[=\s]+[\'"]?[a-zA-Z0-9_\-]+[\'"]?', 'API_KEY=[REDACTED]', text)
    # Redact PEM-formatted private keys with multi-line matching
    text = re.sub(r'-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----', 
                  '-----BEGIN PRIVATE KEY-----\n[REDACTED]\n-----END PRIVATE KEY-----', text, flags=re.DOTALL)
    # Redact .env file patterns and environment variable assignments
    text = re.sub(r'\.env[=\s]+[^\s]+', '.env=[REDACTED]', text)
    return text


def safe_extract_path(base_path: Path, member_path: str) -> Path:
    """
    Safely resolve an extracted path to prevent Zip-Slip attacks.
    
    This function implements security checks to prevent Zip-Slip attacks,
    which occur when a malicious archive contains paths with '../' sequences
    that could escape the intended extraction directory. It ensures that
    the final path remains within the base extraction directory.
    
    Args:
        base_path (Path): Base directory path where extraction should occur
        member_path (str): Member path from archive to be extracted
        
    Returns:
        Path: Resolved and validated path within base directory
        
    Raises:
        ValueError: If path traversal is detected (attempted Zip-Slip attack)
        
    Example:
        >>> safe_extract_path(Path('/safe/dir'), 'file.txt')
        Path('/safe/dir/file.txt')
        
    Note:
        - Uses Path.resolve() to normalize the path and resolve symlinks
        - Uses relative_to() to verify the path stays within base directory
        - Raises ValueError for any attempt at path traversal
        - Essential security measure for archive extraction operations
    """
    # Resolve the target path to normalize it and handle symlinks
    target_path = (base_path / member_path).resolve()
    # Ensure the target path is within the base path to prevent directory traversal
    try:
        target_path.relative_to(base_path.resolve())
        return target_path
    except ValueError:
        raise ValueError(f"Attempted path traversal detected: {member_path}")


def exit_with_error(code: int, message: str, fix_hint: str = ""):
    """
    Exit the program with error code and formatted error message.
    
    This function provides standardized error handling across all Charlotte AI
    tools. It prints formatted error messages to stderr and exits with the
    specified error code, optionally including a helpful hint for resolution.
    
    Args:
        code (int): Exit code to return to the operating system
        message (str): Error message to display
        fix_hint (str, optional): Suggested solution or next steps
        
    Example:
        >>> exit_with_error(2, "Config file not found", "Copy config.example.yaml to config.yaml")
        
    Note:
        - Always prints to stderr for proper error stream handling
        - Includes optional fix hint when provided for better user experience
        - Uses sys.exit() to terminate the program immediately
        - Standardized across all tools for consistent error reporting
    """
    print(f"[ERROR] {message}", file=sys.stderr)
    if fix_hint:
        print(f"Hint: {fix_hint}", file=sys.stderr)
    sys.exit(code)


# Standard exit codes for consistent error handling across tools
EXIT_BAD_INPUT = 2      # Invalid command line arguments or configuration
EXIT_NOTHING_TO_DO = 3  # No files found or no operations needed
EXIT_WRITE_ERROR = 4    # Filesystem write operation failed