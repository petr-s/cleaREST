import json

from six import StringIO

from clearest import POST, HTTP_NOT_FOUND, GET, unregister_all, HTTP_OK, HTTP_UNSUPPORTED_MEDIA_TYPE, \
    MIME_WWW_FORM_URLENCODED, MIME_FORM_DATA, HTTP_CREATED, HTTP_BAD_REQUEST, HttpNotFound, CONTENT_TYPE, \
    MIME_TEXT_PLAIN, MIME_JSON, HTTP_NOT_IMPLEMENTED, MIME_XML
from tests.util import called_with
from tests.wsgi import WSGITestCase


def g_login(user, password):
    return 1


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
        self.assertCalledWith(asd)

    def test_application_simple_var(self):
        @GET("/asd")
        @called_with
        def asd(a):
            return {}

        self.get("/asd?a=hi")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, "hi")

    def test_application_simple_var_parse(self):
        @GET("/asd")
        @called_with
        def asd(a=int):
            return {}

        self.get("/asd?a=42")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, 42)

    def test_application_simple_var_parse_many(self):
        @GET("/asd")
        @called_with
        def asd(a=int):
            return {}

        self.get("/asd?a=42&a=84")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, [42, 84])

    def test_application_simple_var_default(self):
        @GET("/asd")
        @called_with
        def asd(a=(int, 0)):
            return {}

        self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, 0)

    def test_application_simple_var_parse_default(self):
        @GET("/asd")
        @called_with
        def asd(a=(int, 0)):
            return {}

        self.get("/asd?a=42")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, 42)

    def test_application_simple_post(self):
        @POST("/asd")
        @called_with
        def asd():
            return {}

        self.post("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd)

    def test_application_simple_post_body_var(self):
        @POST("/asd")
        @called_with
        def asd(a):
            return {}

        self.post("/asd", input_=StringIO("a=hello"), content_type=MIME_WWW_FORM_URLENCODED, content_len=7)
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, "hello")

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
        self.assertCalledWith(asd, "asd")

    def test_application_missing_content_type(self):
        @GET("/asd")
        @called_with
        def asd():
            return []

        self.get("/asd")
        self.assertEqual(HTTP_NOT_IMPLEMENTED, self.status)

    def test_application_content_type_default_text(self):
        @GET("/asd")
        @called_with
        def asd():
            return "hi"

        result = self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_TEXT_PLAIN, self.headers[CONTENT_TYPE])
        self.assertEqual("hi", result)

    def test_application_content_type_default_json(self):
        @GET("/asd")
        @called_with
        def asd():
            return {"hello": "world"}

        result = self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_JSON, self.headers[CONTENT_TYPE])
        self.assertEqual({"hello": "world"}, json.loads(result))

    def test_application_content_type_default_xml_mimidom(self):
        from xml.dom.minidom import Document, parseString

        @GET("/asd")
        @called_with
        def asd():
            doc = Document()
            root = doc.createElement("root")
            doc.appendChild(root)
            return doc

        result = self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XML, self.headers[CONTENT_TYPE])
        self.assertEqual(parseString("<root/>").toxml(), result)

    def test_application_content_type_default_xml_etree(self):
        from xml.etree.ElementTree import Element, fromstring, tostring

        @GET("/asd")
        @called_with
        def asd():
            root = Element("root")
            return root

        result = self.get("/asd")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XML, self.headers[CONTENT_TYPE])
        self.assertEqual(tostring(fromstring("<root/>")), tostring(fromstring(result)))

    def test_application_simple_lambda_closure(self):
        def login(user, password):
            return 1

        @GET("/asd")
        @called_with
        def asd(user_id=lambda user, password: login):
            return {}

        self.get("/asd?user=guest&password=secret")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, 1)

    def test_application_simple_lambda(self):
        @GET("/asd")
        @called_with
        def asd(user_id=lambda user, password: g_login):
            return {}

        self.get("/asd?user=guest&password=secret")
        self.assertEqual(HTTP_OK, self.status)
        self.assertCalledWith(asd, 1)
