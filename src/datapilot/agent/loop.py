import json
import re

from datapilot.agent.prompts import build_system_prompt
from datapilot.config import MAX_STEPS
from datapilot.llm import llm
from datapilot.tools.db import get_schema, run_sql


def parse(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def ask(question: str, verbose: bool = True) -> str:
    # le transcript est la "mémoire" de l'agent : il grandit à chaque tour
    transcript = f"{build_system_prompt(get_schema())}\n\nQuestion : {question}\n"

    for step in range(1, MAX_STEPS + 1):
        raw = llm(transcript)                                  # 1) le LLM décide
        try:
            msg = parse(raw)
        except json.JSONDecodeError:
            transcript += "\nObservation : réponse invalide, renvoie uniquement du JSON.\n"
            continue

        if verbose:
            print(f"[étape {step}] {msg.get('thought')}")

        if msg.get("action") == "final":                       # 2) fin de la boucle
            return msg["answer"]

        if msg.get("action") == "sql":                         # 3) exécution de l'outil
            obs = run_sql(msg["sql"])
            if verbose:
                print("   SQL :", msg["sql"])
                print("   ->", str(obs)[:200])
            transcript += (                                    # 4) l'observation revient au LLM
                f"\nAction : {json.dumps(msg, ensure_ascii=False)}"
                f"\nObservation : {json.dumps(obs, ensure_ascii=False, default=str)}\n"
            )

    return "Je n'ai pas réussi à répondre dans la limite d'étapes."