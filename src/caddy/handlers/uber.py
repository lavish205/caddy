from collections import defaultdict
from rauth import OAuth2Service
from tornado.options import options
from tornado.web import RequestHandler
from uber_rides.client import UberRidesClient
from uber_rides.session import Session
from .utils import *

session = Session(server_token=options.UBER_SERVICE_TOKEN)


def get_ride():
    client = UberRidesClient(session)
    response = client.get_products(12.937308, 77.627056)
    return response.json.get("products")


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

            url = options.UBER_SERVER + "/v1/requests"
            # # # url = "https://sandbox-api.uber.com/v1/products"
            token = self.request.headers.get_list("token")
            assert len(token) and len(token[0]), {'message': 'Valid Access-Token is required', 'status': 401}

            headers = {
                    "Authorization": "Bearer {access_token}".format(access_token=token[0]),
                    "Content-Type": "application/json"
                }
            print headers
            start_lat = self.get_argument("start_lat")
            start_long = self.get_argument("start_long")
            end_lat = self.get_argument("end_lat")
            end_long = self.get_argument("end_long")
            assert start_lat and start_long and end_lat and end_long, {
                "message": "either of `start_lat`, `start_long`, `end_lat` or `end_long key is missing",
                "status": 400
            }

            body_params = {
                "start_latitude": start_lat,
                "start_longitude": start_long,
                "end_latitude": end_lat,
                "end_longitude": end_long
            }

            uber_res = yield fetch_from_datastore(apiurl=url, headers=headers, body=body_params, is_json=True, method="POST")

            response = uber_res
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

            uber_res = yield fetch_from_datastore(apiurl=url, headers=headers)

            response = uber_res
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
