from abc import ABCMeta, abstractmethod
from collections import defaultdict
import functools
import inspect
import re

import six

from clearest.exceptions import MissingArgumentError, AlreadyRegisteredError, NotUniqueError, HttpError, HttpBadRequest
from clearest.http import HTTP_GET, HTTP_POST, CONTENT_TYPE, MIME_TEXT_PLAIN
from clearest.wsgi import REQUEST_METHOD

KEY_PATTERN = re.compile("\{(.*)\}")

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
    parts = path[1:].split("/") if path.startswith("/") else path.split("/") # meh
    for index, part in enumerate(parts):
        found = KEY_PATTERN.match(part)
        if found:
            parts[index] = Key(found.group(1), tuple(parts[:index]))
    return tuple(parts)


def get_function_args(fn):
    spec = inspect.getargspec(fn)
    n_args = len(spec.args)
    if not spec.defaults:
        defaults = [None] * n_args
    else:
        defaults = spec.defaults + [None] * (n_args - len(spec.defaults))
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

def application(environ, start_response):
    try:
        if environ[REQUEST_METHOD] not in all_registered():
            raise HttpBadRequest()
        registered = BaseDecorator.registered[environ[REQUEST_METHOD]]
    except HttpError as error:
        start_response("{code} {msg}".format(code=error.code, msg=error.msg), [(CONTENT_TYPE, MIME_TEXT_PLAIN)])
        return []
    else:
        pass


@six.add_metaclass(ABCMeta)
class BaseDecorator(object):
    registered = defaultdict(lambda: dict())

    def __init__(self, path):
        self.path = parse_path(path)

    def __call__(self, fn):
        registered = BaseDecorator.registered[self.type()]
        if self.path in registered:
            old = registered[self.path][0].__name__
            path = "/".join(x.name if isinstance(x, Key) else x for x in self.path)
            raise AlreadyRegisteredError(path, old)
        fn_args = get_function_args(fn)
        check_function(self.path, fn.__name__, fn_args)
        registered[self.path] = fn, fn_args

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapped

    @abstractmethod
    def type(self):
        pass

class GET(BaseDecorator):
    def type(self):
        return HTTP_GET

class POST(BaseDecorator):
    def type(self):
        return HTTP_POST

