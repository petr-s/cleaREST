import functools
import inspect
import json
import logging
import os
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy
from xml.dom.minidom import Document
from xml.etree.ElementTree import tostring, Element

from clearest.docs import generate_index

try:  # pragma: no cover
    from urllib.parse import parse_qs  # pragma: no cover
except ImportError:  # pragma: no cover
    from urlparse import parse_qs  # pragma: no cover

import six

from clearest.exceptions import MissingArgumentError, AlreadyRegisteredError, NotUniqueError, HttpError, \
    HttpNotFound, NotRootError, HttpUnsupportedMediaType, HttpBadRequest, HttpNotImplemented
from clearest.http import HTTP_GET, HTTP_POST, CONTENT_TYPE, MIME_TEXT_PLAIN, HTTP_OK, MIME_WWW_FORM_URLENCODED, \
    MIME_FORM_DATA, CONTENT_DISPOSITION, MIME_JSON, MIME_XML, MIME_XHTML_XML, MIME_TEXT_CSS, MIME_JAVASCRIPT, \
    MIME_TEXT_HTML
from clearest.wsgi import REQUEST_METHOD, PATH_INFO, QUERY_STRING, WSGI_INPUT, WSGI_CONTENT_TYPE, WSGI_CONTENT_LENGTH, \
    HTTP_ACCEPT

KEY_PATTERN = re.compile("\{(.*)\}")
STATUS_FMT = "{0} {1}"
CALLABLE = 0
DEFAULT = 1
ACCEPT_MIMES = "accept_mimes"
_content_types = {}
_static_content_types = {}
_static_files = {}


class Key(object):
    def __init__(self, name, pre):
        self.name = name
        self.pre = pre

    def __eq__(self, other):
        return self.pre == other.pre

    def __hash__(self):
        return hash(self.pre)


def signature_to_path(signature):
    return "/" + "/".join("{%s}" % x.name if isinstance(x, Key) else x for x in signature)


def parse_path(path):
    if path is None:
        raise TypeError
    elif not path.startswith("/"):
        raise NotRootError(path)
    parts = path[1:].split("/")
    for index, part in enumerate(parts):
        found = KEY_PATTERN.match(part)
        if found:
            parts[index] = Key(found.group(1), tuple(parts[:index]))
    return tuple(parts)


def get_function_args(fn):
    spec = inspect.getargspec(fn)
    n_args = len(spec.args)
    if not spec.defaults:
        defaults = tuple([None] * n_args)
    else:
        defaults = tuple([None] * (n_args - len(spec.defaults))) + spec.defaults
    return dict(zip(spec.args, defaults))


def check_function(path, fn_name, args):
    names = set()
    for part in path:
        if isinstance(part, Key):
            if part.name not in args:
                raise MissingArgumentError(fn_name, part.name)
            elif part.name in names:
                raise NotUniqueError(part.name)
            names.add(part.name)


def all_registered():
    return BaseDecorator.registered


def unregister_all():
    BaseDecorator.registered.clear()


def register_content_type(type_, content_type, handler):
    _content_types[type_] = content_type, handler


def is_matching(signature, args, path, query):
    path_len = len(path)
    signature_len = len(signature)
    if signature_len != path_len:
        if path_len == signature_len - 1 and \
                isinstance(signature[-1], Key) and \
                isinstance(args[signature[-1].name], tuple):  # last optional path var handling
            return True
        else:
            return False
    for s, p in zip(signature, path):
        if not isinstance(s, Key) and s != p:
            return False
    else:
        return True


def isalambda(object_):
    LAMBDA = lambda: 0
    return isinstance(object_, type(LAMBDA)) and object_.__name__ == LAMBDA.__name__


def parse_args(args, path, query, specials):
    def one_or_many(fn_, dict_, key):
        result = [fn_(value) for value in dict_[key]]
        return result[0] if len(result) == 1 else result

    kwargs = {}
    for arg, parse_fn in six.iteritems(args):
        if arg in specials:
            kwargs[arg] = specials[arg]()
        elif parse_fn is None:
            kwargs[arg] = one_or_many(lambda x: x, query, arg)
        elif isinstance(parse_fn, tuple):
            kwargs[arg] = parse_fn[DEFAULT] if arg not in query else one_or_many(parse_fn[CALLABLE], query, arg)
        elif isalambda(parse_fn):
            _code = six.get_function_code(parse_fn)
            closures = six.get_function_closure(parse_fn)
            if closures:
                assert len(closures) <= 1
                fn = closures[0].cell_contents
            else:
                fn = eval(".".join(_code.co_names), six.get_function_globals(parse_fn))
            kwargs[arg] = fn(**parse_args(get_function_args(parse_fn), path, query, specials))
        else:
            kwargs[arg] = one_or_many(parse_fn, query, arg)
    return kwargs


def add_static_file(path, readable, content_type=None):
    if not content_type:
        ext = os.path.splitext(path)[1]
        if ext not in _static_content_types:
            raise KeyError()
        else:
            content_type = _static_content_types[ext]
    _static_files[path] = content_type, readable.read()


def add_static_dir(path, dir_path, open_fn=open):
    for root, sub_dirs, files in os.walk(dir_path):
        for file_ in files:
            add_static_file("/".join((path, file_)), open_fn(file_, "rb"))


def register_static_content_type(ext, content_type):
    _static_content_types[ext] = content_type


def remove_all_static_files():
    _static_files.clear()


