import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime

from datapilot import llm as llm_module
from datapilot.agent.graph import run_graph
from datapilot.config import ROOT
from datapilot.metrics import results_match
from datapilot.tools.db import run_sql

QUESTIONS = ROOT / "data" / "eval" / "sql_questions.jsonl"
RESULTS_DIR = ROOT / "eval" / "results"


def load_questions(limit=None):
    with open(QUESTIONS, encoding="utf-8") as f:
        questions = [json.loads(line) for line in f if line.strip()]
    return questions[:limit] if limit else questions


def save(rows, path):
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = sys.argv[1:]
    with_answer = "--with-answer" in args          # par défaut : on n'évalue que le SQL
    numbers = [a for a in args if a.isdigit()]
    limit = int(numbers[0]) if numbers else None
    tag = next((a.split("=", 1)[1] for a in args if a.startswith("--tag=")), "graph")
    pause = float(os.environ.get("EVAL_PAUSE", "0"))   # secondes entre deux questions

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{tag}_{datetime.now():%Y%m%d_%H%M}.json"
    rows = []

    for i, q in enumerate(load_questions(limit)):
        if i and pause:
            time.sleep(pause)

        gold = run_sql(q["gold_sql"])
        if "error" in gold:
            sys.exit(f"{q['id']} : la requête de référence est invalide : {gold['error']}")

        llm_module.USED.clear()
        start = time.time()
        try:
            final = run_graph(q["question"], with_answer=with_answer)
            crash = None
        except Exception as e:           # ex. quota épuisé : on note et on continue
            final, crash = {}, str(e)
        latency = round(time.time() - start, 1)

        ok = results_match(gold, final.get("result"))
        attempts = final.get("attempts", 0)
        models = sorted(set(llm_module.USED))
        rows.append({
            "id": q["id"], "level": q["level"], "question": q["question"],
            "gold_sql": q["gold_sql"], "pred_sql": final.get("sql"),
            "ok": ok, "attempts": attempts, "latency_s": latency,
            "models": models, "crash": crash,
        })
        save(rows, out)                  # sauvegarde après CHAQUE question

        status = "PLANTE" if crash else ("OK   " if ok else "ECHEC")
        print(f"{status} {q['id']} [{q['level']}] tentatives={attempts} {latency}s {models}")
        if crash:
            print("      plantage :", crash[:120])
        elif not ok:
            print("      SQL produit :", final.get("sql"))

    valid = [r for r in rows if not r["crash"]]
    crashed = [r for r in rows if r["crash"]]
    print(f"\nQuestions évaluées : {len(valid)}/{len(rows)} (plantages exclus du score : {len(crashed)})")
    if valid:
        print(f"Exactitude d'exécution : {sum(r['ok'] for r in valid)}/{len(valid)}")
        by_level = defaultdict(list)
        for r in valid:
            by_level[r["level"]].append(r["ok"])
        for level, oks in by_level.items():
            print(f"  {level:10s} {sum(oks)}/{len(oks)}")
        print(f"Tentatives moyennes : {sum(r['attempts'] for r in valid) / len(valid):.2f}")
        print(f"Latence moyenne : {sum(r['latency_s'] for r in valid) / len(valid):.1f}s")
    usage = Counter(m for r in rows for m in r["models"])
    print("Modèles ayant répondu :", dict(usage))
    if crashed:
        print("ATTENTION : des questions ont planté (quota, délai...) : ce run n'est pas comparable à un run complet.")
    print("Résultats enregistrés :", out)


main()