import importlib, json, os
import random, re, requests
import socket, subprocess, sys
from datetime import datetime


def main():
    scripts = {
        'gisys.py': False,
        'telegram.py': False,
        'gisys-data.json': False
    }
    modules = {
        'psutil': False,
        'influxdb': False
    }
    

    # The following part checks if the required files are present in
    # the current directory. If one or more of these files are missing,
    # the script will exit with an error.
    
    print("Checking required files...")
    scripts = check_scripts(scripts)
    if scripts == True:
        print("\n\u2713 Required files are present.")
    else:
        print("\n\u2717 One or more files are MISSING!")
        print("  Verify that all files are present in the current directory.")
        print("  Quitting!")
        sys.exit(1)


    # The following part checks if all the required Python modules are
    # installed. If one or more are missing, you'll be provided with
    # the option to install them.
    
    print("\nChecking Python Modules...")
    modules = check_modules(modules)
    if modules == True:
        print("\n\u2713 Required modules are installed.")
    else:
        choice = input("\nModules MISSING! Install them now (yes/no)? ").lower()
        if choice == 'y' or choice == 'yes':
            install_modules(modules)
        else:
            print("\u2717 Required modules are MISSING.\nQuitting!")
            sys.exit(1)
    

    # The following part reads the stored values from 'gisys-data.json'
    # and also allows the user to change the values. The values will be
    # stored back to the file after verification, later in this script.
    
    print("\nNow let's get everything configured...")
    print("Note: Press enter to keep current value.")
    print("Note: Fields marked with a \u2605 are required.")

    with open('gisys-data.json', 'r') as file:
        configs = json.load(file)
    
    configs = set_values(configs)


    # The following part will try to connect to the InfluxDB server,
    # and create a new databse with the given name if it doesn't exist
    # already. Skips database creation if one exists with the same name.

    host = configs['InfluxDB Server']['Host']
    port = configs['InfluxDB Server']['Port']
    dbase = configs['InfluxDB Server']['Database']
    reten = configs['InfluxDB Server']['Days to Keep']

    print("\nAttempting to connect to InfluxDB server...")
    if verify_influxdb(host, port):
        print(f"\u2713 SUCCESS! InfluxDB server is reachable on {host}:{port}")
    else:
        print(f"\u2717 FAILED to connect to InfluxDB server on {host}:{port}")
        sys.exit(1)
    
    print("\nAttempting to create InfluxDB database...")
    if create_influxdbase(host, port, dbase, reten):
        print(f"\u2713 Database '{dbase}' created with retention policy duration of {reten} days.")
    else:
        print(f"\u2713 Database '{dbase}' already exists! Skipping creation of new database.")


    # The following part will try to send a test message to your
    # Telegram app using the details entered by you in the previous
    # step. A failure here will need to be resolved before continuing.

    print("\nAttempting to send a test message on your Telegram app...")
    pin = verify_telegram(
        token = configs['Telegram Bot']['Token'],
        chat_id = configs['Telegram Bot']['Chat ID']
    )
    print("A test message was sent to you, on your Telegram app, using the details of\
        \nthe Telegram bot provided by you. The message also contains a 4-digit PIN.")
    user_pin = input("\nWhat is the 4-digit PIN sent to you? ")

    if user_pin == str(pin):
        print("\n\u2713 SUCCESS! Telegram bot configured properly")
    else:
        print("\n\u2717 INCORRECT PIN! Please check your configuration")
        sys.exit(1)


    # The following part opens the main script file 'gisys.py' and
    # modifies the values in-file according to the settings chosen by
    # the user in the previous step or stored in 'gisys-data.json'.

    with open('gisys.py', 'r+') as file:
        lines = file.read()
        lines = modify_gisys(configs, lines)
        file.truncate(0)
        file.seek(0)
        file.write(lines)
    

    # The following part opens the script file 'telegram.py' and
    # modifies the values in-file according to the settings chosen by
    # the user in the previous step or stored in 'gisys-data.json'.

    with open('telegram.py', 'r+') as file:
        lines = file.read()
        lines = modify_telegram(configs, lines)
        file.truncate(0)
        file.seek(0)
        file.write(lines)
    

    # The following part stores the given values back to the settings
    # file 'gisys-data.json'. This concludes this script!

    configs = json.dumps(configs, indent=4)
    with open('gisys-data.json', 'w') as file:
        file.write(configs)


def check_scripts(scripts):
    for script in scripts.keys():
        print(f"  {script} is ", end='')
        if os.path.isfile(script):
            print("present")
            scripts[script] = True
        else:
            print("MISSING")
    
    if all(scripts.values()):
        return True
    else:
        return False


