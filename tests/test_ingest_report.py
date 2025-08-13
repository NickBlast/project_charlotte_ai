import json, os, glob

def test_images_manifest_present():
    dates = sorted(glob.glob("archives/chat_exports/*"))
    assert dates, "no archives found"
    manifest = os.path.join(dates[-1], "assets", "images_manifest.json")
    assert os.path.exists(manifest), "images_manifest.json missing"
    data = json.load(open(manifest, "r", encoding="utf-8"))
    assert "images" in data and isinstance(data["images"], list)
    assert data["counts"]["loose_images"] >= 0
    assert data["counts"]["user_folders"] >= 0

def test_meta_copied():
    dates = sorted(glob.glob("archives/chat_exports/*"))
    meta = os.path.join(dates[-1], "meta")
    assert os.path.exists(os.path.join(meta, "user.json")), "user.json not copied"
    assert os.path.exists(os.path.join(meta, "message_feedback.json")), "message_feedback.json not copied"
