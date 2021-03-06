from collections import namedtuple

HTTP_GET = "GET"
HTTP_POST = "POST"

HttpStatus = namedtuple("HttpStatus", ["code", "msg"])
HTTP_OK = HttpStatus(200, "OK")
HTTP_CREATED = HttpStatus(201, "Created")
HTTP_BAD_REQUEST = HttpStatus(400, "Bad Request")
HTTP_UNAUTHORIZED = HttpStatus(401, "Unauthorized")
HTTP_FORBIDDEN = HttpStatus(403, "Forbidden")
HTTP_NOT_FOUND = HttpStatus(404, "Not Found")
HTTP_GONE = HttpStatus(410, "Gone")
HTTP_UNSUPPORTED_MEDIA_TYPE = HttpStatus(415, "Unsupported Media Type")
HTTP_NOT_IMPLEMENTED = HttpStatus(501, "Not Implemented")

HTTP_1_0 = "HTTP/1.0"
HTTP_1_1 = "HTTP/1.1"

HTTP_METHODS = (HTTP_GET, HTTP_POST)
HTTP_PROTOCOLS = (HTTP_1_0, HTTP_1_1)

MIME_TEXT_PLAIN = "text/plain"
MIME_TEXT_HTML = "text/html"
MIME_TEXT_CSS = "text/css"
MIME_JAVASCRIPT = "application/javascript"
MIME_JSON = "application/json"
MIME_XML = "application/xml"
MIME_XHTML_XML = "application/xhtml+xml"
MIME_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"
MIME_FORM_DATA = "multipart/form-data"

CONTENT_TYPE = "Content-type"
CONTENT_DISPOSITION = "Content-Disposition"
