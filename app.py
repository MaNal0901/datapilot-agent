import logging

import pandas as pd
import streamlit as st

from datapilot.agent.graph import run_graph
from datapilot.config import DB_PATH, GEMINI_API_KEY, MODEL_NAME

LOGGER = logging.getLogger("datapilot.app")

st.set_page_config(page_title="DataPilot", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #17243a;
        --muted: #61728a;
        --line: #dfe7ef;
        --accent: #0f8b81;
        --accent-strong: #087168;
        --accent-soft: #e1f5f1;
        --coral: #f27f70;
    }
    .stApp { background: radial-gradient(ellipse at 72% 0%, #eef7f8 0%, #f7f9fc 42%, #f4f6fa 100%); color: var(--ink); }
    [data-testid="stAppViewContainer"] { background: transparent; color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(247, 249, 252, .94); }
    [data-testid="stSidebar"] { background: #edf3f7; border-right: 1px solid #dce5ec; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #17243a; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #52647a; }
    [data-testid="stSidebar"] hr { border-color: #d4dfe8; }
    [data-testid="stSidebar"] [data-testid="stAlert"] { background: #e1f5f1; border: 1px solid #b7e5dc; }
    [data-testid="stSidebar"] [data-testid="stAlert"] p { color: #155e59; }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button { color: #17243a; background: #fff; border-color: #cbd9e3; }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover { color: #087168; background: #e1f5f1; border-color: #0f8b81; }
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p { color: #26364d; }
    .block-container { max-width: 1100px; padding-top: 2rem; padding-bottom: 5rem; }
    .brand-kicker { color: var(--accent); font-size: .76rem; font-weight: 750; letter-spacing: .14em; text-transform: uppercase; }
    .hero { position: relative; overflow: hidden; padding: 2.35rem 2.55rem; border: 1px solid #d4e9e6; border-radius: 26px; background: linear-gradient(118deg, #e5f7f2 0%, #f1f8fa 54%, #eef2fb 100%); box-shadow: 0 14px 36px rgba(25, 55, 77, .06); margin: .4rem 0 1.8rem; }
    .hero:after { content: ''; position: absolute; width: 230px; height: 230px; right: -60px; top: -85px; border-radius: 50%; background: radial-gradient(circle, rgba(242, 127, 112, .2), rgba(242, 127, 112, 0) 70%); pointer-events: none; }
    .hero h1 { color: var(--ink); font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -.045em; line-height: 1.08; margin: .55rem 0 .65rem; }
    .hero p { color: #4c6077; font-size: 1.04rem; max-width: 650px; margin: 0; }
    .hero-tags { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.15rem; }
    .hero-tag { display: inline-flex; align-items: center; gap: .35rem; padding: .38rem .7rem; border: 1px solid rgba(15, 139, 129, .18); border-radius: 999px; background: rgba(255, 255, 255, .68); color: #35566b; font-size: .78rem; font-weight: 650; }
    .suggestion { min-height: 122px; padding: 1.1rem 1.15rem .7rem; background: rgba(255, 255, 255, .92); border: 1px solid var(--line); border-top: 3px solid var(--accent); border-radius: 16px; box-shadow: 0 8px 22px rgba(25, 45, 75, .045); transition: transform .16s ease, box-shadow .16s ease; }
    .suggestion:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(25, 45, 75, .09); }
    .suggestion-coral { border-top-color: var(--coral); }
    .suggestion-coral .suggestion-label { color: #c65f52; }
    .suggestion-blue { border-top-color: #7185c8; }
    .suggestion-blue .suggestion-label { color: #5b6dad; }
    .suggestion-label { color: var(--accent); font-size: .69rem; font-weight: 750; letter-spacing: .09em; text-transform: uppercase; }
    .suggestion-text { color: var(--ink); font-size: .98rem; font-weight: 620; line-height: 1.4; margin-top: .48rem; }
    div[data-testid="stButton"] > button { min-height: 2.65rem; border-radius: 11px; border-color: #d5e0e9; color: var(--ink); font-weight: 650; transition: all .15s ease; }
    div[data-testid="stButton"] > button:hover { transform: translateY(-1px); border-color: var(--accent); color: var(--accent-strong); background: var(--accent-soft); }
    div[data-testid="stButton"] > button[kind="primary"] { background: var(--accent); border-color: var(--accent); color: #fff; }
    div[data-testid="stButton"] > button[kind="primary"]:hover { background: var(--accent-strong); border-color: var(--accent-strong); color: #fff; }
    [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 17px; background: rgba(255, 255, 255, .94); padding: 1rem 1.2rem; box-shadow: 0 4px 15px rgba(25, 45, 75, .025); }
    [data-testid="stChatInput"] { border: 1px solid #ccdbe4; border-radius: 17px; background: #fff; box-shadow: 0 10px 30px rgba(25, 45, 75, .08); }
    [data-testid="stChatInput"]:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15, 139, 129, .12), 0 10px 30px rgba(25, 45, 75, .08); }
    [data-testid="stChatInput"] textarea { color: #17243a !important; background: #fff !important; -webkit-text-fill-color: #17243a !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #738197 !important; -webkit-text-fill-color: #738197 !important; opacity: 1; }
    [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 12px; background: #fbfcfe; }
    [data-testid="stExpander"] summary { color: var(--accent-strong); font-weight: 650; }
    [data-testid="stCode"] { border-radius: 10px; }
    [data-testid="stDataFrame"] { border: 1px solid #e0e7ee; border-radius: 10px; overflow: hidden; }
    [data-testid="stAlert"] p { color: #26364d; }
    input, textarea { color: #17243a; }
    .sidebar-note { color: var(--muted); font-size: .88rem; line-height: 1.5; }
    @media (max-width: 700px) {
        .block-container { padding: 1rem 1rem 4rem; }
        .hero { padding: 1.6rem 1.35rem; border-radius: 20px; }
        .suggestion { min-height: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_details(details: dict) -> None:
    with st.expander("SQL et données consultées"):
        if details.get("sql"):
            st.code(details["sql"], language="sql")
        elif details.get("clarification"):
            st.caption("L’agent demande une précision ; aucune requête n’a été exécutée.")
        else:
            st.caption("Aucune requête SQL n’a été exécutée.")

        result = details.get("result") or {}
        if result.get("rows"):
            frame = pd.DataFrame(result["rows"], columns=result["columns"])
            st.dataframe(frame, use_container_width=True, hide_index=True)
        elif result.get("error"):
            st.caption("La requête n’a pas abouti après les tentatives de correction.")
        st.caption(f"Tentatives de génération : {details.get('attempts', 0)}")


with st.sidebar:
    st.markdown('<div class="brand-kicker">DATA EXPLORER</div>', unsafe_allow_html=True)
    st.title("DataPilot")
    st.markdown('<p class="sidebar-note">Explorez les données e-commerce Olist en posant vos questions en français.</p>', unsafe_allow_html=True)
    st.divider()
    if DB_PATH.exists():
        st.success("Base Olist connectée", icon="✅")
    else:
        st.error("Base Olist introuvable", icon="⚠️")
    st.caption(f"Modèle actif : `{MODEL_NAME}`")
    st.caption("Accès à la base : lecture seule")
    if st.session_state.get("messages") and st.button("Nouvelle conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown('<p class="sidebar-note">Astuce : indiquez une période, un statut ou un regroupement pour obtenir des résultats plus précis.</p>', unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
      <div class="brand-kicker">Vos données, en langage naturel</div>
      <h1>Que voulez-vous explorer&nbsp;?</h1>
      <p>Interrogez les commandes, les livraisons et les avis clients. DataPilot explique le résultat et vous laisse consulter le SQL utilisé.</p>
      <div class="hero-tags"><span class="hero-tag">● Données Olist</span><span class="hero-tag">● SQL en lecture seule</span><span class="hero-tag">● Réponses vérifiables</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)

if not DB_PATH.exists():
    st.error("La base Olist est absente. Préparez les données en suivant le README.")
    st.stop()
if not GEMINI_API_KEY:
    st.error("La clé Gemini n’est pas configurée. Ajoutez GEMINI_API_KEY dans .env puis redémarrez l’application.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.subheader("Explorez par thème")
    st.caption("Choisissez une suggestion pour lancer directement l’analyse.")
    examples = [
        ("COMMANDES", "Combien de commandes y a-t-il au total ?"),
        ("LIVRAISON", "Quel est le délai moyen de livraison des commandes livrées ?"),
        ("AVIS CLIENTS", "Quelle est la note moyenne des avis clients ?"),
    ]
    columns = st.columns(3, gap="medium")
    for index, (column, (label, example)) in enumerate(zip(columns, examples)):
        with column:
            st.markdown(
                f'<div class="suggestion suggestion-{["teal", "coral", "blue"][index]}"><div class="suggestion-label">{label}</div><div class="suggestion-text">{example}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Poser cette question", key=f"example_{index}", use_container_width=True):
                st.session_state.pending_question = example

for message in st.session_state.messages:
    avatar = "🧑‍💼" if message["role"] == "user" else "📊"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("details"):
            render_details(message["details"])

question = st.chat_input("Posez une question sur les commandes, les livraisons ou les avis…")
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="📊"):
        with st.spinner("DataPilot analyse votre question…"):
            try:
                final = run_graph(question, with_answer=True)
                answer = final.get("answer") or "Je n’ai pas obtenu de réponse exploitable."
                details = {
                    "sql": final.get("sql"),
                    "result": final.get("result"),
                    "attempts": final.get("attempts", 0),
                    "clarification": final.get("clarification", False),
                }
            except Exception:
                LOGGER.exception("Échec du traitement d’une question dans l’interface Streamlit")
                answer = "Le service IA n’a pas pu traiter cette question. Réessayez dans quelques instants ; si le problème persiste, vérifiez l’accès réseau et la clé API."
                details = None

        st.markdown(answer)
        if details:
            render_details(details)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "details": details,
    })
