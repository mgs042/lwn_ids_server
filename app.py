from flask import Flask, request, Response, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from location import rev_geocode
from db import gateway_database, device_database
from dotenv import load_dotenv
from gateway_api import get_gateway_details, get_gateway_metrics, get_gateways_status
from device_api import get_dev_details

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

rssi_metric = Gauge("rssi", "Received Signal Strength Indicator", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
snr_metric = Gauge("snr", "Signal-to-Noise Ratio", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
frame_count = Gauge("frame_count", "Frame count per device", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])
uplink_received = Counter("uplink_received_total", "Total uplinks received", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"])


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", gateway_status = get_gateways_status())

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
        d_addr = request.form.get('addr')
        with device_database() as db:
            result=db.device_write(d_name, d_id, d_addr)
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


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/data', methods=['POST'])
def data():
    event_type = request.args.get('event')
    if event_type == 'up':
        #Recieve and process JSON data
        data = request.get_json()
        try:
            device_name = data['deviceInfo']['deviceName']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_name = "Unknown"
        try:
            device_id = data['deviceInfo']['devEui']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_id = "Unknown"
        try:
            device_addr = data['devAddr']
            with device_database() as db:
                check = db.check_device_registered(device_id)
                if check == 0:
                    pass
                elif not db.check_device_addr(device_id):
                    db.set_dev_addr(device_id, device_addr)
                    print("Device Address Recorded")
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_addr = "Unknown"
        try:
            gateway_id = data['rxInfo'][0]['gatewayId']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            gateway_id = "Unknown"
        try:
            rssi = data['rxInfo'][0]['rssi']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            rssi = 0
        try:
            snr = data['rxInfo'][0]['snr']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            snr = 0
        try:
            f_cnt = data['fCnt']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            f_cnt = -1
        with gateway_database() as db:
            gateway_location = db.fetch_gateway_location(gateway_id)
            gateway_name = db.fetch_gateway_name(gateway_id)
            if gateway_location is None:
                try:
                    coordinates = data['rxInfo'][0]['location']
                    gateway_location = rev_geocode(coordinates['latitude'], coordinates['longitude'], gateway_id)
                except KeyError as e:
                    print(f"KeyError encountered: {e}")
                    gateway_location = "Unknown"
        print("Device Name: "+device_name)
        print("Device Id: "+device_id)
        print("Gateway Name: "+gateway_name)
        print("Gateway Id: "+gateway_id)
        print("Gateway Location: "+gateway_location)
        rssi_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(rssi)
        snr_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(snr)
        frame_count.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(f_cnt)
        uplink_received.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).inc()
        # Update Prometheus metrics
        try:
            rssi_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(rssi)
            snr_metric.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(snr)
            frame_count.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).set(f_cnt)
            uplink_received.labels(device_name=device_name, device_id=device_id, gateway_name=gateway_name, gateway_id=gateway_id, gateway_location=gateway_location).inc()
        except Exception as e:
            print(f"Error updating metrics: {e}")
            return '', 500  # Internal Server Error
    elif event_type == 'join':
        #Recieve and process JSON data
        data = request.get_json()
        try:
            device_name = data['deviceInfo']['deviceName']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_name = "Unknown"
        try:
            device_id = data['deviceInfo']['devEui']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_id = "Unknown"
        try:
            device_addr = data['deviceAddr']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            device_addr = "Unknown"
        with device_database() as db:
            if db.check_device_registered(device_id):
                print("Join Request Replay")
            else:
                db.device_write(device_name, device_id, device_addr)
        print("Device Name: "+device_name)
        print("Device Id: "+device_id)
        print("Gateway Name: "+gateway_name)
        print("Gateway Id: "+gateway_id)
        print("Gateway Location: "+gateway_location)

    return '', 204  # No Content

if __name__ == '__main__':

    # Load environment variables
    load_dotenv()

    app.run(host="0.0.0.0", port=5000, debug=True)
