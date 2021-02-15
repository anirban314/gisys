import sys
import time
import psutil
import subprocess
from datetime import datetime

def sysinfo(measure):
	sys_load = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
	cpu_temp = float(psutil.sensors_temperatures()['cpu_thermal'][0][1])
	ram_used = float(psutil.virtual_memory().percent)
	dsk_root = float(psutil.disk_usage('/').percent)
	
	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"fields":{
			"sys_load_1m" : sys_load[0],
			"sys_load_5m" : sys_load[1],
			"sys_load_15m": sys_load[2],
			"cpu_temp": cpu_temp,
			"ram_used": ram_used,
			"dsk_used": dsk_root
		}
	}]
	print(DATASET)

def callSubProc(command):
	return subprocess.run(command, shell=True, capture_output=True).stdout.decode()


isTest = False if '--commit' in sys.argv else True
dbTest = 'playground'

dtmins = datetime.now().minute
dthour = datetime.now().hour
epochs = int(time.time())

sysinfo(measure='sys_info' if not isTest else dbTest)