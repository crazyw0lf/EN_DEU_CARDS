# api_data.py
import json
import os

API_KEYS_FILE = "api_keys.json"


def load_api_keys():
    # load api keys from a JSON file. if the file does not exist or is empty, return an empty list
    if not os.path.exists(API_KEYS_FILE):
        return []

    try:
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():  # empty file check
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        # incorrect file format, return an empty list
        print("Error: Invalid JSON format in API keys file.")
        return []


def save_api_keys(keys):
    # save api keys to a JSON file
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)