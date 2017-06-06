from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from tornado_restplus import Api


def make_app():
    return Application()


class ApiTest(AsyncHTTPTestCase):
    def get_app(self):
        app = make_app()
        self.api = Api(app)
        return app

    def setUp(self):
        super(ApiTest, self).setUp()
        # self.app = make_app()
        self.api = Api(self._app)

    def test_namespace_single_route(self):
        ns = self.api.namespace('TestNamespace')

        @ns.route('/first_handler', reply='[0]')
        class SomeFirstHandler(RequestHandler):
            def initialize(self, reply):
                self.reply = reply

            def get(self):
                self.write(self.reply)

        response = self.fetch('/TestNamespace/first_handler')
        assert response.code == 200
        assert response.body == b'[0]'

    def test_namespace_multiple_routes(self):
        ns = self.api.namespace('api')

        class BaseTestHandler(RequestHandler):
            def initialize(self, reply):
                self.reply = reply

            def get(self):
                self.write(self.reply)

        @ns.route('/first_handler', reply='[1]')
        class FirstTestHandler(BaseTestHandler):
            pass

        @ns.route('/second_handler', reply='[2]')
        class SecondTestHandler(BaseTestHandler):
            pass

        @ns.route('/third_handler', reply='[3]')
        class ThirdTestHandler(BaseTestHandler):
            pass

        response = self.fetch('/api/first_handler')
        assert response.code == 200
        assert response.body == b'[1]'
        response = self.fetch('/api/second_handler')
        assert response.code == 200
        assert response.body == b'[2]'
        response = self.fetch('/api/third_handler')
        assert response.code == 200
        assert response.body == b'[3]'

    def test_multiple_namespaces(self):
        ns1 = self.api.namespace('first_api')
        ns2 = self.api.namespace('sedond_api')

        class BaseTestHandler(RequestHandler):
            def initialize(self, reply):
                self.reply = reply

            def get(self):
                self.write(self.reply)

        @ns1.route('/first_handler', reply='[1]')
        class FirstTestHandler(BaseTestHandler):
            pass

        @ns1.route('/second_handler', reply='[2]')
        class SecondTestHandler(BaseTestHandler):
            pass

        @ns2.route('/third_handler', reply='[3]')
        class ThirdTestHandler(BaseTestHandler):
            pass

        @ns2.route('/fourth_handler', reply='[4]')
        class FourthTestHandler(BaseTestHandler):
            pass

        response = self.fetch('/first_api/first_handler')
        assert response.code == 200
        assert response.body == b'[1]'
        response = self.fetch('/first_api/second_handler')
        assert response.code == 200
        assert response.body == b'[2]'
        response = self.fetch('/sedond_api/third_handler')
        assert response.code == 200
        assert response.body == b'[3]'
        response = self.fetch('/sedond_api/fourth_handler')
        assert response.code == 200
        assert response.body == b'[4]'


class ApiLazyLoadingTest(AsyncHTTPTestCase):
    def get_app(self):
        # AsyncHTTPTestCase keeps application under self._app
        # but in order to keep convention and not touch _prefixed
        # variables, lets store it under self.app in ordef to use it later
        # for api initialization
        self.app = make_app()
        return self.app

    def test_lazy_loading(self):
        api = Api()
        ns = api.namespace('TestNamespace')

        @ns.route('/first_handler', reply='[0]')
        class SomeFirstHandler(RequestHandler):
            def initialize(self, reply):
                self.reply = reply

            def get(self):
                self.write(self.reply)

        api.init_app(self.app)
        response = self.fetch('/TestNamespace/first_handler')
        assert response.code == 200
        assert response.body == b'[0]'
