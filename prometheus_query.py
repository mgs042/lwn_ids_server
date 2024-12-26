import os
import requests
from db import device_database
from math import ceil
prometheus_server = os.getenv('PROMETHEUS_SERVER')

def generate_alert(packet_rate, uplink_interval):
    
    for interval in uplink_interval:
        if packet_rate[interval[0]] > (1/interval[1]):
            print('Packet Flooding -- ' + f'{ceil(packet_rate[interval[0]]*60)} Packets per minute')
        elif packet_rate[interval[0]] < (1/interval[1]):
            print('Packet Loss -- ' + f'{ceil(packet_rate[interval[0]]*60)} Packets per minute')



def packet_rate_task():
    device_list = []
    uplink_interval = []
    packet_rate = {}
    with device_database() as db:
        device_list += db.device_query()
        uplink_interval += db.device_up_int_query()
    if not device_list or not uplink_interval:
        print("No devices or uplink intervals found.")
        return
    for device in device_list:
        url = f'http://{prometheus_server}/api/v1/query?query=rate(uplink_received_total{{device_id="{device[2]}"}}[10m])'
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()['data']['result']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for device {device[2]}: {e}")
            packet_rate[str(device[2])] = 0
            continue
        except KeyError:
            print(f"Unexpected response format for device {device[2]}")
            packet_rate[str(device[2])] = 0
            continue
        if len(result) == 0:
            packet_rate[str(device[2])] = 0
        else:
            packet_rate[str(device[2])] = float(result[0]['value'][1])
    generate_alert(packet_rate, uplink_interval)
    print(packet_rate)

packet_rate_task()