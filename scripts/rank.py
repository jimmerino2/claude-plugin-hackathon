#!/usr/bin/env python3
"""Parse .hackathon/ideas/sdg-*.md, check the idea schema, and rank ideas.

Usage: python rank.py <project-root> [--format md|json] [--config <path>]

Formula (mix from config.ranking_mix, defaults shown):
  wow     = avg(creativity, ui_impact)
  balance = ui_weight * wow + feasibility_weight * feasibility
  final   = rubric*rubric_fit + balance_mix*balance - penalty*max(0, similarity - threshold)
Exit code: 0 = schema OK and constraint met, 1 = problems found, 2 = usage error.
"""
import glob
import json
import os
import re
import sys

DEFAULT_MIX = {"rubric": 0.5, "balance": 0.5, "similarity_penalty": 0.3, "similarity_threshold": 5}
SCORE_KEYS = {
    "similarity": r"Similarity",
    "feasibility": r"Feasibility",
    "creativity": r"Creativity",
    "ui_impact": r"UI impact",
    "rubric_fit": r"Rubric fit",
}
FIELDS = {
    "type": r"\*\*Type:\*\*",
    "description": r"\*\*Description:\*\*",
    "target": r"\*\*Target user & problem:\*\*",
    "competitors": r"\*\*Competitor analysis:\*\*",
    "scores": r"\*\*Scores",
    "demo": r"\*\*Demo workflow:\*\*",
}
HEADER = re.compile(r"^## \[(SDG\d+-\d+)\]\s*(.+?)\s*$", re.M)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def field_value(block, label_re):
    m = re.search(r"^\s*-\s*" + label_re + r"[^\n]*?\s*(.*)$", block, re.M)
    return m.group(1).strip() if m else None


def parse_block(idea_id, title, block, criteria, problems):
    idea = {"id": idea_id, "title": title}
    for key, rx in FIELDS.items():
        if not re.search(r"^\s*-\s*" + rx, block, re.M):
            problems.append(f"{idea_id}: missing field '{key}'")
    t = field_value(block, FIELDS["type"])
    idea["type"] = t or ""
    if t is not None and not t:
        problems.append(f"{idea_id}: empty Type")

    for key, label in SCORE_KEYS.items():
        m = re.search(r"^\s*-\s*" + label + r":\s*([0-9]+(?:\.[0-9]+)?)", block, re.M)
        if not m:
            problems.append(f"{idea_id}: missing or non-numeric score '{label}'")
            idea[key] = None
            continue
        v = float(m.group(1))
        if not 0 <= v <= 10:
            problems.append(f"{idea_id}: score '{label}' = {v} outside 0-10")
        idea[key] = v

    # Optional rubric breakdown -> recompute rubric fit
    m = re.search(r"^\s*-\s*Rubric breakdown:\s*(.+)$", block, re.M)
    if m and criteria:
        parts = {}
        for chunk in re.split(r"[·;|]", m.group(1)):
            mm = re.match(r"\s*(.+?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*$", chunk)
            if mm:
                parts[mm.group(1).strip().lower()] = float(mm.group(2))
        names = [c["name"] for c in criteria]
        if all(n.lower() in parts for n in names):
            calc = sum(c["weight"] * parts[c["name"].lower()] for c in criteria)
            idea["rubric_fit_calc"] = round(calc, 2)
            if idea.get("rubric_fit") is not None and abs(calc - idea["rubric_fit"]) > 0.15:
                problems.append(
                    f"{idea_id}: Rubric fit {idea['rubric_fit']} != weighted breakdown {calc:.2f} (using breakdown)"
                )
                idea["rubric_fit"] = round(calc, 2)
        else:
            missing = [n for n in names if n.lower() not in parts]
            problems.append(f"{idea_id}: rubric breakdown missing criteria {missing}")

    # Competitor table: at least one data row
    comp = re.search(r"\*\*Competitor analysis:\*\*(.*?)(?=^\s*-\s*\*\*Scores)", block, re.M | re.S)
    rows = []
    if comp:
        for line in comp.group(1).splitlines():
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|\s*-{2,}", line) and "Existing project" not in line:
                rows.append(line)
    if not rows:
        problems.append(f"{idea_id}: competitor table has no rows (use '| none found | — | — | — |')")
    idea["competitor_rows"] = len(rows)

    # Demo workflow: 3-6 numbered steps
    demo = re.search(r"\*\*Demo workflow:\*\*(.*)$", block, re.S)
    steps = len(re.findall(r"^\s*\d+[.)]\s+\S", demo.group(1), re.M)) if demo else 0
    if not 3 <= steps <= 6:
        problems.append(f"{idea_id}: demo workflow has {steps} steps (need 3-6)")
    idea["demo_steps"] = steps
    return idea


def score(idea, cfg, mix):
    if any(idea.get(k) is None for k in SCORE_KEYS):
        return None
    wow = (idea["creativity"] + idea["ui_impact"]) / 2
    bal = cfg["ui_weight"] * wow + cfg["feasibility_weight"] * idea["feasibility"]
    pen = mix["similarity_penalty"] * max(0.0, idea["similarity"] - mix["similarity_threshold"])
    final = mix["rubric"] * idea["rubric_fit"] + mix["balance"] * bal - pen
    idea.update(wow=round(wow, 2), balance=round(bal, 2), penalty=round(pen, 2), final=round(final, 2))
    return idea


