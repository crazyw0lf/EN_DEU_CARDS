import genanki
import random
import os
from gtts import gTTS
import base64
import io

def create_s_deck(label):

    MODEL_ID = random.randint(1, 10000)
    DECK_ID = random.randint(1, 10000)

    deck_name = f"Unit {label} Substantiv"

    CSS_STYLE = """
        .card {
          font-family: Arial, sans-serif;
          font-size: 24px;
          text-align: center;
          color: #2e2e2e;
          background-color: #f9f9f9;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .input-box {
          margin-top: 20px;
          padding: 10px;
          font-size: 20px;
          width: 80%;
          max-width: 300px;
          border: 2px solid #ccc;
          border-radius: 5px;
        }

        .check-btn {
          margin-top: 15px;
          padding: 10px 20px;
          font-size: 18px;
          cursor: pointer;
          background-color: #4CAF50;
          color: white;
          border: none;
          border-radius: 5px;
        }

        .audio-btn {
          margin-top: 10px;
          padding: 8px 16px;
          font-size: 16px;
          background-color: #2196F3;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        }
        """

    HTML_QUESTION = """
        <div class="card">
          <div>{{Front}}</div>
          <input type="text" id="user_input" class="input-box" placeholder="Input translation">
          <br>
          <button class="check-btn" onclick="checkAnswer()">Check</button>
        </div>

        <script>
        function checkAnswer() {
          const userInput = document.getElementById('user_input').value.trim();
          const correctAnswer = "{{Back}}".trim();

          if (!userInput) {
            alert("Input translation!");
            return;
          }

          const inputBox = document.getElementById('user_input');
          if (userInput.toLowerCase() === correctAnswer.toLowerCase()) {
            inputBox.style.backgroundColor = '#baffc9'; // red
          } else {
            inputBox.style.backgroundColor = '#ffb3b3'; // green
          }
        }
        </script>
        """

    HTML_ANSWER = """
        {{FrontSide}}
        <hr>
        <div class="card">
          <div>Correct translation:</div>
          <div style="margin-top: 10px; font-weight: bold;">{{Back}}</div>
          <button class="audio-btn" onclick="playAudio()">🔊 Play</button>
          <audio id="back_audio"></audio>
        </div>

        <script>
        function playAudio() {
          const audioElement = document.getElementById('back_audio');
          if (!audioElement.src) {
            audioElement.src = "{{Audio_Back}}";
          }
          audioElement.play().catch(e => console.error("Play error:", e));
        }
        </script>
        """

    model = genanki.Model(
        model_id=MODEL_ID,
        name='Interactive Input Card with Audio',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'Audio_Back'},
        ],
        templates=[{
            'name': 'Card',
            'qfmt': HTML_QUESTION,
            'afmt': HTML_ANSWER,
        }],
        css=CSS_STYLE)

    deck = genanki.Deck(deck_id=DECK_ID, name=deck_name)
    word_pairs = []

    filename = f"C:/Users/GANT-NB/Music/anki/sources/subs {label}.txt"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file.read().splitlines():
                if line.strip():
                    arr = line.split(";")
                    if len(arr) == 2:
                        word_pairs.append(arr)
    except FileNotFoundError:
        print(f"Can't find file: {filename}!")
        return

    random.shuffle(word_pairs)

    for front, back in word_pairs:
        try:
            # Создаём TTS объект
            tts = gTTS(text=back, lang='de', slow=False)

            # Сохраняем в BytesIO (в памяти)
            fp = io.BytesIO()
            tts.write_to_fp(fp)  # <-- Вот правильный способ!
            fp.seek(0)

            # Читаем байты и кодируем в Base64
            audio_bytes = fp.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            audio_field = f"data:audio/mpeg;base64,{audio_base64}"
        except Exception as e:
            print(f"Error while generating audio for '{back}': {e}")
            audio_field = ""

        note = genanki.Note(
            model=model,
            fields=[front.strip(), back.strip(), audio_field]
        )
        deck.add_note(note)

    # Экспорт колоды
    package = genanki.Package(deck)
    path = f'C:/Users/GANT-NB/Music/anki/packages/en_to_deu_subs_{label}.apkg'

    if os.path.exists(path):
        os.remove(path)

    package.write_to_file(path)
    print(f'Successfully created deck at the path: {path}')

