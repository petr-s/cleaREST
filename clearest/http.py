from collections import namedtuple

HTTP_GET = "GET"
HTTP_POST = "POST"

HttpStatus = namedtuple("HttpStatus", ["code", "msg"])
HTTP_OK = HttpStatus(200, "OK")
HTTP_BAD_REQUEST = HttpStatus(403, "Bad-request")

HTTP_1_0 = "HTTP/1.0"
HTTP_1_1 = "HTTP/1.1"

HTTP_METHODS = (HTTP_GET, HTTP_POST)
HTTP_PROTOCOLS = (HTTP_1_0, HTTP_1_1)

MIME_TEXT_PLAIN = "text/plain"

CONTENT_TYPE = "Content-type"
