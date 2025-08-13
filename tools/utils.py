#!/usr/bin/env python3
"""
Shared utilities for Charlotte AI memory tools.
"""

# Constants
BYTES_PER_MB = 1024 * 1024
ROUTING_CONFIDENCE_THRESHOLD = 0.6
INVALID_FILENAME_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1F]'
MAX_TEXT_MB_DEFAULT = 25
MAX_CONVERSATIONS_JSON_MB = 500
FILENAME_LENGTH_LIMIT = 200

import os
import re
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Union, Optional


def utc_ts() -> str:
    """Generate UTC timestamp in YYYY-MM-DD_HHMMSSZ format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")


def as_posix_sorted(paths: List[Union[str, Path]]) -> List[str]:
    """Sort paths by their forward-slash representation for deterministic ordering."""
    return sorted(str(Path(p).as_posix()) for p in paths)


def sanitize_filename(name: str) -> str:
    """Sanitize filename by replacing invalid characters."""
    # Replace invalid characters with underscores
    sanitized = re.sub(INVALID_FILENAME_CHARS_PATTERN, '_', name)
    # Limit length to prevent filesystem issues
    return sanitized[:FILENAME_LENGTH_LIMIT] if len(sanitized) > FILENAME_LENGTH_LIMIT else sanitized


def redact_sensitive_content(text: str) -> str:
    """Redact sensitive information from text.
    
    Only used for memory_candidates.md and reports, not for audit trail preservation.
    """
    # Redact API keys
    text = re.sub(r'sk-[a-zA-Z0-9]{48}', '[REDACTED]', text)
    # Redact API key patterns
    text = re.sub(r'API_KEY[=\s]+[\'"]?[a-zA-Z0-9_\-]+[\'"]?', 'API_KEY=[REDACTED]', text)
    # Redact private keys
    text = re.sub(r'-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----', 
                  '-----BEGIN PRIVATE KEY-----\n[REDACTED]\n-----END PRIVATE KEY-----', text, flags=re.DOTALL)
    # Redact .env patterns
    text = re.sub(r'\.env[=\s]+[^\s]+', '.env=[REDACTED]', text)
    return text


def safe_extract_path(base_path: Path, member_path: str) -> Path:
    """Safely resolve an extracted path to prevent Zip-Slip attacks."""
    # Resolve the target path
    target_path = (base_path / member_path).resolve()
    # Ensure the target path is within the base path
    try:
        target_path.relative_to(base_path.resolve())
        return target_path
    except ValueError:
        raise ValueError(f"Attempted path traversal detected: {member_path}")


def exit_with_error(code: int, message: str, fix_hint: str = ""):
    """Exit with error code and message."""
    print(f"[ERROR] {message}", file=sys.stderr)
    if fix_hint:
        print(f"Hint: {fix_hint}", file=sys.stderr)
    sys.exit(code)


# Standard exit codes
EXIT_BAD_INPUT = 2
EXIT_NOTHING_TO_DO = 3
EXIT_WRITE_ERROR = 4
