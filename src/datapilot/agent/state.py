from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str      # la question de l'utilisateur
    schema: str        # description des tables
    sql: str           # dernière requête générée
    result: dict       # résultat (colonnes/lignes) ou erreur
    error: str | None  # message d'erreur éventuel
    feedback: str      # consigne de correction pour la prochaine tentative
    attempts: int      # nombre de tentatives déjà faites
    answer: str        # réponse finale