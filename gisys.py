import re
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

def netinfo(measure):
	response = callSubProc("netstat -s")

	ip_now   = int(re.findall("(\d+) total packets received", response, re.MULTILINE)[0])
	icmp_now = int(re.findall("(\d+) ICMP messages received", response, re.MULTILINE)[0])
	icmp_now+= int(re.findall("(\d+) ICMP messages sent", response, re.MULTILINE)[0])
	tcp_now  = int(re.findall("(\d+) segments received", response, re.MULTILINE)[0])
	tcp_now += int(re.findall("(\d+) segments sent out", response, re.MULTILINE)[0])
	udp_now  = int(re.findall("(\d+) packets received", response, re.MULTILINE)[0])
	udp_now += int(re.findall("(\d+) packets sent", response, re.MULTILINE)[0])

	DATASET = [{
		"measurement": measure,
		"time": epochs,
		"tags":{
			"metric": "total"
		},
		"fields":{
			"IP"   : ip_now,
			"ICMP" : icmp_now,
			"TCP"  : tcp_now,
			"UDP"  : udp_now
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
		response = callSubProc("ping "+ip+" -c "+c+" | awk '/rtt/{print $4}'")
		if response:
			ping = float(response.split('/')[0])  #Select ping metric: [0]=min,[1]=avg,[2]=max,[3]=mdev
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