__author__ = 'lavish'
from handlers.handlers import *
from handlers.uber import *

url_patterns = [
    (r'/api/uber/redirect/', UberAuthorizeRedirectionHandler),
    (r'/api/uber/request/', UberRideRequestHandler),
    (r'/api/uber/authorize/', UberAuthorizeHandler),
    (r'/api/uber/status/', UberRideStatusHandler),
]
