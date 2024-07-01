import io

import tiktoken
from PIL import Image

from .models import GPT_3_MODELS
from .models import GPT_3_16K_MODELS
from .models import GPT_35_TURBO_1106
from .models import GPT_4_MODELS
from .models import GPT_4_32K_MODELS
from .models import GPT_4_VISION_MODELS
from .models import GPT_4_128K_MODELS
from .models import GPT_4O_MODELS
from utils import decode_image


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


# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def count_tokens(model, vision_model, vision_detail, messages) -> int:
    """
    Counts the number of tokens required to send the given messages.
    :param messages: the messages to send
    :return: the number of tokens required
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("gpt-3.5-turbo")

    if model in GPT_3_MODELS + GPT_3_16K_MODELS:
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model in GPT_4_MODELS + GPT_4_32K_MODELS + GPT_4_VISION_MODELS + GPT_4_128K_MODELS + GPT_4O_MODELS:
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"num_tokens_from_messages() is not implemented for model {model}.")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if key == 'content':
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                else:
                    for message1 in value:
                        if message1['type'] == 'image_url':
                            image = decode_image(message1['image_url']['url'])
                            num_tokens += __count_tokens_vision(vision_model, vision_detail, image)
                        else:
                            num_tokens += len(encoding.encode(message1['text']))
            else:
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


# no longer needed

def __count_tokens_vision(model, detail, image_bytes: bytes) -> int:
    """
    Counts the number of tokens for interpreting an image.
    :param image_bytes: image to interpret
    :return: the number of tokens required
    """
    image_file = io.BytesIO(image_bytes)
    image = Image.open(image_file)
    if model not in GPT_4_VISION_MODELS:
        raise NotImplementedError(f"count_tokens_vision() is not implemented for model {model}.")
    
    w, h = image.size
    if w > h: w, h = h, w
    # this computation follows https://platform.openai.com/docs/guides/vision
    # and https://openai.com/pricing#gpt-4-turbo
    base_tokens = 85
    if detail == 'low':
        return base_tokens
    elif detail == 'high' or detail == 'auto': # assuming worst cost for auto
        f = max(w / 768, h / 2048)
        if f > 1:
            w, h = int(w / f), int(h / f)
        tw, th = (w + 511) // 512, (h + 511) // 512
        tiles = tw * th
        num_tokens = base_tokens + tiles * 170
        return num_tokens
    else:
        raise NotImplementedError(f"Unknown parameter detail={detail} for model {model}.")