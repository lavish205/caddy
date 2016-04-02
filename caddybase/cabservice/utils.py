import requests
from caddybase.settings import db

def book_cab(token, start_lat, start_long, end_lat, end_long):
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
    return cab_details