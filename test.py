from flask import Flask
from celery import Celery, shared_task, Task
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from db import gateway_database, device_database, alert_database
from location import rev_geocode
from influx import get_influxdb_client
gateway_id="e787a4c0abae2223"
device_id="f5724095b187ecdc"
device_name="TEST_DEV_TEST"
device_addr="0001"
with gateway_database() as db:
    gateway_location = db.fetch_gateway_location(gateway_id)
    gateway_name = db.fetch_gateway_name(gateway_id)
    with device_database() as db1:
        check = db1.check_device_registered(device_id)
        print(check)
        if check == 0:
            pass
        print(db1.check_device_addr(device_id))
        print(db1.check_device_gw(device_id))

