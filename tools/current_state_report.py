#!/usr/bin/env python3
import os, json, subprocess, datetime, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
UTC = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
DATE = datetime.datetime.utcnow().strftime("%Y-%m-%d")

def run(cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()

def head():
    sha = run(["git", "rev-parse", "HEAD"])
    title = run(["git", "log", "-1", "--pretty=%s"]) 
    return {"commit": sha, "title": title}

def dir_presence(path):
    return os.path.isdir(ROOT / path)

def tree_depth2():
    out = collections.defaultdict(lambda: {"files":0, "subdirs":[]})
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if len(rel.parts) > 2: 
            continue
        if p.is_file():
            top = rel.parts[0]
            out[top]["files"] += 1
        else:
            if rel.parts:
                top = rel.parts[0]
                if len(rel.parts) == 2:
                    out[top]["subdirs"].append(rel.parts[1])
    items = [{"path": k, "files": v["files"], "subdirs": sorted(set(v["subdirs"]))} 
             for k,v in sorted(out.items())]
    return items

def counts_by_ext():
    exts = collections.Counter()
    files = run(["git", "ls-files"]).splitlines()
    for f in files:
        ext = os.path.splitext(f)[1] or f  # count dotless as their name
        exts[ext] += 1
    return {"files_total": sum(exts.values()), "by_ext": dict(sorted(exts.items()))}

def grep_deprecated():
    patterns = [
        r"Track B",
        r"Weekly Self[\-\s]?Dump",
        r"self[\-_\s]?dump",
        r"Diff Proposer",
        r"\\bproposer\\b",
        r"Propose-MemoryDiff",
        r"proposed_patches",
        r"unclassified\\.md",
        r"routing confidence",
        r"memory_self_dump"
    ]
    # one allowed mention in charlotte_ops.md (deprecation note)
    import re
    hits = []
    for f in run(["git", "ls-files"]).splitlines():
        if f.endswith("charlotte_core/charlotte_ops.md"):
            allowed = True
        else:
            allowed = False
        try:
            text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                if allowed: 
                    continue
                hits.append(f)
                break
    return {"matches": len(hits), "files": sorted(hits)}

def changed_files():
    try:
        base = run(["git", "merge-base", "HEAD", "origin/main"])
        diff = run(["git", "diff", "--name-only", base, "HEAD"])
        return [p for p in diff.splitlines() if p]
    except Exception:
        return []

def todos():
    import re
    results=[]
    for f in run(["git", "ls-files"]).splitlines():
        if any(part.startswith(".venv") for part in f.split("/")):
            continue
        try:
            for i, line in enumerate((ROOT / f).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if re.search(r"\b(TODO|FIXME)\b", line):
                    results.append({"file": f, "line": i, "text": line.strip()[:200]})
        except Exception:
            pass
    return results

def main():
    report_json = {
        "generated_at_utc": UTC,
        "head": head(),
        "counts": counts_by_ext(),
        "folders": tree_depth2(),
        "expected_paths_present": {
            "charlotte_core": dir_presence("charlotte_core"),
            "imports/chatgpt_export": dir_presence("imports/chatgpt_export"),
            "archives/chat_exports": dir_presence("archives/chat_exports"),
            "snapshots": dir_presence("snapshots"),
            "out": dir_presence("out"),
        },
        "deprecated_scan": grep_deprecated(),
        "changed_files": changed_files(),
        "todos": todos(),
    }
    outdir = ROOT / "docs" / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    jpath = outdir / f"current_state_{DATE}.json"
    mpath = outdir / f"current_state_{DATE}.md"
    jpath.write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    md = [ "# Current State Repo Snapshot",
           f"Generated: {UTC}",
           "## Summary",
           f"- HEAD: {report_json['head']['commit']}",
           f"- Title: {report_json['head']['title']}",
           f"- Files tracked: {report_json['counts']['files_total']}",
           "## Key Paths Check" ]
    for k,v in report_json["expected_paths_present"].items():
        md.append(f"- {k}: {'present' if v else 'MISSING'}")
    md.append("## Deprecated Scan")
    md.append(f"- Matches (excluding allowed ops note): {report_json['deprecated_scan']['matches']}")
    md.append("## Changed Files")
    md.extend([f"- {p}" for p in report_json["changed_files"]] or ["- (none)"])
    md.append("## TODO / FIXME")
    md.extend([f"- {t['file']}:{t['line']} {t['text']}" for t in report_json["todos"]] or ["- (none)"])
    mpath.write_text("\n".join(md) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
