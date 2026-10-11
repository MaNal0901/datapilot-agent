import sqlite3
import sys
import pandas as pd
from datapilot.config import DB_PATH, RAW_DIR

csv_files = sorted(RAW_DIR.glob("*.csv"))
if not csv_files:
    sys.exit(f"Aucun fichier CSV trouvé dans {RAW_DIR}. Télécharge le dataset Olist d'abord.")

if DB_PATH.exists():
    DB_PATH.unlink()          # repart d'une base propre

conn = sqlite3.connect(DB_PATH)
for path in csv_files:
    name = path.stem.removeprefix("olist_").removesuffix("_dataset")
    df = pd.read_csv(path)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"chargé : {name} ({len(df)} lignes)")
conn.close()