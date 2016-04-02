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
            pnr = self.request.get_argument('pnr')
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

            cities = json.load(open('cities.json'))
            if item.get('to') not in cities:
                assert False, {
                "message": "Uber not available at this city",
                "status": 400
                }

            item.pop('_id')
            response = item

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()