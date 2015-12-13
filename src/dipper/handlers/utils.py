import json
import time
import logging

from StringIO import StringIO
from gzip import GzipFile
from urllib import urlencode
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.options import options

def writeObjToResponse(self, object, return_type='json', status=200, headers=None):
    if return_type == 'json':
        if object is not None:
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(object))
        self.set_status(status)
    elif return_type == 'json_gzip':
        zbuf = StringIO()
        zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        zfile.write(json.dumps(object))
        zfile.close()

        compressed_content = zbuf.getvalue()
        zbuf.close()

        self.set_header('Content-Type', 'application/json')
        self.set_header('Content-Encoding', 'gzip')
        self.set_header('Content-Length', str(len(compressed_content)))
        self.write(compressed_content)
        self.set_status(status)

    if headers is None:
        self.add_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    else:
        for name, value in headers.items():
            self.add_header(name, value)
