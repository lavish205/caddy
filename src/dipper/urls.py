__author__ = 'lavish'
from handlers.main import *

url_patterns = [
    (r'/api/request/', ProcessRequestHandler),
#     (r"/api/serverStatus/", LoginHandler),
#     (r"/api/kill/", StoreInfo)
]
