.. image:: https://travis-ci.org/petr-s/cleaREST.svg?branch=master
  :target: https://travis-ci.org/petr-s/cleaREST

.. image:: https://coveralls.io/repos/github/petr-s/cleaREST/badge.svg?branch=master
  :target: https://coveralls.io/github/petr-s/cleaREST?branch=master

========
cleaREST
========
**Light-weight Python framework for building REST apis**

Examples:
---------
Hello world: ::

  from wsgiref.simple_server import make_server
  from clearest import application, GET


  @GET("/")
  def hello():
      return "hello world!"

   httpd = make_server("", 8000, application)
   httpd.serve_forever()

Output:

  curl localhost:8000

  hello world!
