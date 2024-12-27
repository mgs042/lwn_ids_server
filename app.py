import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from flask import Flask, request, Response, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from db import gateway_database, device_database, alert_database
from application_api import get_tenant_count, get_app_count
from gateway_api import get_gateway_details, get_gateway_metrics, get_gateways_status
from device_api import get_dev_details, get_dev_status
from alert_api import get_alert_status
from celery_tasks import celery_init_app, update_influx, configure_celery_beat

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config.from_mapping(
    CELERY=dict(
        broker_url=f"amqp://guest:guest@{os.getenv('MESSAGE_BROKER')}//",
        result_backend=None,
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)

configure_celery_beat(celery_app)

@app.route('/dashboard', methods=['GET'])
def index():
    return render_template("dashboard.html", gateway_status = get_gateways_status(), device_status = get_dev_status(), alert_status = get_alert_status(), tenant_count=get_tenant_count(), app_count=get_app_count())

@app.route('/gateway_registration', methods=['GET', 'POST'])
def gateway_register():
    if request.method == 'POST':
        g_name = request.form.get('name')
        g_id = request.form.get('eui')
        g_address = request.form.get('address')
        g_number = request.form.get('number')
        with gateway_database() as db:
            result=db.gateway_write(g_name, g_id, g_address, g_number)
        return redirect(url_for('gateways'))

        
    return render_template("gateway_reg.html")

@app.route('/device_registration', methods=['GET', 'POST'])
def dev_register():
    if request.method == 'POST':
        d_name = request.form.get('name')
        d_id = request.form.get('eui')
        d_gw = request.form.get('dev_gw') or "Unknown"
        d_addr = request.form.get('addr') or "Unknown"
        d_up_int = request.form.get('dev_up') or 60
        with device_database() as db:
            result=db.device_write(d_name, d_id, d_gw, d_addr, d_up_int)
        
        return redirect(url_for('devices'))
        
    return render_template("device_reg.html")

@app.route('/gateways', methods=['GET'])
def gateways():
    return render_template("gateways_list.html")

@app.route('/devices', methods=['GET'])
def devices():
    return render_template("devices_list.html")

@app.route('/gateway', methods=['GET'])
def gateway():
    # Get the 'id' parameter from the query string
    gateway_id = request.args.get('id')
    if gateway_id:
        with gateway_database() as db:
            check = db.check_gateway_registered(gateway_id)
        if check==0:
            return "Unknown Gateway"
        else:
            gateway_details = get_gateway_details(gateway_id)
            return render_template("gateway_details.html", gateway=gateway_details)
    
    else:
        # If no 'id' is passed, return a 400 error or some default message
        return 'No gateway ID provided', 400
    
@app.route('/device', methods=['GET'])
def device():
    # Get the 'id' parameter from the query string
    device_eui = request.args.get('id')
    if device_eui:
        with device_database() as db:
            check = db.check_device_registered(device_eui)
        if check==0:
            return "Unknown Device"
        else:
            device_details = get_dev_details(device_eui)
            return render_template("device_details.html", device=device_details)
    
    else:
        # If no 'id' is passed, return a 400 error or some default message
        return 'No device ID provided', 400
    
@app.route('/gateway_metrics', methods=['GET'])
def gateway_metrics():
    # Get the 'id' parameter from the query string
    gateway_id = request.args.get('id')
    return get_gateway_metrics(gateway_id)

@app.route('/gateway_data', methods=["GET"])
def gateway_data():
    with gateway_database() as db:
        rows=db.gateway_query()
    return jsonify(rows)

@app.route('/device_data', methods=["GET"])
def device_data():
    with device_database() as db:
        rows=db.device_query()
    return jsonify(rows)       


@app.route('/data', methods=['POST'])
def data():
    event_type = request.args.get('event')
    if event_type == 'up':
        #Recieve and process JSON data
        data = request.get_json()
        device_name = data.get('deviceInfo', {}).get('deviceName', 'Unknown')
        device_id = data.get('deviceInfo', {}).get('devEui', 'Unknown')
        device_addr = data.get('devAddr', 'Unknown')
        gateway_id = data.get('rxInfo', [{}])[0].get('gatewayId', 'Unknown')
        rssi = data.get('rxInfo', [{}])[0].get('rssi', 0)
        snr = data.get('rxInfo', [{}])[0].get('snr', 0)
        f_cnt = data.get('fCnt', -1)
        coordinates = data.get('rxInfo', [{}])[0].get('location', 'Unknown')
        # Metrics data
        metrics_data = {
            'device_name': device_name,
            'device_id': device_id,
            'gateway_id': gateway_id,
            'rssi': rssi,
            'snr': snr,
            'f_cnt': f_cnt
        }
        
        # Update device metrics
        try:   
            update_influx.apply_async(args=[metrics_data, coordinates, device_addr])
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
            return '', 500  # Internal Server Error
    elif event_type == 'join':
        #Recieve and process JSON data
        data = request.get_json()
        device_name = data.get('deviceInfo', {}).get('deviceName', 'Unknown')
        device_id = data.get('deviceInfo', {}).get('devEui', 'Unknown')
        device_addr = data.get('devAddr', 'Unknown')
        with device_database() as db:
            if db.check_device_registered(device_id):
                print("Join Request Replay")
                with alert_database() as db2:
                    db2.alert_write(device_name, device_id, "Join Request Replay")
            else:
                db.device_write(device_name, device_id, "Unknown", device_addr, 60)

    return '', 204  # No Content

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
