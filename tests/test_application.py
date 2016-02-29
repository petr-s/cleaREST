from clearest import POST, HTTP_BAD_REQUEST
from tests.wsgi import WSGITestCase


class Test(WSGITestCase):
    def test_application_bad_request(self):
        @POST("/asd")
        def asd():
            return {}
        result = self.get("/asd")
        self.assertEqual(HTTP_BAD_REQUEST, self.status)
