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

# Глобальный клиент (будет обновляться при смене ключа)
current_client_index = 0


def get_client() -> Groq:
    # Список ключей
    API_KEYS = load_api_keys()
    global current_client_index
    key_info = API_KEYS[current_client_index]
    print(f"Using API key from: {key_info['name']}")  # Для отладки
    return Groq(api_key=key_info["key"])


def make_request_with_retry(messages, model="llama-3.3-70b-versatile"):
    # Список ключей
    API_KEYS = load_api_keys()
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
    instruction = """
    You will receive a list of German words or short phrases.  
    Your task is to clean this list and keep only the words/phrases that are relevant ones that are too complicated.

    1. Remove:
       - Single letters (e.g., "a", "x")
       - Numbers
       - Symbols, special characters, or unreadable strings
       - Incomplete or nonsensical entries

    2. Correct:
       - Verbs should be converted to their infinitive form (e.g., "komme" → "kommen")
       - Misspelled words should be corrected if the meaning is recognizable
       - Fix lowercase letters at the beginning of sentences

    3. Keep:
       - Verbs in infinitive form
       - Nouns (substantives)
       - Adjectives
       - Short sentences or phrases

    Return just a list of words without any numeration and enter rows.
    At the end, provide a clean list of processed and corrected words/phrases.

    Example:
    Input: `komme aus Ich heiße Greg Hello frageD`
    Output:
    kommen aus
    Ich heiße Greg
    Hallo
    fragen
    """

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": text},
    ]

    return make_request_with_retry(messages)


# === Функция extract_verbs ===
def extract_verbs(text):
    instruction_step1 = """
You will receive a list of German words or phrases.

Your task is to:
1. Select only verbs (Verben).
2. Ignore:
   - Nouns, adjectives, pronouns (like ich, du, er, sie, es)
   - Numbers, symbols, and incomplete entries
   - Common non-verbs like "bitte", "danke", "ja", "nein", "und", etc.
   - Rare or complex verbs

3. For each selected verb:
   - Convert it to its infinitive form if it's in a conjugated or misspelled form.
   - Correct any spelling errors if the verb is recognizable.
   - Provide a **clear English translation** of the verb (not the German word itself), suitable for learners with B1 English level.
   - Conjugate the verb in the following forms:
     [ich], [du], [er/sie/es], [wir], [ihr], [sie/Sie]
   - Return the result in this STRICT EXACT format:
     [English translation of the verb];[German infinitive];[ich];[du];[er/sie/es];[wir];[ihr];[sie/Sie]
   - Do NOT include personal pronouns — only the verb form.
   - Use semicolons (;) to separate values.
   - Return only the final list — one verb per line. No explanations.

Important:
- Do not return duplicates.
- If the same verb appears multiple times in the input, include it only once in the output.
- Focus only on common, core verbs typically taught in A1–B2 curricula.
"""

    messages1 = [
        {"role": "system", "content": instruction_step1},
        {"role": "user", "content": text},
    ]
    intermediate_result = make_request_with_retry(messages1)

    instruction_step2 = """
    You will receive a list of lines, each containing:
[English translation];[German infinitive];[ich];[du];[er/sie/es];[wir];[ihr];[sie/Sie]

Your task is to:
1. Check each line for correctness and completeness. Output only the lines that are valid.
2. For each line, verify:
   - The first field is a correct English translation of the German verb (not the German word itself).
   - The second field is a valid German infinitive verb.
   - The following fields are correct conjugated forms for each pronoun.
   - The line follows the exact format with semicolons and no extra fields.
3. Remove:
   - Lines where the English translation is missing or incorrect.
   - Lines where the word is not a verb (e.g., noun, adjective, conjunction).
   - Duplicate lines (keep only one copy of each verb).
   - Lines with spelling errors in the German verb or incorrect conjugations.
4. For each valid line:
   - If the English translation is unclear or unnatural, suggest a better one.
   - If conjugations are wrong, correct them.
5. Return the final list in the same format:
   [English translation];[German infinitive];[ich];[du];[er/sie/es];[wir];[ihr];[sie/Sie]
6. Do not add explanations, comments, or additional text — only the corrected list.

If no lines are valid, return: "No valid entries found."
    """

    messages2 = [
        {"role": "system", "content": instruction_step2},
        {"role": "user", "content": intermediate_result},
    ]

    return make_request_with_retry(messages2)


# === Функция extract_except_verbs ===
def extract_except_verbs(text):
    instruction_step1 = """
You will receive a list of German words or phrases.  
Process each row exactly once using the following rules:

- If the word is a **concrete noun (Substantiv)**, such as objects, people, places:
  Format: [translation];[article singular German word] / [article plural German word]
  Example: house;das Haus / die Häuser

- If the word is a **verb (Verb)**:
  delete 

- If the word is an **abstract concept**, **phrase**, **adjective**, **adverb**, **pronoun**, **preposition**, etc.:
  Format: [translation];[original German word/phrase]
  - Translation must be accurate and in lowercase unless it's a proper noun

Rules:
- Each input word or phrase must be processed only once
- Only classify clearly concrete nouns as nouns
- Nouns must be capitalized correctly with appropriate articles in both singular and plural
- Phrases should remain intact
- Keep vocabulary strictly within A1–B1 CEFR level

Provide the result strictly in the format described above, one entry per line, without any explanations or additional text.

Example input:
sein
Haus
Guten Morgen
Entschuldigung

Expected output:
house;das Haus / die Häuser
good morning;Guten Morgen
excuse;Entschuldigung
            """

    messages1 = [
        {"role": "system", "content": instruction_step1},
        {"role": "user", "content": text},
    ]
    intermediate_result = make_request_with_retry(messages1)

    instruction_step2 = """
    You are a language expert who checks and corrects German-to-English vocabulary processing according to specific rules.

You will receive:
1. A list of German words or phrases.
2. The processed output generated from these words/phrases.

Your task:
- For each line, check whether it follows the rules correctly.
- If the line is **correct**, leave it unchanged.
- If the line is **incorrect**, provide the corrected version in the proper format.

Format: [translation];[original German word/phrase]

Rules:
- Verbs must be deleted entirely.
- Concrete nouns must show: [translation];[article singular German word] / [article plural German word]
- Abstract nouns, phrases, adjectives, adverbs, pronouns, prepositions, etc. must show: [translation];[original German word/phrase]
- Translation must be in lowercase unless it's a proper noun.
- Nouns must be capitalized correctly with appropriate articles in both singular and plural.
- Each German word must be processed exactly once.
- Keep vocabulary strictly within A1–B1 CEFR level.

Provide the result strictly in the format described above, one entry per line, without any markdown or explanations beyond the required format.
                """

    messages2 = [
        {"role": "system", "content": instruction_step2},
        {"role": "user", "content": intermediate_result},
    ]

    return make_request_with_retry(messages2)