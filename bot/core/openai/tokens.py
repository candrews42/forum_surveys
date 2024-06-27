from .models import GPT_3_MODELS
from .models import GPT_3_16K_MODELS
from .models import GPT_35_TURBO_1106
from .models import GPT_4_MODELS
from .models import GPT_4_32K_MODELS
from .models import GPT_4_VISION_MODELS
from .models import GPT_4_128K_MODELS
from .models import GPT_4O_MODELS


def default_max_tokens(model: str) -> int:
    """
    Gets the default number of max tokens for the given model.
    :param model: The model name
    :return: The default number of max tokens
    """
    base = 1200
    if model in GPT_3_MODELS:
        return base
    elif model in GPT_4_MODELS:
        return base * 2
    elif model in GPT_3_16K_MODELS:
        if model == GPT_35_TURBO_1106:
            return 4096
        return base * 4
    elif model in GPT_4_32K_MODELS:
        return base * 8
    elif model in GPT_4_VISION_MODELS:
        return 4096
    elif model in GPT_4_128K_MODELS:
        return 4096
    elif model in GPT_4O_MODELS:
        return 4096
    

def max_model_tokens(model):
    base = 4096
    if model in GPT_3_MODELS:
        return base
    if model in GPT_3_16K_MODELS:
        return base * 4
    if model in GPT_4_MODELS:
        return base * 2
    if model in GPT_4_32K_MODELS:
        return base * 8
    if model in GPT_4_VISION_MODELS:
        return base * 31
    if model in GPT_4_128K_MODELS:
        return base * 31
    if model in GPT_4O_MODELS:
        return base * 31
    raise NotImplementedError(
        f"Max tokens for model {model} is not implemented yet."
    )