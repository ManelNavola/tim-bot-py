import json
import os
from typing import Union

TRANSLATIONS = {}
FALLBACK = None


def load():
    global FALLBACK
    trans_path = 'lang'
    sub_folders = [f.name for f in os.scandir(trans_path) if f.is_dir()]
    for folder in sub_folders:
        with open(f"{trans_path}/{folder}/translations.json", 'r', encoding='utf-8') as f:
            TRANSLATIONS[folder] = json.load(f)
            print(folder)
    FALLBACK = TRANSLATIONS['en']
    print(f"Loaded {len(TRANSLATIONS)} languages")


def get_available() -> list[str]:
    return list(TRANSLATIONS.keys())


def tr(lang_lang_lang: str, text_id: str, **kwargs) -> str:
    language_json: dict[str, str] = TRANSLATIONS.get(lang_lang_lang, FALLBACK)
    paths: list[str] = text_id.split('.')
    access: Union[dict, str] = language_json[paths[0]]
    for i in range(1, len(paths)):
        access = access[paths[i]]
    return access.format(**kwargs)