def application(environ, start_response):
    def parse_content_type(value):
        parts = value.split(";")
        return (parts[0], {k.lstrip(): v for k, v in
                           (kv.split("=") for kv in parts[1:])}) if len(parts) > 1 else (value, {})

    def parse_www_form(input_file, n, extras):
        return parse_qs(input_file.read(n))

    def parse_form_data(input_file, n, extras):
        assert "boundary" in extras
        kwargs = {}
        state = 0  # TODO: enum
        name = None
        for line in input_file.read(n).splitlines():
            if state == 0 and line == extras["boundary"]:
                state = 1
            elif state == 1 and line.startswith(CONTENT_DISPOSITION):
                name = re.match(CONTENT_DISPOSITION + ": form\-data; name=\"(.*)\"", line).group(1)
                state = 2
            elif state == 2 and not len(line):
                state = 3
            elif state == 3:
                kwargs[name] = [line]
                state = 0
        return kwargs

    def parse_json(input_file, n, extras):
        encoding = "utf-8" if "encoding" not in extras else extras["encoding"]
        return {k: [v] for k, v in six.iteritems(json.loads(input_file.read(n), encoding=encoding))}

    def parse_accept():
        if HTTP_ACCEPT in environ:
            result = []
            parts = (x.split(";") for x in environ[HTTP_ACCEPT].split(","))
            for part in parts:
                if len(part) == 1:
                    result.append((1.0, part[0]))
                else:
                    mime, q = part
                    result.append((float(q[2:]), mime))
            return tuple(value for (weight, value) in sorted(result, key=lambda x: x[0], reverse=True))
        else:
            return {}

    content_types = {MIME_WWW_FORM_URLENCODED: parse_www_form,
                     MIME_FORM_DATA: parse_form_data,
                     MIME_JSON: parse_json}
    specials = {ACCEPT_MIMES: parse_accept}
    try:
        if environ[REQUEST_METHOD] == HTTP_GET and environ[PATH_INFO] in _static_files:
            content_type, content = _static_files[environ[PATH_INFO]]
            start_response(STATUS_FMT.format(*HTTP_OK), [(CONTENT_TYPE, content_type)])
            return [content]
        elif environ[REQUEST_METHOD] in all_registered():
            path = tuple(environ[PATH_INFO][1:].split("/"))
            query = parse_qs(environ[QUERY_STRING]) if QUERY_STRING in environ else {}
            if environ[REQUEST_METHOD] == HTTP_GET and MIME_XHTML_XML in parse_accept() and path == ("",):
                start_response(STATUS_FMT.format(*HTTP_OK), [(CONTENT_TYPE, MIME_TEXT_HTML)])
                for method in six.iterkeys(BaseDecorator.registered):
                    all_ = [(desc, method, signature_to_path(signature), fn.__doc__)
                            for signature, (fn, args, status, desc) in
                            six.iteritems(BaseDecorator.registered[method])]
                    return [generate_index(all_).encode("utf-8")]
            elif WSGI_CONTENT_TYPE in environ and environ[WSGI_CONTENT_TYPE] != MIME_TEXT_PLAIN:
                content_type, extras_ = parse_content_type(environ[WSGI_CONTENT_TYPE])
                if content_type not in content_types:
                    raise HttpUnsupportedMediaType()
                query.update(content_types[content_type](environ[WSGI_INPUT],
                                                         int(environ[WSGI_CONTENT_LENGTH]),
                                                         extras_))
            for signature, (fn, args, status, desc) in six.iteritems(BaseDecorator.registered[environ[REQUEST_METHOD]]):
                if is_matching(signature, args, path, query):
                    try:
                        updated_query = query.copy()
                        updated_query.update({key.name: [value]
                                              for key, value in zip(signature, path)
                                              if isinstance(key, Key)})
                        parsed_args = parse_args(args, path, updated_query, specials)
                    except Exception as e:
                        logging.exception(e)
                        raise HttpBadRequest()
                    result = fn(**parsed_args)
                    for type_ in six.iterkeys(_content_types):
                        if isinstance(result, type_):
                            content_type, content_handler = _content_types[type_]
                            break
                    else:
                        raise HttpNotImplemented()
                    start_response(STATUS_FMT.format(*status),
                                   [(CONTENT_TYPE, content_type)])
                    return [content_handler(result)]
        raise HttpNotFound()
    except HttpError as error:
        status = STATUS_FMT.format(error.code, error.msg)
        start_response(status, [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
        return [status]


@six.add_metaclass(ABCMeta)
class BaseDecorator(object):
    registered = defaultdict(lambda: dict())

    def __init__(self, path, status=HTTP_OK, description=None):
        self.path = parse_path(path)
        self.status = status
        self.description = description

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            result = fn(*args, **kwargs)
            wrapped.__dict__ = deepcopy(fn.__dict__["__wrapped__"].__dict__ if
                                        "__wrapped__" in fn.__dict__ else
                                        fn.__dict__)
            return result

        registered = BaseDecorator.registered[self.type()]
        if self.path in registered:
            old = registered[self.path][0].__name__
            path = signature_to_path(self.path)  # "/".join(x.name if isinstance(x, Key) else x for x in self.path)
            raise AlreadyRegisteredError(path, old)
        fn_args = get_function_args(fn)
        check_function(self.path, fn.__name__, fn_args)
        registered[self.path] = wrapped, fn_args, self.status, self.description
        return wrapped

    @abstractmethod
    def type(self):
        pass  # pragma: no cover


class GET(BaseDecorator):
    def type(self):
        return HTTP_GET


class POST(BaseDecorator):
    def type(self):
        return HTTP_POST


register_content_type(str, MIME_TEXT_PLAIN, lambda x: x)
register_content_type(dict, MIME_JSON, json.dumps)
register_content_type(Document, MIME_XML, lambda x: x.toxml())
register_content_type(Element, MIME_XML, lambda x: tostring(x))

register_static_content_type(".css", MIME_TEXT_CSS)
register_static_content_type(".js", MIME_JAVASCRIPT)
