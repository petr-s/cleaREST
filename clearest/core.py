from abc import ABCMeta, abstractmethod
from collections import defaultdict
import functools
import inspect
import re
import six
from clearest.exceptions import MissingArgumentError, AlreadyRegisteredError

KEY_PATTERN = re.compile("\{(.*)\}")

class Key(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

def parse_path(path):
    if path is None:
        raise TypeError
    parts = path[1:].split("/") if path.startswith("/") else path.split("/") # meh
    for index, part in enumerate(parts):
        found = KEY_PATTERN.match(part)
        if found:
            parts[index] = Key(found.group(1))
    return tuple(parts)


def get_function_args(fn):
    spec = inspect.getargspec(fn)
    return dict(zip(reversed(spec.args), reversed(spec.defaults) if spec.defaults else []))


def check_function(path, fn_name, args):
    for part in path:
        if isinstance(part, Key) and part.name not in args:
            raise MissingArgumentError(fn_name, part.name)


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
        return "GET"

class POST(BaseDecorator):
    def type(self):
        return "POST"

