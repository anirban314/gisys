from influxdb import InfluxDBClient
import psutil, socket, time

# NOTE: The lines that are modified in-file by 'gisys-setup.py' during
# the setup process are, and need to be, marked with '#X#' at the end.



def sys_info(influx, client, measure):
    load_avg = [load/psutil.cpu_count()*100 for load in psutil.getloadavg()]
    cpu_temp = float(psutil.sensors_temperatures()['cpu_thermal'][0][1])
    ram_used = float(psutil.virtual_memory().percent)
    dsk_used = float(psutil.disk_usage('/').percent)

    dataset = [{
        'measurement': measure,
        'time': epochs,
        'tags': {
            'client': client
        },
        'fields': {
            'load_avg_1m' : load_avg[0],
            'load_avg_5m' : load_avg[1],
            'load_avg_15m': load_avg[2],
            'cpu_temp': cpu_temp,
            'ram_used': ram_used,
            'dsk_used': dsk_used
        }
    }]
    influx.write_points(dataset, time_precision='s')
    return dataset[0]['fields']



def net_info(influx, client, measure):
    io_now = psutil.net_io_counters()
    dataset = [{
        'measurement': measure,
        'time': epochs,
        'tags': {
            'record_type': 'total',
            'client': client
        },
        'fields': {
            'bytes_sent'  : io_now.bytes_sent,
            'bytes_recv'  : io_now.bytes_recv,
            'packets_sent': io_now.packets_sent,
            'packets_recv': io_now.packets_recv,
            'errin'       : io_now.errin,
            'errout'      : io_now.errout,
            'dropin'      : io_now.dropin,
            'dropout'     : io_now.dropout
        }
    }]
    query_string = f"SELECT last(*) FROM {measure} WHERE record_type='total' AND client='{client}'"
    io_last = list(influx.query(query_string).get_points())
    if io_last:
        io_last = io_last[0]
        if io_now.bytes_sent - io_last['last_bytes_sent'] > 0:
            dataset.append({
            'measurement': measure,
            'time': epochs,
            'tags': {
                'record_type': 'delta',
                'client': client
            },
            'fields': {
                'bytes_sent'  : io_now.bytes_sent - io_last['last_bytes_sent'],
                'bytes_recv'  : io_now.bytes_recv - io_last['last_bytes_recv'],
                'packets_sent': io_now.packets_sent - io_last['last_packets_sent'],
                'packets_recv': io_now.packets_recv - io_last['last_packets_recv'],
                'errin'       : io_now.errin - io_last['last_errin'],
                'errout'      : io_now.errout - io_last['last_errout'],
                'dropin'      : io_now.dropin - io_last['last_dropin'],
                'dropout'     : io_now.dropout - io_last['last_dropout']
            }
        })
    influx.write_points(dataset, time_precision='s')
    return False



def send_telegram(sys_, client, epochs):
    message = f"ALERT\nClient: {client}\nEpochS: {epochs}\n"

    cpu_temp = sys_['cpu_temp']
    ram_used = sys_['ram_used']
    dsk_used = sys_['dsk_used']
    if cpu_temp >= 60: #X#
        message+= f"\nCPU Temperature: {cpu_temp}\u2103"
    if ram_used >= 80: #X#
        message+= f"\nMemory Usage: {ram_used}%"
    if dsk_used >= 80: #X#
        message+= f"\nRoot Disk Usage: {dsk_used}%"

    message+= f"\n\nLoad Avg, 1 min: {sys_['load_1m']}%"
    message+= f"\nLoad Avg, 5 min: {sys_['load_5m']}%"
    message+= f"\nLoad Avg, 15 min: {sys_['load_15m']}%"

    import telegram
    telegram.send_message(message)



if __name__ == '__main__':
    influx = InfluxDBClient(host='', port=8086, database='') #X#
    client = socket.gethostname()
    epochs = int(time.time())

    sys_data = sys_info(influx, client, measure='sys_info')
    net_data = net_info(influx, client, measure='net_info')
    influx.close()

    if (sys_data['cpu_temp'] >= 60 #X#
        or sys_data['ram_used'] >= 80 #X#
        or sys_data['dsk_used'] >= 80 #X#
        ): #Appropiate sad face!
        send_telegram(sys_data, client, epochs)
