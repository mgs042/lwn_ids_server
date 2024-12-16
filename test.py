from db import device_database
if __name__ == "__main__":
    with device_database() as db:
        
        print(db.check_device_addr("f5724095b187ecdc"))
