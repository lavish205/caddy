import requests
from src.caddy.handlers.utils import send_sms_plivo
from caddybase.settings import db

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

    cab_details["cab"] = uber_res["body"]
    db.rides.insert_one(cab_details)
    cab_details.pop("_id")
    message = "Vehicle: {vehicle}\nEstimated Time: {eta}\nDriver: {driver}".format(
        vehicle=uber_res["body"]["vehicle"],
        eta=uber_res["body"]["eta"],
        driver=uber_res["body"]["driver"]
    )
    send_sms_plivo(message, contact_no)
    return cab_details