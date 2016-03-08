from unittest import TestCase

from clearest import GET, MissingArgumentError, AlreadyRegisteredError, NotUniqueError, unregister_all, NotRootError


class Test(TestCase):
    def setUp(self):
        unregister_all()

    def test_decorator_none_path(self):
        def test_fn():
            @GET(None)
            def asd():
                pass

        self.assertRaises(TypeError, test_fn)

    def test_decorator_missing_argument(self):
        def test_fn():
            @GET("/{key}")
            def asd():
                pass

        self.assertRaises(MissingArgumentError, test_fn)

    def test_decorator_already_registered_simple(self):
        def test_fn():
            @GET("/asd/asd")
            def asd():
                pass

            @GET("/asd/asd")
            def asd2():
                pass

        self.assertRaises(AlreadyRegisteredError, test_fn)

    def test_decorator_already_registered_keys_simple(self):
        def test_fn():
            @GET("/asd/{a}")
            def asd(a):
                pass

            @GET("/asd/{b}")
            def asd2(b):
                pass

        self.assertRaises(AlreadyRegisteredError, test_fn)

    def test_decorator_already_registered_keys_complex(self):
        def test_fn():
            @GET("/asd/{a}/asd/{b}")
            def asd(a, b):
                pass

            @GET("/asd/{a}/asd/{c}")
            def asd2(b, c):
                pass

        self.assertRaises(AlreadyRegisteredError, test_fn)

    def test_decorator_var_not_unique(self):
        def test_fn():
            @GET("/asd/{a}/{a}")
            def asd(a, b):
                pass

        self.assertRaises(NotUniqueError, test_fn)

    def test_not_root(self):
        def test_fn():
            @GET("asd")
            def asd(a, b):
                pass

        self.assertRaises(NotRootError, test_fn)
