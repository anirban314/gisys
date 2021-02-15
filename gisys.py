import sys
import time
import psutil
import subprocess
from datetime import datetime

def sysinfo(measure):
	sys_load = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
	cpu_temp = float(psutil.sensors_temperatures()['cpu_thermal'][0][1])
	ram_used = float(psutil.virtual_memory().percent)
	dsk_used = float(psutil.disk_usage('/').percent)
	
	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"tags":{
			"host": "localhost"
		},
		"fields":{
			"sys_load_1m" : sys_load[0],
			"sys_load_5m" : sys_load[1],
			"sys_load_15m": sys_load[2],
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
	text += "\nTimestamp: {}\nEpochs: {}".format(time.strftime("%H:%M:%S",time.localtime(epochs)), epochs)
	response = requests.get("https://api.telegram.org/bot"+token+"/sendMessage?chat_id="+chatID+"&parse_mode=Markdown&text="+text)

def callSubProc(command):
	return subprocess.run(command, shell=True, capture_output=True).stdout.decode()

if __name__ == '__main__':
	isTest = False if '--commit' in sys.argv else True
	dbTest = 'test'

	dtmins = datetime.now().minute
	dthour = datetime.now().hour
	epochs = int(time.time())

	sysinfo(measure='sys_info' if not isTest else dbTest)