def check_modules(modules):
    for module in modules.keys():
        print(f"  {module} is ", end='')
        try:
            importlib.import_module(module)
        except Exception:
            print("MISSING")
        else:
            print("installed")
            modules[module] = True

    if all(modules.values()):
        return True
    else:
        return modules


def install_modules(modules):
    command = ['sudo', 'pip3', 'install']
    for module, installed in modules.items():
        if not installed:
            command.append(module)
    if len(command) > 3:
        subprocess.run(command)


def set_values(configs):
    for section, settings in configs.items():
        for key, val in settings.items():
            is_empty = True if val=='' else False
            is_required = '\u2605' if is_empty else '\u2606'
            
            while True:
                print(f"\n{is_required} {section.upper()} \u27A1 {key.upper()}")
                print(f"  Current value   : {val}")
                user_input = input("  Enter new value : ")

                if is_empty and user_input == '':
                    print(f"\u2717 {key.upper()} can not be left empty!")
                elif not is_empty and user_input == '':
                    break
                else:
                    configs[section][key] = user_input
                    break
    return configs


def verify_influxdb(host, port):
    from influxdb import InfluxDBClient
    try:
        influx = InfluxDBClient(host=host, port=port)
        influx_ver = influx.ping()
    except:
        return False
    else:
        influx.close()
        return True


def create_influxdbase(host, port, dbase, reten):
    from influxdb import InfluxDBClient
    influx = InfluxDBClient(host=host, port=port)
    shard = '1h' if reten=='1' else '1d'

    if not {'name': dbase} in influx.get_list_database():
        influx.create_database(dbase)
        influx.create_retention_policy(
            name = f'RP_{dbase}', 
            duration = f'{reten}d',
            replication = '1',
            database = dbase,
            default = True,
            shard_duration = shard
        )
        influx.drop_retention_policy(
            name = 'autogen',
            database = dbase
        )
        influx.close()
        return True
    else:
        influx.close()
        return False


def verify_telegram(token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    pin = random.randint(1000,9999)
    params = {
        'chat_id': chat_id,
        'parse_mode': 'markdown',
        'text': f"Test message sent using *gisys-setup.py*\
            \n\u23AE Hostname - *{socket.gethostname()}*\
            \n\u23AE Date - {datetime.now().strftime('%b %d, %Y')}\
            \n\u23AE Time - {datetime.now().strftime('%X')}\n\
            \n*Verification PIN \u2014 {pin}*"
    }
    requests.get(url, params=params)
    return pin


def modify_gisys(configs, lines):
    host = configs['InfluxDB Server']['Host']
    port = configs['InfluxDB Server']['Port']
    database = configs['InfluxDB Server']['Database']
    cpu_temp = configs['Alert Threshold']['CPU Temperature (C)']
    ram_used = configs['Alert Threshold']['RAM Usage (%)']
    dsk_used = configs['Alert Threshold']['Disk Usage (%)']

    lines = re.sub(
        r"cpu_temp >= [\d]+: #X#",
        f"cpu_temp >= {cpu_temp}: #X#",
        lines, count=1
    )
    lines = re.sub(
        r"ram_used >= [\d]+: #X#",
        f"ram_used >= {ram_used}: #X#",
        lines, count=1
    )
    lines = re.sub(
        r"dsk_used >= [\d]+: #X#",
        f"dsk_used >= {dsk_used}: #X#",
        lines, count=1
    )
    lines = re.sub(
        r"\(host='.*', port=[\d]+, database='.*'\) #X#",
        f"(host='{host}', port={port}, database='{database}') #X#",
        lines, count=1
    )
    lines = re.sub(
        r"\['cpu_temp'\] >= [\d]+ #X#",
        f"['cpu_temp'] >= {cpu_temp} #X#",
        lines, count=1
    )
    lines = re.sub(
        r"\['ram_used'\] >= [\d]+ #X#",
        f"['ram_used'] >= {ram_used} #X#",
        lines, count=1
    )
    lines = re.sub(
        r"\['dsk_used'\] >= [\d]+ #X#",
        f"['dsk_used'] >= {dsk_used} #X#",
        lines, count=1
    )
    return lines


def modify_telegram(configs, lines):
    token = configs['Telegram Bot']['Token']
    chat_id = configs['Telegram Bot']['Chat ID']

    lines = re.sub(
        r"token = '.*' #X#",
        f"token = '{token}' #X#",
        lines, count=1
    )
    lines = re.sub(
        r"chat_id = '.*' #X#",
        f"chat_id = '{chat_id}' #X#",
        lines, count=1
    )
    return lines


if __name__ == "__main__":
    main()
