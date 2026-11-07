import json
import sys

from datapilot.config import ROOT

RESULTS = ROOT / "eval" / "results"


def latest(tag):
    files = sorted(RESULTS.glob(f"{tag}_*.json"))
    return files[-1] if files else None


runs = {}
for tag in sys.argv[1:]:
    f = latest(tag)
    if f is None:
        print(f"(aucun fichier pour l'étiquette {tag})")
        continue
    rows = json.loads(f.read_text(encoding="utf-8"))
    runs[tag] = {r["id"]: r for r in rows}

ids = sorted({i for r in runs.values() for i in r})
print("question  " + "  ".join(f"{t:14s}" for t in runs))
for i in ids:
    cells = []
    for r in runs.values():
        row = r.get(i)
        cells.append("-" if row is None else ("PLANTE" if row["crash"] else ("OK" if row["ok"] else "ECHEC")))
    flag = "   <-- varie" if len(set(cells)) > 1 else ""
    print(f"{i:8s}  " + "  ".join(f"{c:14s}" for c in cells) + flag)

print()
for tag, r in runs.items():
    valid = [x for x in r.values() if not x["crash"]]
    if valid:
        acc = sum(x["ok"] for x in valid)
        lat = sum(x["latency_s"] for x in valid) / len(valid)
        print(f"{tag:14s} {acc}/{len(valid)} corrects, latence moyenne {lat:.1f}s, plantages : {len(r) - len(valid)}")