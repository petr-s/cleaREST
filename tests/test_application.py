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

        self.get("asd")
        self.assertEqual(((), {}), asd.called_with)
        self.assertEqual(HTTP_OK, self.status)
