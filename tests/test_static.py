from mock import patch, mock_open
from six import StringIO

from clearest import *
from tests.wsgi import WSGITestCase


class Test(WSGITestCase):
    def setUp(self):
        remove_all_static_files()

    def test_add_static_file(self):
        css = "h1 { color: red; }"
        add_static_file("/test.css", StringIO(css), MIME_TEXT_CSS)
        result = self.get("/test.css")
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_TEXT_CSS, self.headers[CONTENT_TYPE])
        self.assertEqual(css, result)

    def test_add_static_file_detect_css(self):
        add_static_file("/test.css", StringIO(""))
        self.get("/test.css")
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_TEXT_CSS, self.headers[CONTENT_TYPE])

    def test_add_static_file_detect_js(self):
        add_static_file("/test.js", StringIO(""))
        self.get("/test.js")
        self.assertEqual(HTTP_OK, self.status)
        self.assertTrue(CONTENT_TYPE in self.headers)
        self.assertEqual(MIME_JAVASCRIPT, self.headers[CONTENT_TYPE])

    def test_add_static_file_detect_unknown(self):
        def test():
            add_static_file("/test.asd", StringIO(""))

        self.assertRaises(KeyError, test)

    @patch("os.walk")
    def test_add_static_dir(self, walk_mock):
        walk_mock.return_value = [("test", [], ["test.css"])]
        add_static_dir("/css", "test", open_fn=mock_open())
        self.get("/css/test.css")
        self.assertEqual(HTTP_OK, self.status)
