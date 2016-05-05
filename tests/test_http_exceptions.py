from clearest import *
from tests.wsgi import WSGITestCase


class Test(WSGITestCase):
    def setUp(self):
        unregister_all()

    def test_http_bad_request(self):
        @GET("/asd")
        def asd():
            raise HttpBadRequest()

        self.get("/asd")
        self.assertEqual(HTTP_BAD_REQUEST, self.status)

    def test_http_unauthorized(self):
        @GET("/asd")
        def asd():
            raise HttpUnauthorized

        self.get("/asd")
        self.assertEqual(HTTP_UNAUTHORIZED, self.status)

    def test_http_forbidden(self):
        @GET("/asd")
        def asd():
            raise HttpForbidden

        self.get("/asd")
        self.assertEqual(HTTP_FORBIDDEN, self.status)

    def test_http_not_found(self):
        @GET("/asd")
        def asd():
            raise HttpNotFound

        self.get("/asd")
        self.assertEqual(HTTP_NOT_FOUND, self.status)

    def test_http_gone(self):
        @GET("/asd")
        def asd():
            raise HttpGone

        self.get("/asd")
        self.assertEqual(HTTP_GONE, self.status)

    def test_http_unsupported_media_type(self):
        @GET("/asd")
        def asd():
            raise HttpUnsupportedMediaType

        self.get("/asd")
        self.assertEqual(HTTP_UNSUPPORTED_MEDIA_TYPE, self.status)
