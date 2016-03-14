from six import StringIO

from clearest import POST, HTTP_NOT_FOUND, GET, unregister_all, HTTP_OK, HTTP_UNSUPPORTED_MEDIA_TYPE, \
    MIME_WWW_FORM_URLENCODED, MIME_FORM_DATA, HTTP_CREATED, HTTP_BAD_REQUEST, HttpNotFound
from tests.util import called_with
from tests.wsgi import WSGITestCase


class Test(WSGITestCase):
    def setUp(self):
        unregister_all()

    def test_application_not_found_1(self):
        self.get("/asd")
        self.assertEqual(HTTP_NOT_FOUND, self.status)

    def test_application_not_found_2(self):
        @POST("/asd")
        def asd():
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_NOT_FOUND, self.status)

    def test_application_not_found_3(self):
        @GET("/asd")
        def asd():
            return {}

        self.get("/asd/42")
        self.assertEqual(HTTP_NOT_FOUND, self.status)

    def test_application_unsupported_media_type(self):
        @POST("/asd")
        def asd():
            return {}

        self.post("/asd/42", content_type="application/unsupported")
        self.assertEqual(HTTP_UNSUPPORTED_MEDIA_TYPE, self.status)

    def test_application_bad_request_1(self):
        @GET("/asd")
        @called_with
        def asd(a=int):
            return {}

        self.get("/asd?a=hi")
        self.assertEqual(HTTP_BAD_REQUEST, self.status)

    def test_application_bad_request_2(self):
        @GET("/asd")
        @called_with
        def asd(a):
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_BAD_REQUEST, self.status)

    def test_application_status_default(self):
        @GET("/asd")
        @called_with
        def asd():
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((), {}), asd.called_with)

    def test_application_status(self):
        @POST("/asd", HTTP_CREATED)
        @called_with
        def asd():
            return {}

        self.post("/asd")
        self.assertEqual(HTTP_CREATED, self.status)
        self.assertEqual(((), {}), asd.called_with)

    def test_application_raise_custom(self):
        @GET("/asd")
        @called_with
        def asd():
            raise HttpNotFound()
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_NOT_FOUND, self.status)

    def test_application_simple_query(self):
        @GET("/asd")
        @called_with
        def asd():
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((), {}), asd.called_with)

    def test_application_simple_var(self):
        @GET("/asd")
        @called_with
        def asd(a):
            return {}

        self.get("/asd?a=hi")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual((("hi",), {}), asd.called_with)

    def test_application_simple_var_parse(self):
        @GET("/asd")
        @called_with
        def asd(a=int):
            return {}

        self.get("/asd?a=42")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((42,), {}), asd.called_with)

    def test_application_simple_var_default(self):
        @GET("/asd")
        @called_with
        def asd(a=(int, 0)):
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((0,), {}), asd.called_with)

    def test_application_simple_var_parse_default(self):
        @GET("/asd")
        @called_with
        def asd(a=(int, 0)):
            return {}

        self.get("/asd?a=42")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((42,), {}), asd.called_with)

    def test_application_simple_post(self):
        @POST("/asd")
        @called_with
        def asd():
            return {}

        self.post("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual(((), {}), asd.called_with)

    def test_application_simple_post_body_var(self):
        @POST("/asd")
        @called_with
        def asd(a):
            return {}

        self.post("/asd", input_=StringIO("a=hello"), content_type=MIME_WWW_FORM_URLENCODED, content_len=7)
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual((("hello",), {}), asd.called_with)

    def test_application_simple_post_multipart_var(self):
        @POST("/asd")
        @called_with
        def asd(a):
            return {}

        boundary = "-----------------------------12345"
        body = """{boundary}
Content-Disposition: form-data; name="a"

asd
{boundary}""".format(boundary=boundary)
        self.post("/asd",
                  input_=StringIO(body),
                  content_type="{name}; boundary={boundary}".format(name=MIME_FORM_DATA, boundary=boundary),
                  content_len=len(body))
        self.assertEqual(HTTP_OK, self.status)
        self.assertEqual((("asd",), {}), asd.called_with)
