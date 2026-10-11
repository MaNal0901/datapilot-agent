from datapilot.tools.db import run_sql

SQL = """
WITH order_cat AS (
    SELECT DISTINCT oi.order_id, p.product_category_name AS cat
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    WHERE p.product_category_name IS NOT NULL
)
SELECT COALESCE(t.product_category_name_english, oc.cat) AS categorie,
       COUNT(*) AS nb_avis,
       ROUND(AVG(r.review_score), 2) AS note_moyenne
FROM order_cat oc
JOIN order_reviews r ON r.order_id = oc.order_id
LEFT JOIN product_category_name_translation t ON t.product_category_name = oc.cat
GROUP BY oc.cat
HAVING COUNT(*) >= 100
ORDER BY note_moyenne ASC
LIMIT 5
"""

res = run_sql(SQL)
if "error" in res:
    print("Erreur :", res["error"])
else:
    print(res["columns"])
    for row in res["rows"]:
        print(row)