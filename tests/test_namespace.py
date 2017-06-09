from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from tornado_restplus import Api, Namespace

from tests.common import BaseEchoHandler


class NamespaceTest(AsyncHTTPTestCase):
    def get_app(self):
        app = Application()
        self.app = app
        return app

    def setUp(self):
        super(NamespaceTest, self).setUp()
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
        ns = self.api.namespace('ns')

        @ns.route('/first_handler', reply='[1]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns.route('/second_handler', reply='[2]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        @ns.route('/third_handler', reply='[3]')
        class ThirdTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/ns/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/ns/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/ns/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'

    def test_multiple_namespaces(self):
        ns1 = self.api.namespace('first_ns')
        ns2 = self.api.namespace('second_ns')

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

        response = self.fetch('/first_ns/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/first_ns/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/second_ns/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'
        response = self.fetch('/second_ns/fourth_handler')
        assert response.code == 200
        assert response.body == b'FourthTestHandler [4]'

    def test_multiple_routes(self):
        ns = self.api.namespace('ns')

        @ns.route('/first_route_first_handler', reply='[1]')
        @ns.route('/second_route_first_handler', reply='[2]')
        @ns.route('/third_route_first_handler', reply='[3]')
        class FirstTestHandler(BaseEchoHandler):
            pass

        @ns.route('/first_route_second_handler', reply='[4]')
        @ns.route('/second_route_second_handler', reply='[5]')
        class SecondTestHandler(BaseEchoHandler):
            pass

        response = self.fetch('/ns/first_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/ns/second_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [2]'
        response = self.fetch('/ns/third_route_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [3]'

        response = self.fetch('/ns/first_route_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [4]'
        response = self.fetch('/ns/second_route_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [5]'

    def test_multiple_paths_in_single_route(self):
        ns = self.api.namespace('ns')

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

        response = self.fetch('/ns/first_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/ns/second_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/ns/third_path_first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'

        response = self.fetch('/ns/first_path_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/ns/second_path_second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'

    def test_prefixes(self):
        api = Api(self.app, prefix='/api_prefix')
        ns = api.namespace('ns_prexif')

        @ns.route('/some_endpoint', reply='[0]')
        class SomeHandler(BaseEchoHandler):
            pass

        api.init_app(self.app)
        response = self.fetch('/api_prefix/ns_prexif/some_endpoint')
        assert response.code == 200
        assert response.body == b'SomeHandler [0]'

    def test_namespaces_lazy_loading(self):
        ns1 = Namespace('first_ns')
        ns2 = Namespace('second_ns')

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

        self.api.add_namespace(ns1)
        self.api.add_namespace(ns2)

        response = self.fetch('/first_ns/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/first_ns/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/second_ns/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'
        response = self.fetch('/second_ns/fourth_handler')
        assert response.code == 200
        assert response.body == b'FourthTestHandler [4]'

    def test_multiple_apis_and_namespaces(self):
        api1 = Api(self.app, prefix='/api1')
        api2 = Api(self.app, prefix='/api2')
        ns1 = Namespace('ns1')
        ns2 = Namespace('ns2')
        ns3 = Namespace('ns3')

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
        @ns3.route('/fourth_handler', reply='[5]')
        class FourthTestHandler(BaseEchoHandler):
            pass

        api1.add_namespace(ns1)
        api1.add_namespace(ns2)
        api2.add_namespace(ns2)
        api2.add_namespace(ns3)

        response = self.fetch('/api1/ns1/first_handler')
        assert response.code == 200
        assert response.body == b'FirstTestHandler [1]'
        response = self.fetch('/api1/ns1/second_handler')
        assert response.code == 200
        assert response.body == b'SecondTestHandler [2]'
        response = self.fetch('/api1/ns2/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'
        response = self.fetch('/api2/ns2/third_handler')
        assert response.code == 200
        assert response.body == b'ThirdTestHandler [3]'
        response = self.fetch('/api2/ns2/fourth_handler')
        assert response.code == 200
        assert response.body == b'FourthTestHandler [4]'
        response = self.fetch('/api2/ns3/fourth_handler')
        assert response.code == 200
        assert response.body == b'FourthTestHandler [5]'
