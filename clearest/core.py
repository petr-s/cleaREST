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
    HttpNotFound, NotRootError
from clearest.http import HTTP_GET, HTTP_POST, CONTENT_TYPE, MIME_TEXT_PLAIN, HTTP_OK
from clearest.wsgi import REQUEST_METHOD, PATH_INFO, QUERY_STRING

KEY_PATTERN = re.compile("\{(.*)\}")
STATUS_FMT = "{code} {msg}"
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
    try:
        if environ[REQUEST_METHOD] in all_registered():
            path = tuple(environ[PATH_INFO][1:].split("/"))
            query = parse_qs(environ[QUERY_STRING]) if QUERY_STRING in environ else tuple()
            for signature, (fn, args) in six.iteritems(BaseDecorator.registered[environ[REQUEST_METHOD]]):
                if is_matching(signature, args, path, query):
                    result = fn(**parse_args(args, path, query))
                    start_response(STATUS_FMT.format(**HTTP_OK._asdict()),
                                   [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
                    return [result]
        raise HttpNotFound()
    except HttpError as error:
        status = STATUS_FMT.format(code=error.code, msg=error.msg)
        start_response(status, [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
        return [status]
    else:
        pass


@six.add_metaclass(ABCMeta)
class BaseDecorator(object):
    registered = defaultdict(lambda: dict())

    def __init__(self, path):
        self.path = parse_path(path)

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
        registered[self.path] = wrapped, fn_args
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
