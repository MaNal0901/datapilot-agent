import json
from datapilot.config import ROOT
from datapilot.tools.db import run_sql

path = ROOT / "data" / "eval" / "sql_questions.jsonl"
with open(path, encoding="utf-8") as f:
    questions = [json.loads(line) for line in f if line.strip()]

for q in questions[16:]:                      # les questions q17 à q22
    res = run_sql(q["gold_sql"])
    print(f"\n{q['id']} {q['question']}")
    if "error" in res:
        print("   ERREUR :", res["error"])
    else:
        for row in res["rows"][:12]:
            print("  ", row)