#!/usr/bin/env python3
"""Validate .hackathon/handoff/ against the plugin's section 9 checks.

Usage: python validate_handoff.py <project-root> [--format md|json]
Exit 0 if all checks pass, 1 otherwise.
"""
import glob
import json
import os
import re
import sys


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def norm(p):
    p = p.strip().strip("`").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = re.sub(r"/\*\*?$", "/", p)
    return p.lstrip("/")


def under(child, parent):
    """True if child is parent or inside parent (parent treated as a directory prefix)."""
    c, pa = norm(child), norm(parent)
    if c == pa or c.rstrip("/") == pa.rstrip("/"):
        return True
    return c.startswith(pa.rstrip("/") + "/")


def overlap(a, b):
    return under(a, b) or under(b, a)


def sections(text):
    """Map heading text -> body for ## and ### headings."""
    out = {}
    heads = list(re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.M))
    for i, h in enumerate(heads):
        level = len(h.group(1))
        end = len(text)
        for h2 in heads[i + 1:]:
            if len(h2.group(1)) <= level:
                end = h2.start()
                break
        out[h.group(2)] = text[h.end():end]
    return out


def find_section(secs, prefix):
    for k, v in secs.items():
        if k.lower().startswith(prefix.lower()):
            return v
    return ""


def table_rows(body):
    rows = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|\s*:?-{2,}", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        rows.append(cells)
    return rows[1:] if rows else []  # drop header row


def is_placeholder(s):
    s = s.strip()
    return (not s) or s in ("—", "-", "–", "n/a", "N/A", "none", "TBD") or (s.startswith("<") and s.endswith(">"))


def parse_handoff(fp):
    text = open(fp, encoding="utf-8").read()
    secs = sections(text)
    h = {"file": os.path.basename(fp)}
    m = re.search(r"\*\*Integration owner:\*\*\s*(yes|no)", text, re.I)
    h["integration"] = (m.group(1).lower() == "yes") if m else None
    m = re.search(r"\*\*Demo (?:&|and) pitch owner:\*\*\s*(yes|no)", text, re.I)
    h["demo"] = (m.group(1).lower() == "yes") if m else None
    own = find_section(secs, "Files you OWN")
    h["owns"] = [norm(p) for p in re.findall(r"^\s*-\s*`([^`]+)`", own, re.M)]
    h["provide"], h["consume"] = [], []
    for cells in table_rows(find_section(secs, "You PROVIDE")):
        refs = re.findall(r"C-\d+", " ".join(cells[1:2] or cells))
        h["provide"] += [{"ref": r, "row": cells} for r in refs]
    for cells in table_rows(find_section(secs, "You CONSUME")):
        refs = re.findall(r"C-\d+", " ".join(cells[1:2] or cells))
        mock = cells[3] if len(cells) > 3 else ""
        h["consume"] += [{"ref": r, "mock": mock, "row": cells} for r in refs]
    tasks = []
    body = find_section(secs, "Tasks")
    parts = re.split(r"^\s*-\s*\[[ xX]\]\s*", body, flags=re.M)[1:]
    for p in parts:
        tid = re.match(r"(T\d+)", p)
        fm = re.search(r"^\s*-\s*Files:\s*(.+)$", p, re.M)
        am = re.search(r"^\s*-\s*Acceptance:\s*(\S.*)$", p, re.M)
        tasks.append({
            "id": tid.group(1) if tid else p.split("\n")[0][:30],
            "files": [norm(x) for x in re.findall(r"`([^`]+)`", fm.group(1))] if fm else [],
            "has_files_line": bool(fm),
            "has_acceptance": bool(am),
        })
    h["tasks"] = tasks
    return h


