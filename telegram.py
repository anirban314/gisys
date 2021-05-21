# NOTE: The lines that have '#X#' at the end are modified in-file by
# gisys-setup.py during the setup process and need to be marked that
# way for the setup to work correctly. Please do not remove them.

import requests

def alert_user(sys_, client, epochs):
    load_1m = sys_['load_1m']
    load_5m = sys_['load_5m']
    load_15m = sys_['load_15m']
    cpu_temp = sys_['cpu_temp']
    ram_used = sys_['ram_used']
    dsk_used = sys_['dsk_used']

    message = f"::: SYSTEM ALERT\n::: Reporting for {client}\n"
    if cpu_temp >= 60: #X#
        message+= f"\nCPU Temperature at {cpu_temp}\u2103"
    if ram_used >= 80: #X#
        message+= f"\nMemory Usage at {ram_used}%"
    if dsk_used >= 80: #X#
        message+= f"\nRoot Disk Usage at {dsk_used}%"

    message+= f"\n\nLoad Average (1 min.) at {load_1m}%"
    message+= f"\nLoad Average (5 min.) at {load_5m}%"
    message+= f"\nLoad Average (15 min.) at {load_15m}%"
    message += f"\n\nEvent Epoch (sec.): {epochs}"
    send_message(message)

def send_message(message):
    token = '' #X#
    chat_id = '' #X#
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'parse_mode': 'markdown', 'text': message}
    requests.get(url, params=params)
