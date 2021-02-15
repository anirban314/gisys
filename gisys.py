import psutil
import requests
import subprocess
import sys
import time
from datetime import datetime

def sysinfo(measure):
	load_avg = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
	cpu_temp = float(psutil.sensors_temperatures()['cpu_thermal'][0][1])
	ram_used = float(psutil.virtual_memory().percent)
	dsk_used = float(psutil.disk_usage('/').percent)
	
	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"tags": {
			"host": "localhost"
		},
		"fields": {
			"load_avg_1m" : load_avg[0],
			"load_avg_5m" : load_avg[1],
			"load_avg_15m": load_avg[2],
			"cpu_temp": cpu_temp,
			"ram_used": ram_used,
			"dsk_used": dsk_used
		}
	}]
	print(DATASET)

	#Send message via Telegram bot
	if cpu_temp >= 50 or ram_used >= 50 or dsk_used >= 50:
		text = '''
			::: WARNING ::: System Status Critical\n
			CPU Temperature at {}\u2103
			Memory Usage at {}%
			Disk Usage at {}%
			'''.format(cpu_temp, ram_used, dsk_used)
		sendTelegram(text)

def sendTelegram(text):
	token = "token"
	chatID = "chatid"
	text += "\nTimestamp: {}\nEpochs: {}".format(time.strftime('%H:%M:%S',time.localtime(epochs)), epochs)
	url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(token, chatID, text)
	response = requests.get(url)

def callSubProc(command):
	return subprocess.run(command, shell=True, capture_output=True).stdout.decode()

if __name__ == "__main__":
	isTest = False if "--commit" in sys.argv else True
	dbTest = "test"

	dtmins = datetime.now().minute
	dthour = datetime.now().hour
	epochs = int(time.time())

	sysinfo(measure='sys_info' if not isTest else dbTest)