#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP="tmp/export_fixture"
rm -rf "$TMP" && mkdir -p "$TMP/user_images/sub" "$TMP/loose"

# Minimal fixtures
echo '{"dummy":"ok"}' > "$TMP/user.json"
echo '[{"id":"m1","rating":"thumbsUp"}]' > "$TMP/message_feedback.json"
# Add a minimal conversations.json that ingestion recognizes
cat > "$TMP/conversations.json" <<'JSON'
[
  {
    "id": "conv1",
    "title": "Test conversation",
    "mapping": {}
  }
]
JSON

convert -size 10x10 xc:white "$TMP/user_images/u1.png" 2>/dev/null || :  # if ImageMagick absent, skip
# write a tiny PNG via base64 (portable inside script)
base64 -d > "$TMP/loose/file_xyz.png" <<'B64' || true
iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFElEQVQoU2NkYGD4z0AEYBxVSF8A
AAcEAAD+8e3KAAAAAElFTkSuQmCC
B64

# Zip it: put files at zip root so ingestion detects conversations.json
ZIP="tmp/chatgpt-export-fixture.zip"
rm -f "$ZIP"
( cd tmp/export_fixture && zip -r "../$(basename \"$ZIP\")" . >/dev/null )


# Dry-run: point at the already-created extracted directory so detection sees conversations.json
python3 tools/ingest_chatgpt_export.py --dir "$TMP" --dry-run

# Real run
python3 tools/ingest_chatgpt_export.py --zip "$ZIP"

# Verify outputs exist
DATE=$(ls -1 imports/chatgpt_export | tail -n1)
test -d "imports/chatgpt_export/$DATE/raw"
test -f "archives/chat_exports/$DATE/assets/images_manifest.json"
test -f "archives/chat_exports/$DATE/meta/user.json"
test -f "archives/chat_exports/$DATE/meta/message_feedback.json"

echo "OK: ingest smoke passed for $DATE"
