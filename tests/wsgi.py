from unittest import TestCase

from six import StringIO

from clearest.core import application
from clearest.http import *
from clearest.wsgi import *


class WSGITestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(WSGITestCase, self).__init__(*args, **kwargs)
        self.headers = {}
        self.status = None

    def _start_response(self, status, headers):
        code, msg = status.split(" ", 1)
        self.status = HttpStatus(code=int(code), msg=msg)
        self.headers = dict(headers)

    def request(self, app, method, query, input_, content_type=None, content_len=0, accept=None):
        assert method in HTTP_METHODS
        env = {REQUEST_METHOD: method,
               SERVER_PROTOCOL: HTTP_1_1,
               SERVER_NAME: "wsgi_unit_test",
               SERVER_PORT: 42,
               SCRIPT_NAME: "",
               WSGI_INPUT: input_ if input_ else StringIO()}
        parts = query.split("?", 1)
        if len(parts) is 2:
            env[PATH_INFO], env[QUERY_STRING] = parts
        else:
            env[PATH_INFO] = query
        if content_type:
            env[WSGI_CONTENT_TYPE] = content_type
        if content_len > 0:
            env[WSGI_CONTENT_LENGTH] = content_len
        if accept:
            env[HTTP_ACCEPT] = accept
        result = None
        for data in app(env, self._start_response):  # TODO: PY2 vs PY3 string/bytes
            result = data
            break
        return result

    def get(self, query, app=application, **kwargs):
        return self.request(app, HTTP_GET, query, None, **kwargs)

    def post(self, query, app=application, input_=None, content_type=None, content_len=0):
        return self.request(app, HTTP_POST, query, input_, content_type, content_len)

    def assertCalledWith(self, fn, *args, **kwargs):
        self.assertEqual((args, kwargs), fn.called_with)
