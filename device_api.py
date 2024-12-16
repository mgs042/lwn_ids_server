import grpc
from google.protobuf.json_format import MessageToJson
from chirpstack_api import api
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta
import json
import os

def convert_to_readable_format(timestamp_str, offset_hours=5, offset_minutes=30):
    # Parse the ISO 8601 timestamp (e.g., 2024-12-11T10:34:23.225809Z)
    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    
    # Apply the timezone offset (e.g., UTC +5:30 for IST)
    offset = timedelta(hours=offset_hours, minutes=offset_minutes)
    dt = dt + offset
    
    # Convert to a more readable format (e.g., 2024-12-11 16:15:23)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_dev_details(dev_eui):
     # Get environment variables
    api_token = os.getenv('CHIRPSTACK_APIKEY')
    chirpstack_server = os.getenv('CHIRPSTACK_SERVER')
    auth_token = [("authorization", "Bearer %s" % api_token)]
    """
    Fetches the details of a specific device by its ID.
    """
    try:
        with grpc.insecure_channel(chirpstack_server) as channel:
            client = api.DeviceServiceStub(channel)
            req = api.GetDeviceRequest()
            req.dev_eui=dev_eui
            resp = client.Get(req, metadata=auth_token)
        if resp:
            resp_json = json.loads(MessageToJson(resp))
            result = {
                    "deviceId": resp_json["device"].get("devEui","Unknown"),
                    "name": resp_json["device"].get("name","Unknown"),
                    "appId": resp_json["device"].get("applicationId","Unknown"),
                    "devProfileId": resp_json["device"].get("deviceProfileId","Unknown"),
                    "createdAt": convert_to_readable_format(resp_json.get("createdAt", "")) if resp_json.get("createdAt") else "Unknown",
                    "updatedAt": convert_to_readable_format(resp_json.get("updatedAt", "")) if resp_json.get("updatedAt") else "Unknown",
                    "lastSeenAt": convert_to_readable_format(resp_json.get("lastSeenAt", "")) if resp_json.get("lastSeenAt") else "Unknown",
                    "status": resp_json.get("deviceStatus", "Unknown")
            }
            return result
        # If the device_id is not found
        return f"Device ID {dev_eui} not found in the list."

    except grpc.RpcError as e:
        return f"gRPC error: {e.code()} - {e.details()}"
    except Exception as ex:
        return f"An unexpected error occurred: {str(ex)}"