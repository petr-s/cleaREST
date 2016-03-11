from clearest.http import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_UNSUPPORTED_MEDIA_TYPE


class MissingArgumentError(Exception):
    def __init__(self, fn_name, arg):
        super(MissingArgumentError, self).__init__(
            "function {name} is missing argument {arg}!".format(name=fn_name, arg=arg))


class AlreadyRegisteredError(Exception):
    def __init__(self, path, old_fn_name):
        super(AlreadyRegisteredError, self).__init__(
            "path {path} is already registered to the function {old}!".format(old=old_fn_name, path=path))


class NotUniqueError(Exception):
    def __init__(self, var_name):
        super(NotUniqueError, self).__init__("variable {var} is not unique".format(var=var_name))


class NotRootError(Exception):
    def __init__(self, path):
        super(NotRootError, self).__init__("path is not it the root (change it to /{path})".format(path=path))


class HttpError(Exception):
    def __init__(self, code, msg):
        super(HttpError, self).__init__()
        self.code = code
        self.msg = msg


class HttpBadRequest(HttpError):
    def __init__(self):
        super(HttpBadRequest, self).__init__(*HTTP_BAD_REQUEST)


class HttpNotFound(HttpError):
    def __init__(self):
        super(HttpNotFound, self).__init__(*HTTP_NOT_FOUND)


class HttpUnsupportedMediaType(HttpError):
    def __init__(self):
        super(HttpUnsupportedMediaType, self).__init__(*HTTP_UNSUPPORTED_MEDIA_TYPE)