def create_v_deck(label):
    MODEL_ID = random.randint(1, 10000)
    DECK_ID = random.randint(1, 10000)

    deck_name = f"Unit {label} Verb"

    CSS_STYLE = """
    .card {
      font-family: Arial, sans-serif;
      font-size: 24px;
      text-align: center;
      color: #2e2e2e;
      background-color: #f9f9f9;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .input-box {
      margin-top: 20px;
      padding: 10px;
      font-size: 20px;
      width: 80%;
      max-width: 300px;
      border: 2px solid #ccc;
      border-radius: 5px;
    }

    .check-btn {
      margin-top: 15px;
      padding: 10px 20px;
      font-size: 18px;
      cursor: pointer;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
    }

    .audio-btn {
      margin-top: 15px;
      padding: 8px 16px;
      font-size: 16px;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    """

    HTML_QUESTION = """
    <div class="card">
      <div>{{Front}}</div>
      <input type="text" id="user_input" class="input-box" placeholder="Input translation">
      <br>
      <button class="check-btn" onclick="checkAnswer()">Check</button>
    </div>

    <script>
    function checkAnswer() {
      const userInput = document.getElementById('user_input').value.trim();
      const correctAnswer = "{{Back}}".trim();

      if (!userInput) {
        alert("Input translation!");
        return;
      }

      const inputBox = document.getElementById('user_input');
      if (userInput.toLowerCase() === correctAnswer.toLowerCase()) {
        inputBox.style.backgroundColor = '#baffc9'; // red
      } else {
        inputBox.style.backgroundColor = '#ffb3b3'; // green
      }
    }
    </script>
    """

    HTML_ANSWER = """
    {{FrontSide}}
    <hr>
    <div class="card">
      <div>Correct translation:</div>
      <div style="margin-top: 10px; font-weight: bold;">{{Back}}</div>
      <div style="margin-top: 8px;">ich {{ich}} ; du {{du}}</div>
      <div style="margin-top: 8px;">er {{er}} ; wir {{wir}}</div>
      <div style="margin-top: 8px;">ihr {{ihr}} ; sie {{sie}}</div>

      <button class="audio-btn" onclick="playAudio()">🔊 Play</button>
      <audio id="back_audio"></audio>
    </div>

    <script>
    function playAudio() {
      const audioElement = document.getElementById('back_audio');
      if (!audioElement.src) {
        audioElement.src = "data:audio/mpeg;base64,{{Audio_Back}}";
      }
      audioElement.play().catch(e => console.error("Error playing:", e));
    }
    </script>
    """

    # Модель с новым полем Audio_Back
    model = genanki.Model(
        model_id=MODEL_ID,
        name='Interactive Verb Card with Audio',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'ich'},
            {'name': 'du'},
            {'name': 'er'},
            {'name': 'wir'},
            {'name': 'ihr'},
            {'name': 'sie'},
            {'name': 'Audio_Back'},  # Поле для Base64-аудио
        ],
        templates=[{
            'name': 'Card',
            'qfmt': HTML_QUESTION,
            'afmt': HTML_ANSWER,
        }],
        css=CSS_STYLE)

    deck = genanki.Deck(deck_id=DECK_ID, name=deck_name)
    word_pairs = []

    filename = f"C:/Users/GANT-NB/Music/anki/sources/verbs {label}.txt"

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file.read().splitlines():
                if line.strip():
                    arr = line.split(";")
                    if len(arr) == 8:
                        word_pairs.append(arr)
                    else:
                        print(f"Incorrect structure: {line}")
    except FileNotFoundError:
        print(f"Can't find file: {filename}")
        return

    random.shuffle(word_pairs)

    for row in word_pairs:
        back = " ; ".join(row[1:])

        # Audio generation
        try:
            tts = gTTS(text=back, lang='de', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error while generating audio '{back}': {e}")
            audio_base64 = ""

        # Adding the audio field
        fields = row + [audio_base64]

        note = genanki.Note(model=model, fields=fields)
        deck.add_note(note)

    package = genanki.Package(deck)
    path = f'C:/Users/GANT-NB/Music/anki/packages/en_to_deu_verbs_{label}.apkg'

    if os.path.exists(path):
        os.remove(path)

    package.write_to_file(path)
    print(f'Successfully created deck at the path: {path}')