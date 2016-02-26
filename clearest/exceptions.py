class MissingArgumentError(Exception):
    def __init__(self, fn_name, arg):
        super(MissingArgumentError, self).__init__("function {name} is missing argument {arg}!".format(name=fn_name, arg=arg))

class AlreadyRegisteredError(Exception):
    def __init__(self, path, old_fn_name):
        super(AlreadyRegisteredError, self).__init__("path {path} is already registered to the function {old}!".format(old=old_fn_name, path=path))