def main(argv):
    args = [a for a in argv[1:]]
    fmt = "md"
    cfg_path = None
    if "--format" in args:
        i = args.index("--format"); fmt = args[i + 1]; del args[i:i + 2]
    if "--config" in args:
        i = args.index("--config"); cfg_path = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        print(__doc__); return 2
    root = args[0]
    hk = os.path.join(root, ".hackathon")
    cfg = load_json(cfg_path or os.path.join(hk, "config.json"))
    rubric_path = os.path.join(hk, "rubric.json")
    criteria = load_json(rubric_path).get("criteria", []) if os.path.exists(rubric_path) else []
    mix = dict(DEFAULT_MIX, **(cfg.get("ranking_mix") or {}))
    problems = []

    w = cfg.get("ui_weight", 0) + cfg.get("feasibility_weight", 0)
    if abs(w - 1.0) > 1e-6:
        problems.append(f"config: ui_weight + feasibility_weight = {w} (must be 1.0)")

    files = sorted(glob.glob(os.path.join(hk, "ideas", "sdg-*.md")))
    if not files:
        problems.append("no ideas/sdg-*.md files found")
    if len(files) > 3:
        problems.append(f"{len(files)} SDG files found (max 3)")
    ideas = []
    for fp in files:
        text = open(fp, encoding="utf-8").read()
        sdg = re.search(r"sdg-(\d+)\.md$", fp).group(1)
        heads = list(HEADER.finditer(text))
        if len(heads) != 5:
            problems.append(f"{os.path.basename(fp)}: {len(heads)} ideas (need exactly 5)")
        for i, h in enumerate(heads):
            if not h.group(1).startswith(f"SDG{sdg}-"):
                problems.append(f"{os.path.basename(fp)}: idea ID {h.group(1)} doesn't match SDG {sdg}")
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            idea = parse_block(h.group(1), h.group(2), text[h.end():end], criteria, problems)
            idea["sdg"] = int(sdg)
            ideas.append(idea)

    scored = [i for i in (score(x, cfg, mix) for x in ideas) if i]
    scored.sort(key=lambda x: x["final"], reverse=True)
    feas8 = [i["id"] for i in scored if i["feasibility"] >= 8]
    creat8 = [i["id"] for i in scored if i["creativity"] >= 8]
    picks = {}
    if scored:
        picks["best_overall"] = scored[0]["id"]
        picks["most_realistic"] = max(scored, key=lambda x: (x["feasibility"], x["final"]))["id"]
        picks["most_creative"] = max(scored, key=lambda x: (x["creativity"], x["final"]))["id"]
    constraint = {"feasibility_ge_8": feas8, "creativity_ge_8": creat8, "met": bool(feas8 and creat8)}
    ids = [i["id"] for i in ideas]
    dups = sorted({x for x in ids if ids.count(x) > 1})
    if dups:
        problems.append(f"duplicate idea IDs: {dups}")

    result = {"focus": cfg.get("focus"), "ui_weight": cfg.get("ui_weight"),
              "feasibility_weight": cfg.get("feasibility_weight"), "mix": mix,
              "ideas": scored, "picks": picks, "constraint": constraint, "problems": problems}

    if fmt == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        out = []
        out.append(f"Focus: {cfg.get('focus')} (UI {cfg.get('ui_weight')} / feasibility {cfg.get('feasibility_weight')})")
        out.append(f"final = {mix['rubric']}*rubric_fit + {mix['balance']}*balance "
                   f"- {mix['similarity_penalty']}*max(0, similarity-{mix['similarity_threshold']}); "
                   f"balance = {cfg.get('ui_weight')}*wow + {cfg.get('feasibility_weight')}*feasibility; "
                   f"wow = avg(creativity, ui_impact)")
        out.append("")
        out.append("| Rank | ID | Title | Type | Sim | Feas | Creat | UI | Rubric | Wow | Balance | Penalty | Final |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for n, i in enumerate(scored, 1):
            out.append(f"| {n} | {i['id']} | {i['title']} | {i['type']} | {i['similarity']:g} | {i['feasibility']:g} | "
                       f"{i['creativity']:g} | {i['ui_impact']:g} | {i['rubric_fit']:g} | {i['wow']:g} | "
                       f"{i['balance']:g} | {i['penalty']:g} | **{i['final']:g}** |")
        out.append("")
        for k, v in picks.items():
            out.append(f"- {k.replace('_', ' ').title()}: {v}")
        out.append(f"- Constraint (feasibility>=8: {feas8 or 'MISSING'}; creativity>=8: {creat8 or 'MISSING'}): "
                   f"{'met' if constraint['met'] else 'NOT MET'}")
        if problems:
            out.append("")
            out.append("Problems:")
            out += [f"- {p}" for p in problems]
        print("\n".join(out))
    return 0 if (not problems and constraint["met"]) else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
