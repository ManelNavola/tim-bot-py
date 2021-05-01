import json
from os import walk

TRANSLATIONS = {}
FALLBACK = None


def load():
    global FALLBACK
    trans_path = 'lang'
    _, _, filenames = next(walk(trans_path))
    for filename in filenames:
        with open(f"{trans_path}/{filename}", 'r', encoding='utf-8') as f:
            TRANSLATIONS[filename[:filename.find('.json')]] = json.load(f)
    FALLBACK = TRANSLATIONS['en']
    print(f"Loaded {len(TRANSLATIONS)} languages")


def get_available() -> list[str]:
    return list(TRANSLATIONS.keys())


def tr(lang_lang_lang: str, text_id: str, **kwargs) -> str:
    language_json: dict[str, str] = TRANSLATIONS.get(lang_lang_lang, FALLBACK)
    return language_json[text_id].format(**kwargs)
