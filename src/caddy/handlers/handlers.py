__author__ = 'lavish'

import datetime
import time
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.web import RequestHandler
from utils import *

class XYZHandler(RequestHandler):
    @coroutine
    def get(self):
        response = {}
        status = 200
        """
        https://login.uber.com/oauth/v2/authorize?client_id=UTQo43jef0A1GQaHTbNOBAD_hkrxcSkJ&redirect_uri=http://localhost:8888/api/request/&response_type=code&scope=all_trips
        """
        try:
            pass

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()
