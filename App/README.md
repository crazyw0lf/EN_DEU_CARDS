# EN_DEU_CARDS

A Python application for generating interactive Anki decks to help users learn German vocabulary and verbs. The app uses AI-powered text-to-speech for audio, custom card templates, and supports easy deck creation from source files.

## Features

- \*\*Interactive Anki Cards\*\*: Cards with input fields for translation, instant feedback, and audio playback.
- \*\*Text-to-Speech Audio\*\*: German audio generated for each card using Google TTS.
- \*\*Customizable Decks\*\*: Create decks for nouns (Substantiv) and verbs with conjugations.
- \*\*Modern Card Styling\*\*: Clean, responsive card design for better learning experience.
- \*\*Easy Source Management\*\*: Import word pairs and verb conjugations from `.txt` files.
- \*\*API Key Management\*\*: Securely store and manage API keys (if needed for future features).

## Directory Structure

```
App/
├── about_page.py
├── ai_utils.py
├── anki_utils.py
├── api_data.py
├── api_keys_page.py
├── api_keys.json
├── custom_dialog.py
├── main_screen.py
├── main_window.py
├── main.py
├── settings_screen.py
├── source_to_txt_utils.py
├── styles.py
├── requirements.txt
├── icons/
│   ├── app_icon.png
│   ├── confirm_icon.png
│   ├── create_key.jpg
│   ├── create_key.png
│   ├── delete_key.png
│   ├── edit_key.png
│   └── warning_icon.png
└── __pycache__/
```

## Requirements

- Python 3.8+
- [genanki](https://github.com/kerrickstaley/genanki)
- [gtts](https://pypi.org/project/gTTS/)
- Other dependencies (see `requirements.txt` if available)

## Installation

1. \*\*Clone the repository:\*\*
   ```
   git clone https://github.com/crazyw0lf/EN_DEU_CARDS.git
   cd EN_DEU_CARDS
   ```

2. \*\*Install dependencies:\*\*
   ```
   pip install -r requirements.txt
   ```

3. \*\*Prepare source files:\*\*
   - Place your vocabulary files in `C:/Users/GANT-NB/Music/anki/sources/`:
     - For nouns: `subs <label>.txt` (format: `EN;DE`)
     - For verbs: `verbs <label>.txt` (format: `EN;DE;ich;du;er;wir;ihr;sie`)

## Usage

1. \*\*Run the application:\*\*
   ```
   python App/main.py
   ```

2. \*\*Create a deck:\*\*
   - Use the UI to select deck type (Substantiv or Verb) and label.
   - The app will generate an `.apkg` file in `C:/Users/GANT-NB/Music/anki/packages/`.

3. \*\*Import into Anki:\*\*
   - Open Anki.
   - Go to `File > Import` and select the generated `.apkg` file.

## Card Templates

- \*\*Substantiv Cards:\*\* Input translation, check answer, play German audio.
- \*\*Verb Cards:\*\* Input translation, view conjugations, play German audio.

## Troubleshooting

- \*\*File Not Found:\*\* Ensure your source files are named and placed correctly.
- \*\*Audio Issues:\*\* Check your internet connection (Google TTS requires it).
- \*\*Deck Not Created:\*\* Check for errors in the console and verify file formats.

## Contributing

Pull requests and suggestions are welcome! Please open an issue for bugs or feature requests.

## License

This project is licensed under the MIT License.

---

**Author:** [crazyw0lf](https://github.com/crazyw0lf)
