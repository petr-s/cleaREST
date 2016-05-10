from wsgiref.simple_server import make_server

from clearest import application, GET


@GET("/api/answer")
def answer(name, another_parameter=int):
    """
    says hello and computes the ultimate answer

    :param str name: Your name
    :param int another_parameter: So it's not so empty
    :return: json

    :example::

        GET /api/hello?name=Pete&another_parameter=1

    :rexample::

        {
            "greetings": "Hello Pete!",
            "the_answer": 42
        }
    """
    return {"greetings": "Hello {name}!".format(name=name), "the_answer": 42}


httpd = make_server("", 8000, application)
httpd.serve_forever()
