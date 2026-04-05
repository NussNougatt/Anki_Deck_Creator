import deepl
import genanki
import requests
import os
import tkinter as tk
import pykakasi
import keyboard

from deepl import version

notes = []

def show_confirmation(deck_notes, on_confirm):
    confirm_window = tk.Toplevel(root)
    confirm_window.title("Confirm Cards")

    tk.Label(confirm_window, text="The following cards will be added:", font=("Arial", 12, "bold")).pack(pady=5)

    frame = tk.Frame(confirm_window)
    frame.pack(padx=10, pady=5)

    # Headers
    tk.Label(frame, text="Kanji", width=15, font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=0, padx=5)
    tk.Label(frame, text="Furigana", width=20, font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=1, padx=5)
    tk.Label(frame, text="Translation", width=20, font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=2, padx=5)

    for i, note in enumerate(deck_notes):
        front = note.fields[0]
        back = note.fields[1]

        if "[" in front:
            kanji = front[:front.index("[")]
            furigana = front[front.index("[")+1:front.index("]")]
        else:
            kanji = front
            furigana = front

        tk.Label(frame, text=kanji, width=15, anchor="w").grid(row=i+1, column=0, padx=5, pady=2)
        tk.Label(frame, text=furigana, width=20, anchor="w").grid(row=i+1, column=1, padx=5, pady=2)
        tk.Label(frame, text=back, width=20, anchor="w").grid(row=i+1, column=2, padx=5, pady=2)

    btn_frame = tk.Frame(confirm_window)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Confirm", command=lambda: [confirm_window.destroy(), on_confirm()]).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", command=confirm_window.destroy).pack(side="left", padx=10)

def get_furigana(text):
    kks = pykakasi.kakasi()
    result = kks.convert(text)

    furigana_field = ""
    for item in result:
        if item['hira'] and item['orig'] != item['hira']:
            furigana_field += f"{item['orig']}[{item['hira']}]"
        else:
            furigana_field += item['orig']
    return furigana_field


auth_key = "REMOVED_DEEPL_KEY"
translator = deepl.Translator(auth_key)

root = tk.Tk()
root.title("Anki Deck")


def get_lines(deck_notes):
    deck_notes.clear()  # <-- reset before adding new notes
    all_content = text_box.get("1.0", "end-1c")
    lines_array = all_content.split('\n')

    for line in lines_array:
        if line.strip() == "":
            continue
        result = translator.translate_text(line, target_lang="DE")
        deck_notes.append(genanki.Note(model=my_model, fields=[get_furigana(line), result.text]))
    show_confirmation(deck_notes, on_confirm=root.quit)

text_box = tk.Text(root, height=10, width=40)
text_box.pack(pady=10)

btn = tk.Button(root, text="Read Input", command=lambda: get_lines(notes))
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

def deck_exists(deck_name):
    payload = {
        "action": "deckNames",
        "version": 6,
    }
    try:
        response = requests.post("http://localhost:8765", json=payload)
        result = response.json()

        if result.get("error"):
            print("AnkiConnect error:", result["error"])
            return False

        deck_names = result.get("result", [])
        return deck_name.strip().lower() in [d.strip().lower() for d in deck_names]

    except requests.exceptions.ConnectionError:
        print("Could not connect to Anki. Make sure Anki is open and AnkiConnect is installed.")
        return False
    except Exception as e:
        print("Unexpected error:", e)
        return False


def add_notes_to_deck(deck_name, deck_notes):
    model_name = get_deck_model_name(deck_name)  # <-- fetch dynamically
    anki_notes = []
    for deck_note in deck_notes:
        anki_notes.append({
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {
                "Front": deck_note.fields[0],
                "Back": deck_note.fields[1],
            },
            "options": {
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


def create_or_update_deck(deck, deck_notes, path):
    deck_name = deck.name

    if deck_exists(deck_name):
        print(f"Deck '{deck_name}' already exists. Adding new cards...")
        add_notes_to_deck(deck_name, deck_notes)
    else:
        print(f"Deck '{deck_name}' not found. Creating new deck...")
        for note in deck_notes:  # <-- add notes to deck object before writing
            deck.add_note(note)
        genanki.Package(deck).write_to_file(path)
        auto_import(os.path.abspath(path))

#notes = [
#    genanki.Note(model=my_model, fields=["定義する[ていぎ]", "definieren"]),
#]

for note in notes:
    my_deck.add_note(note)

root.mainloop()
root.quit()

def get_deck_model_name(deck_name):
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f"deck:{deck_name}"}
    }
    response = requests.post("http://localhost:8765", json=payload)
    note_ids = response.json().get("result", [])

    if note_ids:
        payload2 = {
            "action": "notesInfo",
            "version": 6,
            "params": {"notes": [note_ids[0]]}
        }
        response2 = requests.post("http://localhost:8765", json=payload2)
        model_name = response2.json().get("result", [])[0].get("modelName")
        print("Using model:", model_name)
        return model_name

    return "Anki Deck"

#get_deck_model("KGU_Japanese")

package_path = os.path.abspath("japanese_deck.apkg")

create_or_update_deck(my_deck, notes, package_path)
