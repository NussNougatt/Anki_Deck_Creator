import deepl
import genanki
import requests
import os

from deepl import version

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


my_note = genanki.Note(
    model=my_model,
    fields=['定義する[ていぎ]', 'definieren']
)

my_deck = genanki.Deck(
    1111111111,
    'KGU_Japanese'
)

my_deck.add_note(my_note)

genanki.Package(my_deck).write_to_file('japanese_deck.apkg')

package_path = os.path.abspath("japanese_deck.apkg")
auto_import(package_path)
