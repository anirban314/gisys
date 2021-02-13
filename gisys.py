import re
import sys
import time
import psutil
import subprocess
from datetime import datetime

def sysinfo(measure):
	SYS_load = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
	CPU_temp = float(psutil.sensors_temperatures()['cpu_thermal'][0][1])
	RAM_used = float(psutil.virtual_memory().percent)
	DSK_root = float(psutil.disk_usage('/').percent)
	
	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"fields":{
			"sys_load_1m" : SYS_load[0],
			"sys_load_5m" : SYS_load[1],
			"sys_load_15m": SYS_load[2],
			"cpu_temp": CPU_temp,
			"ram_used": RAM_used,
			"dsk_used": DSK_root
		}
	}]
	print(DATASET)

def netinfo(measure):
	RESPONSE = callSubProc("netstat -s")

	IP_now   = int(re.findall("(\d+) total packets received", RESPONSE, re.MULTILINE)[0])
	ICMP_now = int(re.findall("(\d+) ICMP messages received", RESPONSE, re.MULTILINE)[0])
	ICMP_now+= int(re.findall("(\d+) ICMP messages sent", RESPONSE, re.MULTILINE)[0])
	TCP_now  = int(re.findall("(\d+) segments received", RESPONSE, re.MULTILINE)[0])
	TCP_now += int(re.findall("(\d+) segments sent out", RESPONSE, re.MULTILINE)[0])
	UDP_now  = int(re.findall("(\d+) packets received", RESPONSE, re.MULTILINE)[0])
	UDP_now += int(re.findall("(\d+) packets sent", RESPONSE, re.MULTILINE)[0])

	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"tags":{
			"metric": "total"
		},
		"fields":{
			"IP"   : IP_now,
			"ICMP" : ICMP_now,
			"TCP"  : TCP_now,
			"UDP"  : UDP_now
		}
	}]
	print(DATASET)

def pingtest(measure):
	IPaddresses = {
		'lan_gate' : (1, '10.0.0.1', '2'),
		'web_dns'  : (2, '1.1.1.1', '1')
	}
	DATASET = [{'measurement': measure, 'time': epochs, 'fields': {}}]

	for tag, IPset in IPaddresses.items():
		i, ip, c = IPset
		RESPONSE = callSubProc("ping "+ip+" -c "+c+" | awk '/rtt/{print $4}'")
		if RESPONSE:
			ping = float(RESPONSE.split('/')[0])  #Select ping metric: [0]=min,[1]=avg,[2]=max,[3]=mdev
			DATASET[0]['fields'][tag] = ping
		elif i>0 : break
	print(DATASET)

def callSubProc(command):
	return subprocess.run(command, shell=True, capture_output=True).stdout.decode()


isTest = False if '--commit' in sys.argv else True
dbTest = 'playground'

dtmins = datetime.now().minute
dthour = datetime.now().hour
epochs = int(time.time())

sysinfo(measure='sys_info' if not isTest else dbTest)
netinfo(measure='net_info' if not isTest else dbTest)
pingtest(measure='ping_test' if not isTest else dbTest)