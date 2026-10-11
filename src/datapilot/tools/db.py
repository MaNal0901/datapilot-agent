import sqlite3
from datapilot.config import DB_PATH, MAX_ROWS
from datapilot.tools.sql_guard import validate_sql


def _connect() -> sqlite3.Connection:
    # mode=ro : connexion en lecture seule
    return sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)


def get_schema() -> str:
    conn = _connect()
    lines = []
    for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cols = [f"{c[1]} {c[2]}" for c in conn.execute(f"PRAGMA table_info({table})")]
        lines.append(f"- {table}({', '.join(cols)})")
    conn.close()
    return "\n".join(lines)


def run_sql(sql: str) -> dict:
    """Retourne les résultats ou l'erreur (qui servira d'observation à l'agent)."""
    try:
        sql = validate_sql(sql)
        conn = _connect()
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchmany(MAX_ROWS)
        conn.close()
        return {"columns": cols, "rows": rows}
    except Exception as e:
        return {"error": str(e)}