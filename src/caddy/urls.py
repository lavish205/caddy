__author__ = 'lavish'
from handlers.handlers import *
from handlers.uber import *

url_patterns = [
    (r'/api/redirect/', UberAuthorizeRedirectionHandler),
    (r'/api/uber/me/', UberRideRequestHandler),
    (r'/api/uber/authorize/', UberAuthorizeHandler),
    (r'/api/uber/status/', UberRideStatusHandler),
]
