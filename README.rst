.. image:: https://travis-ci.org/petr-s/cleaREST.svg?branch=master
  :target: https://travis-ci.org/petr-s/cleaREST

.. image:: https://coveralls.io/repos/github/petr-s/cleaREST/badge.svg?branch=master
  :target: https://coveralls.io/github/petr-s/cleaREST?branch=master

========
cleaREST
========
**Light-weight Python framework for building REST APIs**
 * pure WSGI
 * minimalistic
 * easy to use
 * advanced variables processing


URL Routing
===========
is done by decorating your handling function with one of these decorators:
 * @GET
 * @POST

only one argument is required (url to handle) ie: ::

  @GET("/my/awesome/url")

optionally you can specify successful http result status (default is HTTP_OK) ie: ::

  @GET("/my/awesome/url", status=HTTP_CREATED)

list of status tuples:
 * HTTP_OK
 * HTTP_CREATED

you can also specify url path variables, with curly brackets similarly to python string formating ie: ::

  @GET("/my/awesome/url/{variable}")


Variables
=========
are specified directly to a function ie: ::

  @GET("/my/awesome/url")
  def my_function(first, second):
    ...

so when you call GET with query string like:

  curl localhost:8001/my/awesome/url?first=hello&second=world

those values are directly passed to the handling function.

**POST variables** can be send either as:
 * application/x-www-form-urlencoded
or
 * multipart/form-data


Parsing
=======
when variable is passed to the function it's a string, you can specify per parameter parsing function as default value ie: ::

  @GET("/my/awesome/url")
  def my_function(myid=int):

or optinal: ::

  @GET("/my/awesome/url")
  def my_function(myid=(int, 0)):

or reduction multiple arguments into one: ::

  @GET("/my/awesome/url")
  def my_function(user_id=lambda user, password: login)

Returning data
==============
just return value, there is build-in support for serializing:

+---------+-------------------+
| Class   | Content-type      |
+=========+===================+
| str     | text/plain        |
+---------+-------------------+
| dict    | application/json  |
+---------+-------------------+
| minidom | application/xml   |
+---------+-------------------+
| etree   | application/xml   |
+---------+-------------------+

but also you can register any custom data-type or override table above with: ::

  register_content_type(type_, content_type, handler)


Errors
======
you can return a http error by raising one of these exceptions:
 * HttpBadRequest
 * HttpNotFound
 * HttpUnsupportedMediaType
 * HttpNotImplemented

ie: ::

  @GET("/my/awesome/url")
  def my_function(myid=int):
      if myid == -1:
           raise HttpNotFound()
      ...


=========
Examples:
=========
**GET Hello world:** ::

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

**POST var:** ::

  from wsgiref.simple_server import make_server
  from clearest import application, POST


  @POST("/")
  def hello(what):
      return "hello {what}!".format(what=what)


  httpd = make_server("", 8000, application)
  httpd.serve_forever()

Output:

  curl --data "what=world" localhost:8000

  hello world!
