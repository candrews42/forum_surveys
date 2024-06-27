import datetime
import json
import logging
from os import pardir
from os.path import join
from os.path import dirname

from .models import DEPRECATED_MODELS
from .models import GPT_4_VISION_PREVIEW
from .models import DEPRECATION_NOTICE_MODELS
from .models import STABLE_MODELS


def are_functions_available(model: str) -> bool:
    """
    Whether the given model supports functions
    """
    # Deprecated models
    if model in DEPRECATED_MODELS:
        return False
    # Stable models will be updated to support functions on June 27, 2023
    if model in STABLE_MODELS:
        return datetime.date.today() > datetime.date(2023, 6, 27)
    # Models gpt-3.5-turbo-0613 and  gpt-3.5-turbo-16k-0613 will be deprecated
    # on June 13, 2024
    if model in DEPRECATION_NOTICE_MODELS:
        return datetime.date.today() < datetime.date(2024, 6, 13)
    if model == GPT_4_VISION_PREVIEW:
        return False
    return True

def localized_text(key, bot_language, translations):
    """
    Return translated text for a key in specified bot_language.
    Keys and translations can be found in the translations.json.
    """
    try:
        return translations[bot_language][key]
    except KeyError:
        logging.warning(f"No translation available for bot_language code '{bot_language}' and key '{key}'")
        # Fallback to English if the translation is not available
        if key in translations['en']:
            return translations['en'][key]
        else:
            logging.warning(f"No english definition found for key '{key}' in translations.json")
            # return key as text
            return key

def load_translations(filename: str) -> list:
    # Load translations
    parent_dir_path = join(dirname(__file__), pardir)
    translations_file_path = join(parent_dir_path, filename)
    with open(translations_file_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    return translations