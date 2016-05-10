.. image:: https://travis-ci.org/petr-s/cleaREST.svg?branch=master
  :target: https://travis-ci.org/petr-s/cleaREST

.. image:: https://coveralls.io/repos/github/petr-s/cleaREST/badge.svg?branch=master
  :target: https://coveralls.io/github/petr-s/cleaREST?branch=master

========
cleaREST
========

Light-weight Python framework for building REST APIs

* WSGI
* minimalistic
* easy to use
* advanced variables processing
* automatic html documentation generation


URL Routing
===========

is done by decorating your handling function with one of these decorators:

* @GET
* @POST

only one argument is required (url to handle) ie: ::

  @GET("/my/awesome/url")
  def my_function():
      ...

optionally you can specify successful http result status (default is HTTP_OK) ie: ::

  @GET("/my/awesome/url", status=HTTP_CREATED)
  def my_function():
      ...

list of status tuples:

* HTTP_OK
* HTTP_CREATED



Variables
=========

- GET variables from query string

* POST variables can be send as:

 * application/x-www-form-urlencoded
 * multipart/form-data
 * application/json

* url path variables (identifier inside curly brackets) ie: ::

   @GET("/my/awesome/url/{variable}")
   def my_function(variable):
       ...



Parsing
=======

per parameter parsing function assigned as default value ie: ::

  @GET("/my/awesome/url")
  def my_function(myid=int):
      ...

optional parameter: ::

  @GET("/my/awesome/url")
  def my_function(myid=(int, 0)):
      ...

reduction multiple into one: ::

  @GET("/my/awesome/url")
  def my_function(user_id=lambda user, password: login):
      ...



Returning data
==============

build-in support:

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

you can also register any custom data-type or override table above with: ::

  register_content_type(type_, content_type, handler)



Errors
======

to return a http error raise one of these exceptions:

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

HTML Documentation
==================

when is url opened by web-browser html documentation is shown instead of actual function call.
* "application/xhtml+xml" in accept http header
* similar tags to sphinx/docutils
* extra example tags: ":example:" and for response ":rexample":

ie: ::

  @GET("/my/api")
  def my_function(a, b=int):
      """
      Describe your function here.

      :param str a: Describe a here.
      :param int b: Describe b here.
      :return: W/E you function returns.

      :example::

          GET /my/api?a=someting&b=42

      :rexample::

          {
              "something": "something"
              ...
          }
      """
      ...

"real app" example:
.. image:: https://cloud.githubusercontent.com/assets/4590121/15144637/01abb660-16b1-11e6-85b4-bdb46d33e3cf.png


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
