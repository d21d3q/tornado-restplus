# from unittest import TestCase
from tornado.web import Application, RequestHandler
from tornado.testing import AsyncHTTPTestCase

from tornado_restplus import Api, Namespace

from tests.common import BaseEchoHandler

# class ApiUnitTest(TestCase):
#     pass

class ApiTest(AsyncHTTPTestCase):
    def get_app(self):
        # AsyncHTTPTestCase keeps application under self._app
        # but in order to keep convention and not touch _prefixed
        # variables, lets store it under self.app in ordef to use it later
        # for api initialization
        self.app = Application()
        return self.app

    def test_lazy_loading(self):
        api = Api()
        ns = api.namespace('TestNamespace')

        @ns.route('/some_endpoint', reply='[0]')
        class SomeHandler(BaseEchoHandler):
            pass

        api.init_app(self.app)
        response = self.fetch('/TestNamespace/some_endpoint')
        assert response.code == 200
        assert response.body == b'SomeHandler [0]'

    def test_register_resource(self):
        api = Api(self.app)

        class SomeHandler(BaseEchoHandler):
            pass

        api.register_resource(None, SomeHandler, '/some_endpoint', reply='[0]')
        response = self.fetch('/some_endpoint')
        assert response.code == 200
        assert response.body == b'SomeHandler [0]'

    def test_api_prefix(self):
        api = Api(self.app, prefix='/api')

        class SomeHandler(BaseEchoHandler):
            pass

        api.register_resource(None, SomeHandler, '/some_endpoint', reply='[0]')
        response = self.fetch('/api/some_endpoint')
        assert response.code == 200
        assert response.body == b'SomeHandler [0]'

    def test_namepsace_path(self):
        api = Api(self.app, prefix='/api')
        ns1 = Namespace('ns1_prefix')
        ns2 = Namespace('ns1_prefix')

        @ns1.route('/endpoint1', reply='[0]')
        @ns2.route('/endpoint2', reply='[1]')
        class SomeHandler(BaseEchoHandler):
            pass

        api.add_namespace(ns1, path='/n1s_path')
        api.add_namespace(ns2, path='/ns2_path')

        response = self.fetch('/api/n1s_path/endpoint1')
        assert response.code == 200
        assert response.body == b'SomeHandler [0]'

        response = self.fetch('/api/ns2_path/endpoint2')
        assert response.code == 200
        assert response.body == b'SomeHandler [1]'
