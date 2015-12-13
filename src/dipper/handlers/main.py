__author__ = 'lavish'

import datetime
import time
from utils import *
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.gen import coroutine, engine, Task
from tornado.web import asynchronous


# shared variable to keep track of resources
process = dict()

class ProcessRequestHandler(RequestHandler):
    @asynchronous
    @engine
    def get(self):
        response = {}
        status = 200

        try:
            conn_id = self.get_query_argument('connId', None)
            assert conn_id, {'message' : 'Vaild connId is required'}
    
            timeout = self.get_query_argument('timeout', None)
            assert timeout, {'message' : 'Vaild timeout is required'}

            # setting value of connection id when it will be completed
            if not process.get(int(conn_id), None):
                process[int(conn_id)] =  datetime.datetime.now() + datetime.timedelta(0, int(timeout)) #keeping track of processes
                yield Task(IOLoop.instance().add_timeout, time.time() + int(timeout)) #making process busy for given timeout
                response = {'status': 'ok'}

                process.pop(int(conn_id)) # removing process from record of server status
            else:
                response = {'message': 'process already exists'}
                status = 400

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object = response, status = status)

        self.finish()


class ServerStatusHandler(RequestHandler):
    @asynchronous
    @engine
    def get(self):
        response = {}
        status = 200

        try:
            for k in process.keys():
                process[k] = str(process[k] - datetime.datetime.now())
            response = process
        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object = response, status = status)

        self.finish()