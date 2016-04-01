from pymongo import MongoClient

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.options import options

from settings import settings
from caddy import urls


class Caddy(Application):
    def __init__(self):
        Application.__init__(self, urls.url_patterns, **settings)
        self.conn = MongoClient()
        self.db = self.conn["caddy"]


def main():
    app = Caddy()
    http_server = HTTPServer(app)
    http_server.bind(options.port)
    if settings['debug']:
        http_server.start()
    else:
        http_server.start(0)
    global_ioloop = IOLoop.instance()
    global_ioloop.start()

if __name__ == "__main__":
    main()
