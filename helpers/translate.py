import json
from os import walk

TRANSLATIONS = {}
FALLBACK = None


def load():
    global FALLBACK
    trans_path = 'lang'
    _, _, filenames = next(walk(trans_path))
    for filename in filenames:
        with open(f"{trans_path}/{filename}", 'r') as f:
            TRANSLATIONS[filename[:filename.find('.json')]] = json.load(f)
    FALLBACK = TRANSLATIONS['en']


def tr(lang: str, text_id: str, **kwargs) -> str:
    language_json: dict[str, str] = TRANSLATIONS.get(lang, FALLBACK)
    return language_json[text_id].format(**kwargs)
