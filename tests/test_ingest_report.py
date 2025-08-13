#!/usr/bin/env python3
"""
Charlotte AI Ingest Report Test Suite - Validate ChatGPT Export Processing Results

This test suite validates the integrity and completeness of ChatGPT export
processing by checking for the presence of expected files and data structures
in the archive directories. It ensures that the ingestion process properly
preserves artifacts and generates required documentation.

Test Coverage:
1. Images manifest validation - Verifies artifact preservation and tracking
2. Metadata file copying - Confirms export metadata is properly archived
3. Archive structure validation - Ensures proper directory organization
4. Manifest data consistency - Validates internal data integrity

Usage:
    pytest tests/test_ingest_report.py -v

Note:
    These tests assume that at least one ChatGPT export has been processed
    and archived in the archives/chat_exports/ directory structure.
"""

import json
import os
import glob
from pathlib import Path


def test_images_manifest_present():
    """
    Test that images manifest file exists and contains valid data structure.
    
    This test validates that the ChatGPT export processing successfully
    created and populated the images manifest file, which tracks all
    preserved images and their integrity hashes.
    
    Test Steps:
        1. Find the most recent chat export archive directory
        2. Verify images_manifest.json exists in the expected location
        3. Load and validate the JSON structure
        4. Check for required fields and data types
        
    Expected Structure:
        {
            "copied_at": "timestamp",
            "export_date": "YYYY-MM-DD",
            "counts": {
                "user_folders": int,
                "loose_images": int,
                "total_images": int
            },
            "images": [
                {
                    "dest": "path/to/image.jpg",
                    "sha256": "hash_string",
                    "bytes": file_size
                },
                ...
            ]
        }
    
    Assertions:
        - Archive directory exists with processed exports
        - images_manifest.json file exists
        - JSON is valid and contains required fields
        - Images list is properly structured
        - Count values are non-negative integers
        
    Note:
        Tests the most recent export archive (dates[-1]) to ensure
        the latest processing run is validated.
    """
    # Find all chat export archive directories and sort by date
    dates = sorted(glob.glob("archives/chat_exports/*"))
    
    # Verify that at least one archive exists
    assert dates, "No chat export archives found. Run ChatGPT export ingestion first."
    
    # Construct path to images manifest in the most recent archive
    archive_path = Path(dates[-1])
    manifest = archive_path / "assets" / "images_manifest.json"
    
    # Verify manifest file exists
    assert manifest.exists(), f"images_manifest.json missing from {archive_path}"
    
    # Load and validate manifest content
    with open(manifest, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Validate required top-level structure
    assert "images" in data, "Missing 'images' field in manifest"
    assert isinstance(data["images"], list), "'images' field should be a list"
    
    # Validate counts structure
    assert "counts" in data, "Missing 'counts' field in manifest"
    counts = data["counts"]
    
    # Ensure count values are valid non-negative integers
    assert counts.get("loose_images", 0) >= 0, "loose_images count should be >= 0"
    assert counts.get("user_folders", 0) >= 0, "user_folders count should be >= 0"
    assert counts.get("total_images", 0) >= 0, "total_images count should be >= 0"
    
    # Validate individual image entries if present
    if data["images"]:
        for image in data["images"]:
            assert "dest" in image, "Image entry missing 'dest' field"
            assert "sha256" in image, "Image entry missing 'sha256' field"
            assert "bytes" in image, "Image entry missing 'bytes' field"
            assert isinstance(image["bytes"], int), "Image 'bytes' should be an integer"
            assert image["bytes"] > 0, "Image 'bytes' should be positive"


def test_meta_copied():
    """
    Test that metadata files are properly copied to archive structure.
    
    This test validates that the ChatGPT export processing successfully
    copied the essential metadata files (user.json and message_feedback.json)
    from the raw export to the organized archive structure.
    
    Test Steps:
        1. Find the most recent chat export archive directory
        2. Verify metadata directory exists
        3. Check for presence of required metadata files
        4. Validate file accessibility and JSON validity
        
    Expected Files:
        - user.json: User profile and account information
        - message_feedback.json: Message feedback and interaction data
        
    Assertions:
        - Archive directory exists with processed exports
        - metadata directory exists within archive
        - user.json file exists and is accessible
        - message_feedback.json file exists and is accessible
        - Both files contain valid JSON data
        
    Note:
        These metadata files are valuable for preserving user-specific
        data and interaction history from ChatGPT exports.
    """
    # Find all chat export archive directories and sort by date
    dates = sorted(glob.glob("archives/chat_exports/*"))
    
    # Verify that at least one archive exists
    assert dates, "No chat export archives found. Run ChatGPT export ingestion first."
    
    # Construct path to metadata directory in the most recent archive
    archive_path = Path(dates[-1])
    meta_dir = archive_path / "meta"
    
    # Verify metadata directory exists
    assert meta_dir.exists(), f"Metadata directory missing from {archive_path}"
    
    # Check for user.json file
    user_json = meta_dir / "user.json"
    assert user_json.exists(), "user.json not copied to metadata directory"
    assert user_json.is_file(), "user.json should be a file"
    
    # Check for message_feedback.json file
    feedback_json = meta_dir / "message_feedback.json"
    assert feedback_json.exists(), "message_feedback.json not copied to metadata directory"
    assert feedback_json.is_file(), "message_feedback.json should be a file"
    
    # Additional validation: verify files are readable and contain valid JSON
    try:
        with open(user_json, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        assert isinstance(user_data, (dict, list)), "user.json should contain valid JSON"
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        assert False, f"user.json contains invalid JSON or encoding: {e}"
    
    try:
        with open(feedback_json, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)
        assert isinstance(feedback_data, (dict, list)), "message_feedback.json should contain valid JSON"
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        assert False, f"message_feedback.json contains invalid JSON or encoding: {e}"


def test_archive_structure_integrity():
    """
    Test overall archive structure integrity and organization.
    
    This comprehensive test validates the complete archive structure created
    by the ChatGPT export processing, ensuring all expected directories and
    organizational patterns are present.
    
    Test Steps:
        1. Verify archive root directory structure
        2. Check for required subdirectories
        3. Validate file organization patterns
        4. Ensure no broken symlinks or missing references
        
    Expected Structure:
        archives/chat_exports/YYYY-MM-DD/
        ├── assets/
        │   ├── user_folders/          # User-specific image folders
        │   ├── loose/                 # Loose image files
        │   └── images_manifest.json   # Image inventory and hashes
        ├── meta/                      # Metadata files
        │   ├── user.json
        │   └── message_feedback.json
        └── [conversation files...]    # Processed conversation Markdown files
    
    Assertions:
        - Root archive directory exists
        - Date-based subdirectory structure is maintained
        - All required subdirectories exist
        - File organization follows expected patterns
        
    Note:
        This test serves as a comprehensive validation of the entire
        archive structure created by the ingestion process.
    """
    # Find all chat export archive directories and sort by date
    dates = sorted(glob.glob("archives/chat_exports/*"))
    
    # Verify that at least one archive exists
    assert dates, "No chat export archives found. Run ChatGPT export ingestion first."
    
    # Test the most recent archive
    archive_path = Path(dates[-1])
    
    # Verify root archive structure
    assert archive_path.exists(), f"Archive directory missing: {archive_path}"
    assert archive_path.is_dir(), f"Archive path should be a directory: {archive_path}"
    
    # Check for assets directory
    assets_dir = archive_path / "assets"
    assert assets_dir.exists(), "assets directory missing from archive"
    assert assets_dir.is_dir(), "assets should be a directory"
    
    # Check for user_folders subdirectory
    user_folders_dir = assets_dir / "user_folders"
    assert user_folders_dir.exists(), "user_folders directory missing"
    assert user_folders_dir.is_dir(), "user_folders should be a directory"
    
    # Check for loose images subdirectory
    loose_images_dir = assets_dir / "loose"
    assert loose_images_dir.exists(), "loose images directory missing"
    assert loose_images_dir.is_dir(), "loose should be a directory"
    
    # Check for metadata directory
    meta_dir = archive_path / "meta"
    assert meta_dir.exists(), "meta directory missing from archive"
    assert meta_dir.is_dir(), "meta should be a directory"
    
    # Verify that conversation files exist (processed from ChatGPT export)
    conversation_files = list(archive_path.glob("*.md"))
    assert conversation_files, "No conversation Markdown files found in archive"
    
    # Verify that all directories are accessible and not broken symlinks
    for directory in [assets_dir, user_folders_dir, loose_images_dir, meta_dir]:
        assert directory.exists(), f"Directory access issue: {directory}"
        assert directory.is_dir(), f"Not a directory: {directory}"


def test_manifest_data_consistency():
    """
    Test that manifest data is consistent and internally valid.
    
    This test validates the internal consistency of the images manifest data,
    ensuring that counts match actual file entries and that all referenced
    files actually exist in the expected locations.
    
    Test Steps:
        1. Load images manifest data
        2. Validate count calculations are correct
        3. Verify all referenced image files exist
        4. Check for data integrity and consistency
        
    Validation Points:
        - Total images count matches sum of user_folders + loose_images
        - All image destinations in manifest actually exist
        - File sizes match manifest entries
        - SHA-256 hashes are valid hexadecimal strings
        
    Note:
        This test ensures data integrity by cross-referencing manifest
        entries with actual filesystem state.
    """
    # Find all chat export archive directories and sort by date
    dates = sorted(glob.glob("archives/chat_exports/*"))
    
    # Verify that at least one archive exists
    assert dates, "No chat export archives found. Run ChatGPT export ingestion first."
    
    # Load manifest data
    archive_path = Path(dates[-1])
    manifest_path = archive_path / "assets" / "images_manifest.json"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    
    # Validate count consistency
    counts = manifest_data.get("counts", {})
    images = manifest_data.get("images", [])
    
    # Check that total count matches actual image count
    total_count = len(images)
    expected_total = counts.get("total_images", 0)
    assert total_count == expected_total, f"Image count mismatch: {total_count} != {expected_total}"
    
    # Check that loose_images + user_folders equals total
    loose_count = counts.get("loose_images", 0)
    folder_count = counts.get("user_folders", 0)
    calculated_total = loose_count + folder_count
    assert total_count == calculated_total, f"Count calculation error: {total_count} != {calculated_total}"
    
    # Validate each image entry
    for image in images:
        # Check required fields
        assert "dest" in image, "Image entry missing destination"
        assert "sha256" in image, "Image entry missing hash"
        assert "bytes" in image, "Image entry missing size"
        
        # Validate SHA-256 format (64-character hex string)
        sha256_hash = image["sha256"]
        assert len(sha256_hash) == 64, f"Invalid SHA-256 length: {len(sha256_hash)}"
        assert all(c in "0123456789abcdefABCDEF" for c in sha256_hash), f"Invalid SHA-256 characters: {sha256_hash}"
        
        # Validate file size
        file_size = image["bytes"]
        assert isinstance(file_size, int), f"File size should be integer: {file_size}"
        assert file_size > 0, f"File size should be positive: {file_size}"
        
        # Verify referenced file actually exists
        image_path = archive_path / image["dest"]
        assert image_path.exists(), f"Referenced image missing: {image_path}"
        assert image_path.is_file(), f"Referenced path should be file: {image_path}"
        
        # Verify file size matches manifest
        actual_size = image_path.stat().st_size
        assert actual_size == file_size, f"Size mismatch for {image_path}: {actual_size} != {file_size}"
        
        # Verify SHA-256 hash matches (optional - can be slow for large files)
        # Uncomment the following block to enable hash verification
        # import hashlib
        # actual_hash = hashlib.sha256()
        # with open(image_path, "rb") as f:
        #     for chunk in iter(lambda: f.read(8192), b""):
        #         actual_hash.update(chunk)
        # assert actual_hash.hexdigest() == sha256_hash, f"Hash mismatch for {image_path}"
