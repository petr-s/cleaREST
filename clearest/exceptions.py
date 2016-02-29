from clearest.http import HTTP_BAD_REQUEST


class MissingArgumentError(Exception):
    def __init__(self, fn_name, arg):
        super(MissingArgumentError, self).__init__("function {name} is missing argument {arg}!".format(name=fn_name, arg=arg))

class AlreadyRegisteredError(Exception):
    def __init__(self, path, old_fn_name):
        super(AlreadyRegisteredError, self).__init__("path {path} is already registered to the function {old}!".format(old=old_fn_name, path=path))

class NotUniqueError(Exception):
    def __init__(self, var_name):
        super(NotUniqueError, self).__init__("variable {var} is not unique".format(var=var_name))

class HttpError(Exception):
    def __init__(self, code, msg):
        super(HttpError, self).__init__()
        self.code = code
        self.msg = msg

class HttpBadRequest(HttpError):
    def __init__(self):
        super(HttpBadRequest, self).__init__(*HTTP_BAD_REQUEST)
