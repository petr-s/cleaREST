from unittest import TestCase
from clearest.http import *
from clearest.wsgi import *
from clearest.core import application


class WSGITestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(WSGITestCase, self).__init__(*args, **kwargs)
        self.headers = []
        self.status = None

    def _start_response(self, status, headers):
        code, msg = status.split(" ", 1)
        self.status = HttpStatus(code=int(code), msg=msg)
        self.headers = headers

    def request(self, app, method, query):
        assert method in HTTP_METHODS
        env = {REQUEST_METHOD: method,
               SERVER_PROTOCOL: HTTP_1_1,
               SERVER_NAME: "wsgi_unit_test",
               SERVER_PORT: 42,
               SCRIPT_NAME: ""}
        parts = query.split("?", 1)
        if len(parts) is 2:
            env[PATH_INFO], env[QUERY_STRING] = parts
        else:
            env[PATH_INFO] = query
        result = []
        for data in app(env, self._start_response):
            result.append(data)
        return result

    def get(self, query, app=application):
        return self.request(app, HTTP_GET, query)
