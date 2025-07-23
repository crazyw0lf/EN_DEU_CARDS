# api_data.py
import json
import os

API_KEYS_FILE = "api_keys.json"


def load_api_keys():
    """Загружает API-ключи из файла. Если файл пустой или не существует — возвращает пустой список."""
    if not os.path.exists(API_KEYS_FILE):
        return []

    try:
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():  # Если файл пустой
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        # Если файл повреждён или содержит некорректный JSON
        print("Ошибка: файл содержит некорректные данные JSON.")
        return []


def save_api_keys(keys):
    """Сохраняет список API-ключей в файл."""
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)