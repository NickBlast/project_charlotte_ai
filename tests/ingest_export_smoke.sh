#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP="tmp/export_fixture"
rm -rf "$TMP" && mkdir -p "$TMP/user_images/sub" "$TMP/loose"

# Minimal fixtures
echo '{"dummy":"ok"}' > "$TMP/user.json"
echo '[{"id":"m1","rating":"thumbsUp"}]' > "$TMP/message_feedback.json"
echo '{"mapping":{}}' > "$TMP/conversations.json"
convert -size 10x10 xc:white "$TMP/user_images/u1.png" 2>/dev/null || :  # if ImageMagick absent, skip
printf '\x89PNG\r\n\x1a\n' > "$TMP/loose/file_xyz.png" || :

# Zip it
ZIP="tmp/chatgpt-export-fixture.zip"
rm -f "$ZIP"
( cd tmp && zip -r "$(basename "$ZIP")" "export_fixture" >/dev/null )

# Dry-run should detect json + images + meta
python3 tools/ingest_chatgpt_export.py --zip "$ZIP" --dry-run

# Real run
python3 tools/ingest_chatgpt_export.py --zip "$ZIP"

# Verify outputs exist
DATE=$(ls -1 imports/chatgpt_export | tail -n1)
test -d "imports/chatgpt_export/$DATE/raw"
test -f "archives/chat_exports/$DATE/assets/images_manifest.json"
test -f "archives/chat_exports/$DATE/meta/user.json"
test -f "archives/chat_exports/$DATE/meta/message_feedback.json"

echo "OK: ingest smoke passed for $DATE"
