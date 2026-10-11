import re

from datapilot.agent.state import AgentState
from datapilot.llm import llm
from datapilot.tools.db import get_schema, run_sql


def clean_sql(text: str) -> str:
    """Retire les balises markdown que le LLM ajoute parfois."""
    return re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.M | re.I).strip()


def load_schema(state: AgentState) -> dict:
    return {"schema": get_schema()}


def generate_sql(state: AgentState) -> dict:
    feedback = state.get("feedback", "")
    prompt = f"""Tu es un expert SQL (SQLite). Écris UNE requête SELECT qui répond à la question.

Schéma :
{state['schema']}

Question : {state['question']}
{feedback}
Règles :
- Inclus toujours dans le SELECT les valeurs qui justifient la réponse (moyenne, effectif, total...), pas seulement un nom.
- Les catégories de produits sont en portugais : joins product_category_name_translation pour afficher le nom anglais.
- Attention aux jointures qui dupliquent des lignes (une commande a plusieurs articles) : dédoublonne avec DISTINCT ou une sous-requête avant d'agréger.
Réponds uniquement avec la requête SQL, sans explication ni balises markdown."""
    sql = clean_sql(llm(prompt))
    return {"sql": sql, "attempts": state.get("attempts", 0) + 1}


def execute_sql(state: AgentState) -> dict:
    result = run_sql(state["sql"])
    if "error" in result:
        feedback = (f"Ta requête précédente `{state['sql']}` a échoué avec l'erreur : "
                    f"{result['error']}. Corrige-la.")
        return {"result": result, "error": result["error"], "feedback": feedback}
    if not result["rows"]:
        feedback = (f"Ta requête précédente `{state['sql']}` a renvoyé 0 ligne. "
                    "Vérifie les jointures, les filtres et les noms de colonnes.")
        return {"result": result, "error": None, "feedback": feedback}
    return {"result": result, "error": None, "feedback": ""}


def write_answer(state: AgentState) -> dict:
    prompt = f"""Question : {state['question']}
Requête SQL exécutée : {state['sql']}
Résultat (colonnes, lignes) : {state['result']}

Réponds clairement en français à la question, uniquement à partir de ce résultat.
N'invente aucun chiffre ni aucun fait absent du résultat. Si le résultat est vide, dis-le."""
    return {"answer": llm(prompt).strip()}


def give_up(state: AgentState) -> dict:
    return {"answer": f"Je n'ai pas réussi à produire une requête valide après "
                      f"{state.get('attempts', 0)} tentatives. Dernière erreur : {state.get('error')}"}