import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


headers_settings_lang = {
    1: {
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("lang1"),
    },
    2: {
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("lang2"),
    },
}
