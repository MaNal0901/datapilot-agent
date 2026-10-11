import re
from datapilot.config import MAX_ROWS

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace)\b", re.I
)


def validate_sql(sql: str) -> str:
    """Valide une requête et la renvoie nettoyée, sinon lève ValueError."""
    sql = sql.strip().rstrip(";")
    if ";" in sql:
        raise ValueError("Une seule requête autorisée.")
    if not re.match(r"(?is)^\s*(select|with)\b", sql):
        raise ValueError("Seules les requêtes SELECT sont autorisées.")
    if FORBIDDEN.search(sql):
        raise ValueError("Mot-clé interdit dans la requête.")
    if not re.search(r"\blimit\b", sql, re.I):
        sql += f" LIMIT {MAX_ROWS}"
    return sql