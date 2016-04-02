from celery import task
from caddybase.settings import db
import datetime
from .utils import book_cab

@task
def schedule_ride():
    from_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
    to_time = datetime.datetime.now()
    cursor = db.rides.find({"schedule_data.arrival_time":{'$gt':from_time}})
    for user in cursor:
        # find all
        print user
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        pnr = user["pnr"]
        pnr_status = db.pnr.find_one({"pnr": pnr})
        if pnr_status:
            flight = pnr_status["flight"]
            a_time = db.status.find_one({"flight":flight})['arrival']
            if a_time > user["schedule_data"]["arrival_time"]:
                user["schedule_data"]["arrival_time"] = pnr_status["arrival_time"]
            else:
                data = {
                    "token": user["authorization"],
                    "start_lat": user["schedule_data"]["start_latitude"],
                    "start_long": user["schedule_data"]["start_longitude"],
                    "end_lat": user["schedule_data"]["end_latitude"],
                    "end_long": user["schedule_data"]["end_longitude"],
                    "contact_no": user["contact_no"]
                }
                print "booking cab"
                booking_info = book_cab(**data)
                print "booked"
                import logging
                logging.error(booking_info)
                print booking_info
