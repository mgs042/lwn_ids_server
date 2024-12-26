from prometheus_client import Gauge, Counter, CollectorRegistry

# Create a custom registry
registry = CollectorRegistry()

rssi_metric = Gauge("rssi", "Received Signal Strength Indicator", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"], registry=registry)
snr_metric = Gauge("snr", "Signal-to-Noise Ratio", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"], registry=registry)
frame_count = Gauge("frame_count", "Frame count per device", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"], registry=registry)
uplink_received = Counter("uplink_received_total", "Total uplinks received", ["device_name", "device_id", "gateway_name", "gateway_id", "gateway_location"], registry=registry)