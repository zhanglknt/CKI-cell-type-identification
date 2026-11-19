"""nc85: mechanical aggregation of the six blind reviewer reports.

Deliberately does NOT write the panel report -- it only extracts scores and
prints a reproducible table/JSON for the editor to compose the narrative.
Run only after all six _nc85_review_R*.md files exist.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
AUDIT = BASE / "results" / "audit"
REPORTS = [AUDIT / f"_nc85_review_R{i}.md" for i in range(1, 7)]

missing = [str(p) for p in REPORTS if not p.exists()]
if missing:
    print("INCOMPLETE -- missing reports:")
    for m in missing:
        print("  " + m)
    sys.exit(2)

DIMS = ["novelty", "theory", "statistics", "evidence", "clarity", "impact"]
DIM_LABELS = {
    "novelty": "新颖性",
    "theory": "理论严谨",
    "statistics": "统计严谨",
    "evidence": "证据充分",
    "clarity": "表达清晰",
    "impact": "影响力/NC",
}
DIM_ALIASES = {
    "novelty": ["新颖性", "novelty"],
    "theory": ["理论严谨", "理论", "theory"],
    "statistics": ["统计严谨", "统计", "statistics", "statistical"],
    "evidence": ["证据充分", "证据", "evidence"],
    "clarity": ["表达清晰", "表达", "clarity", "presentation"],
    "impact": ["影响力", "影响力/nc", "影响力与nc适配度", "impact"],
}


def parse_total(text):
    m = re.search(r"\*\*总分[：:]\s*([0-9]+(?:\.[0-9]+)?)\s*/?\s*10?\*?\*?", text)
    return float(m.group(1)) if m else None


def parse_reco(text):
    m = re.search(r"\*\*建议[：:]\s*([^*]+?)\*\*", text)
    if not m:
        return None
    s = m.group(1).strip()
    for key in ("Reject", "Major Revision", "Minor Revision", "Accept"):
        if key.lower() in s.lower():
            return key
    return s


def parse_dims(text):
    out = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].strip("* ").lower()
        for dim, aliases in DIM_ALIASES.items():
            if any(a.lower() in label for a in aliases):
                for c in cells[1:]:
                    mm = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)", c.strip())
                    if mm:
                        out[dim] = float(mm.group(1))
                        break
                break
    return out


rows = []
for p in REPORTS:
    t = p.read_text(encoding="utf-8")
    total = parse_total(t)
    reco = parse_reco(t)
    dims = parse_dims(t)
    rows.append({"id": p.stem.replace("_nc85_review_", ""), "total": total,
                "reco": reco, "dims": dims})
    print(f"{p.name:28s} total={total}  reco={reco}  dims={dims}")

ok = all(r["total"] is not None and r["reco"] is not None and len(r["dims"]) == 6 for r in rows)
print("\nparse complete:", ok)
if not ok:
    sys.exit(3)

totals = [r["total"] for r in rows]
print(f"mean total = {sum(totals)/len(totals):.3f}")
print("recommendations:", {k: sum(1 for r in rows if r["reco"] == k)
                          for k in ("Reject", "Major Revision", "Minor Revision", "Accept")})
for d in DIMS:
    vals = [r["dims"][d] for r in rows]
    print(f"  {DIM_LABELS[d]:10s} mean={sum(vals)/len(vals):.3f}  values={vals}")

print("\n--- vs prior rounds ---")
print("nc81 mean 6.10 (6/6 Major) | nc83 mean 5.92 (6/6 Major, R6 Return before review)")

out = {
    "round": "nc85",
    "reviewers": rows,
    "mean_total": round(sum(totals) / len(totals), 3),
    "dim_means": {d: round(sum(r["dims"][d] for r in rows) / 6, 3) for d in DIMS},
    "reco_counts": {k: sum(1 for r in rows if r["reco"] == k)
                    for k in ("Reject", "Major Revision", "Minor Revision", "Accept")},
}
(AUDIT / "_nc85_panel_scores.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("\nwrote _nc85_panel_scores.json")
