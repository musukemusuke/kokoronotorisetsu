import os
import json
from typing import Dict, Any

DATA_FILE = "user_manuals.json"

def load_manuals() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_manuals(manuals: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(manuals, f, ensure_ascii=False, indent=4)