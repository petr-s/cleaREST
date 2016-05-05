from mock import patch

from clearest import *
from clearest.docs import set_templates_path
from tests.wsgi import WSGITestCase


def strip_ws(source):
    return "".join(source.split())


BROWSER_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"


class Test(WSGITestCase):
    def setUp(self):
        unregister_all()

    def test_docs_simple(self):
        @GET("/asd")
        def asd():
            """doc_string"""
            return {}

        result = self.get("/asd", accept=BROWSER_ACCEPT)
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XHTML_XML, self.headers[CONTENT_TYPE])
        self.assertIsNotNone(result)
        self.assertTrue("GET" in result)
        self.assertTrue("/asd" in result)

    @patch("jinja2.FileSystemLoader.get_source")
    def test_docs_custom_template(self, mock_get_source):
        @GET("/asd")
        def asd():
            """asd"""
            return {}

        custom_template = "I'm a custom template"
        mock_get_source.return_value = custom_template, "single.html", True
        set_templates_path("/my/template/dir")
        result = self.get("/asd", accept=BROWSER_ACCEPT)
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XHTML_XML, self.headers[CONTENT_TYPE])
        self.assertIsNotNone(result)
        self.assertTrue(mock_get_source.called)
        self.assertTrue(custom_template in result)

    @patch("jinja2.FileSystemLoader.get_source")
    def test_docs_custom_template_second_time(self, mock_get_source):
        @GET("/asd")
        def asd():
            """asd"""
            return {}

        custom_template = "custom template"
        mock_get_source.return_value = custom_template, "single.html", True
        set_templates_path("/my/template/dir")
        result = self.get("/asd", accept=BROWSER_ACCEPT)
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XHTML_XML, self.headers[CONTENT_TYPE])
        self.assertIsNotNone(result)
        self.assertTrue(mock_get_source.called)
        self.assertTrue(custom_template in result)

        custom_template = "second custom template"
        mock_get_source.return_value = custom_template, "single.html", True
        set_templates_path("/my/template/dir")
        result = self.get("/asd", accept=BROWSER_ACCEPT)
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_XHTML_XML, self.headers[CONTENT_TYPE])
        self.assertIsNotNone(result)
        self.assertTrue(mock_get_source.called)
        self.assertTrue(custom_template in result)
