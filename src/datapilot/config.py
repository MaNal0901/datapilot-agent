import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "olist.db"
RAW_DIR = ROOT / "data" / "raw"

MAX_STEPS = 6   # garde-fou : nombre max d'itérations de l'agent
MAX_ROWS = 50   # garde-fou : nombre max de lignes renvoyées

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")