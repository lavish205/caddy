import requests
from caddybase.settings import db
import os


def send_sms_plivo(msg, phn):
    auth_id = os.getenv("PLIVO_AUTH_ID")
    auth_token = os.getenv("PLIVO_AUTH_TOKEN")
    msgdict = {'src': os.getenv("PLIVO_SRC")}
    msgdict['dst'] = str(phn)
    msgdict['text'] = msg


def book_cab(token, start_lat, start_long, end_lat, end_long, contact_no):
    cab_details = dict()
    headers = {"Authorization": "Bearer {access_token}".format(access_token=token[0]),
               "Content-Type": "application/json"}

    body_params = {
                "start_latitude": start_lat,
                "start_longitude": start_long,
                "end_latitude": end_lat,
                "end_longitude": end_long
            }
    # TODO:
    url = "https://sandbox-api.uber.com/v1/requests"
    uber_res = requests.post(url, json=body_params, headers=headers)
    print uber_res.content
    import json
    uber_res = json.loads(uber_res.content)
    cab_details["cab"] = uber_res
    db.rides.insert_one(cab_details)
    cab_details.pop("_id")
    print type(uber_res)
    print uber_res
    from collections import defaultdict
    print "sending message"
    message = "Vehicle: {vehicle}\nEstimated Time: {eta}\nDriver: {driver}".format(
        vehicle=uber_res["vehicle"],
        eta=uber_res["eta"],
        driver=uber_res["driver"]
    )
    print "message sent"
    send_sms_plivo(message, contact_no)
    return cab_details
