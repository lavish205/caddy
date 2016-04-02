__author__ = 'KT'

import datetime
import time
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.web import RequestHandler
from utils import *
import json


class PNRHandler(RequestHandler):
    @coroutine
    def get(self):
        response = {}
        status = 200

        try:
            pnr = self.get_argument('pnr')
            assert pnr, {
            "message" : "PNR not provided",
            "status" : 400
            }

            db = self.application.db
            item = db.pnr.find_one({'pnr': pnr})
            assert item, {
            "message" : "Invalid PNR",
            "status" : 400
            }

            cities = [city.lower() for city in json.load(open('uber_cities.json'))]
            if item.get('to').lower() not in cities:
                assert False, {
                "message": "Uber not available at this city",
                "status": 400
                }

            item.pop('_id')
            airport = db.airport.find_one()
            item['start_lat'] = airport.get('latitude')
            item['start_long'] = airport.get('longitude')
            response = item

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()


class OTPHandler(RequestHandler):
    @coroutine
    def post(self):
        db = self.application.db
        response = {}
        status = 200
        try:
            contact_no = self.get_argument("contact_no")
            exp_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
            data = {
                'contact_no': contact_no,
                'otp': get_otp(contact_no, db),
                'exp_time': exp_time,
                'is_active': True
            }
            otp_data = db.otp.find_one({"contact_no": contact_no})
            if otp_data:
                if otp_data["exp_time"] > datetime.datetime.now():
                    otp_data.update({"exp_time": datetime.datetime.now()})

            db.otp.insert(data)
            message = "Your OTP for caddy is {otp}. Please note " \
                      "this OTP will expire in 15 mins.".format(otp=data['otp'])
            send_sms_plivo(message, contact_no)
            data.pop("_id")
            data["exp_time"] = str(data["exp_time"])
            status = 201

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()

    @coroutine
    def put(self):
        db = self.application.db
        response = {}
        status = 200
        try:
            contact_no = self.get_argument("contact_no")
            otp = self.get_argument("otp")
            assert contact_no and otp, {
                "message": "`contact_no` and `otp` key required",
                "status": 400
            }
            print contact_no, otp
            otp_data = db.otp.find_one({"contact_no": contact_no, "otp": int(otp)})
            if otp_data:
                otp_data.update({"exp_time": datetime.datetime.now()})
                response = {"message": "verified"}
            else:
                response = {"message": "wrong combination"}
                status = 400

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()