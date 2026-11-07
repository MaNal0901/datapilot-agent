def _norm(value):
    """Arrondit les décimaux pour ne pas échouer sur 12.4999 contre 12.5."""
    return round(value, 2) if isinstance(value, float) else value


def _columns(res: dict) -> list:
    """Transforme un résultat en liste de colonnes, chacune triée (l'ordre des lignes est ignoré)."""
    rows = res["rows"]
    return [
        tuple(sorted((_norm(r[i]) for r in rows), key=str))
        for i in range(len(res["columns"]))
    ]


def results_match(gold: dict, pred) -> bool:
    """Vrai si le résultat de l'agent contient les mêmes valeurs que la référence."""
    if not pred or "error" in pred or "error" in gold:
        return False
    if len(gold["rows"]) != len(pred["rows"]):
        return False
    pred_cols = _columns(pred)
    return all(col in pred_cols for col in _columns(gold))