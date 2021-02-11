import sys
import time
import psutil
from datetime import datetime

def sysinfo(measure='test'):
	SYS_load = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
	CPU_temp = psutil.sensors_temperatures()['cpu_thermal'][0][1]
	RAM_used = psutil.virtual_memory().percent
	DSK_root = psutil.disk_usage('/').percent
	
	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"fields":{
			"sys_load_1m" : SYS_load[0],
			"sys_load_5m" : SYS_load[1],
			"sys_load_15m": SYS_load[2],
			"cpu_temp": float(CPU_temp),
			"ram_used": float(RAM_used),
			"dsk_used": float(DSK_root)
		}
	}]
	print(DATASET)


isTest = False if '--commit' in sys.argv else True
dbTest = 'playground'

dtmins = datetime.now().minute
dthour = datetime.now().hour
epochs = int(time.time())

sysinfo(measure='sys_info' if not isTest else dbTest)