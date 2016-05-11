from clearest.core import GET, POST, CONTENT_TYPE, unregister_all, \
    add_static_file, add_static_dir, remove_all_static_files, application
from clearest.docs import set_templates_path
from clearest.exceptions import *
from clearest.http import *

__all__ = [
    "GET",
    "POST",
    "CONTENT_TYPE",

    "HTTP_NOT_FOUND",
    "HTTP_UNSUPPORTED_MEDIA_TYPE",
    "HTTP_BAD_REQUEST",
    "HTTP_OK",
    "HTTP_CREATED",
    "HTTP_NOT_IMPLEMENTED",
    "HTTP_UNAUTHORIZED",
    "HTTP_FORBIDDEN",
    "HTTP_GONE",

    "MIME_WWW_FORM_URLENCODED",
    "MIME_FORM_DATA",
    "MIME_JSON",
    "MIME_TEXT_PLAIN",
    "MIME_XML",
    "MIME_TEXT_HTML",
    "MIME_TEXT_CSS",
    "MIME_XHTML_XML",
    "MIME_JAVASCRIPT",

    "HttpBadRequest",
    "HttpUnauthorized",
    "HttpForbidden",
    "HttpNotFound",
    "HttpGone",
    "HttpUnsupportedMediaType",

    "MissingArgumentError",
    "AlreadyRegisteredError",
    "NotUniqueError",

    "application",

    "unregister_all",

    "add_static_file",
    "add_static_dir",
    "remove_all_static_files",

    "set_templates_path"
]

__version__ = "0.3.1"
__author__ = "Petr Skramovsky"
__contact__ = "petr.skramovsky@gmail.com"
__homepage__ = "https://github.com/petr-s/cleaREST"
