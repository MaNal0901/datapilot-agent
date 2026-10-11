import sys
from datapilot.agent.loop import ask

question = " ".join(sys.argv[1:]) or "Quels sont les 5 états brésiliens avec le plus de commandes ?"
print("\nRéponse :", ask(question))