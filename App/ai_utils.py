import json
import os
from groq import Groq, InternalServerError, RateLimitError, APIStatusError
from typing import List, Dict


# Загрузка API-ключей из файла
def load_api_keys(filepath: str = "api_keys.json") -> List[Dict[str, str]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"API keys file '{filepath}' not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [{"name": item["name"], "key": item["key"]} for item in data]


# Список ключей
API_KEYS = load_api_keys()

# Глобальный клиент (будет обновляться при смене ключа)
current_client_index = 0


def get_client() -> Groq:
    global current_client_index
    key_info = API_KEYS[current_client_index]
    print(f"Using API key from: {key_info['name']}")  # Для отладки
    return Groq(api_key=key_info["key"])


def make_request_with_retry(messages, model="llama-3.3-70b-versatile"):
    global current_client_index
    max_retries = len(API_KEYS)  # Количество попыток = количество ключей
    last_exception = None

    for attempt in range(max_retries):
        try:
            client = get_client()
            chat_completion = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return chat_completion.choices[0].message.content

        except RateLimitError as e:
            if e.status_code == 429:
                print(f"Rate limit exceeded with key '{API_KEYS[current_client_index]['name']}'. Switching key...")
                current_client_index = (current_client_index + 1) % len(API_KEYS)
            else:
                raise e

        except APIStatusError as e:
            if e.status_code == 429:
                print(f"Status 429 with key '{API_KEYS[current_client_index]['name']}'. Switching key...")
                current_client_index = (current_client_index + 1) % len(API_KEYS)
            else:
                raise e

        except Exception as e:
            print(f"Unexpected error with key '{API_KEYS[current_client_index]['name']}': {str(e)}")
            current_client_index = (current_client_index + 1) % len(API_KEYS)

    raise RuntimeError("All API keys have been rate-limited. Try again later.")


# === Функция clean_tokenized_text ===
def clean_tokenized_text(text):
    instruction = """You are given a list of German vocabulary items, including nouns with articles, verbs, adjectives, and category headings such as "Lernwortschatz", "Kleidung", "Gegenstände", "Im Kaufhaus", and "Weitere wichtige Wörter". Your task is to process the input as follows:

1. **Remove all category headings** — skip any lines that are section titles (e.g., "Kleidung", "Im Kaufhaus", etc.).
2. **Process each lexical item**:
   - If a noun is marked with an article (e.g., "Jacke die,-n"), output it in the form "die Jacke", placing the article before the noun in its singular nominative form.
   - Ignore plural forms, declension endings (like "-n", ":'e", "-s"), and grammatical notes.
3. **Extract verbs in infinitive form**: if a verb appears in a line (e.g., "an·probieren, (hat anprobiert)"), extract only the infinitive (e.g., "anprobieren"). Ignore past participles, auxiliary verbs, and usage examples in parentheses.
4. **Split lines with multiple entries**: if a single line contains two separate words with their own articles or markers (e.g., "Brieftasche die,-n Koffer der,"), split them into two separate lines: "die Brieftasche" and "der Koffer".
5. **Omit all extra content**: remove example sentences, page numbers, explanations, conjugations, and non-lexical information (like "einhunderteinundvierzig 141 LEKTION 13").
6. **Output a clean vertical list**: one correctly formatted word per line, in the order they appear in the original list. Do not add titles, numbering, or explanations.

Only return the final formatted list with no additional text."""

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": text},
    ]

    return make_request_with_retry(messages)


# === Функция extract_verbs ===
def extract_verbs(text):
    instruction_step1 = """
You will receive a list of German words containing nouns, verbs, and adjectives. Your task is to:

1. **Identify only the verbs** in their infinitive form (e.g., "anprobieren", "zahlen", "mögen").
2. For each verb, generate a conjugation line in the present tense (Präsens) with the following format:
   [English translation];[Infinitive];[ich-form];[du-form];[er/sie/es-form];[wir-form];[ihr-form];[sie/Sie-form]

   Example:
   to try on;anprobieren;probiere an;probierst an;probiert an;probieren an;probiert an;probieren an

3. Use correct separable verb formatting if applicable (e.g., "anprobieren" → "probiere an", not "probiere").
4. Ensure accurate conjugation for irregular verbs (e.g., "mögen" → ich mag, du magst, etc.).
5. Provide only one line per verb, and output **only** the resulting lines in the specified format.
6. Do not include pronouns, explanations, titles, or additional text — only the semicolon-separated conjugation lines.
7. If a verb has multiple common English meanings, list them separated by slashes (e.g., "to like/to be fond of").

Process all verbs in the input list and output the result as a clean, line-by-line list.
"""

    message = [
        {"role": "system", "content": instruction_step1},
        {"role": "user", "content": text},
    ]

    return make_request_with_retry(message)


# === Функция extract_except_verbs ===
def extract_except_verbs(text):
    instruction_step1 = """
You are given a list of German words, one per line. Your task is to process the list as follows:

1. **Remove all verbs** from the list. Verbs are words that do not have a definite article (der, die, das) and typically end in -en or -n (e.g. anprobieren, anziehen, trainieren, zahlen, gehören, mögen, schauen). These must be excluded from the output.

2. **Identify nouns**: Any word **preceded by an article** (der, die, das) is a noun. Format each noun as:
   [English translation];[singular article] [singular German noun] / [plural article] [plural German noun]
   - Use the correct English translation.
   - Provide the standard plural form of the noun in German, along with its plural article (usually "die", but adjust if different).
   - Example: clothing;die Kleidung / die Kleidungen

3. **All other non-verb words without articles that are not nouns** (e.g. adjectives, pronouns, adverbs, numerals, etc.) should be included as:
   [English translation];[original German word]
   - Example: this;dieser

4. **Important annotation for parsing**:
   - Nouns will **always** be prefixed with one of the definite articles: *der*, *die*, or *das*.
   - Words **without** an article are **not nouns**, but may still be valid entries (e.g. adjectives, pronouns) — **do not remove them**, unless they are verbs.
   - Verbs (infinitive forms, often ending in -en/-n, no article) must be **removed entirely**.

5. Use the provided vocabulary mapping (as in e_verbs.txt) to ensure accurate English translations.

6. Output only the formatted lines — one per entry — in the order they appear in the original list, excluding verbs. Do not include headers, explanations, or comments.

Example:
Input: dieser → no article, not a verb → Output: this;dieser
Input: die Hose → has article → noun → Output: trousers;die Hose / die Hosen
Input: schauen → verb → skip

Process all lines accordingly.
"""

    message = [
        {"role": "system", "content": instruction_step1},
        {"role": "user", "content": text},
    ]

    return make_request_with_retry(message)