import deepl
import genanki

my_model = genanki.Model(
    1234567890,
    'Anki Deck',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
    ],
    templates=[
        {
        'name': 'Card 1',
        'qfmt': '''{{kanji:Front}}''',
        'afmt': '{{furigana:Front}}<hr id=answer>{{kanji:Back}}',
        },
    ],
)


my_note = genanki.Note(
    model=my_model,
    fields=['定義する', 'definieren']
)

my_deck = genanki.Deck(
    1111111111,
    'KGU_Japanese'
)

my_deck.add_note(my_note)

genanki.Package(my_deck).write_to_file('japanese_deck.apkg')
