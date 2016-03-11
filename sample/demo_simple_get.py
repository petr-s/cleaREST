from wsgiref.simple_server import make_server

from clearest import application, GET


@GET("/")
def hello():
    return "hello world!"


httpd = make_server("", 8000, application)
httpd.serve_forever()
