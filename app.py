from flask import Flask, request, Response, render_template
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from location import rev_geocode

app = Flask(__name__)

rssi_metric = Gauge("rssi", "Received Signal Strength Indicator", ["device_name", "device_id", "gateway_id", "location"])
snr_metric = Gauge("snr", "Signal-to-Noise Ratio", ["device_name", "device_id", "gateway_id", "location"])
frame_count = Gauge("frame_count", "Frame count per device", ["device_name", "device_id", "gateway_id", "location"])
uplink_received = Counter("uplink_received_total", "Total uplinks received", ["device_name", "device_id", "gateway_id", "location"])

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        g_name = request.form.get('name')
        g_id = request.form.get('eui')
        g_address = request.form.get('address')
        g_number = request.form.get('number')

        
    return render_template("index.html")


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/data', methods=['POST'])
def data():
    event_type = request.args.get('event')
    if event_type == 'up':
        #Recieve and process JSON data
        data = request.get_json()
        print(data)
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
            gateway_id = data['rxInfo'][0]['gatewayId']
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            gateway_id = "Unknown"
        try:
            coordinates = data['rxInfo'][0]['location']
            location = rev_geocode(coordinates['latitude'], coordinates['longitude'])
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            location = "Unknown"
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
        print(device_name, device_id, gateway_id, rssi, snr, f_cnt,location)
        # Update Prometheus metrics
        try:
            rssi_metric.labels(device_name=device_name, device_id=device_id, gateway_id=gateway_id, location=location).set(rssi)
            snr_metric.labels(device_name=device_name, device_id=device_id, gateway_id=gateway_id, location=location).set(snr)
            frame_count.labels(device_name=device_name, device_id=device_id, gateway_id=gateway_id, location=location).set(f_cnt)
            uplink_received.labels(device_name=device_name, device_id=device_id, gateway_id=gateway_id, location=location).inc()
        except Exception as e:
            print(f"Error updating metrics: {e}")
            return '', 500  # Internal Server Error

    return '', 204  # No Content

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
