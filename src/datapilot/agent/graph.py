from langgraph.graph import END, START, StateGraph

from datapilot.agent.nodes import execute_sql, generate_sql, give_up, load_schema, write_answer
from datapilot.agent.state import AgentState

MAX_ATTEMPTS = 3   # garde-fou : nombre max de tentatives de génération SQL


def route_after_execute(state: AgentState) -> str:
    """Arête conditionnelle : décide de la suite selon l'état."""
    failed = state.get("error") is not None
    empty = (not failed) and len(state["result"]["rows"]) == 0
    if (failed or empty) and state["attempts"] < MAX_ATTEMPTS:
        return "retry"
    if failed:
        return "give_up"
    return "answer"


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("load_schema", load_schema)
    g.add_node("generate_sql", generate_sql)
    g.add_node("execute_sql", execute_sql)
    g.add_node("write_answer", write_answer)
    g.add_node("give_up", give_up)

    g.add_edge(START, "load_schema")
    g.add_edge("load_schema", "generate_sql")
    g.add_edge("generate_sql", "execute_sql")
    g.add_conditional_edges(
        "execute_sql",
        route_after_execute,
        {"retry": "generate_sql", "answer": "write_answer", "give_up": "give_up"},
    )
    g.add_edge("write_answer", END)
    g.add_edge("give_up", END)

    return g.compile()


def ask_graph(question: str, verbose: bool = True) -> str:
    app = build_graph()
    final = {"question": question, "attempts": 0}
    # stream_mode="updates" : on reçoit la mise à jour de chaque nœud, au fur et à mesure
    for event in app.stream(dict(final), stream_mode="updates"):
        for node, update in event.items():
            final.update(update)
            if verbose:
                print(f"[nœud : {node}]")
                if "sql" in update:
                    print("   SQL :", update["sql"])
                if "result" in update:
                    print("   ->", str(update["result"])[:200])
                if update.get("error"):
                    print("   erreur :", update["error"])
    return final.get("answer", "")