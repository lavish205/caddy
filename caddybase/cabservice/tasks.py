from celery import task
from caddybase.settings import db
import datetime
from .utils import book_cab

def schedule_ride():
    schedule_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
    cursor = db.rides.find()
    for user in cursor:
        data = {
            "token": user["authorization"],
            "start_lat": user["start_lat"],
            "start_long": user["start_long"],
            "end_lat": user["end_lat"]
        }
        book_cab()
