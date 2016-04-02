from collections import defaultdict
import datetime
from rauth import OAuth2Service
from tornado.options import options
from tornado.web import RequestHandler
from uber_rides.client import UberRidesClient
from uber_rides.session import Session
from .utils import *

session = Session(server_token=options.UBER_SERVICE_TOKEN)


class UberAuthorizeRedirectionHandler(RequestHandler):
    @coroutine
    def get(self):
        response = defaultdict(dict)
        status = 200
        """
        https://login.uber.com/oauth/v2/authorize?client_id=UTQo43jef0A1GQaHTbNOBAD_hkrxcSkJ&redirect_uri=http://localhost:8888/api/request/&response_type=code&scope=all_trips
        """
        try:
            if self.get_argument("error", None):
                response["errors"] = self.get_argument("error")
            code = self.get_argument("code")+"#_"

            params = {
                "client_secret": options.UBER_CLIENT_SECRET,
                "client_id": options.UBER_CLIENT_ID,
                "grant_type": "authorization_code",
                "redirect_uri": options.UBER_REDIRECT_URI,
                "code": code
            }

            uber_res = yield fetch_from_datastore(apiurl="https://login.uber.com/oauth/v2/token", body=params, is_json=False, method="POST")
            assert 'error' not in uber_res, {
                'message': uber_res['error'],
                'status': uber_res['status_code']
            }
            resp = uber_res.get("body")

            if resp:
                headers = {
                    "Authorization": "Bearer {access_token}".format(access_token=resp["access_token"])
                }
                params = {
                    "latitude": "12.9372572",
                    "longitude": "77.619736"
                }
                url = "https://api.uber.com/v1/products"
                # user_info_url = options.UBER_SERVER + "/v1/me"
                # user_res = fetch_from_datastore(apiurl=user_info_url, headers=headers)
                product_resp = fetch_from_datastore(apiurl=url, url_params=params, headers=headers)
                products = yield product_resp
                assert 'error' not in products, {
                    'message': products['error'],
                    'status': products['status_code']
                }
                # user_res = yield user_res
                # assert 'error' not in user_res, {
                #     'message': user_res['error'],
                #     'status': user_res['status_code']
                # }
                response["products"] = products["body"]["products"]
                # response["user"] = user_res["body"]
                response["authorization"] = resp["access_token"]
                self.redirect("http://localhost:1212/?success=True", status=302)
        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()


class UberRideRequestHandler(RequestHandler):
    @coroutine
    def post(self):
        response = {}
        status = 200
        try:
            # token = self.request.headers.get_list("token")
            # assert len(token) and len(token[0]), {'message': 'Valid Access-Token is required', 'status': 401}

            db = self.application.db
            name = self.get_argument("name")
            contact_no = self.get_argument("contact_no")
            pnr = self.get_argument("pnr")
            service = self.get_argument("service", "uber")
            cab_type = self.get_argument("cab_type", 1)  # 1, 2, 3 for mini, sedan, suv respectively
            arrival_time = self.get_argument("arrival_time")
            start_lat = self.get_argument("start_lat")
            start_long = self.get_argument("start_long")
            end_lat = self.get_argument("end_lat")
            end_long = self.get_argument("end_long")


            assert name and contact_no and pnr and arrival_time, {
                "message": "either `name` or `contact_no` or `pnr` or `arrival_time`  key is missing",
                "status": 400
            }
            arrival_time = datetime.datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%S")
            user_details = {
                "name": name,
                "contact_no": contact_no,
                "is_cancelled": 0,
                "pnr": pnr,
                "authorization": ""
            }

            scheduling_data = {
                "start_latitude": start_lat,
                "start_longitude": start_long,
                "end_latitude": end_lat,
                "end_longitude": end_long,
                "arrival_time": arrival_time,
                "service": service,
                "cab_type": cab_type,
            }

            # url = options.UBER_SERVER + "/v1/requests"
            # # # url = "https://sandbox-api.uber.com/v1/products"

            # headers = {
            #         "Authorization": "Bearer {access_token}".format(access_token=token[0]),
            #         "Content-Type": "application/json"
            #     }

            if not db.rides.find({'pnr': pnr, 'is_cancelled': 0}).count():

                # uber_res = yield fetch_from_datastore(apiurl=url, headers=headers, body=body_params, is_json=True, method="POST")
                #
                # user_details["cab"] = uber_res["body"]
                user_details["schedule_data"] = scheduling_data
                db.rides.insert_one(user_details)
                user_details.pop("_id")
                user_details["schedule_data"]["arrival_time"] = str(user_details["schedule_data"]["arrival_time"])
                response = user_details
            else:
                assert False, {
                    "message": "Ride already scheduled",
                    "status": 400
                }
        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()


