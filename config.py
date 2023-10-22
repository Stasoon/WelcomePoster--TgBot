import json
import os
from typing import Final
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    TOKEN: Final = os.getenv('BOT_TOKEN', 'define me')
    ADMIN_IDS: Final = tuple(int(i) for i in str(os.getenv('BOT_ADMIN_IDS')).split(','))

    class Paths:
        CSV_FOLDER = 'csv_exports'
        WELCOME_POST_CONTENT_JSON = 'welcome_data.json'

    DEBUG: Final = bool(os.getenv('DEBUG'))


if not os.path.exists(Config.Paths.WELCOME_POST_CONTENT_JSON):
    with open(Config.Paths.WELCOME_POST_CONTENT_JSON, 'w') as file:
        initial_data = {'text': "Спасибо, что подписались!", 'images': []}
        json.dump(initial_data, file, indent=4)
