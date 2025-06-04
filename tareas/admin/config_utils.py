import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config.json'

def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open('r', encoding='utf-8') as f:
            return json.load(f)
    return {'nombre_clinica': 'BioSalud', 'logo_url': ''}

def save_config(data):
    with CONFIG_PATH.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
