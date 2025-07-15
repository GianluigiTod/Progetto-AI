# utils.py
from pathlib import Path
import os

def write_to_file(content: str, filename: str) -> bool:
    try:
        os.makedirs("output", exist_ok=True)
        full_path = Path("output") / filename
        full_path.write_text(content.strip(), encoding='utf-8')
        print(f"📂 File salvato: {full_path}")
        return True
    except Exception as e:
        print(f"❌ Errore scrittura {filename}: {e}")
        return False

def read_file(filepath: str) -> str:
    try:
        return Path(filepath).read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Errore lettura {filepath}: {e}")
        return ""