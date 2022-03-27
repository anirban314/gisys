# NOTE: The lines that have '#X#' at the end are modified in-file by
# gisys-setup.py during the setup process and need to be marked that
# way for the setup to work correctly. Please do not remove them.

import requests

def send_message(message):
    token = '' #X#
    chat_id = '' #X#
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'parse_mode': 'markdown', 'text': message}
    requests.get(url, params=params)
