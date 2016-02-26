from unittest import TestCase
from clearest import GET, MissingArgumentError, AlreadyRegisteredError

class Test(TestCase):
    def test_decorator_missing_argument(self):
        def test_fn():
            @GET("/{key}")
            def asd():
                pass
        self.assertRaises(MissingArgumentError, test_fn)

    def test_d(self):
        def test_fn():
            @GET("/asd/asd")
            def asd():
                pass

            @GET("/asd/asd")
            def asd2():
                pass
        self.assertRaises(AlreadyRegisteredError, test_fn)
