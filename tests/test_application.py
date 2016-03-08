from clearest import POST, HTTP_NOT_FOUND, GET, unregister_all, HTTP_OK
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
