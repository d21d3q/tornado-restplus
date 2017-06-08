from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from tornado_restplus import Api

from tests.common import BaseEchoHandler

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

        @ns.route('/first_handler', reply='[1]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns.route('/second_handler', reply='[2]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        @ns.route('/third_handler', reply='[3]')
        class ThirdTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/api/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/api/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/api/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'

    def test_multiple_namespaces(self):
        ns1 = self.api.namespace('first_api')
        ns2 = self.api.namespace('sedond_api')

        @ns1.route('/first_handler', reply='[1]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns1.route('/second_handler', reply='[2]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        @ns2.route('/third_handler', reply='[3]')
        class ThirdTestHandler(BaseEchoHandler):
            pass

        @ns2.route('/fourth_handler', reply='[4]')
        class FourthTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/first_api/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/first_api/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/sedond_api/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'
        response = self.fetch('/sedond_api/fourth_handler')
        assert response.code == 200
        assert response.body == b'FourthTestHandler [4]'

    def test_multiple_routes(self):
        ns = self.api.namespace('api')

        @ns.route('/first_route_first_handler', reply='[1]')
        @ns.route('/second_route_first_handler', reply='[2]')
        @ns.route('/third_route_first_handler', reply='[3]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns.route('/first_route_second_handler', reply='[4]')
        @ns.route('/second_route_second_handler', reply='[5]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/api/first_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/api/second_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [2]'
        response = self.fetch('/api/third_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [3]'

        response = self.fetch('/api/first_route_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [4]'
        response = self.fetch('/api/second_route_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [5]'

    def test_multiple_paths_in_single_route(self):
        ns = self.api.namespace('api')

        @ns.route('/first_path_first_handler',
                  '/second_path_first_handler',
                  '/third_path_first_handler', reply='[1]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns.route('/first_path_second_handler',
                  '/second_path_second_handler',
                  reply='[2]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/api/first_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/api/second_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/api/third_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'

        response = self.fetch('/api/first_path_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/api/second_path_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'

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
