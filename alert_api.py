from db import alert_database, device_database

def get_alert_status():
    alerts = []
    result = []
    with alert_database() as db:
        alerts += db.query_alert()
    with device_database() as db:
        for alert in alerts:
            result.append((alert[1], db.get_dev_gw(alert[2]), alert[3]))
    print(result)        
    return result
