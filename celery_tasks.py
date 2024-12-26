from flask import Flask
from celery import Celery, shared_task, Task
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from metrics import rssi_metric, snr_metric, frame_count, uplink_received
from db import gateway_database, device_database, alert_database
from location import rev_geocode
from influx import get_influxdb_client
import requests
import os


prometheus_server = os.getenv('PROMETHEUS_SERVER')

client, bucket, org = get_influxdb_client()
write_api = client.write_api(write_options=SYNCHRONOUS)

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def configure_celery_beat(celery_app: Celery):
    celery_app.conf.beat_schedule = {
        'packet-rate-task': {
            'task': 'celery_tasks.packet_rate_task',  # Reference your task name
            'schedule': 60.0,  # Run every 60 seconds
        }
    }



@shared_task
def update_influx(metrics_data, coordinates, device_addr):
    device_name = metrics_data.get('device_name', 'Unknown')
    device_id = metrics_data.get('device_id', 'Unknown')
    gateway_id = metrics_data.get('gateway_id', 'Unknown')
    rssi = metrics_data.get('rssi', 0)
    snr = metrics_data.get('snr', 0)
    f_cnt = metrics_data.get('f_cnt', -1)
    with device_database() as db:
                check = db.check_device_registered(device_id)
                if check == 0:
                    pass
                elif not db.check_device_addr(device_id):
                    db.set_dev_addr(device_id, device_addr)
                    print("Device Address Recorded")
    with gateway_database() as db:
            gateway_location = db.fetch_gateway_location(gateway_id)
            gateway_name = db.fetch_gateway_name(gateway_id)
            if gateway_location is None:
                try:
                    gateway_location = rev_geocode(coordinates['latitude'], coordinates['longitude'], metrics_data.get(gateway_id))
                except KeyError as e:
                    print(f"KeyError encountered: {e}")
                    gateway_location = "Unknown"
            try:
                # Update Prometheus metrics
                rssi_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(rssi)
                snr_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(snr)
                frame_count.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(f_cnt)
                uplink_received.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).inc()
                
                p = influxdb_client.Point("device_metrics").tag("device_name", device_name).tag("device_id", device_id).tag("gateway_name", gateway_name).tag("gateway_id", gateway_id).tag("gateway_location", gateway_location).field("rssi", rssi).field("snr", snr).field("f_cnt", f_cnt)
                write_api.write(bucket=bucket, org=org, record=p)

                
                # Here, you can implement your database logic (e.g., using SQLAlchemy)
                print(f"Simulating database update for: {metrics_data}")
                return "Metrics and database updated successfully"
            
            except Exception as e:
                return str(e)
            
@shared_task
def packet_rate_task():
    device_list = []
    uplink_interval = []
    packet_rate = {}
    with device_database() as db:
        device_list += db.device_query()
        uplink_interval += db.device_up_int_query()
    for device in device_list:
        url = f'http://{prometheus_server}/api/v1/query?query=rate(uplink_received_total{{device_id="{device[2]}"}}[10m])'
        response = requests.get(url)
        result = response.json()['data']['result']
        if len(result) == 0:
            packet_rate[str(device[2])] = None
        else:
            packet_rate[str(device[2])] = result[0]['value'][1]
    return packet_rate