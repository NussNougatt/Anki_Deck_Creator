import deepl
import genanki
import requests
import os
import tkinter as tk
import pykakasi

from deepl import version

def get_furigana(text):
    kks = pykakasi.kakasi()
    result = kks.convert(text)

    furigana = "".join([item['hira'] for item in result])
    return furigana

#print(get_furigana("定義する"))

auth_key = "REMOVED_DEEPL_KEY"
translator = deepl.Translator(auth_key)

root = tk.Tk()
root.title("Anki Deck")


def get_lines():
    all_content = text_box.get("1.0", "end-1c")
    lines_array = all_content.split('\n')

    print(lines_array)
    for line in lines_array:
        result = translator.translate_text(line, target_lang="DE")
        print(result.text)
    root.destroy()

text_box = tk.Text(root, height=10, width=40)
text_box.pack(pady=10)

btn = tk.Button(root, text="Read Input", command=get_lines)
btn.pack()


my_css = """
.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

/* This creates a container that fills the screen and centers its contents */
.centered-content {
    display: flex;
    justify-content: center; /* Horizontal center */
    align-items: center;     /* Vertical center */
    height: 100vh;           /* Full viewport height */
}
"""

my_model = genanki.Model(
    1234567890,
    'Anki Deck',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
    ],
    templates=[
        {
        'name': 'Front_Card',
        'qfmt': '''{{kanji:Front}}''',
        'afmt': '{{furigana:Front}}<hr id=answer>{{kanji:Back}}',
        },
        {
        'name': 'Reverse_Card',
        'qfmt': '''{{kanji:Back}}''',
        'afmt': '{{{kanji:Back}}<hr id=answer>{{furigana:Front}}',
        },
    ],
    css=my_css,
)

def auto_import(path):
    payload = {
        "action": "importPackage",
        "version": 6,
        "params": { "path": path }
    }
    try:
        response = requests.post("http://localhost:8765", json=payload)
        print("Import Success:", response.json())
    except Exception as e:
        print("Error connecting to Anki:", e)


my_deck = genanki.Deck(
    1111111111,
    'KGU_Japanese'
)

def deck_exists(deckName):
    payload = {
        "action": "getDeckNames",
        "version": 6,
    }
    try:
        response = requests.post("http://localhost:8765", json=payload)
        deck_names = response.json()
        return deckName in deck_names
    except Exception as e:
        print("Error connecting to Anki:", e)
        return False

def add_notes_to_deck(deckName, notes):
    anki_notes = []
    for note in notes:
        anki_notes.append({
            "deckName": deckName,
            "modelName": "Anki Deck",
            "fields":{
                "Front": note.fields[0],
                "Back": note.fields[1],
            },
            "options":{
                "allowDuplicates": False,
            }
        })
    payload = {
        "action": "addNotes",
        "version": 6,
        "params": {"notes": anki_notes}
    }
    try:
        response = requests.post("http://localhost:8765", json=payload)
        print("Notes added:", response.json())
    except Exception as e:
        print("Error connecting to Anki:", e)


def create_or_update_deck(deck, notes, package_path):
    deck_name = deck.name

    if deck_exists(deck_name):
        print(f"Deck '{deck_name}' already exists. Adding new cards...")
        add_notes_to_deck(notes, deck_name)
    else:
        print(f"Deck '{deck_name}' not found. Creating new deck...")
        genanki.Package(deck).write_to_file(package_path)
        auto_import(os.path.abspath(package_path))

notes = [
    genanki.Note(model=my_model, fields=["定義する", "definieren"]),
]

for note in notes:
    my_deck.add_note(note)

root.mainloop()

package_path = os.path.abspath("japanese_deck.apkg")

create_or_update_deck(my_deck, notes, package_path)
