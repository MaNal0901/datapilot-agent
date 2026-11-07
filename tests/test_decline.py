from datapilot.agent.graph import route_after_generate
from datapilot.agent.nodes import CLARIFY_PREFIX, generate_sql


def test_route_decline():
    assert route_after_generate({"declined": True}) == "decline"


def test_route_execute():
    assert route_after_generate({"declined": False}) == "execute"
    assert route_after_generate({}) == "execute"


def test_generate_sql_declines(monkeypatch):
    monkeypatch.setattr(
        "datapilot.agent.nodes.llm",
        lambda prompt: "CANNOT_ANSWER: L'âge des clients n'existe pas dans la base.",
    )
    out = generate_sql({"question": "âge moyen ?", "schema": "x", "attempts": 0})
    assert out["declined"] is True
    assert "âge" in out["decline_reason"]


def test_generate_sql_requests_clarification(monkeypatch):
    monkeypatch.setattr(
        "datapilot.agent.nodes.llm",
        lambda prompt: f"{CLARIFY_PREFIX} Parlez-vous du salaire ou des achats ?",
    )
    out = generate_sql({"question": "revenu moyen ?", "schema": "x", "attempts": 0})
    assert out["declined"] is True
    assert out["clarification"] is True
    assert "salaire" in out["decline_reason"]


def test_generate_sql_returns_clean_sql(monkeypatch):
    monkeypatch.setattr("datapilot.agent.nodes.llm", lambda prompt: "```sql\nSELECT 1\n```")
    out = generate_sql({"question": "q", "schema": "x", "attempts": 0})
    assert out["declined"] is False
    assert out["sql"] == "SELECT 1"
    assert out["attempts"] == 1
