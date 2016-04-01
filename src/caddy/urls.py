__author__ = 'lavish'
from handlers.handlers import *
from handlers.apis import *

url_patterns = [
    (r'/api/request/', XYZHandler),
]
