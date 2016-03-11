from wsgiref.simple_server import make_server

from clearest import application, POST


@POST("/")
def hello(what):
    return "hello {what}!".format(what=what)


httpd = make_server("", 8001, application)
httpd.serve_forever()