class UberRideStatusHandler(RequestHandler):
    @coroutine
    def get(self):
        response = {}
        status = 200
        try:
            db = self.application.db
            pnr = self.get_argument("pnr")
            assert pnr, {
                "message": "`pnr` key is required",
                "status": 400
            }
            data = db.rides.find_one({"pnr": pnr, "is_cancelled": 0})
            if not data:
                assert False, {
                    "message": "invalid pnr",
                    "status": 400
                }
            print data
            request_id = data["cab"]["request_id"]
            url = options.UBER_SERVER + "/v1/requests/{request_id}".format(request_id=request_id)
            # # # url = "https://sandbox-api.uber.com/v1/products"
            token = self.request.headers.get_list("token")
            assert len(token) and len(token[0]), {'message': 'Valid Access-Token is required', 'status': 401}

            headers = {
                    "Authorization": "Bearer {access_token}".format(access_token=token[0]),
                }
            print headers

            uber_res = yield fetch_from_datastore(apiurl=url, headers=headers)
            assert 'error' not in uber_res, {
                    'message': uber_res['error'],
                    'status': uber_res['status_code']
                }
            uber_res = uber_res["body"]
            data["cab"]["status"] = uber_res["status"]
            data.update(**data)
            data.pop("_id")
            data.update({})
            response = data
        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()

    @coroutine
    def delete(self, *args, **kwargs):
        response = {}
        status = 200
        try:
            request_id = self.get_argument("request_id")
            assert request_id, {
                "message": "`request_id` key is missing",
                "status": 400
            }
            url = options.UBER_SERVER + "/v1/requests/{request_id}".format(request_id=request_id)
            # # # url = "https://sandbox-api.uber.com/v1/products"
            token = self.request.headers.get_list("token")
            assert len(token) and len(token[0]), {'message': 'Valid Access-Token is required', 'status': 401}

            headers = {
                    "Authorization": "Bearer {access_token}".format(access_token=token[0]),
                }
            print headers

            uber_res = yield fetch_from_datastore(apiurl=url, headers=headers, method="DELETE")

            response = uber_res
        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()


class UberAuthorizeHandler(RequestHandler):
    @coroutine
    def get(self):
        response = {}
        status = 200
        try:
            uber_api = OAuth2Service(
                client_id=options.UBER_CLIENT_ID,
                client_secret=options.UBER_CLIENT_SECRET,
                name='caddy',
                authorize_url='https://login.uber.com/oauth/authorize',
                access_token_url='https://login.uber.com/oauth/token',
                base_url='https://sandbox-api.uber.com/v1/',
                )

            parameters = {
                'response_type': 'code',
                'redirect_uri': options.UBER_REDIRECT_URI,
                'scope': 'request',
                }

            # Redirect user here to authorize your application
            login_url = uber_api.get_authorize_url(**parameters)
            response["url"] = login_url

        except AssertionError, e:
            e = e.message
            status = e['status'] if 'status' in e else 400
            message = e['message'] if 'message' in e else 'An error occurred'
            response = e['response'] if 'response' in e else {'error': message}
        finally:
            writeObjToResponse(self, object=response, status=status)
        self.finish()
