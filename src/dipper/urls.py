__author__ = 'lavish'
from handlers.main import *

url_patterns = [
    (r'/api/request/', ProcessRequestHandler),
    (r"/api/serverStatus/", ServerStatusHandler),
#     (r"/api/kill/", StoreInfo)
]
