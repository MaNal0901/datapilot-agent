# Comparaison des modèles

Les exécutions ci-dessous utilisent le même jeu SQL de 25 questions et le même code. Une pause de quatre secondes a été appliquée entre les questions.

| Exécution | Modèle | Résultat | Latence moyenne | Plantages | Lecture |
|---|---|---:|---:|---:|---|
| `bench_lite_1` | `gemini-3.5-flash-lite` | 25/25 | 2,0 s | 0 | Complète |
| `bench_lite_2` | `gemini-3.5-flash-lite` | 25/25 | 2,3 s | 0 | Complète |
| `bench_lite_3` | `gemini-3.5-flash-lite` | 25/25 | 2,2 s | 0 | Complète |
| `bench_flash_final` | `gemini-3.5-flash` | 2/2 évaluées | 3,2 s | 1 | Q01–Q02 réussies ; q03 a expiré après quota flash épuisé et surcharge du secours. Q04–Q25 non exécutées. Non comparable. |
| `lite_decline_v5` | `gemini-3.5-flash-lite` | 25/25 | 1,9 s | 0 | Régression après l’ajout du comportement de clarification. |

Le score du run flash ne permet pas de comparer les modèles : seules deux questions ont été évaluées et le modèle de secours n’a pas répondu à la suivante. Il faudra relancer ce run après le rétablissement du quota.

## Robustesse et tests

- `robust_v4` : 10/10, sans plantage — 5 questions de données absentes, 1 ambiguë et 4 dangereuses.
- `pytest` : 25 tests passés.

Les scores sont des observations ponctuelles sur le jeu fourni ; le modèle peut produire des résultats différents lors d’une autre exécution.

## Fichiers de résultats

- [Run lite 1](results/bench_lite_1_20261107_1351.json)
- [Run lite 2](results/bench_lite_2_20261107_1354.json)
- [Run lite 3](results/bench_lite_3_20261107_1357.json)
- [Run flash initial](results/bench_flash_20261107_1400.json)
- [Run flash partiel après reprise](results/bench_flash_final_20261107_1850.json)
- [Régression lite après clarification](results/lite_decline_v5_20261107_1409.json)
- [Robustesse v4](results/robust_v4_20261107_1408.json)
