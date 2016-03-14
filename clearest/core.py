import functools
import inspect
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy

try:  # pragma: no cover
    from urllib.parse import parse_qs  # pragma: no cover
except ImportError:  # pragma: no cover
    from urlparse import parse_qs  # pragma: no cover

import six

from clearest.exceptions import MissingArgumentError, AlreadyRegisteredError, NotUniqueError, HttpError, \
    HttpNotFound, NotRootError, HttpUnsupportedMediaType
from clearest.http import HTTP_GET, HTTP_POST, CONTENT_TYPE, MIME_TEXT_PLAIN, HTTP_OK, MIME_WWW_FORM_URLENCODED, \
    MIME_FORM_DATA, CONTENT_DISPOSITION
from clearest.wsgi import REQUEST_METHOD, PATH_INFO, QUERY_STRING, WSGI_INPUT, WSGI_CONTENT_TYPE, WSGI_CONTENT_LENGTH

KEY_PATTERN = re.compile("\{(.*)\}")
STATUS_FMT = "{0} {1}"
CALLABLE = 0
DEFAULT = 1


class Key(object):
    def __init__(self, name, pre):
        self.name = name
        self.pre = pre

    def __eq__(self, other):
        return self.pre == other.pre

    def __hash__(self):
        return hash(self.pre)


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
        defaults = spec.defaults + tuple([None] * (n_args - len(spec.defaults)))
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


def is_matching(signature, args, path, query):
    if len(signature) != len(path):
        return False
    return True


def parse_args(args, path, query):
    def one_or_many(dict_, key):
        return dict_[key][0] if len(dict_[key]) == 1 else dict_[key]

    kwargs = {}
    for arg, parse_fn in six.iteritems(args):
        if parse_fn is None:
            kwargs[arg] = one_or_many(query, arg)
        elif isinstance(parse_fn, tuple):
            kwargs[arg] = parse_fn[DEFAULT] if arg not in query else parse_fn[CALLABLE](one_or_many(query, arg))
        else:
            kwargs[arg] = parse_fn(one_or_many(query, arg))
    return kwargs


def application(environ, start_response):
    def parse_www_form(input_file, n, rest):
        return parse_qs(input_file.read(n))

    def parse_form_data(input_file, n, rest):
        kwargs = {}
        boundary = re.match(" boundary=(.*)", rest).group(1)
        state = 0  # TODO: enum
        name = None
        for line in input_file.read(n).splitlines():
            if state == 0 and line == boundary:
                state = 1
            elif state == 1 and line.startswith(CONTENT_DISPOSITION):
                name = re.match(CONTENT_DISPOSITION + ": form\-data; name=\"(.*)\"", line).group(1)
                state = 2
            elif state == 2 and not len(line):
                state = 3
            elif state == 3:
                kwargs[name] = line
                state = 0
        return kwargs

    content_types = {MIME_WWW_FORM_URLENCODED: parse_www_form,
                     MIME_FORM_DATA: parse_form_data}
    try:
        if environ[REQUEST_METHOD] in all_registered():
            path = tuple(environ[PATH_INFO][1:].split("/"))
            query = parse_qs(environ[QUERY_STRING]) if QUERY_STRING in environ else {}
            if WSGI_CONTENT_TYPE in environ:
                temp = environ[WSGI_CONTENT_TYPE].split(";")
                assert len(temp) <= 2
                content_type, rest = temp if len(temp) == 2 else (temp[0], None)
                if content_type not in content_types:
                    raise HttpUnsupportedMediaType()
                query.update(content_types[content_type](environ[WSGI_INPUT], int(environ[WSGI_CONTENT_LENGTH]), rest))
            for signature, (fn, args, status) in six.iteritems(BaseDecorator.registered[environ[REQUEST_METHOD]]):
                if is_matching(signature, args, path, query):
                    result = fn(**parse_args(args, path, query))
                    start_response(STATUS_FMT.format(*status),
                                   [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
                    return [result]
        raise HttpNotFound()
    except HttpError as error:
        status = STATUS_FMT.format(error.code, error.msg)
        start_response(status, [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
        return [status]


@six.add_metaclass(ABCMeta)
class BaseDecorator(object):
    registered = defaultdict(lambda: dict())

    def __init__(self, path, status=HTTP_OK):
        self.path = parse_path(path)
        self.status = status

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
            path = "/".join(x.name if isinstance(x, Key) else x for x in self.path)
            raise AlreadyRegisteredError(path, old)
        fn_args = get_function_args(fn)
        check_function(self.path, fn.__name__, fn_args)
        registered[self.path] = wrapped, fn_args, self.status
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
