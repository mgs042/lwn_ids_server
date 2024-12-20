from flask import Flask
from celery import Celery, shared_task, Task
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from db import gateway_database, device_database
from location import rev_geocode

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

rssi_metric = Gauge("rssi", "Received Signal Strength Indicator", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
snr_metric = Gauge("snr", "Signal-to-Noise Ratio", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
frame_count = Gauge("frame_count", "Frame count per device", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
uplink_received = Counter("uplink_received_total", "Total uplinks received", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])

@shared_task
def update_prometheus(metrics_data, coordinates, device_addr):
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
        
        # Simulate database update
        # Here, you can implement your database logic (e.g., using SQLAlchemy)
        print(f"Simulating database update for: {metrics_data}")
        return "Metrics and database updated successfully"
    
    except Exception as e:
        return str(e)