def main(argv):
    args = argv[1:]
    fmt = "md"
    if "--format" in args:
        i = args.index("--format"); fmt = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        print(__doc__); return 2
    root = args[0]
    hk = os.path.join(root, ".hackathon")
    results = []  # (check, ok, details)

    cfg = json.load(open(os.path.join(hk, "config.json"), encoding="utf-8"))
    team = [t["name"] for t in cfg.get("team", [])]
    n_team = len(team)

    # ---- 1. exactly N handoff files, one per teammate
    files = sorted(glob.glob(os.path.join(hk, "handoff", "HANDOFF-*.md")))
    expected = {f"HANDOFF-{i}-{slug(n)}.md": n for i, n in enumerate(team, 1)}
    names = [os.path.basename(f) for f in files]
    det = []
    if len(files) != n_team:
        det.append(f"{len(files)} HANDOFF files for {n_team} teammates")
    for e in expected:
        if e not in names:
            det.append(f"missing {e}")
    for nme in names:
        if nme not in expected:
            det.append(f"unexpected {nme}")
    results.append(("Exactly N HANDOFF files, one per teammate", not det, det))

    handoffs = {}
    for f in files:
        h = parse_handoff(f)
        h["owner"] = expected.get(os.path.basename(f), os.path.basename(f))
        handoffs[h["owner"]] = h

    # ---- 2. no path in two owners' OWN lists
    det = []
    owned = [(p, o) for o, h in handoffs.items() for p in h["owns"]]
    for o, h in handoffs.items():
        if not h["owns"]:
            det.append(f"{h['file']}: empty 'Files you OWN' list")
    for i in range(len(owned)):
        for j in range(i + 1, len(owned)):
            (p1, o1), (p2, o2) = owned[i], owned[j]
            if o1 != o2 and overlap(p1, p2):
                det.append(f"`{p1}` ({o1}) overlaps `{p2}` ({o2})")
    results.append(("No path owned by two people (disjoint ownership)", not det, det))

    # ---- OWNERSHIP.md parsing
    own_fp = os.path.join(hk, "handoff", "OWNERSHIP.md")
    ownership = []
    shared = []
    if os.path.exists(own_fp):
        otext = open(own_fp, encoding="utf-8").read()
        osecs = sections(otext)
        for cells in table_rows(find_section(osecs, "Paths")):
            m = re.match(r"`([^`]+)`", cells[0]) if cells else None
            if m and len(cells) > 1:
                ownership.append((norm(m.group(1)), cells[1].strip()))
        shared = [norm(p) for p in re.findall(r"^\s*-\s*`([^`]+)`", find_section(osecs, "Shared files"), re.M)]

    # ---- 3. every repo-structure path has an owner in OWNERSHIP.md
    det = []
    arch_fp = os.path.join(hk, "design", "architecture.md")
    repo_paths = []
    if os.path.exists(arch_fp):
        m = re.search(r"```repo-structure\s*\n(.*?)```", open(arch_fp, encoding="utf-8").read(), re.S)
        if m:
            for line in m.group(1).splitlines():
                p = line.split("#", 1)[0].strip()
                if p:
                    repo_paths.append(norm(p))
        else:
            det.append("architecture.md has no ```repo-structure block")
    else:
        det.append("design/architecture.md missing")
    if not os.path.exists(own_fp):
        det.append("handoff/OWNERSHIP.md missing")
    for p, o in ownership:
        if o not in team:
            det.append(f"OWNERSHIP.md: `{p}` owner '{o}' is not a team member")
    for i in range(len(ownership)):
        for j in range(i + 1, len(ownership)):
            (p1, o1), (p2, o2) = ownership[i], ownership[j]
            if o1 != o2 and overlap(p1, p2):
                det.append(f"OWNERSHIP.md: `{p1}` ({o1}) overlaps `{p2}` ({o2})")
    for rp in repo_paths:
        if not any(under(rp, op) for op, _ in ownership):
            det.append(f"repo path `{rp}` has no owner in OWNERSHIP.md")
    # HANDOFF lists must agree with OWNERSHIP.md
    for o, h in handoffs.items():
        for p in h["owns"]:
            ok = any(under(p, op) and oo == o for op, oo in ownership)
            if not ok:
                det.append(f"{h['file']}: owns `{p}` but OWNERSHIP.md doesn't assign it to {o}")
    results.append(("Every repo-structure path has an owner in OWNERSHIP.md", not det, det))

    # ---- 4. every CONSUME has a PROVIDE elsewhere and a mock
    det = []
    providers = {}
    for o, h in handoffs.items():
        for pr in h["provide"]:
            providers.setdefault(pr["ref"], []).append(o)
    for ref, os_ in providers.items():
        if len(set(os_)) > 1:
            det.append(f"{ref} provided by several people: {sorted(set(os_))}")
    for o, h in handoffs.items():
        for c in h["consume"]:
            provs = [p for p in providers.get(c["ref"], []) if p != o]
            if not provs:
                det.append(f"{h['file']}: consumes {c['ref']} but no other HANDOFF provides it")
            if is_placeholder(c["mock"]):
                det.append(f"{h['file']}: consumes {c['ref']} with no mock")
    results.append(("Every CONSUME has a matching PROVIDE in another file, and a mock", not det, det))

    # ---- 5. exactly one integration owner and one demo & pitch owner
    det = []
    integ = [o for o, h in handoffs.items() if h["integration"]]
    demo = [o for o, h in handoffs.items() if h["demo"]]
    for o, h in handoffs.items():
        if h["integration"] is None:
            det.append(f"{h['file']}: no '- **Integration owner:** yes|no' line")
        if h["demo"] is None:
            det.append(f"{h['file']}: no '- **Demo & pitch owner:** yes|no' line")
    if len(integ) != 1:
        det.append(f"integration owners: {integ or 'none'} (need exactly 1)")
    if len(demo) != 1:
        det.append(f"demo & pitch owners: {demo or 'none'} (need exactly 1)")
    if integ and shared:
        io = integ[0]
        for sp in shared:
            if not any(under(sp, p) for p in handoffs[io]["owns"]):
                det.append(f"shared file `{sp}` is not in the integration owner's ({io}) OWN list")
    results.append(("Exactly one integration owner and one demo & pitch owner", not det, det))

    # ---- 6. every task lists only files inside its owner's paths
    det = []
    for o, h in handoffs.items():
        if not h["tasks"]:
            det.append(f"{h['file']}: no tasks")
        for t in h["tasks"]:
            if not t["has_files_line"] or not t["files"]:
                det.append(f"{h['file']} {t['id']}: no '- Files:' list")
            if not t["has_acceptance"]:
                det.append(f"{h['file']} {t['id']}: no '- Acceptance:' line")
            for f in t["files"]:
                if not any(under(f, p) for p in h["owns"]):
                    det.append(f"{h['file']} {t['id']}: `{f}` is outside {o}'s owned paths")
    results.append(("Every task touches only its owner's paths", not det, det))

    # ---- 7. every referenced interface exists in contracts.md
    det = []
    c_fp = os.path.join(hk, "design", "contracts.md")
    contract_ids = set()
    if os.path.exists(c_fp):
        contract_ids = set(re.findall(r"^#{2,4}\s.*?\b(C-\d+)\b", open(c_fp, encoding="utf-8").read(), re.M))
    else:
        det.append("design/contracts.md missing")
    for o, h in handoffs.items():
        for x in h["provide"] + h["consume"]:
            if x["ref"] not in contract_ids:
                det.append(f"{h['file']}: {x['ref']} not defined in contracts.md")
    unprovided = sorted(contract_ids - set(providers))
    if unprovided:
        det.append(f"contracts with no provider in any HANDOFF: {unprovided}")
    results.append(("Every referenced interface exists in contracts.md", not det, det))

    ok_all = all(r[1] for r in results)
    if fmt == "json":
        print(json.dumps({"ok": ok_all, "checks": [{"check": c, "ok": k, "details": d} for c, k, d in results]}, indent=2))
    else:
        for c, k, d in results:
            print(f"[{'x' if k else ' '}] {c}")
            for x in d:
                print(f"      - {x}")
        print("\nALL CHECKS PASSED" if ok_all else "\nVALIDATION FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
