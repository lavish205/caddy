from celery import task
from caddybase.settings import db
import datetime
from .utils import book_cab

def schedule_ride():
    from_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
    to_time = datetime.datetime.now()
    cursor = db.rides.find({"schedule_data.arrival_time":{'$gt':from_time}})
    for user in cursor:
        # find all
        print user
        pnr = user["pnr"]
        pnr_status = db.pnr.find_one({"pnr": pnr})
        if pnr_status:
            if pnr_status["arrival_time"] > user["schedule_data"]["arrival_time"]:
                user["schedule_data"]["arrival_time"] = pnr_status["arrival_time"]
            else:
                data = {
                    "token": user["authorization"],
                    "start_lat": user["schedule_data"]["start_lat"],
                    "start_long": user["schedule_data"]["start_long"],
                    "end_lat": user["schedule_data"]["end_lat"],
                    "end_long": user["schedule_data"]["end_long"],
                    "contact_no": user["contact_no"]
                }
                booking_info = book_cab(**data)
                print booking_info
