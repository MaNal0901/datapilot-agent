# DataPilot Agent

Agent Data Scientist connecté à une base de données SQL (text-to-SQL, analyse, ML).

## État du projet
- [x] Étape 1 : boucle agent minimale (question -> SQL -> exécution -> réponse)
- [ ] Étape 2 : LangGraph + auto-correction
- [ ] Étape 3 : schéma RAG + ML en sandbox
- [ ] Étape 4 : garde-fous + évaluation chiffrée

## Architecture de l'agent

```mermaid
graph TD
    debut([Question]) --> load_schema[load_schema<br/>lire le schéma de la base]
    load_schema --> generate_sql[generate_sql<br/>le LLM écrit le SQL]
    generate_sql --> execute_sql[execute_sql<br/>exécution en lecture seule]
    execute_sql -.->|erreur ou 0 ligne, moins de 3 tentatives| generate_sql
    execute_sql -.->|résultat valide| write_answer[write_answer<br/>le LLM rédige la réponse]
    execute_sql -.->|trop d'échecs| give_up[give_up<br/>abandon explicite]
    write_answer --> fin([Réponse])
    give_up --> fin
```

Les flèches en pointillés sont des arêtes conditionnelles : le routeur choisit la suite selon l'état.