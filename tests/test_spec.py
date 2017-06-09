from tornado.web import Application
from unittest import TestCase

from tornado_restplus import Api
from tests.common import BaseEchoHandler


class SpecTest(TestCase):
    def setUp(self):
        super(SpecTest, self).setUp()
        self.app = Application()
        self.api = Api(self.app, title='Api title')
        self.ns = self.api.namespace('api')

    def test_route_spec(self):

        @self.ns.route('/path', _doc=True)
        class SomeHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                '''
                pass

            def post():
                pass

        @self.ns.route('/another_path', _doc=True)
        class AnotherHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting from another handler
                responses:
                    200:
                        description: A greeting to the client from another
                                     handler
                '''
                pass

        doc = self.api.spec.to_dict()
        assert doc['info']['title'] == 'Api title'
        assert '/api/path' in doc['paths']
        assert doc['paths']['/api/path']['get']['description'] == \
            'Get a greeting'
        assert '/api/another_path' in doc['paths']
        assert doc['paths']['/api/another_path']['get']['description'] == \
            'Get a greeting from another handler'

    def test_route_without_spec(self):
        @self.ns.route('/path', _doc=False)
        class SomeHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                '''
                pass

            def post():
                pass

        doc = self.api.spec.to_dict()
        assert doc['info']['title'] == 'Api title'
        assert '/api/path' not in doc['paths']
